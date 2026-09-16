from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

from fmp.contracts import Decision, Direction, QuoteBar, ScheduledExit
from fmp.shadow.cli import build_parser, main
from fmp.shadow.contracts import NormalizedQuote, ShadowOutcome
from fmp.shadow.runner import ShadowRunner
from fmp.shadow.simulation import ShadowSimulator
from fmp.shadow.strategy import ShadowStrategyDecision
from fmp.strategies.contracts import SignalCandidate


UTC = timezone.utc
BASE = datetime(2026, 9, 15, 8, 15, tzinfo=UTC)


def provider_time(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def heartbeat(value: datetime) -> dict[str, object]:
    return {"type": "HEARTBEAT", "time": provider_time(value)}


def price(value: datetime, *, bid: float = 140.00, ask: float = 140.02) -> dict[str, object]:
    return {
        "type": "PRICE",
        "time": provider_time(value),
        "instrument": "USD_JPY",
        "tradeable": True,
        "bids": [{"price": f"{bid:.3f}"}],
        "asks": [{"price": f"{ask:.3f}"}],
    }


def bar(value: datetime = BASE) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=value,
        symbol="USDJPY",
        bid_open=140.00,
        bid_high=140.10,
        bid_low=139.90,
        bid_close=140.05,
        ask_open=140.02,
        ask_high=140.12,
        ask_low=139.92,
        ask_close=140.07,
    )


def directional_strategy_decision() -> ShadowStrategyDecision:
    observation = BASE - timedelta(minutes=15)
    candidate = SignalCandidate(
        candidate_id="SB-USDJPY-20260915-15m-B5-R1p5-LONG",
        symbol="USDJPY",
        observation_bar_timestamp_utc=observation,
        signal_known_timestamp_utc=BASE,
        direction=Direction.LONG,
        stop_price=139.50,
        target_price=140.50,
        latest_exit_timestamp_utc=datetime(2026, 9, 15, 15, 0, tzinfo=UTC),
        reason_code="BREAKOUT_LONG",
        metadata={"session_date": "2026-09-15"},
    )
    decision = Decision(
        decision_id=candidate.candidate_id,
        symbol="USDJPY",
        decision_timestamp_utc=observation,
        direction=Direction.LONG,
        earliest_executable_timestamp_utc=BASE,
        requested_risk_fraction=0.0025,
        stop_price=139.50,
        target_price=140.50,
        reason_code="BREAKOUT_LONG",
    )
    return ShadowStrategyDecision(
        candidate=candidate,
        decision=decision,
        scheduled_exit=ScheduledExit(
            decision_id=candidate.candidate_id,
            symbol="USDJPY",
            timestamp_utc=datetime(2026, 9, 15, 15, 0, tzinfo=UTC),
        ),
    )


class _EvidenceSpy:
    def __init__(self) -> None:
        self.raw: list[object] = []
        self.normalized: list[object] = []
        self.bars: list[tuple[str, object]] = []
        self.decisions: list[dict[str, object]] = []
        self.scenarios: list[dict[str, object]] = []
        self.operational: list[dict[str, object]] = []
        self.code_commit = "a" * 40
        self.account_fingerprint_sha256 = "b" * 64

    def append_raw(self, provider_object, *, received_at_utc, receive_monotonic_ns):  # type: ignore[no-untyped-def]
        self.raw.append((provider_object, received_at_utc, receive_monotonic_ns))

    def append_normalized(self, event):  # type: ignore[no-untyped-def]
        self.normalized.append(event)

    def append_bar(self, timeframe, item):  # type: ignore[no-untyped-def]
        self.bars.append((timeframe, item))

    def append_decision(self, record):  # type: ignore[no-untyped-def]
        self.decisions.append(dict(record))

    def append_scenario(self, record):  # type: ignore[no-untyped-def]
        self.scenarios.append(dict(record))

    def append_operational(self, record):  # type: ignore[no-untyped-def]
        self.operational.append(dict(record))


