from __future__ import annotations

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import unittest

from fmp.portfolio.challenger_discovery import build_exp015_challengers
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.portfolio.selection_runner import (
    DEC042_EXPERIMENT_ID,
    DEC042_PREFLIGHT_PROTOCOL,
    DEC042_RESULT_PROTOCOL,
    build_dec042_pool_records,
    build_dec042_preflight,
    run_dec042_selection,
    write_dec042_preflight_artifacts,
    write_dec042_result_artifacts,
)


RUNNER_COMMIT = "f" * 40
EXP015_COMMIT = "a" * 40


def _baseline():
    eligible = [
        item
        for item in build_phase4_baseline_inventory()
        if item.lifecycle.value == "HISTORICAL_QUALIFIED"
    ]
    assert len(eligible) == 1
    return eligible[0]


def _exp015_final(count: int = 2) -> dict[str, object]:
    catalog = build_exp015_challengers(code_commit=EXP015_COMMIT)
    selected = [item.strategy.fingerprint for item in catalog[:count]]
    selected_set = set(selected)
    dispositions = []
    for item in catalog:
        qualified = item.strategy.fingerprint in selected_set
        dispositions.append(
            {
                "strategy_fingerprint": item.strategy.fingerprint,
                "symbol": item.strategy.symbol,
                "family": item.strategy.family,
                "timeframe": item.strategy.timeframe,
                "lifecycle": "HISTORICAL_QUALIFIED" if qualified else "RETIRED",
                "evidence_id": "EXP-20260922-015:FINAL_SHORTLIST",
                "reason": "SELECTED_FINAL_SHORTLIST" if qualified else "FAILED_STAGE_A_GATE",
            }
        )
    pair_counts = {}
    family_counts = {}
    cell_counts = {}
    for item in catalog[:count]:
        s = item.strategy
        pair_counts[s.symbol] = pair_counts.get(s.symbol, 0) + 1
        family_counts[s.family] = family_counts.get(s.family, 0) + 1
        key = f"{s.symbol}|{s.family}|{s.timeframe}"
        cell_counts[key] = cell_counts.get(key, 0) + 1
    return {
        "protocol": "fmp-phase8a-exp015-final-shortlist-v1",
        "experiment_id": "EXP-20260922-015",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "promotion_authorized": False,
        "stage_a_runner_code_commit": EXP015_COMMIT,
        "stage_b_runner_code_commit": "b" * 40,
        "stage_c_runner_code_commit": "c" * 40,
        "catalog_identity_sha256": "d" * 64,
        "strategy_source_sha256": "e" * 64,
        "tested_candidate_count": 567,
        "stage_a_survivor_count": count,
        "stage_b_pass_count": count,
        "stage_c_pass_count": count,
        "final_ranked_fingerprints": selected,
        "historical_qualified_count": count,
        "historical_qualified_fingerprints": selected,
        "selected_pair_counts": pair_counts,
        "selected_family_counts": family_counts,
        "selected_cell_counts": cell_counts,
        "outcome": "CHALLENGER_DISCOVERY_PASS" if count else "NO_CHALLENGER_QUALIFIED",
        "lifecycle_dispositions": dispositions,
    }


