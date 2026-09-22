from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

from fmp.phase8b.bridge import (
    Phase8BBridgeHeartbeatRecord,
    Phase8BBridgeStartRecord,
    Phase8BBridgeTickRecord,
)
from fmp.phase8b.design import build_phase8b_design
from fmp.phase8b.qualification import (
    FeedQualificationOutcome,
    FeedQualificationResult,
    MAX_QUALIFICATION_SECONDS,
    MIN_HEARTBEAT_COUNT,
    MIN_PRICE_COUNT,
    Phase8BQualificationOutcome,
    qualify_phase8b_feed,
    summarize_phase8b_qualification,
)
from fmp.portfolio.challenger_discovery import build_exp015_challengers
from fmp.portfolio.contracts import StrategyLifecycle, StrategyRecord
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.portfolio.registry import freeze_shadow_champion_set, transition_strategy


UTC = timezone.utc
NOW = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)
ACCOUNT = "a" * 64
SERVER = "FPMarketsSC-Demo"
DESIGN_COMMIT = "d" * 40
QUAL_COMMIT = "e" * 40


class _Tail:
    def __init__(self, start_record, batches):
        self.start_record = start_record
        self._batches = list(batches)

    def read_available(self):
        if not self._batches:
            return ()
        return self._batches.pop(0)


class _Clock:
    def __init__(self, times_ns):
        self._times = iter(times_ns)

    def utc_now(self):
        return NOW

    def monotonic_ns(self):
        return next(self._times)


def _accepted_artifact() -> dict[str, object]:
    baseline = next(
        item
        for item in build_phase4_baseline_inventory()
        if item.lifecycle is StrategyLifecycle.HISTORICAL_QUALIFIED
    )
    challenger_source = next(
        item
        for item in build_exp015_challengers(code_commit="c" * 40)
        if item.strategy.symbol != baseline.strategy.symbol
    )
    challenger = StrategyRecord(
        strategy=challenger_source.strategy,
        lifecycle=StrategyLifecycle.HISTORICAL_QUALIFIED,
        evidence_id="EXP-20260922-015:FINAL_SHORTLIST",
    )
    before = (baseline, challenger)
    after = tuple(
        transition_strategy(
            item,
            StrategyLifecycle.SHADOW_CANDIDATE,
            evidence_id=(
                "EXP-20260922-016:PHASE8A_ACCEPT_SHADOW_CANDIDATE"
            ),
        )
        for item in before
    )
    champion = freeze_shadow_champion_set(
        after,
        champion_set_id="phase8a-exp016-qualification-test",
    )
    prior = {item.strategy.fingerprint: item for item in before}
    rows = []
    for item in sorted(after, key=lambda x: x.strategy.fingerprint):
        old = prior[item.strategy.fingerprint]
        rows.append(
            {
                "fingerprint": item.strategy.fingerprint,
                "identity_json": item.strategy.identity_json,
                "family": item.strategy.family,
                "symbol": item.strategy.symbol,
                "timeframe": item.strategy.timeframe,
                "parameters_json": item.strategy.parameters_json,
                "code_commit": item.strategy.code_commit,
                "prior_lifecycle": old.lifecycle.value,
                "prior_evidence_id": old.evidence_id,
                "lifecycle": item.lifecycle.value,
                "evidence_id": item.evidence_id,
            }
        )
    return {
        "protocol": "fmp-phase8a-acceptance-v1",
        "experiment_id": "EXP-20260922-016",
        "outcome": "PHASE8A_SHADOW_CANDIDATE_ACCEPTED",
        "acceptance_code_commit": "b" * 40,
        "shadow_candidate_authorized": True,
        "phase8b_design_authorized": True,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
        "shadow_candidate": {
            "champion_set_id": champion.champion_set_id,
            "champion_set_experiment_id": champion.experiment_id,
            "champion_set_fingerprint": champion.fingerprint,
            "strategy_fingerprints": [
                item.fingerprint for item in champion.strategies
            ],
            "strategies": rows,
        },
    }


def _design():
    return build_phase8b_design(
        acceptance=_accepted_artifact(),
        acceptance_sha256="1" * 64,
        code_commit=DESIGN_COMMIT,
    )


