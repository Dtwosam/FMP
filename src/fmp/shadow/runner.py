from __future__ import annotations

import time
from dataclasses import asdict
from collections.abc import Callable, Mapping
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Protocol
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, EquityCheckpoint, QuoteBar
from fmp.reporting.backtest import compute_backtest_metrics

from .bars import LiveBarBuilder
from .campaign import load_campaign_registration
from .contracts import (
    LIVENESS_TIMEOUT_SECONDS,
    NormalizedQuote,
    STARTING_EQUITY_USD,
)
from .evidence import EvidenceWriter
from .mt5_bridge import (
    BridgeFileTail,
    BridgeHeartbeatRecord,
    BridgeProtocolError,
    BridgeRecord,
    BridgeSessionValidator,
    BridgeStartRecord,
    BridgeTickRecord,
)
from .simulation import ShadowSimulator
from .state import restore_shadow_simulator
from .strategy import ShadowStrategyDecision, generate_shadow_strategy_decisions


LONDON = ZoneInfo("Europe/London")
_LIVENESS_TIMEOUT_NS = int(LIVENESS_TIMEOUT_SECONDS * 1_000_000_000)
_FIFTEEN_MINUTES = timedelta(minutes=15)


class EvidenceSink(Protocol):
    code_commit: str
    account_fingerprint_sha256: str

    def append_raw(
        self,
        provider_object: Mapping[str, object],
        *,
        received_at_utc: datetime,
        receive_monotonic_ns: int,
    ) -> None: ...

    def append_normalized(self, event: object) -> None: ...
    def append_bar(self, timeframe: str, bar: object) -> None: ...
    def append_decision(self, record: Mapping[str, object]) -> None: ...
    def append_scenario(self, record: Mapping[str, object]) -> None: ...
    def append_operational(self, record: Mapping[str, object]) -> None: ...


def _require_utc(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} must use UTC")


def _london_date(value: datetime) -> date:
    _require_utc(value, field_name="timestamp")
    return value.astimezone(LONDON).date()


