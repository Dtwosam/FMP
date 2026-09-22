from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import unittest

from fmp.contracts import Direction, QuoteBar, RejectionCode
from fmp.portfolio import StrategyVersion
from fmp.portfolio.joint_research import (
    JOINT_PORTFOLIO_PROTOCOL,
    Phase8AJointPortfolioPlan,
    run_phase8a_joint_portfolio,
)
from fmp.portfolio.research_data import (
    LoadedRetrospectiveBars,
    PHASE8A_RETROSPECTIVE_LABEL,
    RetrospectiveRange,
)
from fmp.strategies.contracts import SignalCandidate


DAY = datetime(2024, 1, 2, 8, 0, tzinfo=timezone.utc)
COMMIT = "c" * 40
RUNNER_COMMIT = "d" * 40


def _strategy(version: str, *, symbol: str = "EURUSD") -> StrategyVersion:
    return StrategyVersion.create(
        family="session_breakout",
        version=version,
        symbol=symbol,
        timeframe="15m",
        parameters={"buffer_pips": 5, "target_range_multiple": 1.5},
        signal_contract_version="phase8a-joint-test-v1",
        code_commit=COMMIT,
    )


def _bar(ts: datetime, *, symbol: str = "EURUSD") -> QuoteBar:
    if symbol == "USDJPY":
        mid = 150.0
        half = 0.01
        width = 0.03
    else:
        mid = 1.1000
        half = 0.0001
        width = 0.0003
    return QuoteBar(
        timestamp_utc=ts,
        symbol=symbol,
        bid_open=mid - half,
        bid_high=mid + width,
        bid_low=mid - width,
        bid_close=mid,
        ask_open=mid + half,
        ask_high=mid + width + 2 * half,
        ask_low=mid - width + 2 * half,
        ask_close=mid + 2 * half,
    )


def _loaded(symbol: str, timeframe: str) -> LoadedRetrospectiveBars:
    if timeframe == "1m":
        bars = tuple(_bar(DAY + timedelta(minutes=i), symbol=symbol) for i in range(11))
    else:
        bars = (_bar(DAY, symbol=symbol),)
    return LoadedRetrospectiveBars(
        bars=bars,
        excluded_incomplete_count=0,
        eligible_utc_dates=(DAY.date(),),
        evidence_label=PHASE8A_RETROSPECTIVE_LABEL,
        start=DAY.date(),
        end_exclusive=DAY.date() + timedelta(days=1),
        processed_manifest_sha256=("a" if symbol == "EURUSD" else "b") * 64,
        opened_artifact_months=("2024-01",),
    )


def _candidate(strategy: StrategyVersion, *, direction: Direction, minute: int = 5) -> SignalCandidate:
    if strategy.symbol == "USDJPY":
        stop = 149.50 if direction is Direction.LONG else 150.50
        target = 151.00 if direction is Direction.LONG else 149.00
    else:
        stop = 1.0900 if direction is Direction.LONG else 1.1100
        target = 1.1200 if direction is Direction.LONG else 1.0800
    return SignalCandidate(
        candidate_id="RAW-CANDIDATE",
        symbol=strategy.symbol,
        observation_bar_timestamp_utc=DAY,
        signal_known_timestamp_utc=DAY + timedelta(minutes=minute),
        direction=direction,
        stop_price=stop,
        target_price=target,
        latest_exit_timestamp_utc=DAY + timedelta(minutes=9),
        reason_code="TEST_DIRECTIONAL",
        metadata={"source": "fixture"},
    )


