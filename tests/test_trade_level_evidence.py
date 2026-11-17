from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from fmp.contracts import Direction
from fmp.research.trade_level_evidence import (
    EvidenceProvenance,
    StatisticalEvidenceDeclaration,
    SubmittedTrade,
    TradeSubmission,
    WindowAggregate,
    assess_statistical_readiness,
    phase7_public_preservation_record,
    validate_trade_submission,
)
from fmp.risk.sizing import pnl_usd

UTC = timezone.utc
RISK = 0.0025


def _ts(month: int, day: int, hour: int) -> datetime:
    return datetime(2024, month, day, hour, tzinfo=UTC)


def _trade(
    *,
    trade_id: str,
    decision_id: str,
    window_id: str,
    equity_before: float,
    entry_at: datetime,
    exit_at: datetime,
    entry_reference: float,
    exit_reference: float,
    entry_price: float,
    exit_price: float,
    stop_price: float,
    target_price: float | None,
    symbol: str = "EURUSD",
    direction: str = "LONG",
    units: int = 10_000,
    commission: float = 0.0,
    financing: float = 0.0,
    spread: float = 0.0,
    spread_basis: str = "included_in_bid_ask_reference",
    risk: float = RISK,
    intrabar_ambiguous: bool = False,
    intrabar_resolution: str = "not_applicable",
    exit_reason: str = "TARGET",
) -> SubmittedTrade:
    side = Direction(direction)
    gross = pnl_usd(
        symbol=symbol,
        direction=side,
        units=units,
        entry_price=entry_reference,
        exit_price=exit_reference,
    )
    slipped = pnl_usd(
        symbol=symbol,
        direction=side,
        units=units,
        entry_price=entry_price,
        exit_price=exit_price,
    )
    slippage = max(0.0, gross - slipped)
    spread_deduction = spread if spread_basis == "separate_from_reference" else 0.0
    net = gross - slippage - commission - financing - spread_deduction
    return SubmittedTrade(
        trade_id=trade_id,
        decision_id=decision_id,
        window_id=window_id,
        symbol=symbol,
        direction=direction,
        units=units,
        entry_timestamp_utc=entry_at,
        exit_timestamp_utc=exit_at,
        entry_reference_price=entry_reference,
        exit_reference_price=exit_reference,
        entry_price=entry_price,
        exit_price=exit_price,
        stop_price=stop_price,
        target_price=target_price,
        exit_reason=exit_reason,
        intrabar_ambiguous=intrabar_ambiguous,
        intrabar_resolution=intrabar_resolution,
        gross_pnl_usd=gross,
        slippage_cost_usd=slippage,
        commission_cost_usd=commission,
        financing_cost_usd=financing,
        spread_cost_usd=spread,
        spread_basis=spread_basis,
        net_pnl_usd=net,
        risk_equity_before_usd=equity_before,
        risk_equity_after_usd=equity_before + net,
        claimed_net_r=net / (equity_before * risk),
    )


def _window(
    window_id: str,
    start: datetime,
    end: datetime,
    trades: tuple[SubmittedTrade, ...],
    *,
    starting_equity: float = 100_000.0,
    overlap_role: str = "none",
) -> WindowAggregate:
    nets = [trade.net_pnl_usd for trade in trades]
    return WindowAggregate(
        window_id=window_id,
        start_utc=start,
        end_exclusive_utc=end,
        starting_equity_usd=starting_equity,
        trade_count=len(trades),
        net_pnl_usd=sum(nets),
        gross_profit_usd=sum(value for value in nets if value > 0),
        gross_loss_usd=sum(value for value in nets if value < 0),
        slippage_cost_usd=sum(trade.slippage_cost_usd for trade in trades),
        commission_cost_usd=sum(trade.commission_cost_usd for trade in trades),
        financing_cost_usd=sum(trade.financing_cost_usd for trade in trades),
        overlap_role=overlap_role,
    )


def _submit(
    trades: tuple[SubmittedTrade, ...],
    windows: tuple[WindowAggregate, ...],
    *,
    role: str = "synthetic_fixture",
    label: str = "synthetic-closed-trades",
    risk: float = RISK,
    source_run_id: str | None = None,
    source_artifact_id: str | None = None,
    source_commit: str | None = None,
    claims_trades_from_stage2_zip: bool = False,
    expected_trade_ids: tuple[str, ...] | None = None,
) -> TradeSubmission:
    return TradeSubmission(
        provenance=EvidenceProvenance(
            role=role,
            label=label,
            source_run_id=source_run_id,
            source_artifact_id=source_artifact_id,
            source_commit=source_commit,
        ),
        requested_risk_fraction=risk,
        windows=windows,
        trades=trades,
        expected_trade_ids=expected_trade_ids,
        claims_trades_from_stage2_zip=claims_trades_from_stage2_zip,
    )


