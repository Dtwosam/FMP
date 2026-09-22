from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from fmp.contracts import QuoteBar
from fmp.portfolio.challenger_discovery import (
    EXP015_ID,
    build_exp015_challengers,
    exp015_catalog_identity_sha256,
)
from fmp.portfolio.challenger_discovery_stage_a import (
    EXP015_STAGE_A_AUTHORIZATION_PROTOCOL,
    EXP015_STAGE_A_CELL_PROTOCOL,
    EXP015_STAGE_A_GATE_PROTOCOL,
    aggregate_exp015_stage_a_gates,
    evaluate_exp015_stage_a_cell,
    run_exp015_stage_a_cell,
    write_exp015_stage_a_authorization_artifacts,
    write_exp015_stage_a_cell_artifacts,
)
from fmp.portfolio.research_data import (
    LoadedRetrospectiveBars,
    PHASE8A_RETROSPECTIVE_LABEL,
)


COMMIT = "a" * 40
CATALOG_SHA = exp015_catalog_identity_sha256(code_commit=COMMIT)


def _bar(symbol: str) -> QuoteBar:
    price = 150.0 if symbol == "USDJPY" else 1.10
    half = 0.01 if symbol == "USDJPY" else 0.0001
    return QuoteBar(
        timestamp_utc=datetime(2016, 1, 4, 8, 0, tzinfo=timezone.utc),
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
        eligible_utc_dates=(date(2016, 1, 4),),
        evidence_label=PHASE8A_RETROSPECTIVE_LABEL,
        start=research_range.start,
        end_exclusive=research_range.end_exclusive,
        processed_manifest_sha256=("e" if symbol == "EURUSD" else "f") * 64,
        opened_artifact_months=("2016-01",),
    )


def _metrics(*, net_return: float, pf: float = 1.20, trades: int = 60, dd: float = 0.02):
    return {
        "trade_count": trades,
        "phase3_metrics": {
            "net_return": net_return,
            "expectancy_usd": 5.0 if net_return > 0 else -5.0,
            "profit_factor": pf,
            "max_drawdown_fraction": dd,
        },
    }