class ShadowRunner:
    def __init__(
        self,
        *,
        evidence: EvidenceSink,
        bar_builder: LiveBarBuilder | None = None,
        simulator: ShadowSimulator | None = None,
        strategy_adapter: Callable[
            [tuple[QuoteBar, ...]], tuple[ShadowStrategyDecision, ...]
        ] = generate_shadow_strategy_decisions,
        processing_monotonic_ns: Callable[[], int] | None = None,
    ) -> None:
        self.evidence = evidence
        self.bar_builder = bar_builder or LiveBarBuilder()
        self.simulator = simulator or ShadowSimulator()
        self.strategy_adapter = strategy_adapter
        self._processing_monotonic_ns = processing_monotonic_ns
        self.bridge_validator = BridgeSessionValidator()
        self._bridge_last_monotonic_ns: int | None = None
        self._market_last_monotonic_ns: int | None = None
        self._bridge_start_received_at_utc: datetime | None = None
        self._last_market_source_time: datetime | None = None
        self._market_quiet = False
        self._market_quiet_started_at_utc: datetime | None = None
        self.ineligible_london_dates: set[date] = set()
        self.stale = False
        self._started = False
        self._strategy_bars: dict[date, list[QuoteBar]] = {}
        self._seen_decisions: set[str] = set()
        self._date_ineligible_evidenced: set[date] = set()
        self._seen_open: dict[float, set[str]] = {
            scenario: set() for scenario in self.simulator.states
        }
        self._trade_counts: dict[float, int] = {
            scenario: 0 for scenario in self.simulator.states
        }
        self._seen_outcomes: dict[float, set[str]] = {
            scenario: set() for scenario in self.simulator.states
        }
        self._seen_rejections: dict[float, set[str]] = {
            scenario: set() for scenario in self.simulator.states
        }
        self._metrics_recorded = False

    def start(self, *, now_utc: datetime, restarted: bool) -> None:
        _require_utc(now_utc, field_name="now_utc")
        if self._started:
            raise RuntimeError("Phase 8 shadow runner already started")
        self._started = True
        self.evidence.append_operational(
            {
                "event": "segment_start",
                "timestamp_utc": now_utc,
                "code_commit": self.evidence.code_commit,
                "account_fingerprint_sha256": self.evidence.account_fingerprint_sha256,
            }
        )
        if restarted:
            self.evidence.append_operational(
                {"event": "restart", "timestamp_utc": now_utc}
            )
            self._mark_date_ineligible(_london_date(now_utc), reason="restart")
            self.simulator.mark_stale_gap(now_utc, now_utc)
            self._record_scenario_changes()
        self.evidence.append_operational(
            {"event": "connect", "timestamp_utc": now_utc}
        )

    def disconnect(self, *, now_utc: datetime, reason: str = "bridge_end") -> None:
        _require_utc(now_utc, field_name="now_utc")
        if not self._started:
            raise RuntimeError("Phase 8 shadow runner is not started")
        self.evidence.append_operational(
            {"event": "disconnect", "timestamp_utc": now_utc, "reason": reason}
        )
        self._mark_date_ineligible(_london_date(now_utc), reason="disconnect")
        self.simulator.mark_stale_gap(now_utc, now_utc)
        self._record_scenario_changes()
        self._record_financial_metrics()

    def _process_normalized_event(
        self,
        event: NormalizedQuote,
        *,
        received_at_utc: datetime,
        receive_monotonic_ns: int,
    ) -> None:
        self.evidence.append_normalized(event)
        if self._processing_monotonic_ns is not None:
            append_completed_monotonic_ns = self._processing_monotonic_ns()
            if (
                isinstance(append_completed_monotonic_ns, bool)
                or not isinstance(append_completed_monotonic_ns, int)
                or append_completed_monotonic_ns < receive_monotonic_ns
            ):
                raise ValueError("normalized append completion monotonic time is invalid")
            self.evidence.append_operational(
                {
                    "event": "normalized_append_latency",
                    "timestamp_utc": received_at_utc,
                    "source_time_utc": event.source_time_utc,
                    "receive_monotonic_ns": receive_monotonic_ns,
                    "append_completed_monotonic_ns": append_completed_monotonic_ns,
                    "processing_latency_ms": (
                        append_completed_monotonic_ns - receive_monotonic_ns
                    )
                    / 1_000_000,
                }
            )

        if self.stale:
            self.stale = False
            self.evidence.append_operational(
                {"event": "recovered", "timestamp_utc": received_at_utc}
            )
        if self._market_quiet:
            self.evidence.append_operational(
                {
                    "event": "market_resumed",
                    "timestamp_utc": received_at_utc,
                    "gap_start_utc": self._market_quiet_started_at_utc
                    or event.source_time_utc,
                    "gap_end_utc": event.source_time_utc,
                }
            )
            self._market_quiet = False
            self._market_quiet_started_at_utc = None

        completed = self.bar_builder.on_quote(event)
        self._record_completed_bars(completed)
        self.simulator.on_quote(event)
        self._record_scenario_changes()

    def process_bridge_record(
        self,
        record: BridgeRecord,
        *,
        received_at_utc: datetime,
        receive_monotonic_ns: int,
    ) -> None:
        if not self._started:
            raise RuntimeError("Phase 8 shadow runner is not started")
        _require_utc(received_at_utc, field_name="received_at_utc")
        if (
            isinstance(receive_monotonic_ns, bool)
            or not isinstance(receive_monotonic_ns, int)
            or receive_monotonic_ns < 0
        ):
            raise ValueError("receive_monotonic_ns must be a non-negative integer")

        raw = asdict(record)
        try:
            event = self.bridge_validator.accept(
                record,
                received_at_utc=received_at_utc,
                receive_monotonic_ns=receive_monotonic_ns,
            )
        except (BridgeProtocolError, TypeError):
            self.evidence.append_operational(
                {
                    "event": "rejection",
                    "timestamp_utc": received_at_utc,
                    "reason": "bridge_record_rejected",
                }
            )
            raise

        self.evidence.append_raw(
            raw,
            received_at_utc=received_at_utc,
            receive_monotonic_ns=receive_monotonic_ns,
        )

        if isinstance(record, BridgeStartRecord):
            self._bridge_last_monotonic_ns = receive_monotonic_ns
            self._market_last_monotonic_ns = receive_monotonic_ns
            self._bridge_start_received_at_utc = received_at_utc
            self._last_market_source_time = None
            return

        if self._bridge_last_monotonic_ns is None or self._market_last_monotonic_ns is None:
            raise BridgeProtocolError("bridge record received before BRIDGE_START binding")

        bridge_gap_ns = receive_monotonic_ns - self._bridge_last_monotonic_ns
        market_gap_ns = receive_monotonic_ns - self._market_last_monotonic_ns
        if bridge_gap_ns < 0 or market_gap_ns < 0:
            raise ValueError("receive monotonic time regressed")

        gap_start = (
            self._last_market_source_time
            or self._bridge_start_received_at_utc
            or received_at_utc
        )
        if not self.stale and bridge_gap_ns >= _LIVENESS_TIMEOUT_NS:
            self._mark_stale(
                start_utc=gap_start,
                end_utc=received_at_utc,
                detected_at_utc=received_at_utc,
                liveness_reason="bridge",
            )
        elif (
            not self.stale
            and not self._market_quiet
            and market_gap_ns >= _LIVENESS_TIMEOUT_NS
        ):
            self._mark_market_quiet(
                start_utc=gap_start,
                detected_at_utc=received_at_utc,
                observed_gap_ns=market_gap_ns,
            )

        self._bridge_last_monotonic_ns = receive_monotonic_ns
        if isinstance(record, BridgeHeartbeatRecord):
            return
        if not isinstance(record, BridgeTickRecord):
            raise TypeError("unsupported MT5 bridge record")
        if event is None:
            return
        if not isinstance(event, NormalizedQuote):
            raise TypeError("MT5 bridge tick did not normalize to a quote")

        self._market_last_monotonic_ns = receive_monotonic_ns
        self._last_market_source_time = event.source_time_utc
        self._process_normalized_event(
            event,
            received_at_utc=received_at_utc,
            receive_monotonic_ns=receive_monotonic_ns,
        )

    def check_liveness(
        self,
        *,
        now_utc: datetime,
        now_monotonic_ns: int,
    ) -> bool:
        _require_utc(now_utc, field_name="now_utc")
        if (
            isinstance(now_monotonic_ns, bool)
            or not isinstance(now_monotonic_ns, int)
            or now_monotonic_ns < 0
        ):
            raise ValueError("now_monotonic_ns must be a non-negative integer")
        if self._bridge_last_monotonic_ns is not None:
            if self.stale:
                return True
            if self._market_last_monotonic_ns is None:
                raise RuntimeError("MT5 bridge market liveness baseline is missing")
            bridge_gap_ns = now_monotonic_ns - self._bridge_last_monotonic_ns
            market_gap_ns = now_monotonic_ns - self._market_last_monotonic_ns
            if bridge_gap_ns < 0 or market_gap_ns < 0:
                raise ValueError("monotonic clock regressed")
            gap_start = (
                self._last_market_source_time
                or self._bridge_start_received_at_utc
                or now_utc
            )
            if bridge_gap_ns >= _LIVENESS_TIMEOUT_NS:
                self._mark_stale(
                    start_utc=gap_start,
                    end_utc=now_utc,
                    detected_at_utc=now_utc,
                    liveness_reason="bridge",
                )
            elif not self._market_quiet and market_gap_ns >= _LIVENESS_TIMEOUT_NS:
                self._mark_market_quiet(
                    start_utc=gap_start,
                    detected_at_utc=now_utc,
                    observed_gap_ns=market_gap_ns,
                )
            return self.stale

        return self.stale

    def _mark_market_quiet(
        self,
        *,
        start_utc: datetime,
        detected_at_utc: datetime,
        observed_gap_ns: int,
    ) -> None:
        self._market_quiet = True
        self._market_quiet_started_at_utc = start_utc
        self.evidence.append_operational(
            {
                "event": "market_quiet",
                "timestamp_utc": detected_at_utc,
                "gap_start_utc": start_utc,
                "observed_gap_seconds": observed_gap_ns / 1_000_000_000,
            }
        )

    def _mark_stale(
        self,
        *,
        start_utc: datetime,
        end_utc: datetime,
        detected_at_utc: datetime,
        liveness_reason: str | None = None,
    ) -> None:
        if end_utc <= start_utc:
            end_utc = start_utc + timedelta(microseconds=1)
        self.stale = True
        self._mark_date_ineligible(_london_date(detected_at_utc), reason="stale")
        self.bar_builder.mark_stale_interval(start_utc, end_utc)
        self.simulator.mark_stale_gap(start_utc, end_utc)
        stale_record: dict[str, object] = {
            "event": "stale",
            "timestamp_utc": detected_at_utc,
            "gap_start_utc": start_utc,
            "gap_end_utc": end_utc,
        }
        if liveness_reason is not None:
            stale_record["liveness_reason"] = liveness_reason
        self.evidence.append_operational(stale_record)
        self._record_scenario_changes()

    def _mark_date_ineligible(self, session_date: date, *, reason: str) -> None:
        self.ineligible_london_dates.add(session_date)
        if session_date in self._date_ineligible_evidenced:
            return
        self._date_ineligible_evidenced.add(session_date)
        self.evidence.append_decision(
            {
                "event": "date_ineligible",
                "session_date": session_date,
                "reason": reason,
            }
        )

    def _record_completed_bars(self, completed: tuple[QuoteBar, ...]) -> None:
        drain = getattr(self.bar_builder, "drain_completed_minute_bars", None)
        if callable(drain):
            for minute_bar in drain():
                self.evidence.append_bar("1m", minute_bar)
        for fifteen_bar in completed:
            self.evidence.append_bar("15m", fifteen_bar)
            session_date = _london_date(fifteen_bar.timestamp_utc)
            if session_date in self.ineligible_london_dates:
                self._mark_date_ineligible(session_date, reason="date_already_ineligible")
                continue
            day_bars = self._strategy_bars.setdefault(session_date, [])
            day_bars.append(fifteen_bar)
            self._evaluate_strategy(session_date, tuple(day_bars))

    def _evaluate_strategy(
        self,
        session_date: date,
        bars: tuple[QuoteBar, ...],
    ) -> None:
        results = self.strategy_adapter(bars)
        knowledge_time = max(item.timestamp_utc for item in bars) + _FIFTEEN_MINUTES
        for result in results:
            candidate = result.candidate
            decision = result.decision
            decision_id = decision.decision_id
            if decision_id in self._seen_decisions:
                continue

            if candidate.reason_code == "INCOMPLETE_SESSION":
                missing = candidate.metadata.get("missing_timestamp_utc")
                if isinstance(missing, datetime) and missing >= knowledge_time:
                    continue
                self._mark_date_ineligible(session_date, reason="missing_required_context")

            self._seen_decisions.add(decision_id)
            self.evidence.append_decision(
                {
                    "event": "strategy_decision",
                    "candidate": candidate,
                    "decision": decision,
                    "scheduled_exit": result.scheduled_exit,
                }
            )
            if decision.direction is Direction.NO_TRADE:
                continue
            if result.scheduled_exit is None:
                self.evidence.append_operational(
                    {
                        "event": "rejection",
                        "timestamp_utc": knowledge_time,
                        "reason": "directional_decision_missing_scheduled_exit",
                    }
                )
                self._mark_date_ineligible(session_date, reason="invalid_strategy_output")
                continue
            self.simulator.register_decision(decision, result.scheduled_exit)

    def _record_scenario_changes(self) -> None:
        for scenario, state in self.simulator.states.items():
            seen_open = self._seen_open[scenario]
            for decision_id in sorted(state.open_positions):
                if decision_id in seen_open:
                    continue
                seen_open.add(decision_id)
                self.evidence.append_scenario(
                    {
                        "event": "position_opened",
                        "slippage_pips": scenario,
                        "decision_id": decision_id,
                        "position": state.open_positions[decision_id],
                    }
                )

            trade_count = self._trade_counts[scenario]
            for trade in state.completed_trades[trade_count:]:
                self.evidence.append_scenario(
                    {
                        "event": "trade_completed",
                        "slippage_pips": scenario,
                        "decision_id": trade.decision_id,
                        "trade": trade,
                    }
                )
            self._trade_counts[scenario] = len(state.completed_trades)

            seen_outcomes = self._seen_outcomes[scenario]
            for decision_id in sorted(state.outcomes):
                if decision_id in seen_outcomes:
                    continue
                seen_outcomes.add(decision_id)
                self.evidence.append_scenario(
                    {
                        "event": "outcome",
                        "slippage_pips": scenario,
                        "decision_id": decision_id,
                        "outcome": state.outcomes[decision_id],
                    }
                )

            seen_rejections = self._seen_rejections[scenario]
            for decision_id in sorted(state.rejections):
                if decision_id in seen_rejections:
                    continue
                seen_rejections.add(decision_id)
                self.evidence.append_scenario(
                    {
                        "event": "risk_rejection",
                        "slippage_pips": scenario,
                        "decision_id": decision_id,
                        "rejection": state.rejections[decision_id],
                    }
                )

    def _record_financial_metrics(self) -> None:
        if self._metrics_recorded:
            return
        self._metrics_recorded = True
        for scenario, state in self.simulator.states.items():
            trades = tuple(
                sorted(
                    state.completed_trades,
                    key=lambda item: (item.exit_timestamp_utc, item.trade_id),
                )
            )
            checkpoints = tuple(
                EquityCheckpoint(
                    timestamp_utc=trade.exit_timestamp_utc,
                    realized_risk_equity_usd=trade.risk_equity_after_usd,
                )
                for trade in trades
            )
            metrics = compute_backtest_metrics(
                starting_equity_usd=STARTING_EQUITY_USD,
                trades=trades,
                equity_checkpoints=checkpoints,
            )
            self.evidence.append_scenario(
                {
                    "event": "financial_metrics",
                    "slippage_pips": scenario,
                    "metrics": metrics,
                }
            )


