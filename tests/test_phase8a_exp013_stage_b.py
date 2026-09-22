from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from fmp.contracts import QuoteBar
from fmp.portfolio.challenger_round1 import opening_range_momentum_source_sha256
from fmp.portfolio.challenger_round1_stage_b import (
    EXP013_STAGE_B_PROTOCOL,
    run_exp013_stage_b,
    validate_exp013_stage_a_authorization,
    write_exp013_stage_b_artifacts,
)
from fmp.portfolio.challengers import build_opening_range_momentum_challengers
from fmp.portfolio.research_data import (
    LoadedRetrospectiveBars,
    PHASE8A_RETROSPECTIVE_LABEL,
)


STAGE_A_COMMIT = "a" * 40
STAGE_B_COMMIT = "b" * 40


def _records():
    records = build_opening_range_momentum_challengers(code_commit=STAGE_A_COMMIT)
    return (
        next(
            item
            for item in records
            if item.strategy.symbol == "EURUSD"
            and item.strategy.timeframe == "15m"
            and '"body_fraction_threshold":0.5' in item.strategy.parameters_json
            and '"target_r_multiple":1.0' in item.strategy.parameters_json
        ),
        next(
            item
            for item in records
            if item.strategy.symbol == "USDJPY"
            and item.strategy.timeframe == "1h"
            and '"body_fraction_threshold":0.7' in item.strategy.parameters_json
            and '"target_r_multiple":1.5' in item.strategy.parameters_json
        ),
    )


def _authorization(*, survivors: tuple[str, ...], source_sha: str | None = None):
    catalog = build_opening_range_momentum_challengers(code_commit=STAGE_A_COMMIT)
    cells = []
    for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
        for timeframe in ("5m", "15m", "1h"):
            cell_records = [
                item
                for item in catalog
                if item.strategy.symbol == symbol
                and item.strategy.timeframe == timeframe
            ]
            cell_fps = sorted(item.strategy.fingerprint for item in cell_records)
            cell_survivors = sorted(set(cell_fps).intersection(survivors))
            cells.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "strategy_fingerprints": cell_fps,
                    "survivor_fingerprints": cell_survivors,
                }
            )
    return {
        "protocol": "fmp-phase8a-exp013-stage-a-authorization-v1",
        "experiment_id": "EXP-20260922-013",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "runner_code_commit": STAGE_A_COMMIT,
        "strategy_source_sha256": source_sha or opening_range_momentum_source_sha256(),
        "cell_count": 9,
        "strategy_identity_count": 36,
        "survivor_count": len(survivors),
        "survivor_fingerprints": list(sorted(survivors)),
        "stage_b_source_open_authorized": bool(survivors),
        "cells": cells,
    }