class Exp015StageATests(unittest.TestCase):
    def test_stage_a_cell_runs_exact_63_strategies_three_costs_with_one_load(self) -> None:
        load_calls = []
        run_calls = []

        def loader(**kwargs):
            load_calls.append(kwargs)
            return _loaded(kwargs["symbol"], kwargs["research_range"])

        def runner(**kwargs):
            plan = kwargs["plan"]
            run_calls.append(plan)
            return {
                "strategy_fingerprint": plan.strategy.fingerprint,
                "processed_manifest_sha256": "e" * 64,
                "candidate_sha256": "c" * 64,
                "slippage_pips": plan.slippage_pips,
                "run_identity": {"code_commit": plan.runner_code_commit},
                "metrics": _metrics(net_return=0.01),
            }

        result = run_exp015_stage_a_cell(
            dataset_root=Path("/unused"),
            manifest_path=Path("/unused"),
            symbol="EURUSD",
            timeframe="15m",
            code_commit=COMMIT,
            bars_loader=loader,
            strategy_runner=runner,
        )

        self.assertEqual(result["protocol"], EXP015_STAGE_A_CELL_PROTOCOL)
        self.assertEqual(result["experiment_id"], EXP015_ID)
        self.assertEqual(result["strategy_identity_count"], 63)
        self.assertEqual(result["scenario_run_count"], 189)
        self.assertEqual(len(load_calls), 1)
        self.assertEqual(len(run_calls), 189)
        self.assertEqual({plan.research_range.start for plan in run_calls}, {date(2015, 1, 1)})
        self.assertEqual(
            {plan.research_range.end_exclusive for plan in run_calls},
            {date(2019, 1, 1)},
        )
        self.assertEqual(
            {plan.slippage_pips for plan in run_calls},
            {0.2, 0.5, 1.0},
        )
        self.assertTrue(
            all(plan.strategy.version == "fmp-exp015-rule-challenger-v1" for plan in run_calls)
        )

    def test_stage_a_ranking_keeps_at_most_two_per_family_cell(self) -> None:
        records = [
            item
            for item in build_exp015_challengers(code_commit=COMMIT)
            if item.strategy.symbol == "EURUSD"
            and item.strategy.timeframe == "15m"
        ]
        rows = []
        by_family = {}
        for record in records:
            by_family.setdefault(record.strategy.family, []).append(record)

        for family, family_records in by_family.items():
            for index, record in enumerate(sorted(family_records, key=lambda x: x.strategy.fingerprint)):
                for slippage in (0.2, 0.5, 1.0):
                    # Three pass in every family; ranking must retain only the best two.
                    passing = index < 3
                    base = 0.04 - index * 0.005 if passing else -0.01
                    rows.append(
                        {
                            "strategy_fingerprint": record.strategy.fingerprint,
                            "strategy_identity_json": record.strategy.identity_json,
                            "family": family,
                            "symbol": "EURUSD",
                            "timeframe": "15m",
                            "parameters_json": record.strategy.parameters_json,
                            "slippage_pips": slippage,
                            "candidate_sha256": "c" * 64,
                            "run_identity": {},
                            "metrics": _metrics(
                                net_return=base,
                                pf=1.30 - index * 0.01 if passing else 0.90,
                            ),
                        }
                    )

        cell = {
            "protocol": EXP015_STAGE_A_CELL_PROTOCOL,
            "experiment_id": EXP015_ID,
            "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
            "untouched_oos": False,
            "promotion_authorized": False,
            "historical_status_mutation_authorized": False,
            "symbol": "EURUSD",
            "timeframe": "15m",
            "runner_code_commit": COMMIT,
            "catalog_identity_sha256": CATALOG_SHA,
            "strategy_source_sha256": "d" * 64,
            "processed_manifest_sha256": "e" * 64,
            "range_start": "2015-01-01",
            "range_end_exclusive": "2019-01-01",
            "strategy_identity_count": 63,
            "scenario_run_count": 189,
            "slippage_scenarios": [0.2, 0.5, 1.0],
            "strategy_fingerprints": sorted(item.strategy.fingerprint for item in records),
            "rows": rows,
        }

        gate = evaluate_exp015_stage_a_cell(cell)
        self.assertEqual(gate["protocol"], EXP015_STAGE_A_GATE_PROTOCOL)
        self.assertEqual(len(gate["family_rankings"]), 6)
        self.assertEqual(len(gate["survivor_fingerprints"]), 12)
        for family, ranking in gate["family_rankings"].items():
            self.assertEqual(len(ranking["selected_fingerprints"]), 2, family)
            self.assertEqual(len(ranking["passing_fingerprints"]), 3, family)

    def test_stage_a_gate_requires_pf_above_1_05_and_40_trades_at_both_gating_costs(self) -> None:
        records = [
            item
            for item in build_exp015_challengers(code_commit=COMMIT)
            if item.strategy.symbol == "EURUSD"
            and item.strategy.timeframe == "5m"
        ]
        rows = []
        target = records[0]
        for record in records:
            for slippage in (0.2, 0.5, 1.0):
                pf = 1.05 if record.strategy.fingerprint == target.strategy.fingerprint else 0.9
                rows.append(
                    {
                        "strategy_fingerprint": record.strategy.fingerprint,
                        "strategy_identity_json": record.strategy.identity_json,
                        "family": record.strategy.family,
                        "symbol": "EURUSD",
                        "timeframe": "5m",
                        "parameters_json": record.strategy.parameters_json,
                        "slippage_pips": slippage,
                        "candidate_sha256": "c" * 64,
                        "run_identity": {},
                        "metrics": _metrics(net_return=0.02, pf=pf, trades=40),
                    }
                )
        cell = {
            "protocol": EXP015_STAGE_A_CELL_PROTOCOL,
            "experiment_id": EXP015_ID,
            "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
            "untouched_oos": False,
            "promotion_authorized": False,
            "historical_status_mutation_authorized": False,
            "symbol": "EURUSD",
            "timeframe": "5m",
            "runner_code_commit": COMMIT,
            "catalog_identity_sha256": CATALOG_SHA,
            "strategy_source_sha256": "d" * 64,
            "processed_manifest_sha256": "e" * 64,
            "range_start": "2015-01-01",
            "range_end_exclusive": "2019-01-01",
            "strategy_identity_count": 63,
            "scenario_run_count": 189,
            "slippage_scenarios": [0.2, 0.5, 1.0],
            "strategy_fingerprints": sorted(item.strategy.fingerprint for item in records),
            "rows": rows,
        }
        gate = evaluate_exp015_stage_a_cell(cell)
        self.assertFalse(
            gate["strategy_gates"][target.strategy.fingerprint]["mandatory_gate_pass"]
        )

    def test_aggregate_requires_exact_nine_cells_and_full_567_identity_union(self) -> None:
        catalog = build_exp015_challengers(code_commit=COMMIT)
        gates = []
        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            for timeframe in ("5m", "15m", "1h"):
                records = [
                    item for item in catalog
                    if item.strategy.symbol == symbol and item.strategy.timeframe == timeframe
                ]
                gates.append(
                    {
                        "protocol": EXP015_STAGE_A_GATE_PROTOCOL,
                        "experiment_id": EXP015_ID,
                        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
                        "untouched_oos": False,
                        "promotion_authorized": False,
                        "historical_status_mutation_authorized": False,
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "runner_code_commit": COMMIT,
                        "catalog_identity_sha256": CATALOG_SHA,
                        "strategy_source_sha256": "d" * 64,
                        "strategy_fingerprints": sorted(
                            item.strategy.fingerprint for item in records
                        ),
                        "survivor_fingerprints": [],
                        "family_rankings": {},
                        "strategy_gates": {},
                    }
                )
        auth = aggregate_exp015_stage_a_gates(gates)
        self.assertEqual(auth["protocol"], EXP015_STAGE_A_AUTHORIZATION_PROTOCOL)
        self.assertEqual(auth["cell_count"], 9)
        self.assertEqual(auth["ranking_cell_count"], 54)
        self.assertEqual(auth["strategy_identity_count"], 567)
        self.assertEqual(auth["catalog_identity_sha256"], CATALOG_SHA)
        self.assertEqual(auth["maximum_stage_a_survivors"], 108)
        self.assertEqual(auth["survivor_count"], 0)
        self.assertFalse(auth["stage_b_source_open_authorized"])
        self.assertFalse(auth["promotion_authorized"])

        with self.assertRaises(ValueError):
            aggregate_exp015_stage_a_gates(gates[:-1])

        bad_catalog = [dict(item) for item in gates]
        bad_catalog[-1] = dict(bad_catalog[-1]) | {
            "catalog_identity_sha256": "f" * 64,
        }
        with self.assertRaisesRegex(ValueError, "catalog identity mismatch"):
            aggregate_exp015_stage_a_gates(bad_catalog)

        eurusd_5m_session = sorted(
            item.strategy.fingerprint
            for item in catalog
            if item.strategy.symbol == "EURUSD"
            and item.strategy.timeframe == "5m"
            and item.strategy.family == "session_breakout"
        )
        bad = [dict(item) for item in gates]
        bad[0] = dict(bad[0]) | {
            "survivor_fingerprints": eurusd_5m_session[:3],
        }
        with self.assertRaisesRegex(ValueError, "family-cell survivor cap"):
            aggregate_exp015_stage_a_gates(bad)

    def test_stage_a_artifacts_are_deterministic(self) -> None:
        cell = {
            "protocol": EXP015_STAGE_A_CELL_PROTOCOL,
            "experiment_id": EXP015_ID,
            "promotion_authorized": False,
        }
        gate = {
            "protocol": EXP015_STAGE_A_GATE_PROTOCOL,
            "experiment_id": EXP015_ID,
            "promotion_authorized": False,
        }
        auth = {
            "protocol": EXP015_STAGE_A_AUTHORIZATION_PROTOCOL,
            "experiment_id": EXP015_ID,
            "promotion_authorized": False,
        }
        with TemporaryDirectory() as left_tmp, TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            lm = write_exp015_stage_a_cell_artifacts(cell=cell, gate=gate, out_dir=left)
            rm = write_exp015_stage_a_cell_artifacts(cell=cell, gate=gate, out_dir=right)
            self.assertEqual((left / "cell.json").read_bytes(), (right / "cell.json").read_bytes())
            self.assertEqual((left / "gate.json").read_bytes(), (right / "gate.json").read_bytes())
            self.assertEqual(lm, rm)

        with TemporaryDirectory() as left_tmp, TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            lm = write_exp015_stage_a_authorization_artifacts(auth, left)
            rm = write_exp015_stage_a_authorization_artifacts(auth, right)
            self.assertEqual(
                (left / "authorization.json").read_bytes(),
                (right / "authorization.json").read_bytes(),
            )
            self.assertEqual(lm, rm)


if __name__ == "__main__":
    unittest.main()