class Phase8AJointPortfolioTests(unittest.TestCase):
    def test_plan_sorts_strategy_identity_and_rejects_duplicates(self) -> None:
        a = _strategy("v-a")
        b = _strategy("v-b")
        plan = Phase8AJointPortfolioPlan(
            experiment_id="EXP-20260922-012",
            strategies=(b, a),
            research_range=RetrospectiveRange(
                start=DAY.date(),
                end_exclusive=DAY.date() + timedelta(days=1),
            ),
            slippage_pips=0.2,
            runner_code_commit=RUNNER_COMMIT,
        )
        self.assertEqual(
            tuple(item.fingerprint for item in plan.strategies),
            tuple(sorted((a.fingerprint, b.fingerprint))),
        )
        self.assertFalse(plan.untouched_oos)
        self.assertEqual(plan.evidence_label, PHASE8A_RETROSPECTIVE_LABEL)

        with self.assertRaises(ValueError):
            Phase8AJointPortfolioPlan(
                experiment_id="EXP-20260922-012",
                strategies=(a, a),
                research_range=plan.research_range,
                slippage_pips=0.2,
                runner_code_commit=RUNNER_COMMIT,
            )

    def test_five_simultaneous_quarter_percent_signals_share_one_percent_risk_cap(self) -> None:
        strategies = tuple(_strategy(f"v-{index}") for index in range(5))
        calls: list[tuple[str, str]] = []

        def loader(**kwargs):
            calls.append((kwargs["symbol"], kwargs["timeframe"]))
            return _loaded(kwargs["symbol"], kwargs["timeframe"])

        def generator(strategy, bars):
            return (_candidate(strategy, direction=Direction.LONG),)

        plan = Phase8AJointPortfolioPlan(
            experiment_id="EXP-20260922-012",
            strategies=strategies,
            research_range=RetrospectiveRange(
                start=DAY.date(),
                end_exclusive=DAY.date() + timedelta(days=1),
            ),
            slippage_pips=0.2,
            runner_code_commit=RUNNER_COMMIT,
        )
        result = run_phase8a_joint_portfolio(
            plan=plan,
            dataset_sources={"EURUSD": (Path("/unused"), Path("/unused"))},
            bars_loader=loader,
            candidate_generator=generator,
        )

        self.assertEqual(result["protocol"], JOINT_PORTFOLIO_PROTOCOL)
        self.assertTrue(result["shared_account"])
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["untouched_oos"])
        self.assertEqual(result["execution_timeframe"], "1m")
        self.assertEqual(result["metrics"]["trade_count"], 4)
        self.assertEqual(
            result["metrics"]["rejection_reason_counts"][RejectionCode.SIMULTANEOUS_RISK.value],
            1,
        )
        self.assertEqual(result["portfolio_conflict_rejection_count"], 0)
        self.assertEqual(calls.count(("EURUSD", "15m")), 1)
        self.assertEqual(calls.count(("EURUSD", "1m")), 1)
        self.assertEqual(
            result["run_identity"]["execution_timing_mode"],
            "DECLARED_EARLIEST_BAR",
        )
        self.assertEqual(len(result["strategy_contribution"]), 4)

    def test_same_symbol_same_time_opposite_signals_fail_closed_before_risk(self) -> None:
        long_strategy = _strategy("long")
        short_strategy = _strategy("short")

        def loader(**kwargs):
            return _loaded(kwargs["symbol"], kwargs["timeframe"])

        def generator(strategy, bars):
            direction = Direction.LONG if strategy.version == "long" else Direction.SHORT
            return (_candidate(strategy, direction=direction),)

        plan = Phase8AJointPortfolioPlan(
            experiment_id="EXP-20260922-012",
            strategies=(long_strategy, short_strategy),
            research_range=RetrospectiveRange(
                start=DAY.date(),
                end_exclusive=DAY.date() + timedelta(days=1),
            ),
            slippage_pips=0.5,
            runner_code_commit=RUNNER_COMMIT,
        )
        result = run_phase8a_joint_portfolio(
            plan=plan,
            dataset_sources={"EURUSD": (Path("/unused"), Path("/unused"))},
            bars_loader=loader,
            candidate_generator=generator,
        )

        self.assertEqual(result["metrics"]["trade_count"], 0)
        self.assertEqual(result["portfolio_conflict_rejection_count"], 2)
        self.assertEqual(
            {item["code"] for item in result["portfolio_conflict_rejections"]},
            {"DIRECTION_CONFLICT"},
        )

    def test_joint_result_binds_manifest_and_candidate_identity(self) -> None:
        eur = _strategy("eur")

        result = run_phase8a_joint_portfolio(
            plan=Phase8AJointPortfolioPlan(
                experiment_id="EXP-20260922-012",
                strategies=(eur,),
                research_range=RetrospectiveRange(
                    start=DAY.date(),
                    end_exclusive=DAY.date() + timedelta(days=1),
                ),
                slippage_pips=1.0,
                runner_code_commit=RUNNER_COMMIT,
            ),
            dataset_sources={"EURUSD": (Path("/unused"), Path("/unused"))},
            bars_loader=lambda **kwargs: _loaded(kwargs["symbol"], kwargs["timeframe"]),
            candidate_generator=lambda strategy, bars: (
                _candidate(strategy, direction=Direction.LONG),
            ),
        )

        self.assertEqual(
            result["processed_manifest_sha256_by_symbol"],
            {"EURUSD": "a" * 64},
        )
        self.assertEqual(result["strategy_fingerprints"], [eur.fingerprint])
        self.assertEqual(len(result["candidate_sha256"]), 64)
        self.assertEqual(result["evidence_label"], PHASE8A_RETROSPECTIVE_LABEL)


if __name__ == "__main__":
    unittest.main()