def _joint_result(
    *,
    fingerprints: tuple[str, ...],
    records,
    slippage: float,
    candidate_sha: str = "1" * 64,
    good: bool = True,
) -> dict[str, object]:
    net_return = 0.20 if good else -0.01
    expectancy = 50.0 if good else -5.0
    profit_factor = 1.5 if good else 0.9
    year_breakdown = {
        str(year): {
            "trade_count": 30,
            "net_pnl_usd": 1000.0 if (year <= 2024 or not good) else -100.0,
            "expectancy_usd": 10.0,
            "win_rate": 0.5,
            "average_win_usd": 20.0,
            "average_loss_usd": -10.0,
        }
        for year in range(2019, 2027)
    }
    if not good:
        year_breakdown = {
            str(year): dict(bucket) | {"net_pnl_usd": -100.0}
            for year, bucket in year_breakdown.items()
        }

    strategy_contribution = {}
    for index, fingerprint in enumerate(fingerprints):
        strategy_contribution[fingerprint] = {
            "trade_count": 120,
            "net_pnl_usd": 5000.0,
            "expectancy_usd": 20.0,
            "profit_factor": 1.4,
            "gross_profit_usd": 7000.0,
            "gross_loss_usd": 2000.0,
            "positive_pnl_share": 1.0 / len(fingerprints),
        }
    symbols = sorted(
        {
            next(item.strategy.symbol for item in records if item.strategy.fingerprint == fp)
            for fp in fingerprints
        }
    )
    pair_contribution = {
        symbol: {
            "trade_count": 120,
            "net_pnl_usd": 5000.0,
            "expectancy_usd": 20.0,
            "profit_factor": 1.4,
            "gross_profit_usd": 7000.0,
            "gross_loss_usd": 2000.0,
            "positive_pnl_share": 1.0 / len(symbols),
        }
        for symbol in symbols
    }
    manifests = {symbol: (symbol[0].lower() * 64) for symbol in symbols}
    return {
        "protocol": "fmp-phase8a-joint-portfolio-v1",
        "experiment_id": DEC042_EXPERIMENT_ID,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "promotion_authorized": False,
        "shared_account": True,
        "execution_timeframe": "1m",
        "slippage_pips": slippage,
        "starting_equity_usd": 100_000.0,
        "requested_risk_fraction": 0.0025,
        "runner_code_commit": RUNNER_COMMIT,
        "range_start": "2019-01-01",
        "range_end_exclusive": "2026-08-21",
        "strategy_fingerprints": list(fingerprints),
        "processed_manifest_sha256_by_symbol": manifests,
        "combined_processed_manifest_sha256": "9" * 64,
        "candidate_sha256": candidate_sha,
        "run_identity": {
            "code_commit": RUNNER_COMMIT,
            "slippage_pips": slippage,
        },
        "metrics": {
            "phase3_metrics": {
                "net_pnl_usd": 100_000.0 * net_return,
                "net_return": net_return,
                "expectancy_usd": expectancy,
                "profit_factor": profit_factor,
                "max_drawdown_fraction": 0.03,
            },
            "trade_count": 240,
            "calendar_year_breakdown": year_breakdown,
            "daily_return_summary": {
                "observed_days": 1000,
                "positive_days": 500,
                "negative_days": 400,
                "zero_days": 100,
                "days_ge_10pct": 1,
                "days_ge_10pct_fraction": 0.001,
                "mean_daily_return": 0.0002,
                "best_day_return": 0.11,
                "worst_day_return": -0.02,
            },
        },
        "pair_contribution": pair_contribution,
        "strategy_contribution": strategy_contribution,
        "signal_timeframe_contribution": {},
    }


