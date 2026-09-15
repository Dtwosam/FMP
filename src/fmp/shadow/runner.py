from __future__ import annotations

import hashlib
import time
from collections.abc import Callable, Mapping
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Protocol
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar

from .bars import LiveBarBuilder
from .contracts import HeartbeatEvent, LIVENESS_TIMEOUT_SECONDS, NormalizedQuote
from .evidence import EvidenceWriter
from .normalization import ProviderMessageError, StreamSegmentNormalizer
from .oanda import OandaPracticePricingStream, OandaPracticeStreamError, parse_provider_line
from .simulation import ShadowSimulator
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
    ) -> None:
        self.evidence = evidence
        self.bar_builder = bar_builder or LiveBarBuilder()
        self.simulator = simulator or ShadowSimulator()
        self.strategy_adapter = strategy_adapter
        self.normalizer = StreamSegmentNormalizer()
        self.ineligible_london_dates: set[date] = set()
        self.stale = False
        self._started = False
        self._last_valid_source_time: datetime | None = None
        self._last_valid_received_at: datetime | None = None
        self._last_valid_monotonic_ns: int | None = None
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

    def disconnect(self, *, now_utc: datetime, reason: str = "stream_end") -> None:
        _require_utc(now_utc, field_name="now_utc")
        if not self._started:
            raise RuntimeError("Phase 8 shadow runner is not started")
        self.evidence.append_operational(
            {"event": "disconnect", "timestamp_utc": now_utc, "reason": reason}
        )
        self._mark_date_ineligible(_london_date(now_utc), reason="disconnect")
        self.simulator.mark_stale_gap(now_utc, now_utc)
        self._record_scenario_changes()

    def process_line(
        self,
        line: bytes,
        *,
        received_at_utc: datetime,
        receive_monotonic_ns: int,
    ) -> None:
        try:
            raw = parse_provider_line(line)
        except OandaPracticeStreamError:
            self.evidence.append_operational(
                {
                    "event": "rejection",
                    "timestamp_utc": received_at_utc,
                    "reason": "provider_line_invalid",
                }
            )
            raise
        self.process_provider_message(
            raw,
            received_at_utc=received_at_utc,
            receive_monotonic_ns=receive_monotonic_ns,
        )

    def process_provider_message(
        self,
        raw: Mapping[str, object],
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

        try:
            event = self.normalizer.accept(
                raw,
                received_at_utc=received_at_utc,
                receive_monotonic_ns=receive_monotonic_ns,
            )
        except ProviderMessageError:
            self.evidence.append_operational(
                {
                    "event": "rejection",
                    "timestamp_utc": received_at_utc,
                    "reason": "provider_message_rejected",
                }
            )
            raise

        if event is None:
            self.evidence.append_raw(
                raw,
                received_at_utc=received_at_utc,
                receive_monotonic_ns=receive_monotonic_ns,
            )
            return

        if self._last_valid_monotonic_ns is not None:
            gap_ns = receive_monotonic_ns - self._last_valid_monotonic_ns
            if gap_ns < 0:
                raise ValueError("receive monotonic time regressed")
            if gap_ns >= _LIVENESS_TIMEOUT_NS and not self.stale:
                assert self._last_valid_source_time is not None
                self._mark_stale(
                    start_utc=self._last_valid_source_time,
                    end_utc=event.source_time_utc,
                    detected_at_utc=received_at_utc,
                )

        self.evidence.append_raw(
            raw,
            received_at_utc=received_at_utc,
            receive_monotonic_ns=receive_monotonic_ns,
        )
        self.evidence.append_normalized(event)

        if self.stale:
            self.stale = False
            self.evidence.append_operational(
                {"event": "recovered", "timestamp_utc": received_at_utc}
            )

        self._last_valid_source_time = event.source_time_utc
        self._last_valid_received_at = received_at_utc
        self._last_valid_monotonic_ns = receive_monotonic_ns

        if isinstance(event, NormalizedQuote):
            completed = self.bar_builder.on_quote(event)
        elif isinstance(event, HeartbeatEvent):
            completed = self.bar_builder.on_time_advance(event.source_time_utc)
        else:
            raise TypeError("unsupported normalized Phase 8 event")

        self._record_completed_bars(completed)

        if isinstance(event, NormalizedQuote):
            self.simulator.on_quote(event)
        else:
            self.simulator.on_time_advance(event.source_time_utc)
        self._record_scenario_changes()

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
        if self._last_valid_monotonic_ns is None or self.stale:
            return self.stale
        gap_ns = now_monotonic_ns - self._last_valid_monotonic_ns
        if gap_ns < 0:
            raise ValueError("monotonic clock regressed")
        if gap_ns >= _LIVENESS_TIMEOUT_NS:
            assert self._last_valid_source_time is not None
            self._mark_stale(
                start_utc=self._last_valid_source_time,
                end_utc=now_utc,
                detected_at_utc=now_utc,
            )
        return self.stale

    def _mark_stale(
        self,
        *,
        start_utc: datetime,
        end_utc: datetime,
        detected_at_utc: datetime,
    ) -> None:
        if end_utc <= start_utc:
            end_utc = start_utc + timedelta(microseconds=1)
        self.stale = True
        self._mark_date_ineligible(_london_date(detected_at_utc), reason="stale")
        self.bar_builder.mark_stale_interval(start_utc, end_utc)
        self.simulator.mark_stale_gap(start_utc, end_utc)
        self.evidence.append_operational(
            {
                "event": "stale",
                "timestamp_utc": detected_at_utc,
                "gap_start_utc": start_utc,
                "gap_end_utc": end_utc,
            }
        )
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


def run_live_shadow_capture(
    *,
    account_id: str,
    token: str,
    campaign_dir: Path,
    code_commit: str,
    utc_now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    monotonic_ns: Callable[[], int] = time.monotonic_ns,
    stream_factory: Callable[..., OandaPracticePricingStream] = OandaPracticePricingStream,
) -> int:
    campaign_dir = Path(campaign_dir)
    registration = campaign_dir / "registration.json"
    if not registration.is_file():
        raise RuntimeError("Phase 8 campaign registration is required before live capture")

    start = utc_now()
    _require_utc(start, field_name="run_start_utc")
    restarted = any(path.is_dir() for path in campaign_dir.glob("segment-*"))
    segment_name = start.strftime("segment-%Y%m%dT%H%M%S.%fZ")
    segment_dir = campaign_dir / segment_name
    account_fingerprint = hashlib.sha256(account_id.encode("utf-8")).hexdigest()
    evidence = EvidenceWriter(
        segment_dir,
        code_commit=code_commit,
        account_fingerprint_sha256=account_fingerprint,
        run_start_utc=start,
    )
    runner = ShadowRunner(evidence=evidence)
    runner.start(now_utc=start, restarted=restarted)
    stream = stream_factory(account_id=account_id, token=token)

    try:
        for line in stream.iter_lines():
            received_at = utc_now()
            mono = monotonic_ns()
            runner.process_line(
                line,
                received_at_utc=received_at,
                receive_monotonic_ns=mono,
            )
    except (OandaPracticeStreamError, ProviderMessageError):
        now = utc_now()
        runner.check_liveness(now_utc=now, now_monotonic_ns=monotonic_ns())
        runner.evidence.append_operational(
            {"event": "rejection", "timestamp_utc": now, "reason": "stream_failed"}
        )
        runner.disconnect(now_utc=now, reason="stream_failed")
        return 4

    runner.disconnect(now_utc=utc_now(), reason="stream_end")
    return 0


__all__ = ["EvidenceSink", "ShadowRunner", "run_live_shadow_capture"]