def _start(symbol: str, *, session: str, account=ACCOUNT, server=SERVER):
    return Phase8BBridgeStartRecord(
        protocol="fmp-mt5-demo-multisymbol-file-bridge-v1",
        bridge_session_id=session,
        symbol=symbol,
        server=server,
        account_fingerprint=account,
        account_mode="DEMO",
        bridge_start_time_msc=int(NOW.timestamp() * 1000),
    )


def _pass_feed(symbol: str, *, session: str, account=ACCOUNT, server=SERVER):
    start = _start(
        symbol,
        session=session,
        account=account,
        server=server,
    )
    base_msc = int(NOW.timestamp() * 1000)
    records = []
    for index in range(MIN_PRICE_COUNT):
        records.append(
            Phase8BBridgeTickRecord(
                protocol=start.protocol,
                bridge_session_id=session,
                symbol=symbol,
                server=server,
                account_fingerprint=account,
                source_time_msc=base_msc + index * 10,
                bid=150.0 if symbol == "USDJPY" else 1.10,
                ask=150.02 if symbol == "USDJPY" else 1.1002,
                flags=6,
            )
        )
    for _ in range(MIN_HEARTBEAT_COUNT):
        records.append(
            Phase8BBridgeHeartbeatRecord(
                protocol=start.protocol,
                bridge_session_id=session,
                symbol=symbol,
                server=server,
                account_fingerprint=account,
                bridge_emitted_time_msc=base_msc + 1000,
                last_tick_time_msc=base_msc + 990,
            )
        )
    return start, tuple(records)


def _result(
    symbol: str,
    *,
    outcome=FeedQualificationOutcome.PASS,
    session: str,
    account=ACCOUNT,
    server=SERVER,
    codes=(),
):
    return FeedQualificationResult(
        symbol=symbol,
        outcome=outcome,
        account_fingerprint=account,
        bridge_session_id=session,
        server=server,
        started_at_utc=NOW,
        ended_at_utc=NOW + timedelta(seconds=2),
        elapsed_seconds=2.0,
        price_count=MIN_PRICE_COUNT if outcome is FeedQualificationOutcome.PASS else 0,
        heartbeat_count=MIN_HEARTBEAT_COUNT if outcome is FeedQualificationOutcome.PASS else 0,
        max_bridge_liveness_gap_seconds=2.0,
        max_market_liveness_gap_seconds=2.0,
        rejection_codes=tuple(codes),
    )


