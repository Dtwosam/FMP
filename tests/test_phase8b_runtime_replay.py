from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone

from fmp.contracts import Decision, Direction, ScheduledExit
from fmp.phase8b.bridge import Phase8BBridgeStartRecord, Phase8BBridgeTickRecord
from fmp.phase8b.capture import (
    PHASE8B_CAPTURE_EXPERIMENT_ID,
    PHASE8B_CAPTURE_FOUNDATION_READY,
    PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL,
    Phase8BCaptureFeedEnvelope,
    READER_START_SEMANTICS,
    validate_phase8b_capture_preflight,
)
from fmp.phase8b.design import (
    BRIDGE_FILE_BY_SYMBOL,
    LIVENESS_TIMEOUT_SECONDS,
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
    QUOTE_DEADLINE_SECONDS,
    SLIPPAGE_SCENARIOS,
)
from fmp.phase8b.runtime import (
    PHASE8B_RUNTIME_REPLAY_KERNEL_READY,
    PHASE8B_SEGMENT_PROTOCOL,
    PortfolioShadowSimulator,
    compile_phase8b_segment,
    replay_phase8b_segment,
)
from fmp.portfolio.contracts import ChampionSet, PHASE8A_EXPERIMENT_ID
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.risk import RiskConfig
from fmp.shadow.contracts import ShadowOutcome


UTC = timezone.utc
PREPARED = datetime(2026, 9, 22, 14, 0, tzinfo=UTC)
CAMPAIGN_START = datetime(2026, 9, 22, 13, 55, tzinfo=UTC)
ACCOUNT = "a" * 64
SERVER = "FPMarketsSC-Demo"
COMMIT = "2" * 40


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _strategies():
    inventory = build_phase4_baseline_inventory()
    chosen = []
    symbols = set()
    for record in inventory:
        strategy = record.strategy
        if strategy.symbol in symbols:
            continue
        chosen.append(strategy)
        symbols.add(strategy.symbol)
        if len(chosen) == 2:
            break
    if len(chosen) != 2:
        raise AssertionError("fixture requires two distinct Phase 4 symbols")
    return tuple(sorted(chosen, key=lambda item: item.fingerprint))