class _BarSpy:
    def __init__(self, completed: tuple[QuoteBar, ...] = ()) -> None:
        self.completed = completed
        self.stale: list[tuple[datetime, datetime]] = []
        self.quotes: list[NormalizedQuote] = []
        self.time_advances: list[datetime] = []
        self.minutes: list[QuoteBar] = []

    def on_quote(self, item: NormalizedQuote) -> tuple[QuoteBar, ...]:
        self.quotes.append(item)
        completed, self.completed = self.completed, ()
        return completed

    def on_time_advance(self, value: datetime) -> tuple[QuoteBar, ...]:
        self.time_advances.append(value)
        completed, self.completed = self.completed, ()
        return completed

    def mark_stale_interval(self, start: datetime, end: datetime) -> None:
        self.stale.append((start, end))

    def drain_completed_minute_bars(self) -> tuple[QuoteBar, ...]:
        out = tuple(self.minutes)
        self.minutes.clear()
        return out


class Phase8RunnerTests(unittest.TestCase):
    def test_fifteen_seconds_without_valid_price_or_heartbeat_marks_stale_once(self) -> None:
        evidence = _EvidenceSpy()
        bars = _BarSpy()
        runner = ShadowRunner(evidence=evidence, bar_builder=bars)
        runner.start(now_utc=BASE, restarted=False)
        runner.process_provider_message(heartbeat(BASE), received_at_utc=BASE, receive_monotonic_ns=0)

        self.assertTrue(
            runner.check_liveness(
                now_utc=BASE + timedelta(seconds=15),
                now_monotonic_ns=15_000_000_000,
            )
        )
        self.assertTrue(runner.stale)
        self.assertEqual(len(bars.stale), 1)
        self.assertEqual(
            [item["event"] for item in evidence.operational].count("stale"),
            1,
        )
        runner.check_liveness(
            now_utc=BASE + timedelta(seconds=20),
            now_monotonic_ns=20_000_000_000,
        )
        self.assertEqual(len(bars.stale), 1)

    def test_stale_gap_invalidates_open_shadow_outcomes_and_keeps_date_ineligible_after_recovery(self) -> None:
        simulator = ShadowSimulator()
        item = directional_strategy_decision()
        assert item.scheduled_exit is not None
        simulator.register_decision(item.decision, item.scheduled_exit)
        simulator.on_quote(
            NormalizedQuote(
                source_time_utc=BASE,
                received_at_utc=BASE,
                receive_monotonic_ns=0,
                symbol="USDJPY",
                bid=140.00,
                ask=140.02,
                tradeable=True,
            )
        )
        evidence = _EvidenceSpy()
        runner = ShadowRunner(evidence=evidence, simulator=simulator, bar_builder=_BarSpy())
        runner.start(now_utc=BASE, restarted=False)
        runner.process_provider_message(heartbeat(BASE), received_at_utc=BASE, receive_monotonic_ns=0)
        runner.check_liveness(
            now_utc=BASE + timedelta(seconds=16),
            now_monotonic_ns=16_000_000_000,
        )
        for state in simulator.states.values():
            self.assertEqual(
                state.outcomes[item.decision.decision_id],
                ShadowOutcome.OUTCOME_UNKNOWN_AFTER_GAP,
            )
            self.assertFalse(state.open_positions)

        runner.process_provider_message(
            heartbeat(BASE + timedelta(seconds=17)),
            received_at_utc=BASE + timedelta(seconds=17),
            receive_monotonic_ns=17_000_000_000,
        )
        self.assertFalse(runner.stale)
        self.assertIn(BASE.date(), runner.ineligible_london_dates)
        self.assertIn("recovered", [item["event"] for item in evidence.operational])

    def test_ineligible_london_date_blocks_strategy_entry_but_capture_continues(self) -> None:
        evidence = _EvidenceSpy()
        bars = _BarSpy(completed=(bar(),))
        simulator = ShadowSimulator()
        strategy_calls: list[tuple[QuoteBar, ...]] = []

        def strategy(items):  # type: ignore[no-untyped-def]
            strategy_calls.append(tuple(items))
            return (directional_strategy_decision(),)

        runner = ShadowRunner(
            evidence=evidence,
            bar_builder=bars,
            simulator=simulator,
            strategy_adapter=strategy,
        )
        runner.start(now_utc=BASE, restarted=True)
        runner.process_provider_message(
            price(BASE + timedelta(seconds=1)),
            received_at_utc=BASE + timedelta(seconds=1),
            receive_monotonic_ns=1_000_000_000,
        )
        self.assertEqual(len(evidence.raw), 1)
        self.assertEqual(len(evidence.normalized), 1)
        self.assertEqual(strategy_calls, [])
        self.assertTrue(all(not state.open_positions for state in simulator.states.values()))
        self.assertTrue(any(item.get("event") == "date_ineligible" for item in evidence.decisions))

    def test_restart_marks_current_london_date_ineligible_and_unknowns_any_open_position(self) -> None:
        simulator = ShadowSimulator()
        item = directional_strategy_decision()
        assert item.scheduled_exit is not None
        simulator.register_decision(item.decision, item.scheduled_exit)
        simulator.on_quote(
            NormalizedQuote(
                source_time_utc=BASE,
                received_at_utc=BASE,
                receive_monotonic_ns=1,
                symbol="USDJPY",
                bid=140.00,
                ask=140.02,
                tradeable=True,
            )
        )
        evidence = _EvidenceSpy()
        runner = ShadowRunner(evidence=evidence, simulator=simulator, bar_builder=_BarSpy())
        runner.start(now_utc=BASE + timedelta(minutes=5), restarted=True)
        self.assertIn(BASE.date(), runner.ineligible_london_dates)
        self.assertIn("restart", [record["event"] for record in evidence.operational])
        for state in simulator.states.values():
            self.assertEqual(
                state.outcomes[item.decision.decision_id],
                ShadowOutcome.OUTCOME_UNKNOWN_AFTER_GAP,
            )

    def test_malformed_provider_message_is_durably_rejected_without_strategy_activity(self) -> None:
        evidence = _EvidenceSpy()
        strategy_calls: list[object] = []
        runner = ShadowRunner(
            evidence=evidence,
            bar_builder=_BarSpy(),
            strategy_adapter=lambda items: strategy_calls.append(items) or (),
        )
        runner.start(now_utc=BASE, restarted=False)
        with self.assertRaises(ValueError):
            runner.process_provider_message(
                {"type": "PRICE", "time": provider_time(BASE), "instrument": "EUR_USD"},
                received_at_utc=BASE,
                receive_monotonic_ns=0,
            )
        self.assertEqual(strategy_calls, [])
        self.assertTrue(any(item.get("event") == "rejection" for item in evidence.operational))

    def test_completed_minute_and_fifteen_minute_bars_are_both_evidenced(self) -> None:
        evidence = _EvidenceSpy()
        bars = _BarSpy(completed=(bar(),))
        bars.minutes.append(bar(BASE - timedelta(minutes=1)))
        runner = ShadowRunner(
            evidence=evidence,
            bar_builder=bars,
            strategy_adapter=lambda items: (),
        )
        runner.start(now_utc=BASE, restarted=False)
        runner.process_provider_message(
            price(BASE),
            received_at_utc=BASE,
            receive_monotonic_ns=0,
        )
        self.assertEqual([timeframe for timeframe, _ in evidence.bars], ["1m", "15m"])

    def test_run_cli_is_explicit_env_credentialed_and_has_no_transport_override(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["run", "--campaign-dir", "evidence/phase8/campaign"])
        self.assertEqual(args.command, "run")
        self.assertEqual(args.campaign_dir, Path("evidence/phase8/campaign"))
        for forbidden in ("account_id", "token", "host", "instrument", "method", "base_url"):
            self.assertFalse(hasattr(args, forbidden))

        called: list[dict[str, object]] = []
        rc = main(
            ["run", "--campaign-dir", "campaign"],
            environ={
                "OANDA_PRACTICE_ACCOUNT_ID": "101-001-12345678-001",
                "OANDA_PRACTICE_TOKEN": "secret-token",
            },
            run_command=lambda **kwargs: called.append(kwargs) or 0,
            code_commit_resolver=lambda: "c" * 40,
        )
        self.assertEqual(rc, 0)
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0]["campaign_dir"], Path("campaign"))
        self.assertEqual(called[0]["code_commit"], "c" * 40)

    def test_runner_and_cli_have_no_reconciliation_daemon_or_order_submission_surface(self) -> None:
        source = "\n".join(
            Path(path).read_text(encoding="utf-8").lower()
            for path in ("src/fmp/shadow/runner.py", "src/fmp/shadow/cli.py", "scripts/phase8_shadow.py")
        )
        for forbidden in (
            "order_send",
            "submit_order",
            "place_order",
            "broker_position",
            "reconcile_order",
            "load_history",
            "historical_candle",
            "daemon",
            "cron",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
