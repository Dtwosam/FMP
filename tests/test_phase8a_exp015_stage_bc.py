from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import unittest

from fmp.contracts import QuoteBar
from fmp.portfolio.challenger_discovery import (
    build_exp015_challengers,
    exp015_catalog_identity_sha256,
)
from fmp.portfolio.challenger_discovery_stage_a import (
    EXP015_STAGE_A_AUTHORIZATION_PROTOCOL,
    exp015_strategy_source_sha256,
)
from fmp.portfolio.challenger_discovery_stage_bc import (
    EXP015_FINAL_PROTOCOL,
    EXP015_STAGE_B_PROTOCOL,
    EXP015_STAGE_C_PROTOCOL,
    finalize_exp015_shortlist,
    resolve_exp015_historical_qualified_records,
    run_exp015_stage_b,
    run_exp015_stage_c,
    write_exp015_final_artifacts,
)
from fmp.portfolio.research_data import (
    LoadedRetrospectiveBars,
    PHASE8A_RETROSPECTIVE_LABEL,
)


STAGE_A_COMMIT = "a" * 40
STAGE_B_COMMIT = "b" * 40
STAGE_C_COMMIT = "c" * 40


def _authorization(survivor_fingerprints: tuple[str, ...]) -> dict[str, object]:
    catalog = build_exp015_challengers(code_commit=STAGE_A_COMMIT)
    survivor_set = set(survivor_fingerprints)
    cells = []
    for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
        for timeframe in ("5m", "15m", "1h"):
            records = [
                item
                for item in catalog
                if item.strategy.symbol == symbol
                and item.strategy.timeframe == timeframe
            ]
            fingerprints = sorted(item.strategy.fingerprint for item in records)
            survivors = sorted(survivor_set.intersection(fingerprints))
            by_family = {}
            for item in records:
                by_family.setdefault(item.strategy.family, []).append(
                    item.strategy.fingerprint
                )
            family_rankings = {}
            strategy_gates = {}
            survivor_set_for_cell = set(survivors)
            for family, family_fingerprints in by_family.items():
                selected = sorted(
                    survivor_set_for_cell.intersection(family_fingerprints)
                )
                family_rankings[family] = {
                    "passing_fingerprints": selected,
                    "selected_fingerprints": selected,
                }
                for fingerprint in family_fingerprints:
                    item = next(
                        value
                        for value in records
                        if value.strategy.fingerprint == fingerprint
                    )
                    strategy_gates[fingerprint] = {
                        "family": family,
                        "parameters_json": item.strategy.parameters_json,
                        "mandatory_gate_pass": fingerprint in survivor_set_for_cell,
                        "annualized_return_02": 0.01
                        if fingerprint in survivor_set_for_cell
                        else None,
                        "annualized_return_05": 0.01
                        if fingerprint in survivor_set_for_cell
                        else None,
                    }
            cells.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "strategy_fingerprints": fingerprints,
                    "survivor_fingerprints": survivors,
                    "family_rankings": family_rankings,
                    "strategy_gates": strategy_gates,
                }
            )
    return {
        "protocol": EXP015_STAGE_A_AUTHORIZATION_PROTOCOL,
        "experiment_id": "EXP-20260922-015",
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "runner_code_commit": STAGE_A_COMMIT,
        "catalog_identity_sha256": exp015_catalog_identity_sha256(
            code_commit=STAGE_A_COMMIT
        ),
        "strategy_source_sha256": exp015_strategy_source_sha256(),
        "cell_count": 9,
        "ranking_cell_count": 54,
        "strategy_identity_count": 567,
        "maximum_stage_a_survivors": 108,
        "survivor_count": len(survivor_fingerprints),
        "survivor_fingerprints": list(sorted(survivor_fingerprints)),
        "stage_b_source_open_authorized": bool(survivor_fingerprints),
        "cells": cells,
    }