def _preflight():
    strategies = _strategies()
    champion = ChampionSet(
        champion_set_id="phase8b-dec050-test",
        experiment_id=PHASE8A_EXPERIMENT_ID,
        strategies=strategies,
    )
    rows = [
        {
            "fingerprint": item.fingerprint,
            "identity_json": item.identity_json,
            "family": item.family,
            "symbol": item.symbol,
            "timeframe": item.timeframe,
            "parameters_json": item.parameters_json,
            "code_commit": item.code_commit,
            "lifecycle": "SHADOW_CANDIDATE",
            "evidence_id": "EXP-20260922-016:TEST",
        }
        for item in strategies
    ]
    symbols = sorted({item.symbol for item in strategies})
    timeframe_order = {"5m": 0, "15m": 1, "1h": 2}
    timeframes = sorted(
        {item.timeframe for item in strategies},
        key=timeframe_order.__getitem__,
    )
    sessions = {
        symbol: f"{index + 1:064x}"
        for index, symbol in enumerate(symbols)
    }
    payload = {
        "protocol": PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL,
        "experiment_id": PHASE8B_CAPTURE_EXPERIMENT_ID,
        "outcome": PHASE8B_CAPTURE_FOUNDATION_READY,
        "registration_sha256": "1" * 64,
        "registration_fingerprint": "2" * 64,
        "start_authorization_sha256": "3" * 64,
        "start_authorization_fingerprint": "4" * 64,
        "capture_foundation_code_commit": "1" * 40,
        "prepared_at_utc": PREPARED.isoformat().replace("+00:00", "Z"),
        "campaign_start_utc": CAMPAIGN_START.isoformat().replace("+00:00", "Z"),
        "first_london_date": "2026-09-22",
        "reader_start_semantics": READER_START_SEMANTICS,
        "champion_set_id": champion.champion_set_id,
        "champion_set_fingerprint": champion.fingerprint,
        "strategy_count": len(rows),
        "strategy_fingerprints": [item["fingerprint"] for item in rows],
        "strategies": rows,
        "required_symbols": symbols,
        "required_timeframes": timeframes,
        "provider": MT5_PROVIDER,
        "transport": MT5_TRANSPORT,
        "connector_protocol": MT5_BRIDGE_PROTOCOL,
        "bridge_file_by_symbol": {
            symbol: BRIDGE_FILE_BY_SYMBOL[symbol] for symbol in symbols
        },
        "account_fingerprint": ACCOUNT,
        "server": SERVER,
        "bridge_session_id_by_symbol": sessions,
        "liveness": {
            "bridge_timeout_seconds": LIVENESS_TIMEOUT_SECONDS,
            "market_quiet_threshold_seconds": LIVENESS_TIMEOUT_SECONDS,
            "quote_deadline_seconds": QUOTE_DEADLINE_SECONDS,
            "per_required_symbol": True,
            "market_quiet_is_bridge_failure": False,
            "backfill_allowed": False,
            "interpolation_allowed": False,
            "alternate_provider_repair_allowed": False,
        },
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "capture_runtime_ready": True,
        "live_shadow_segment_started": False,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    result = payload | {"capture_preflight_fingerprint": _digest(payload)}
    validate_phase8b_capture_preflight(result)
    return result


def _capture_records(preflight):
    feeds = {}
    for symbol in preflight["required_symbols"]:
        start = Phase8BBridgeStartRecord(
            protocol=preflight["connector_protocol"],
            bridge_session_id=preflight["bridge_session_id_by_symbol"][symbol],
            symbol=symbol,
            server=preflight["server"],
            account_fingerprint=preflight["account_fingerprint"],
            account_mode="DEMO",
            bridge_start_time_msc=int(CAMPAIGN_START.timestamp() * 1000),
        )
        feeds[symbol] = Phase8BCaptureFeedEnvelope(
            preflight=preflight,
            start_record=start,
        )

    result = []
    monotonic = 1
    for offset_seconds in range(0, 131, 10):
        source_time = PREPARED + timedelta(seconds=offset_seconds)
        for symbol in sorted(feeds):
            base = 150.0 if symbol == "USDJPY" else 1.10
            tick = Phase8BBridgeTickRecord(
                protocol=preflight["connector_protocol"],
                bridge_session_id=preflight["bridge_session_id_by_symbol"][symbol],
                symbol=symbol,
                server=preflight["server"],
                account_fingerprint=preflight["account_fingerprint"],
                source_time_msc=int(source_time.timestamp() * 1000),
                bid=base,
                ask=base + (0.02 if symbol == "USDJPY" else 0.0002),
                flags=6,
            )
            accepted = feeds[symbol].accept(
                tick,
                received_at_utc=source_time,
                receive_monotonic_ns=monotonic * 1_000_000_000,
            )
            monotonic += 1
            if accepted is not None:
                envelope, _ = accepted
                result.append(envelope)
    return tuple(result)


class Phase8BRuntimeReplayKernelTests(unittest.TestCase):
    def test_segment_compiler_emits_only_complete_no_backfill_bars(self) -> None:
        preflight = _preflight()
        records = _capture_records(preflight)
        result = compile_phase8b_segment(
            preflight=preflight,
            capture_records=records,
            code_commit=COMMIT,
        )
        self.assertEqual(result["protocol"], PHASE8B_SEGMENT_PROTOCOL)
        self.assertEqual(result["outcome"], PHASE8B_RUNTIME_REPLAY_KERNEL_READY)
        self.assertEqual(result["capture_record_count"], len(records))
        self.assertFalse(result["live_shadow_segment_started"])
        self.assertFalse(result["acceptance_authorized"])

        for symbol in preflight["required_symbols"]:
            one_minute = result["bars"][symbol]["1m"]
            self.assertEqual(len(one_minute), 2)
            self.assertEqual(one_minute[0]["timestamp_utc"], "2026-09-22T14:00:00Z")
            self.assertEqual(one_minute[1]["timestamp_utc"], "2026-09-22T14:01:00Z")
            self.assertNotIn("2026-09-22T14:02:00Z", {
                row["timestamp_utc"] for row in one_minute
            })

    def test_replay_is_byte_identical_for_same_preflight_and_records(self) -> None:
        preflight = _preflight()
        records = _capture_records(preflight)
        segment = compile_phase8b_segment(
            preflight=preflight,
            capture_records=records,
            code_commit=COMMIT,
        )
        replay = replay_phase8b_segment(
            expected_segment=segment,
            preflight=preflight,
            capture_records=records,
        )
        self.assertTrue(replay["match"])
        self.assertEqual(
            replay["expected_segment_fingerprint"],
            replay["replay_segment_fingerprint"],
        )

    def test_segment_rejects_capture_record_order_regression(self) -> None:
        preflight = _preflight()
        records = list(_capture_records(preflight))
        records[0], records[1] = records[1], records[0]
        with self.assertRaisesRegex(ValueError, "monotonic"):
            compile_phase8b_segment(
                preflight=preflight,
                capture_records=records,
                code_commit=COMMIT,
            )

    def test_shared_risk_budget_is_one_percent_across_symbols(self) -> None:
        simulator = PortfolioShadowSimulator()
        quote_time = PREPARED + timedelta(minutes=1)
        decisions = []
        symbols = ("EURUSD", "EURUSD", "GBPUSD", "USDJPY", "USDJPY")
        for index, symbol in enumerate(symbols):
            price = 150.0 if symbol == "USDJPY" else 1.10
            stop = price - (0.10 if symbol == "USDJPY" else 0.001)
            decision = Decision(
                decision_id=f"d{index}",
                symbol=symbol,
                decision_timestamp_utc=PREPARED,
                direction=Direction.LONG,
                earliest_executable_timestamp_utc=quote_time,
                requested_risk_fraction=RiskConfig().default_risk_fraction,
                stop_price=stop,
                target_price=price + (0.10 if symbol == "USDJPY" else 0.001),
            )
            decisions.append(decision)
            simulator.register_decision(
                decision,
                ScheduledExit(
                    decision_id=decision.decision_id,
                    symbol=symbol,
                    timestamp_utc=quote_time + timedelta(hours=1),
                ),
            )

        from fmp.phase8b.bridge import Phase8BQuote

        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            price = 150.0 if symbol == "USDJPY" else 1.10
            simulator.on_quote(
                Phase8BQuote(
                    source_time_utc=quote_time,
                    received_at_utc=quote_time,
                    receive_monotonic_ns=1,
                    symbol=symbol,
                    bid=price,
                    ask=price + (0.02 if symbol == "USDJPY" else 0.0002),
                )
            )

        baseline = simulator.states[0.2]
        self.assertEqual(len(baseline.open_positions), 4)
        self.assertEqual(len(baseline.rejections), 1)
        rejected = next(iter(baseline.rejections.values()))
        self.assertEqual(rejected.value, "SIMULTANEOUS_RISK")

    def test_symbol_specific_stale_gap_invalidates_only_that_symbol(self) -> None:
        simulator = PortfolioShadowSimulator()
        quote_time = PREPARED + timedelta(minutes=1)
        for symbol in ("EURUSD", "GBPUSD"):
            price = 1.10
            decision = Decision(
                decision_id=f"{symbol}-d",
                symbol=symbol,
                decision_timestamp_utc=PREPARED,
                direction=Direction.LONG,
                earliest_executable_timestamp_utc=quote_time,
                requested_risk_fraction=0.0025,
                stop_price=1.09,
                target_price=1.11,
            )
            simulator.register_decision(
                decision,
                ScheduledExit(
                    decision_id=decision.decision_id,
                    symbol=symbol,
                    timestamp_utc=quote_time + timedelta(hours=1),
                ),
            )

        from fmp.phase8b.bridge import Phase8BQuote

        for symbol in ("EURUSD", "GBPUSD"):
            simulator.on_quote(
                Phase8BQuote(
                    source_time_utc=quote_time,
                    received_at_utc=quote_time,
                    receive_monotonic_ns=1,
                    symbol=symbol,
                    bid=1.10,
                    ask=1.1002,
                )
            )

        simulator.mark_stale_gap(
            "EURUSD",
            quote_time,
            quote_time + timedelta(seconds=20),
        )
        state = simulator.states[0.2]
        self.assertEqual(
            state.outcomes["EURUSD-d"],
            ShadowOutcome.OUTCOME_UNKNOWN_AFTER_GAP,
        )
        self.assertIn("GBPUSD-d", state.open_positions)


if __name__ == "__main__":
    unittest.main()