def _bar(symbol: str) -> QuoteBar:
    price = 150.0 if symbol == "USDJPY" else 1.1
    half = 0.01 if symbol == "USDJPY" else 0.0001
    return QuoteBar(
        timestamp_utc=datetime(2024, 1, 2, 8, 0, tzinfo=timezone.utc),
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
    return LoadedRetrospectiveBars(
        bars=(_bar(symbol),),
        excluded_incomplete_count=0,
        eligible_utc_dates=(date(2024, 1, 2),),
        evidence_label=PHASE8A_RETROSPECTIVE_LABEL,
        start=research_range.start,
        end_exclusive=research_range.end_exclusive,
        processed_manifest_sha256=("e" if symbol == "EURUSD" else "d") * 64,
        opened_artifact_months=("2024-01",),
    )


class Exp013StageBTests(unittest.TestCase):
    def test_no_survivor_authorization_fails_before_source_io(self) -> None:
        touched = False

        def loader(**kwargs):
            nonlocal touched
            touched = True
            return _loaded(kwargs["symbol"], kwargs["research_range"])

        with self.assertRaisesRegex(ValueError, "Stage B source-open"):
            run_exp013_stage_b(
                authorization=_authorization(survivors=()),
                stage_a_authorization_sha256="c" * 64,
                dataset_sources={},
                code_commit=STAGE_B_COMMIT,
                bars_loader=loader,
            )
        self.assertFalse(touched)

    def test_source_digest_mismatch_fails_before_source_io(self) -> None:
        survivor = _records()[0].strategy.fingerprint
        touched = False

        def loader(**kwargs):
            nonlocal touched
            touched = True
            return _loaded(kwargs["symbol"], kwargs["research_range"])

        with self.assertRaisesRegex(ValueError, "source digest"):
            run_exp013_stage_b(
                authorization=_authorization(
                    survivors=(survivor,),
                    source_sha="f" * 64,
                ),
                stage_a_authorization_sha256="c" * 64,
                dataset_sources={"EURUSD": (Path("/unused"), Path("/unused"))},
                code_commit=STAGE_B_COMMIT,
                bars_loader=loader,
            )
        self.assertFalse(touched)

    def test_exact_authorized_survivors_run_on_frozen_range_and_costs(self) -> None:
        records = _records()
        survivors = tuple(item.strategy.fingerprint for item in records)
        load_calls = []
        run_calls = []

        def loader(**kwargs):
            load_calls.append(kwargs)
            return _loaded(kwargs["symbol"], kwargs["research_range"])

        def runner(**kwargs):
            plan = kwargs["plan"]
            run_calls.append(plan)
            trade_count = 80 if plan.slippage_pips == 0.2 else 80
            return {
                "strategy_fingerprint": plan.strategy.fingerprint,
                "processed_manifest_sha256": (
                    "e" * 64 if plan.strategy.symbol == "EURUSD" else "d" * 64
                ),
                "candidate_sha256": (
                    "1" * 63 + ("1" if plan.strategy.symbol == "EURUSD" else "2")
                ),
                "slippage_pips": plan.slippage_pips,
                "run_identity": {"code_commit": plan.runner_code_commit},
                "metrics": {
                    "trade_count": trade_count,
                    "phase3_metrics": {
                        "net_return": 0.02,
                        "expectancy_usd": 10.0,
                        "profit_factor": 1.2,
                        "max_drawdown_fraction": 0.02,
                    },
                },
            }

        result = run_exp013_stage_b(
            authorization=_authorization(survivors=survivors),
            stage_a_authorization_sha256="c" * 64,
            dataset_sources={
                "EURUSD": (Path("/eur"), Path("/eur.json")),
                "USDJPY": (Path("/jpy"), Path("/jpy.json")),
            },
            code_commit=STAGE_B_COMMIT,
            bars_loader=loader,
            strategy_runner=runner,
        )

        self.assertEqual(result["protocol"], EXP013_STAGE_B_PROTOCOL)
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["historical_status_mutation_authorized"])
        self.assertEqual(result["range_start"], "2024-01-01")
        self.assertEqual(result["range_end_exclusive"], "2026-08-21")
        self.assertEqual(result["strategy_identity_count"], 2)
        self.assertEqual(result["scenario_run_count"], 6)
        self.assertEqual(
            result["historical_qualification_candidate_fingerprints"],
            sorted(survivors),
        )
        self.assertTrue(result["historical_qualification_review_authorized"])
        self.assertEqual(len(load_calls), 2)
        self.assertEqual(len(run_calls), 6)
        self.assertEqual(
            {plan.research_range.start for plan in run_calls},
            {date(2024, 1, 1)},
        )
        self.assertEqual(
            {plan.research_range.end_exclusive for plan in run_calls},
            {date(2026, 8, 21)},
        )
        self.assertEqual(
            {plan.slippage_pips for plan in run_calls},
            {0.2, 0.5, 1.0},
        )
        self.assertTrue(
            all(plan.strategy.code_commit == STAGE_A_COMMIT for plan in run_calls)
        )
        self.assertTrue(
            all(plan.runner_code_commit == STAGE_B_COMMIT for plan in run_calls)
        )

    def test_stage_b_gate_rejects_low_sample_even_when_profitability_passes(self) -> None:
        record = _records()[0]

        def runner(**kwargs):
            plan = kwargs["plan"]
            return {
                "strategy_fingerprint": plan.strategy.fingerprint,
                "processed_manifest_sha256": "e" * 64,
                "candidate_sha256": "1" * 64,
                "slippage_pips": plan.slippage_pips,
                "run_identity": {},
                "metrics": {
                    "trade_count": 74 if plan.slippage_pips == 0.2 else 80,
                    "phase3_metrics": {
                        "net_return": 0.02,
                        "expectancy_usd": 10.0,
                        "profit_factor": 1.2,
                        "max_drawdown_fraction": 0.02,
                    },
                },
            }

        result = run_exp013_stage_b(
            authorization=_authorization(
                survivors=(record.strategy.fingerprint,)
            ),
            stage_a_authorization_sha256="c" * 64,
            dataset_sources={"EURUSD": (Path("/eur"), Path("/eur.json"))},
            code_commit=STAGE_B_COMMIT,
            bars_loader=lambda **kwargs: _loaded(
                kwargs["symbol"],
                kwargs["research_range"],
            ),
            strategy_runner=runner,
        )
        self.assertEqual(
            result["historical_qualification_candidate_fingerprints"],
            [],
        )
        gate = result["strategy_gates"][record.strategy.fingerprint]
        self.assertTrue(gate["mandatory_profitability_drawdown_pass"])
        self.assertFalse(gate["sample_pass"])
        self.assertFalse(gate["stage_b_pass"])

    def test_stage_b_artifacts_are_deterministic(self) -> None:
        payload = {
            "protocol": EXP013_STAGE_B_PROTOCOL,
            "experiment_id": "EXP-20260922-013",
            "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
            "untouched_oos": False,
            "promotion_authorized": False,
            "historical_status_mutation_authorized": False,
            "historical_qualification_review_authorized": False,
            "historical_qualification_candidate_fingerprints": [],
        }
        with TemporaryDirectory() as left_tmp, TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            left_manifest = write_exp013_stage_b_artifacts(payload, left)
            right_manifest = write_exp013_stage_b_artifacts(payload, right)
            self.assertEqual(
                (left / "stage-b.json").read_bytes(),
                (right / "stage-b.json").read_bytes(),
            )
            self.assertEqual(left_manifest, right_manifest)
            stored = json.loads(
                (left / "stage-b.json").read_text(encoding="utf-8")
            )
            self.assertFalse(stored["promotion_authorized"])


if __name__ == "__main__":
    unittest.main()
