from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import unittest

from fmp.portfolio.acceptance_review import (
    PHASE8A_RESEARCH_REJECTED,
    PHASE8A_SHADOW_CANDIDATE_ACCEPTED,
    resolve_phase8a_shadow_candidate_records,
    review_phase8a_acceptance,
    write_phase8a_acceptance_artifacts,
)
from fmp.portfolio.challenger_discovery import (
    build_exp015_challengers,
    exp015_catalog_identity_sha256,
)
from fmp.portfolio.challenger_discovery_stage_a import (
    exp015_strategy_source_sha256,
)
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.portfolio.selection_runner import (
    build_dec042_pool_records,
    build_dec042_preflight,
    run_dec042_selection,
)


RUNNER_COMMIT = "f" * 40
EXP015_COMMIT = "a" * 40


def _stable_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _baseline():
    eligible = [
        item
        for item in build_phase4_baseline_inventory()
        if item.lifecycle.value == "HISTORICAL_QUALIFIED"
    ]
    assert len(eligible) == 1
    return eligible[0]


def _exp015_final() -> dict[str, object]:
    baseline = _baseline()
    catalog = build_exp015_challengers(code_commit=EXP015_COMMIT)
    chosen = next(
        item
        for item in catalog
        if item.strategy.symbol != baseline.strategy.symbol
        and item.strategy.family != baseline.strategy.family
    )
    selected = [chosen.strategy.fingerprint]
    dispositions = []
    for item in catalog:
        qualified = item.strategy.fingerprint == chosen.strategy.fingerprint
        dispositions.append(
            {
                "strategy_fingerprint": item.strategy.fingerprint,
                "symbol": item.strategy.symbol,
                "family": item.strategy.family,
                "timeframe": item.strategy.timeframe,
                "lifecycle": (
                    "HISTORICAL_QUALIFIED" if qualified else "RETIRED"
                ),
                "evidence_id": "EXP-20260922-015:FINAL_SHORTLIST",
                "reason": (
                    "SELECTED_FINAL_SHORTLIST"
                    if qualified
                    else "FAILED_STAGE_A_GATE"
                ),
            }
        )
    s = chosen.strategy
    return {
        "protocol": "fmp-phase8a-exp015-final-shortlist-v1",
        "experiment_id": "EXP-20260922-015",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "promotion_authorized": False,
        "stage_a_runner_code_commit": EXP015_COMMIT,
        "stage_b_runner_code_commit": "b" * 40,
        "stage_c_runner_code_commit": "c" * 40,
        "catalog_identity_sha256": exp015_catalog_identity_sha256(
            code_commit=EXP015_COMMIT
        ),
        "strategy_source_sha256": exp015_strategy_source_sha256(),
        "tested_candidate_count": 567,
        "stage_a_survivor_count": 1,
        "stage_b_pass_count": 1,
        "stage_c_pass_count": 1,
        "final_ranked_fingerprints": selected,
        "historical_qualified_count": 1,
        "historical_qualified_fingerprints": selected,
        "selected_pair_counts": {s.symbol: 1},
        "selected_family_counts": {s.family: 1},
        "selected_cell_counts": {
            f"{s.symbol}|{s.family}|{s.timeframe}": 1
        },
        "outcome": "CHALLENGER_DISCOVERY_PASS",
        "lifecycle_dispositions": dispositions,
    }