class Dec042SelectionRunnerTests(unittest.TestCase):
    def test_pool_is_baseline_plus_exact_exp015_qualified_records(self) -> None:
        final = _exp015_final(2)
        records = build_dec042_pool_records(final)
        self.assertEqual(len(records), 3)
        self.assertIn(_baseline().strategy.fingerprint, {x.strategy.fingerprint for x in records})
        self.assertEqual(
            sum(x.evidence_id == "EXP-20260922-015:FINAL_SHORTLIST" for x in records),
            2,
        )

        with self.assertRaisesRegex(ValueError, "between 2 and 12"):
            build_dec042_pool_records(_exp015_final(0))

    def test_preflight_freezes_exact_pool_and_all_sets_deterministically(self) -> None:
        final = _exp015_final(2)
        preflight = build_dec042_preflight(
            exp015_final_result=final,
            exp015_final_sha256="2" * 64,
            runner_code_commit=RUNNER_COMMIT,
        )
        self.assertEqual(preflight["protocol"], DEC042_PREFLIGHT_PROTOCOL)
        self.assertEqual(preflight["experiment_id"], DEC042_EXPERIMENT_ID)
        self.assertEqual(preflight["strategy_count"], 3)
        self.assertEqual(preflight["set_count"], 7)
        self.assertEqual(
            [len(item) for item in preflight["portfolio_sets"]],
            [1, 1, 1, 2, 2, 2, 3],
        )
        self.assertEqual(preflight["range_start"], "2019-01-01")
        self.assertEqual(preflight["range_end_exclusive"], "2026-08-21")
        self.assertEqual(preflight["slippage_scenarios"], [0.2, 0.5, 1.0])
        self.assertEqual(len(preflight["set_universe_sha256"]), 64)
        self.assertFalse(preflight["promotion_authorized"])

        repeated = build_dec042_preflight(
            exp015_final_result=final,
            exp015_final_sha256="2" * 64,
            runner_code_commit=RUNNER_COMMIT,
        )
        self.assertEqual(preflight, repeated)

    def test_selection_runs_exact_frozen_set_universe_and_selects_passing_multistrategy(self) -> None:
        final = _exp015_final(2)
        preflight = build_dec042_preflight(
            exp015_final_result=final,
            exp015_final_sha256="2" * 64,
            runner_code_commit=RUNNER_COMMIT,
        )
        calls = []

        def joint_command(**kwargs):
            plan = kwargs["plan"]
            fps = tuple(item.fingerprint for item in plan.strategies)
            calls.append((fps, plan.slippage_pips))
            return _joint_result(
                fingerprints=fps,
                records=build_dec042_pool_records(final),
                slippage=plan.slippage_pips,
                good=len(fps) >= 2,
            )

        result = run_dec042_selection(
            preflight=preflight,
            preflight_sha256="3" * 64,
            dataset_sources={
                "EURUSD": (Path("/eur"), Path("/eur.json")),
                "GBPUSD": (Path("/gbp"), Path("/gbp.json")),
                "USDJPY": (Path("/jpy"), Path("/jpy.json")),
            },
            code_commit=RUNNER_COMMIT,
            joint_command=joint_command,
        )
        self.assertEqual(result["protocol"], DEC042_RESULT_PROTOCOL)
        self.assertEqual(len(calls), preflight["set_count"] * 3)
        self.assertEqual(result["evaluated_set_count"], preflight["set_count"])
        self.assertEqual(result["outcome"], "PORTFOLIO_SELECTION_PASS")
        self.assertIsNotNone(result["selected_strategy_fingerprints"])
        self.assertGreaterEqual(len(result["selected_strategy_fingerprints"]), 2)
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["shadow_candidate_authorized"])

    def test_selection_rejects_candidate_sequence_drift_across_costs(self) -> None:
        final = _exp015_final(1)
        preflight = build_dec042_preflight(
            exp015_final_result=final,
            exp015_final_sha256="2" * 64,
            runner_code_commit=RUNNER_COMMIT,
        )

        def joint_command(**kwargs):
            plan = kwargs["plan"]
            fps = tuple(item.fingerprint for item in plan.strategies)
            return _joint_result(
                fingerprints=fps,
                records=build_dec042_pool_records(final),
                slippage=plan.slippage_pips,
                candidate_sha=("1" * 64 if plan.slippage_pips != 0.5 else "2" * 64),
            )

        with self.assertRaisesRegex(ValueError, "candidate sequence"):
            run_dec042_selection(
                preflight=preflight,
                preflight_sha256="3" * 64,
                dataset_sources={
                    "USDJPY": (Path("/jpy"), Path("/jpy.json")),
                    "EURUSD": (Path("/eur"), Path("/eur.json")),
                    "GBPUSD": (Path("/gbp"), Path("/gbp.json")),
                },
                code_commit=RUNNER_COMMIT,
                joint_command=joint_command,
            )

    def test_no_passing_set_returns_no_portfolio_selected(self) -> None:
        final = _exp015_final(1)
        preflight = build_dec042_preflight(
            exp015_final_result=final,
            exp015_final_sha256="2" * 64,
            runner_code_commit=RUNNER_COMMIT,
        )

        def joint_command(**kwargs):
            plan = kwargs["plan"]
            fps = tuple(item.fingerprint for item in plan.strategies)
            return _joint_result(
                fingerprints=fps,
                records=build_dec042_pool_records(final),
                slippage=plan.slippage_pips,
                good=False,
            )

        result = run_dec042_selection(
            preflight=preflight,
            preflight_sha256="3" * 64,
            dataset_sources={
                "EURUSD": (Path("/eur"), Path("/eur.json")),
                "GBPUSD": (Path("/gbp"), Path("/gbp.json")),
                "USDJPY": (Path("/jpy"), Path("/jpy.json")),
            },
            code_commit=RUNNER_COMMIT,
            joint_command=joint_command,
        )
        self.assertEqual(result["outcome"], "NO_PORTFOLIO_SELECTED")
        self.assertIsNone(result["selected_strategy_fingerprints"])
        self.assertEqual(result["passing_set_count"], 0)

    def test_preflight_and_result_artifacts_are_deterministic(self) -> None:
        final = _exp015_final(1)
        preflight = build_dec042_preflight(
            exp015_final_result=final,
            exp015_final_sha256="2" * 64,
            runner_code_commit=RUNNER_COMMIT,
        )
        result = {
            "protocol": DEC042_RESULT_PROTOCOL,
            "experiment_id": DEC042_EXPERIMENT_ID,
            "promotion_authorized": False,
        }
        with TemporaryDirectory() as a, TemporaryDirectory() as b:
            left = Path(a)
            right = Path(b)
            self.assertEqual(
                write_dec042_preflight_artifacts(preflight, left),
                write_dec042_preflight_artifacts(preflight, right),
            )
            self.assertEqual(
                (left / "preflight.json").read_bytes(),
                (right / "preflight.json").read_bytes(),
            )
        with TemporaryDirectory() as a, TemporaryDirectory() as b:
            left = Path(a)
            right = Path(b)
            self.assertEqual(
                write_dec042_result_artifacts(result, left),
                write_dec042_result_artifacts(result, right),
            )
            self.assertEqual(
                (left / "selection.json").read_bytes(),
                (right / "selection.json").read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