class Phase8BQualificationTests(unittest.TestCase):
    def test_thresholds_match_legacy_conservative_qualification(self) -> None:
        self.assertEqual(MAX_QUALIFICATION_SECONDS, 600.0)
        self.assertEqual(MIN_PRICE_COUNT, 100)
        self.assertEqual(MIN_HEARTBEAT_COUNT, 6)

    def test_per_feed_passes_with_100_prices_and_6_heartbeats(self) -> None:
        start, records = _pass_feed("EURUSD", session="1" * 64)
        tail = _Tail(start, [records])
        clock = _Clock([0, 1_000_000_000, 2_000_000_000])
        result = qualify_phase8b_feed(
            tail,
            expected_symbol="EURUSD",
            utc_now=clock.utc_now,
            monotonic_ns=clock.monotonic_ns,
            sleep=lambda _: None,
        )
        self.assertEqual(result.outcome, FeedQualificationOutcome.PASS)
        self.assertEqual(result.price_count, 100)
        self.assertEqual(result.heartbeat_count, 6)
        self.assertEqual(result.account_fingerprint, ACCOUNT)
        self.assertEqual(result.server, SERVER)

    def test_per_feed_market_gap_is_inconclusive(self) -> None:
        start = _start("EURUSD", session="1" * 64)
        tail = _Tail(start, [()])
        clock = _Clock(
            [
                0,
                16_000_000_001,
                16_000_000_002,
            ]
        )
        result = qualify_phase8b_feed(
            tail,
            expected_symbol="EURUSD",
            utc_now=clock.utc_now,
            monotonic_ns=clock.monotonic_ns,
            sleep=lambda _: None,
        )
        # Before any post-start activity, bridge inactivity has precedence.
        self.assertEqual(
            result.outcome,
            FeedQualificationOutcome.CONNECTOR_UNAVAILABLE,
        )
        self.assertIn("BRIDGE_INACTIVE", result.rejection_codes)

    def test_summary_pass_requires_same_account_server_and_distinct_sessions(self) -> None:
        design = _design()
        symbols = design["required_symbols"]
        results = {
            symbol: _result(
                symbol,
                session=f"{index + 1:064x}",
            )
            for index, symbol in enumerate(symbols)
        }
        summary = summarize_phase8b_qualification(
            design=design,
            design_sha256="2" * 64,
            code_commit=QUAL_COMMIT,
            feed_results=results,
        )
        self.assertEqual(
            summary["outcome"],
            Phase8BQualificationOutcome.QUALIFIED.value,
        )
        self.assertEqual(summary["common_account_fingerprint"], ACCOUNT)
        self.assertEqual(summary["common_server"], SERVER)
        self.assertTrue(summary["campaign_registration_authorized"])
        self.assertFalse(summary["campaign_start_authorized"])

        mismatch = dict(results)
        first = symbols[0]
        mismatch[first] = _result(
            first,
            session="9" * 64,
            account="f" * 64,
        )
        rejected = summarize_phase8b_qualification(
            design=design,
            design_sha256="2" * 64,
            code_commit=QUAL_COMMIT,
            feed_results=mismatch,
        )
        self.assertEqual(
            rejected["outcome"],
            Phase8BQualificationOutcome.CONNECTOR_REJECTED.value,
        )
        self.assertIn(
            "ACCOUNT_FINGERPRINT_MISMATCH",
            rejected["rejection_codes"],
        )
        self.assertFalse(rejected["campaign_registration_authorized"])

        collision = {
            symbol: _result(symbol, session="8" * 64)
            for symbol in symbols
        }
        rejected_collision = summarize_phase8b_qualification(
            design=design,
            design_sha256="2" * 64,
            code_commit=QUAL_COMMIT,
            feed_results=collision,
        )
        self.assertIn(
            "BRIDGE_SESSION_COLLISION",
            rejected_collision["rejection_codes"],
        )

    def test_summary_outcome_precedence_is_rejected_unavailable_inconclusive(self) -> None:
        design = _design()
        symbols = design["required_symbols"]
        if len(symbols) < 2:
            self.skipTest("fixture unexpectedly has one symbol")
        base = {
            symbol: _result(symbol, session=f"{index + 1:064x}")
            for index, symbol in enumerate(symbols)
        }

        first = symbols[0]
        second = symbols[1]
        cases = (
            (
                FeedQualificationOutcome.INCONCLUSIVE,
                FeedQualificationOutcome.CONNECTOR_UNAVAILABLE,
                Phase8BQualificationOutcome.CONNECTOR_UNAVAILABLE,
            ),
            (
                FeedQualificationOutcome.CONNECTOR_UNAVAILABLE,
                FeedQualificationOutcome.CONNECTOR_REJECTED,
                Phase8BQualificationOutcome.CONNECTOR_REJECTED,
            ),
        )
        for first_outcome, second_outcome, expected in cases:
            with self.subTest(expected=expected):
                results = dict(base)
                results[first] = _result(
                    first,
                    outcome=first_outcome,
                    session="a" * 64,
                    codes=("FIRST",),
                )
                results[second] = _result(
                    second,
                    outcome=second_outcome,
                    session="b" * 64,
                    codes=("SECOND",),
                )
                summary = summarize_phase8b_qualification(
                    design=design,
                    design_sha256="2" * 64,
                    code_commit=QUAL_COMMIT,
                    feed_results=results,
                )
                self.assertEqual(summary["outcome"], expected.value)
                self.assertFalse(summary["campaign_registration_authorized"])

    def test_exact_required_feed_coverage_is_mandatory(self) -> None:
        design = _design()
        symbols = design["required_symbols"]
        results = {
            symbol: _result(
                symbol,
                session=f"{index + 1:064x}",
            )
            for index, symbol in enumerate(symbols)
        }
        results.pop(symbols[0])
        with self.assertRaisesRegex(ValueError, "coverage"):
            summarize_phase8b_qualification(
                design=design,
                design_sha256="2" * 64,
                code_commit=QUAL_COMMIT,
                feed_results=results,
            )


if __name__ == "__main__":
    unittest.main()