def _baseline() -> TradeSubmission:
    first = _trade(
        trade_id="syn-a",
        decision_id="dec-a",
        window_id="synthetic-jan",
        equity_before=100_000.0,
        entry_at=_ts(1, 2, 10),
        exit_at=_ts(1, 2, 14),
        entry_reference=1.1000,
        exit_reference=1.1010,
        entry_price=1.1002,
        exit_price=1.1008,
        stop_price=1.0990,
        target_price=1.1030,
        commission=0.4,
        financing=0.1,
    )
    second = _trade(
        trade_id="syn-b",
        decision_id="dec-b",
        window_id="synthetic-jan",
        equity_before=first.risk_equity_after_usd,
        entry_at=_ts(1, 3, 10),
        exit_at=_ts(1, 3, 16),
        entry_reference=1.2000,
        exit_reference=1.2020,
        entry_price=1.1996,
        exit_price=1.2024,
        stop_price=1.2030,
        target_price=1.1980,
        direction="SHORT",
        commission=0.25,
        financing=-0.05,
    )
    third = _trade(
        trade_id="syn-c",
        decision_id="dec-c",
        window_id="synthetic-feb",
        equity_before=100_000.0,
        entry_at=_ts(2, 4, 10),
        exit_at=_ts(2, 4, 15),
        entry_reference=150.00,
        exit_reference=150.20,
        entry_price=150.02,
        exit_price=150.18,
        stop_price=149.50,
        target_price=150.80,
        symbol="USDJPY",
        units=1_000,
    )
    january = (first, second)
    february = (third,)
    return _submit(
        january + february,
        (
            _window("synthetic-jan", _ts(1, 1, 0), _ts(2, 1, 0), january),
            _window("synthetic-feb", _ts(2, 1, 0), _ts(3, 1, 0), february),
        ),
    )


def _codes(result) -> set[str]:
    return {finding.code for finding in result.findings}