def _bar(symbol: str, day: date) -> QuoteBar:
    price = 150.0 if symbol == "USDJPY" else 1.10
    half = 0.01 if symbol == "USDJPY" else 0.0001
    return QuoteBar(
        timestamp_utc=datetime(day.year, day.month, day.day, 8, 0, tzinfo=timezone.utc),
        symbol=symbol,
        bid_open=price - half,
        bid_high=price + 2 * half,
        bid_low=price - 2 * half,
        bid_close=price,
        ask_open=price + half,
        ask_high=price + 4 * half,
        ask_low=price,
        ask_close=price + 2 * half,
    )


def _loaded(symbol: str, research_range) -> LoadedRetrospectiveBars:
    day = research_range.start + timedelta(days=2)
    return LoadedRetrospectiveBars(
        bars=(_bar(symbol, day),),
        excluded_incomplete_count=0,
        eligible_utc_dates=(day,),
        evidence_label=PHASE8A_RETROSPECTIVE_LABEL,
        start=research_range.start,
        end_exclusive=research_range.end_exclusive,
        processed_manifest_sha256=("e" if symbol == "EURUSD" else "f") * 64,
        opened_artifact_months=(f"{day.year:04d}-{day.month:02d}",),
    )


def _metrics(
    *,
    research_range,
    trade_count: int,
    positive_years: int,
    net_return: float = 0.04,
    profit_factor: float = 1.30,
    drawdown: float = 0.02,
) -> dict[str, object]:
    years = list(range(research_range.start.year, research_range.end_exclusive.year))
    year_breakdown = {}
    for index, year in enumerate(years):
        pnl = 1000.0 if index < positive_years else -100.0
        year_breakdown[str(year)] = {
            "trade_count": max(1, trade_count // max(1, len(years))),
            "net_pnl_usd": pnl,
            "expectancy_usd": pnl / max(1, trade_count // max(1, len(years))),
            "win_rate": 0.5,
            "average_win_usd": 10.0,
            "average_loss_usd": -8.0,
        }
    return {
        "trade_count": trade_count,
        "phase3_metrics": {
            "net_pnl_usd": 100000.0 * net_return,
            "net_return": net_return,
            "expectancy_usd": 10.0 if net_return > 0 else -10.0,
            "profit_factor": profit_factor,
            "max_drawdown_fraction": drawdown,
        },
        "calendar_year_breakdown": year_breakdown,
    }


def _runner(*, positive_years: int = 4, trade_count: int = 60):
    def run(**kwargs):
        plan = kwargs["plan"]
        return {
            "strategy_fingerprint": plan.strategy.fingerprint,
            "processed_manifest_sha256": (
                "e" * 64 if plan.strategy.symbol == "EURUSD" else "f" * 64
            ),
            "candidate_sha256": hashlib.sha256(
                plan.strategy.fingerprint.encode("utf-8")
            ).hexdigest(),
            "slippage_pips": plan.slippage_pips,
            "run_identity": {"code_commit": plan.runner_code_commit},
            "metrics": _metrics(
                research_range=plan.research_range,
                trade_count=trade_count,
                positive_years=positive_years,
            ),
        }
    return run


def _sha(value: object) -> str:
    return hashlib.sha256(
        (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    ).hexdigest()


class Exp015StageBCTests(unittest.TestCase):
    def test_stage_b_no_survivors_fails_before_source_io(self) -> None:
        touched = False

        def loader(**kwargs):
            nonlocal touched
            touched = True
            return _loaded(kwargs["symbol"], kwargs["research_range"])

        with self.assertRaisesRegex(ValueError, "Stage B source-open"):
            run_exp015_stage_b(
                authorization=_authorization(()),
                stage_a_authorization_sha256="1" * 64,
                dataset_sources={},
                code_commit=STAGE_B_COMMIT,
                bars_loader=loader,
            )
        self.assertFalse(touched)

    def test_stage_b_enforces_positive_year_gate(self) -> None:
        record = build_exp015_challengers(code_commit=STAGE_A_COMMIT)[0]
        authorization = _authorization((record.strategy.fingerprint,))
        result = run_exp015_stage_b(
            authorization=authorization,
            stage_a_authorization_sha256="1" * 64,
            dataset_sources={
                record.strategy.symbol: (Path("/data"), Path("/manifest.json")),
            },
            code_commit=STAGE_B_COMMIT,
            bars_loader=lambda **kwargs: _loaded(
                kwargs["symbol"], kwargs["research_range"]
            ),
            strategy_runner=_runner(positive_years=2, trade_count=60),
        )
        self.assertEqual(result["protocol"], EXP015_STAGE_B_PROTOCOL)
        self.assertEqual(result["range_start"], "2019-01-01")
        self.assertEqual(result["range_end_exclusive"], "2023-01-01")
        self.assertEqual(result["stage_b_pass_fingerprints"], [])
        self.assertFalse(result["stage_c_source_open_authorized"])
        gate = result["strategy_gates"][record.strategy.fingerprint]
        self.assertTrue(gate["scenario_02_pass"])
        self.assertTrue(gate["scenario_05_pass"])
        self.assertEqual(gate["positive_year_count_02"], 2)
        self.assertFalse(gate["positive_years_ge_3_02"])
        self.assertFalse(gate["stage_pass"])

    def test_stage_c_requires_exact_stage_b_passers_and_frozen_range(self) -> None:
        record = build_exp015_challengers(code_commit=STAGE_A_COMMIT)[0]
        authorization = _authorization((record.strategy.fingerprint,))
        stage_a_sha = "1" * 64
        stage_b = run_exp015_stage_b(
            authorization=authorization,
            stage_a_authorization_sha256=stage_a_sha,
            dataset_sources={
                record.strategy.symbol: (Path("/data"), Path("/manifest.json")),
            },
            code_commit=STAGE_B_COMMIT,
            bars_loader=lambda **kwargs: _loaded(
                kwargs["symbol"], kwargs["research_range"]
            ),
            strategy_runner=_runner(positive_years=4, trade_count=60),
        )
        self.assertEqual(
            stage_b["stage_b_pass_fingerprints"],
            [record.strategy.fingerprint],
        )
        stage_c = run_exp015_stage_c(
            stage_a_authorization=authorization,
            stage_a_authorization_sha256=stage_a_sha,
            stage_b_result=stage_b,
            stage_b_result_sha256="2" * 64,
            dataset_sources={
                record.strategy.symbol: (Path("/data"), Path("/manifest.json")),
            },
            code_commit=STAGE_C_COMMIT,
            bars_loader=lambda **kwargs: _loaded(
                kwargs["symbol"], kwargs["research_range"]
            ),
            strategy_runner=_runner(positive_years=3, trade_count=40),
        )
        self.assertEqual(stage_c["protocol"], EXP015_STAGE_C_PROTOCOL)
        self.assertEqual(stage_c["range_start"], "2023-01-01")
        self.assertEqual(stage_c["range_end_exclusive"], "2026-08-21")
        self.assertEqual(
            stage_c["stage_c_pass_fingerprints"],
            [record.strategy.fingerprint],
        )
        self.assertTrue(stage_c["final_shortlist_review_authorized"])

        tampered = dict(stage_b) | {"stage_b_pass_fingerprints": []}
        touched = False

        def loader(**kwargs):
            nonlocal touched
            touched = True
            return _loaded(kwargs["symbol"], kwargs["research_range"])

        with self.assertRaises(ValueError):
            run_exp015_stage_c(
                stage_a_authorization=authorization,
                stage_a_authorization_sha256=stage_a_sha,
                stage_b_result=tampered,
                stage_b_result_sha256="2" * 64,
                dataset_sources={},
                code_commit=STAGE_C_COMMIT,
                bars_loader=loader,
            )
        self.assertFalse(touched)

    def test_final_shortlist_enforces_caps_and_retires_all_unselected(self) -> None:
        catalog = build_exp015_challengers(code_commit=STAGE_A_COMMIT)
        # Use up to two per exact family cell, across enough cells to exercise caps.
        survivors = []
        per_cell = {}
        for item in catalog:
            key = (
                item.strategy.symbol,
                item.strategy.family,
                item.strategy.timeframe,
            )
            if per_cell.get(key, 0) >= 2:
                continue
            survivors.append(item.strategy.fingerprint)
            per_cell[key] = per_cell.get(key, 0) + 1
            if len(survivors) == 24:
                break

        authorization = _authorization(tuple(sorted(survivors)))
        stage_a_sha = "1" * 64
        sources = {
            "EURUSD": (Path("/eur"), Path("/eur.json")),
            "GBPUSD": (Path("/gbp"), Path("/gbp.json")),
            "USDJPY": (Path("/jpy"), Path("/jpy.json")),
        }
        stage_b = run_exp015_stage_b(
            authorization=authorization,
            stage_a_authorization_sha256=stage_a_sha,
            dataset_sources=sources,
            code_commit=STAGE_B_COMMIT,
            bars_loader=lambda **kwargs: _loaded(
                kwargs["symbol"], kwargs["research_range"]
            ),
            strategy_runner=_runner(positive_years=4, trade_count=60),
        )
        stage_b_sha = "2" * 64
        stage_c = run_exp015_stage_c(
            stage_a_authorization=authorization,
            stage_a_authorization_sha256=stage_a_sha,
            stage_b_result=stage_b,
            stage_b_result_sha256=stage_b_sha,
            dataset_sources=sources,
            code_commit=STAGE_C_COMMIT,
            bars_loader=lambda **kwargs: _loaded(
                kwargs["symbol"], kwargs["research_range"]
            ),
            strategy_runner=_runner(positive_years=4, trade_count=40),
        )
        final = finalize_exp015_shortlist(
            stage_a_authorization=authorization,
            stage_a_authorization_sha256=stage_a_sha,
            stage_b_result=stage_b,
            stage_b_result_sha256=stage_b_sha,
            stage_c_result=stage_c,
            stage_c_result_sha256="3" * 64,
        )
        self.assertEqual(final["protocol"], EXP015_FINAL_PROTOCOL)
        self.assertEqual(final["tested_candidate_count"], 567)
        self.assertLessEqual(final["historical_qualified_count"], 11)
        self.assertTrue(
            all(value <= 4 for value in final["selected_pair_counts"].values())
        )
        self.assertTrue(
            all(value <= 3 for value in final["selected_family_counts"].values())
        )
        self.assertTrue(
            all(value <= 2 for value in final["selected_cell_counts"].values())
        )
        self.assertEqual(len(final["lifecycle_dispositions"]), 567)
        self.assertEqual(
            sum(
                1
                for item in final["lifecycle_dispositions"]
                if item["lifecycle"] == "HISTORICAL_QUALIFIED"
            ),
            final["historical_qualified_count"],
        )
        self.assertEqual(
            sum(
                1
                for item in final["lifecycle_dispositions"]
                if item["lifecycle"] == "RETIRED"
            ),
            567 - final["historical_qualified_count"],
        )
        resolved = resolve_exp015_historical_qualified_records(final)
        self.assertEqual(
            [item.strategy.fingerprint for item in resolved],
            final["historical_qualified_fingerprints"],
        )

        repeated = finalize_exp015_shortlist(
            stage_a_authorization=authorization,
            stage_a_authorization_sha256=stage_a_sha,
            stage_b_result=stage_b,
            stage_b_result_sha256=stage_b_sha,
            stage_c_result=stage_c,
            stage_c_result_sha256="3" * 64,
        )
        self.assertEqual(final, repeated)

    def test_final_artifact_is_deterministic(self) -> None:
        payload = {
            "protocol": EXP015_FINAL_PROTOCOL,
            "experiment_id": "EXP-20260922-015",
            "promotion_authorized": False,
            "historical_qualified_fingerprints": [],
        }
        with TemporaryDirectory() as left_tmp, TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            lm = write_exp015_final_artifacts(payload, left)
            rm = write_exp015_final_artifacts(payload, right)
            self.assertEqual(
                (left / "final-shortlist.json").read_bytes(),
                (right / "final-shortlist.json").read_bytes(),
            )
            self.assertEqual(lm, rm)


if __name__ == "__main__":
    unittest.main()