def _joint_result(
    *,
    fingerprints: tuple[str, ...],
    records,
    slippage: float,
    net_return: float,
    passing: bool,
) -> dict[str, object]:
    expectancy = 50.0 if passing else 10.0
    profit_factor = 1.5 if passing else 1.2
    year_breakdown = {
        str(year): {
            "trade_count": 30,
            "net_pnl_usd": (
                1000.0 if year <= 2024 else -100.0
            ),
            "expectancy_usd": 10.0,
            "win_rate": 0.5,
            "average_win_usd": 20.0,
            "average_loss_usd": -10.0,
        }
        for year in range(2019, 2027)
    }
    strategy_contribution = {
        fingerprint: {
            "trade_count": 120,
            "net_pnl_usd": 5000.0,
            "expectancy_usd": 20.0,
            "profit_factor": 1.4,
            "gross_profit_usd": 7000.0,
            "gross_loss_usd": 2000.0,
            "positive_pnl_share": 1.0 / len(fingerprints),
        }
        for fingerprint in fingerprints
    }
    symbols = sorted(
        {
            next(
                item.strategy.symbol
                for item in records
                if item.strategy.fingerprint == fingerprint
            )
            for fingerprint in fingerprints
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
    digest_chars = {"EURUSD": "e", "GBPUSD": "b", "USDJPY": "d"}
    manifests = {
        symbol: digest_chars[symbol] * 64
        for symbol in symbols
    }
    combined_manifest_sha = hashlib.sha256(
        json.dumps(
            dict(sorted(manifests.items())),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    candidate_sha = hashlib.sha256(
        "|".join(fingerprints).encode("utf-8")
    ).hexdigest()
    return {
        "protocol": "fmp-phase8a-joint-portfolio-v1",
        "experiment_id": "EXP-20260922-014",
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
        "combined_processed_manifest_sha256": combined_manifest_sha,
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


def _selection_evidence(
    *,
    baseline_return: float,
    portfolio_return: float,
    portfolio_passes: bool = True,
):
    final = _exp015_final()
    preflight = build_dec042_preflight(
        exp015_final_result=final,
        exp015_final_sha256="2" * 64,
        runner_code_commit=RUNNER_COMMIT,
    )
    preflight_sha = hashlib.sha256(_stable_bytes(preflight)).hexdigest()
    records = build_dec042_pool_records(final)
    baseline_fp = _baseline().strategy.fingerprint

    def joint_command(**kwargs):
        plan = kwargs["plan"]
        fingerprints = tuple(item.fingerprint for item in plan.strategies)
        if len(fingerprints) == 1:
            net_return = (
                baseline_return
                if fingerprints[0] == baseline_fp
                else min(baseline_return, portfolio_return) / 2
            )
            passing = True
        else:
            net_return = portfolio_return
            passing = portfolio_passes
        result = _joint_result(
            fingerprints=fingerprints,
            records=records,
            slippage=plan.slippage_pips,
            net_return=net_return,
            passing=passing,
        )
        if not passing:
            result["metrics"]["phase3_metrics"]["net_return"] = -0.01
            result["metrics"]["phase3_metrics"]["expectancy_usd"] = -5.0
            result["metrics"]["phase3_metrics"]["profit_factor"] = 0.9
            result["metrics"]["calendar_year_breakdown"] = {
                str(year): dict(bucket) | {"net_pnl_usd": -100.0}
                for year, bucket in result["metrics"][
                    "calendar_year_breakdown"
                ].items()
            }
        return result

    selection = run_dec042_selection(
        preflight=preflight,
        preflight_sha256=preflight_sha,
        dataset_sources={
            "EURUSD": (Path("/eur"), Path("/eur.json")),
            "GBPUSD": (Path("/gbp"), Path("/gbp.json")),
            "USDJPY": (Path("/jpy"), Path("/jpy.json")),
        },
        code_commit=RUNNER_COMMIT,
        joint_command=joint_command,
    )
    selection_sha = hashlib.sha256(_stable_bytes(selection)).hexdigest()
    return preflight, preflight_sha, selection, selection_sha


class Phase8AAcceptanceReviewTests(unittest.TestCase):
    def test_accepts_exact_dec042_winner_when_05_annualized_beats_baseline(self) -> None:
        preflight, preflight_sha, selection, selection_sha = (
            _selection_evidence(
                baseline_return=0.05,
                portfolio_return=0.20,
            )
        )
        result = review_phase8a_acceptance(
            preflight=preflight,
            preflight_sha256=preflight_sha,
            selection=selection,
            selection_sha256=selection_sha,
        )
        self.assertEqual(
            result["outcome"],
            PHASE8A_SHADOW_CANDIDATE_ACCEPTED,
        )
        self.assertTrue(result["shadow_candidate_authorized"])
        self.assertTrue(result["phase8b_design_authorized"])
        self.assertTrue(result["economic_improvement_gate_passed"])
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["demo_order_authorized"])
        self.assertFalse(result["live_order_authorized"])
        self.assertFalse(result["real_money_authorized"])
        candidate = result["shadow_candidate"]
        self.assertIsInstance(candidate, dict)
        self.assertEqual(
            candidate["strategy_fingerprints"],
            sorted(result["selected_strategy_fingerprints"]),
        )
        self.assertTrue(
            all(
                item["prior_lifecycle"] == "HISTORICAL_QUALIFIED"
                and item["lifecycle"] == "SHADOW_CANDIDATE"
                for item in candidate["strategies"]
            )
        )
        resolved = resolve_phase8a_shadow_candidate_records(result)
        self.assertEqual(
            [item.strategy.fingerprint for item in resolved],
            candidate["strategy_fingerprints"],
        )

    def test_rejects_selected_portfolio_without_strict_05_improvement(self) -> None:
        preflight, preflight_sha, selection, selection_sha = (
            _selection_evidence(
                baseline_return=0.25,
                portfolio_return=0.20,
            )
        )
        result = review_phase8a_acceptance(
            preflight=preflight,
            preflight_sha256=preflight_sha,
            selection=selection,
            selection_sha256=selection_sha,
        )
        self.assertEqual(result["outcome"], PHASE8A_RESEARCH_REJECTED)
        self.assertEqual(
            result["rejection_reason"],
            "NO_STRICT_05_ANNUALIZED_IMPROVEMENT_OVER_PHASE7_BASELINE",
        )
        self.assertFalse(result["shadow_candidate_authorized"])
        self.assertFalse(result["phase8b_design_authorized"])
        self.assertIsNone(result["shadow_candidate"])

    def test_no_dec042_portfolio_selected_is_credible_rejection(self) -> None:
        preflight, preflight_sha, selection, selection_sha = (
            _selection_evidence(
                baseline_return=0.05,
                portfolio_return=-0.01,
                portfolio_passes=False,
            )
        )
        result = review_phase8a_acceptance(
            preflight=preflight,
            preflight_sha256=preflight_sha,
            selection=selection,
            selection_sha256=selection_sha,
        )
        self.assertEqual(result["outcome"], PHASE8A_RESEARCH_REJECTED)
        self.assertEqual(
            result["rejection_reason"],
            "NO_DEC042_PORTFOLIO_SELECTED",
        )
        self.assertFalse(result["shadow_candidate_authorized"])

    def test_tampered_dec042_ranking_fails_closed(self) -> None:
        preflight, preflight_sha, selection, selection_sha = (
            _selection_evidence(
                baseline_return=0.05,
                portfolio_return=0.20,
            )
        )
        tampered = dict(selection)
        tampered["ranked_passing_sets"] = []
        with self.assertRaisesRegex(ValueError, "ranking does not replay"):
            review_phase8a_acceptance(
                preflight=preflight,
                preflight_sha256=preflight_sha,
                selection=tampered,
                selection_sha256=selection_sha,
            )

    def test_tampered_preflight_digest_fails_closed(self) -> None:
        preflight, _, selection, selection_sha = _selection_evidence(
            baseline_return=0.05,
            portfolio_return=0.20,
        )
        with self.assertRaisesRegex(ValueError, "selection/preflight digest"):
            review_phase8a_acceptance(
                preflight=preflight,
                preflight_sha256="9" * 64,
                selection=selection,
                selection_sha256=selection_sha,
            )

    def test_acceptance_artifact_is_deterministic(self) -> None:
        preflight, preflight_sha, selection, selection_sha = (
            _selection_evidence(
                baseline_return=0.05,
                portfolio_return=0.20,
            )
        )
        result = review_phase8a_acceptance(
            preflight=preflight,
            preflight_sha256=preflight_sha,
            selection=selection,
            selection_sha256=selection_sha,
        )
        with TemporaryDirectory() as left_tmp, TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            left_manifest = write_phase8a_acceptance_artifacts(result, left)
            right_manifest = write_phase8a_acceptance_artifacts(result, right)
            self.assertEqual(
                (left / "acceptance.json").read_bytes(),
                (right / "acceptance.json").read_bytes(),
            )
            self.assertEqual(left_manifest, right_manifest)


if __name__ == "__main__":
    unittest.main()