class TradeLevelEvidenceTests(unittest.TestCase):
    def test_synthetic_ledger_reconciles_without_becoming_phase7(self) -> None:
        submission = _baseline()
        result = validate_trade_submission(submission)

        self.assertTrue(result.accepted, result.findings)
        self.assertFalse(result.original_phase7_trade_ledger_verified)
        self.assertFalse(result.probabilities_computed)
        self.assertEqual(result.sample_size, 3)
        self.assertEqual(
            tuple(trade_id for trade_id, _r in result.per_trade_net_r),
            ("syn-a", "syn-b", "syn-c"),
        )
        self.assertAlmostEqual(
            result.per_trade_net_r[0][1],
            submission.trades[0].claimed_net_r,
        )
        self.assertAlmostEqual(
            result.per_trade_net_r[2][1],
            submission.trades[2].net_pnl_usd / (100_000.0 * RISK),
        )
        self.assertEqual(result.window_net_pnl_usd[1][0], "synthetic-feb")
        self.assertAlmostEqual(result.descriptive_mean_net_r or 0.0, sum(
            value for _trade_id, value in result.per_trade_net_r
        ) / 3)
        self.assertIn("Independent windows are not one compounded account.", result.limitations)

    def test_duplicate_trade_and_decision_ids_are_rejected(self) -> None:
        submission = _baseline()
        duplicated = replace(submission.trades[1], trade_id="syn-a", decision_id="dec-a")
        result = validate_trade_submission(
            replace(submission, trades=(submission.trades[0], duplicated, submission.trades[2]))
        )
        self.assertFalse(result.accepted)
        self.assertIn("DUPLICATE_TRADE_ID", _codes(result))
        self.assertIn("DUPLICATE_DECISION_ID", _codes(result))
        self.assertEqual(result.per_trade_net_r, ())
        self.assertIsNone(result.descriptive_mean_net_r)

    def test_timestamps_prices_and_order_are_checked(self) -> None:
        submission = _baseline()
        naive = replace(
            submission.trades[0],
            entry_timestamp_utc=datetime(2024, 1, 2, 10),
        )
        reversed_order = replace(
            submission,
            trades=(submission.trades[1], submission.trades[0], submission.trades[2]),
        )
        outside = replace(submission.trades[0], exit_timestamp_utc=_ts(3, 2, 12))
        bad_stop = replace(submission.trades[0], stop_price=1.2)
        self.assertIn("TIMESTAMP_INVALID", _codes(validate_trade_submission(
            replace(submission, trades=(naive, submission.trades[1], submission.trades[2]))
        )))
        self.assertIn("NOT_CHRONOLOGICAL", _codes(validate_trade_submission(reversed_order)))
        self.assertIn("TIMESTAMP_OUTSIDE_WINDOW", _codes(validate_trade_submission(
            replace(submission, trades=(outside, submission.trades[1], submission.trades[2]))
        )))
        self.assertIn("STOP_GEOMETRY", _codes(validate_trade_submission(
            replace(submission, trades=(bad_stop, submission.trades[1], submission.trades[2]))
        )))

    def test_pnl_slippage_spread_and_r_must_match_the_prices(self) -> None:
        submission = _baseline()
        invented = replace(
            submission.trades[0],
            net_pnl_usd=submission.trades[0].net_pnl_usd + 50.0,
            claimed_net_r=1.0,
            risk_equity_after_usd=submission.trades[0].risk_equity_before_usd + 50.0,
        )
        favorable = _trade(
            trade_id="syn-fav",
            decision_id="dec-fav",
            window_id="synthetic-jan",
            equity_before=100_000.0,
            entry_at=_ts(1, 4, 10),
            exit_at=_ts(1, 4, 12),
            entry_reference=1.1000,
            exit_reference=1.1010,
            entry_price=1.1000,
            exit_price=1.1015,
            stop_price=1.0990,
            target_price=1.1030,
        )
        self.assertEqual(favorable.slippage_cost_usd, 0.0)
        self.assertAlmostEqual(favorable.net_pnl_usd, favorable.gross_pnl_usd)
        charged_twice = replace(
            submission.trades[0],
            spread_cost_usd=1.0,
        )
        separate = _trade(
            trade_id="syn-spread",
            decision_id="dec-spread",
            window_id="synthetic-jan",
            equity_before=100_000.0,
            entry_at=_ts(1, 5, 10),
            exit_at=_ts(1, 5, 12),
            entry_reference=1.1000,
            exit_reference=1.1010,
            entry_price=1.1002,
            exit_price=1.1008,
            stop_price=1.0990,
            target_price=1.1030,
            spread=1.25,
            spread_basis="separate_from_reference",
        )
        negative_commission = replace(submission.trades[0], commission_cost_usd=-1.0)

        self.assertIn("PNL_MISMATCH", _codes(validate_trade_submission(
            replace(submission, trades=(invented, submission.trades[1], submission.trades[2]))
        )))
        self.assertIn("R_MISMATCH", _codes(validate_trade_submission(
            replace(submission, trades=(invented, submission.trades[1], submission.trades[2]))
        )))
        self.assertTrue(validate_trade_submission(_submit((favorable,), (
            _window("synthetic-jan", _ts(1, 1, 0), _ts(2, 1, 0), (favorable,)),
        ))).accepted)
        self.assertIn("DOUBLE_COUNTED_SPREAD", _codes(validate_trade_submission(
            replace(submission, trades=(charged_twice, submission.trades[1], submission.trades[2]))
        )))
        self.assertTrue(validate_trade_submission(_submit((separate,), (
            _window("synthetic-jan", _ts(1, 1, 0), _ts(2, 1, 0), (separate,)),
        ))).accepted)
        self.assertIn("COST_INVALID", _codes(validate_trade_submission(
            replace(submission, trades=(negative_commission,) + submission.trades[1:])
        )))

    def test_windows_reset_equity_and_must_match_declared_aggregates(self) -> None:
        submission = _baseline()
        carried = submission.trades[2]
        wrong_before = submission.trades[1].risk_equity_after_usd
        carried = replace(
            carried,
            risk_equity_before_usd=wrong_before,
            risk_equity_after_usd=wrong_before + carried.net_pnl_usd,
            claimed_net_r=carried.net_pnl_usd / (wrong_before * RISK),
        )
        carried_result = validate_trade_submission(
            replace(submission, trades=submission.trades[:2] + (carried,))
        )
        self.assertIn("EQUITY_NOT_RESET", _codes(carried_result))

        wrong_total = replace(
            submission.windows[0],
            net_pnl_usd=submission.windows[0].net_pnl_usd + 1.0,
        )
        self.assertIn("AGGREGATE_MISMATCH", _codes(validate_trade_submission(
            replace(submission, windows=(wrong_total, submission.windows[1]))
        )))
        self.assertIn("MISSING_TRADES", _codes(validate_trade_submission(
            replace(submission, expected_trade_ids=("syn-a", "syn-b", "syn-c", "syn-missing"))
        )))
        short_count = replace(submission.windows[0], trade_count=1)
        self.assertIn("EXTRA_TRADES", _codes(validate_trade_submission(
            replace(submission, windows=(short_count, submission.windows[1]))
        )))

        same_exit_a = _trade(
            trade_id="syn-a",
            decision_id="dec-a",
            window_id="synthetic-jan",
            equity_before=100_000.0,
            entry_at=_ts(1, 8, 9),
            exit_at=_ts(1, 8, 12),
            entry_reference=1.1000,
            exit_reference=1.1004,
            entry_price=1.1001,
            exit_price=1.1003,
            stop_price=1.0990,
            target_price=1.1020,
        )
        same_exit_b = _trade(
            trade_id="syn-b",
            decision_id="dec-b",
            window_id="synthetic-jan",
            equity_before=same_exit_a.risk_equity_after_usd,
            entry_at=_ts(1, 8, 10),
            exit_at=_ts(1, 8, 12),
            entry_reference=1.3000,
            exit_reference=1.2990,
            entry_price=1.2998,
            exit_price=1.2992,
            stop_price=1.3010,
            target_price=1.2970,
            direction="SHORT",
        )
        tied = validate_trade_submission(_submit((same_exit_a, same_exit_b), (
            _window("synthetic-jan", _ts(1, 1, 0), _ts(2, 1, 0), (same_exit_a, same_exit_b)),
        )))
        self.assertTrue(tied.accepted, tied.findings)
        swapped = validate_trade_submission(_submit((same_exit_b, same_exit_a), (
            _window("synthetic-jan", _ts(1, 1, 0), _ts(2, 1, 0), (same_exit_b, same_exit_a)),
        )))
        self.assertIn("NOT_CHRONOLOGICAL", _codes(swapped))

    def test_synthetic_fixture_cannot_claim_the_original_phase7_archive(self) -> None:
        submission = _baseline()
        record = phase7_public_preservation_record()
        run_id = record["original_historical_run"]["run_id"]
        claimed = validate_trade_submission(_submit(
            submission.trades,
            submission.windows,
            label="original Phase 7 Stage 2 trades",
            source_run_id=run_id,
        ))
        self.assertIn("FABRICATED_PHASE7_CLAIM", _codes(claimed))
        self.assertIn("SYNTHETIC_CLAIMS_SOURCE", _codes(claimed))
        zip_claim = validate_trade_submission(replace(
            submission, claims_trades_from_stage2_zip=True
        ))
        self.assertIn("ARCHIVE_HAS_NO_TRADE_LEDGER", _codes(zip_claim))
        self.assertFalse(zip_claim.original_phase7_trade_ledger_verified)

        cited = validate_trade_submission(_submit(
            submission.trades,
            submission.windows,
            role="separately_authorized_submission",
            label="unauthenticated citation",
            source_run_id=run_id,
            source_artifact_id=record["original_artifact"]["artifact_id"],
            source_commit=record["original_historical_run"]["head_sha"],
        ))
        self.assertTrue(cited.accepted, cited.findings)
        self.assertFalse(cited.original_phase7_trade_ledger_verified)

    def test_overlapping_windows_must_be_separate_resets(self) -> None:
        submission = _baseline()
        overlapped = replace(
            submission.windows[1],
            start_utc=_ts(1, 15, 0),
            end_exclusive_utc=_ts(2, 15, 0),
        )
        self.assertIn("OVERLAPPING_WINDOWS", _codes(validate_trade_submission(
            replace(submission, windows=(submission.windows[0], overlapped))
        )))
        separate = validate_trade_submission(replace(
            submission,
            windows=(
                replace(submission.windows[0], overlap_role="separate_scenario"),
                replace(overlapped, overlap_role="separate_scenario"),
            ),
        ))
        self.assertNotIn("OVERLAPPING_WINDOWS", _codes(separate))
        self.assertTrue(separate.accepted, separate.findings)

    def test_risk_above_the_hard_maximum_is_rejected(self) -> None:
        submission = _baseline()
        result = validate_trade_submission(replace(submission, requested_risk_fraction=0.01))
        self.assertIn("RISK_FRACTION_INVALID", _codes(result))
        self.assertFalse(result.accepted)

    def test_a_path_is_not_opened(self) -> None:
        with self.assertRaises(TypeError):
            validate_trade_submission("/tmp/phase7-stage2.zip")  # type: ignore[arg-type]
        source = Path(validate_trade_submission.__globals__["__file__"]).read_text()
        for token in (
            "urlopen",
            "urlretrieve",
            "archive_download",
            "LoadedPhase7Bars",
            "return_vs_ruin",
            "read_bytes",
        ):
            self.assertNotIn(token, source)

    def test_preservation_record_keeps_the_five_objects_distinct(self) -> None:
        record = phase7_public_preservation_record()
        self.assertEqual(record["original_historical_run"]["run_id"], "35015277625")
        self.assertEqual(record["original_historical_run"]["head_sha"],
                         "a1f8a0466463c79fdbceb9d6ebad9e3ea809474d")
        self.assertEqual(record["original_artifact"]["artifact_id"], "10414817824")
        self.assertEqual(
            record["original_artifact"]["zip_sha256"],
            "2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4",
        )
        self.assertEqual(record["original_artifact"]["expires_at"], "2026-12-14T19:43:07Z")
        self.assertEqual(
            record["original_artifact"]["documented_members"],
            ("manifest.json", "result.json", "windows.json"),
        )
        self.assertFalse(record["original_artifact"]["zip_downloaded_by_this_component"])
        self.assertEqual(
            record["preserved_copy"]["owner_stated_location"],
            "ChatGPT Library /FMP/Phase7/",
        )
        self.assertFalse(record["preserved_copy"]["inspected_by_this_component"])
        self.assertFalse(record["published_aggregates"]["contains_ordered_r_series"])
        self.assertFalse(record["individual_trade_records"]["available_from_authorized_sources"])
        self.assertFalse(
            record["individual_trade_records"]["contained_in_documented_stage2_zip"]
        )

    def test_aggregate_inputs_do_not_produce_probabilities(self) -> None:
        submission = _baseline()
        validation = validate_trade_submission(submission)
        readiness = assess_statistical_readiness(
            validation,
            StatisticalEvidenceDeclaration(data_reuse="already_scored", dependence="iid"),
        )
        by_name = {item.name: item for item in readiness.estimands}
        self.assertFalse(readiness.probabilities_computed)
        self.assertFalse(readiness.demonstrated_edge)
        self.assertFalse(readiness.leverage_optimized)
        self.assertIsNone(readiness.selected_scenario)
        self.assertNotIn("doubling_probability", readiness.__dataclass_fields__)
        self.assertEqual(by_name["after_cost_expectancy"].status, "DESCRIPTIVE_ONLY")
        self.assertIn("INDEPENDENCE_ASSUMED", by_name["probability_double_within_30_days"].reason_codes)
        self.assertIn("DATA_ALREADY_SCORED", by_name["probability_lose_at_least_50_percent"].reason_codes)
        self.assertEqual(by_name["probability_lose_at_least_90_percent"].status, "BLOCKED")
        self.assertEqual(by_name["confidence_interval"].status, "BLOCKED")
        self.assertIsNotNone(readiness.descriptive_mean_net_r)

    def test_declared_inputs_are_still_not_a_computed_probability(self) -> None:
        validation = validate_trade_submission(_baseline())
        declaration = StatisticalEvidenceDeclaration(
            dependence="blocked",
            block_definition="utc-week",
            selection_family_complete=True,
            total_hypotheses=4,
            data_reuse="prospective",
            cost_provenance_id="caller-cost-2026-11-17",
            path_definition="mark_to_market",
            overlap_declaration="no_overlap",
            no_trade_calendar_day_count=30,
            horizon_days=30,
            probability_path="terminal",
            doubling_barrier_declared=True,
            loss_barriers=(0.5, 0.9),
        )
        readiness = assess_statistical_readiness(validation, declaration)
        by_name = {item.name: item for item in readiness.estimands}
        self.assertEqual(by_name["after_cost_expectancy"].status, "DESCRIPTIVE_ONLY")
        self.assertIn("NOT_CONFIRMATORY", by_name["after_cost_expectancy"].reason_codes)
        for name in (
            "confidence_interval",
            "loss_and_drawdown_distribution",
            "probability_double_within_30_days",
            "probability_lose_at_least_50_percent",
            "probability_lose_at_least_90_percent",
        ):
            self.assertEqual(by_name[name].status, "INPUTS_PRESENT_NOT_COMPUTED", name)
            self.assertIn("DATA_REUSE_DECLARED_UNAUTHENTICATED", by_name[name].reason_codes)
        self.assertEqual(by_name["cost_and_frequency_sensitivity"].status, "BLOCKED")
        self.assertIn("NO_COST_SCENARIO", by_name["cost_and_frequency_sensitivity"].reason_codes)
        self.assertFalse(readiness.probabilities_computed)
        self.assertFalse(readiness.demonstrated_edge)

    def test_cost_and_frequency_scenarios_are_listed_and_not_selected(self) -> None:
        primary_trade = _trade(
            trade_id="syn-win",
            decision_id="dec-win",
            window_id="synthetic-jan",
            equity_before=100_000.0,
            entry_at=_ts(1, 2, 10),
            exit_at=_ts(1, 2, 14),
            entry_reference=1.1000,
            exit_reference=1.1010,
            entry_price=1.1002,
            exit_price=1.1008,
            stop_price=1.0990,
            target_price=1.1030,
        )
        losing_trade = _trade(
            trade_id="syn-loss",
            decision_id="dec-loss",
            window_id="synthetic-jan",
            equity_before=100_000.0,
            entry_at=_ts(1, 3, 10),
            exit_at=_ts(1, 3, 16),
            entry_reference=1.2000,
            exit_reference=1.2020,
            entry_price=1.1996,
            exit_price=1.2024,
            stop_price=1.2030,
            target_price=1.1980,
            direction="SHORT",
        )
        primary = validate_trade_submission(_submit((primary_trade,), (
            _window("synthetic-jan", _ts(1, 1, 0), _ts(2, 1, 0), (primary_trade,)),
        )))
        losing = validate_trade_submission(_submit((losing_trade,), (
            _window("synthetic-jan", _ts(1, 1, 0), _ts(2, 1, 0), (losing_trade,)),
        )))
        winning_again = validate_trade_submission(_submit((primary_trade,), (
            _window("synthetic-jan", _ts(1, 1, 0), _ts(2, 1, 0), (primary_trade,)),
        ), label="synthetic-frequency"))
        readiness = assess_statistical_readiness(
            primary,
            StatisticalEvidenceDeclaration(),
            cost_scenarios=(losing, winning_again),
            frequency_scenarios=(losing,),
        )
        self.assertEqual(
            readiness.cost_scenario_mean_net_r,
            (losing.descriptive_mean_net_r, winning_again.descriptive_mean_net_r),
        )
        self.assertTrue(readiness.cost_sign_flip)
        self.assertIsNone(readiness.selected_scenario)
        self.assertFalse(readiness.leverage_optimized)
        sensitivity = {item.name: item for item in readiness.estimands}[
            "cost_and_frequency_sensitivity"
        ]
        self.assertEqual(sensitivity.status, "DESCRIPTIVE_ONLY")
        self.assertIn("NO_SCENARIO_SELECTED", sensitivity.reason_codes)
        self.assertIn("LEVERAGE_NOT_OPTIMIZED", sensitivity.reason_codes)
        self.assertFalse(readiness.probabilities_computed)

        changed_risk_trade = _trade(
            trade_id="syn-risk",
            decision_id="dec-risk",
            window_id="synthetic-jan",
            equity_before=100_000.0,
            entry_at=_ts(1, 2, 10),
            exit_at=_ts(1, 2, 14),
            entry_reference=1.1000,
            exit_reference=1.1010,
            entry_price=1.1002,
            exit_price=1.1008,
            stop_price=1.0990,
            target_price=1.1030,
            risk=0.004,
        )
        changed = validate_trade_submission(_submit(
            (changed_risk_trade,),
            (_window("synthetic-jan", _ts(1, 1, 0), _ts(2, 1, 0), (changed_risk_trade,)),),
            risk=0.004,
        ))
        self.assertTrue(changed.accepted, changed.findings)
        blocked = assess_statistical_readiness(
            primary,
            StatisticalEvidenceDeclaration(),
            cost_scenarios=(changed,),
            frequency_scenarios=(losing,),
        )
        blocked_sensitivity = {item.name: item for item in blocked.estimands}[
            "cost_and_frequency_sensitivity"
        ]
        self.assertEqual(blocked_sensitivity.status, "BLOCKED")
        self.assertIn("SCENARIO_RISK_FRACTION_CHANGED", blocked_sensitivity.reason_codes)
        self.assertEqual(blocked.cost_scenario_mean_net_r, ())


if __name__ == "__main__":
    unittest.main()