def run_live_shadow_capture(
    *,
    bridge_tail: BridgeFileTail,
    campaign_dir: Path,
    code_commit: str,
    utc_now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    monotonic_ns: Callable[[], int] = time.monotonic_ns,
    sleep: Callable[[float], None] = time.sleep,
) -> int:
    campaign_dir = Path(campaign_dir)
    load_campaign_registration(campaign_dir, code_commit=code_commit)

    start = utc_now()
    _require_utc(start, field_name="run_start_utc")
    restarted = any(path.is_dir() for path in campaign_dir.glob("segment-*"))
    segment_name = start.strftime("segment-%Y%m%dT%H%M%S.%fZ")
    segment_dir = campaign_dir / segment_name
    bridge_start = bridge_tail.start_record
    evidence = EvidenceWriter(
        segment_dir,
        code_commit=code_commit,
        bridge_source_commit=code_commit,
        bridge_session_id=bridge_start.bridge_session_id,
        server=bridge_start.server,
        account_fingerprint_sha256=bridge_start.account_fingerprint,
        run_start_utc=start,
    )
    simulator = restore_shadow_simulator(campaign_dir) if restarted else ShadowSimulator()
    runner = ShadowRunner(
        evidence=evidence,
        simulator=simulator,
        processing_monotonic_ns=monotonic_ns,
    )
    runner.start(now_utc=start, restarted=restarted)
    runner.process_bridge_record(
        bridge_start,
        received_at_utc=start,
        receive_monotonic_ns=monotonic_ns(),
    )

    try:
        while True:
            records = bridge_tail.read_available()
            if not records:
                now = utc_now()
                runner.check_liveness(
                    now_utc=now,
                    now_monotonic_ns=monotonic_ns(),
                )
                sleep(0.05)
                continue
            for record in records:
                received_at = utc_now()
                runner.process_bridge_record(
                    record,
                    received_at_utc=received_at,
                    receive_monotonic_ns=monotonic_ns(),
                )
    except KeyboardInterrupt:
        runner.disconnect(now_utc=utc_now(), reason="operator_stop")
        return 0
    except BridgeProtocolError:
        now = utc_now()
        runner.disconnect(now_utc=now, reason="bridge_failed")
        return 4
    except (OSError, ValueError, TypeError):
        now = utc_now()
        runner.evidence.append_operational(
            {
                "event": "rejection",
                "timestamp_utc": now,
                "reason": "bridge_capture_failed",
            }
        )
        runner.disconnect(now_utc=now, reason="bridge_failed")
        return 4


__all__ = ["EvidenceSink", "ShadowRunner", "restore_shadow_simulator", "run_live_shadow_capture"]
