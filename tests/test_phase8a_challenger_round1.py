from datetime import date, datetime, timezone
import json
from pathlib import Path
import unittest

from fmp.contracts import QuoteBar
from fmp.portfolio.challenger_round1 import (
    EXP013_STAGE_A_CELL_PROTOCOL,
    evaluate_exp013_stage_a_cell_pair,
    run_exp013_stage_a_cell,
)
from fmp.portfolio.challengers import build_opening_range_momentum_challengers
from fmp.portfolio.research_data import (
    LoadedRetrospectiveBars,
    PHASE8A_RETROSPECTIVE_LABEL,
)


COMMIT = "a" * 40
SOURCE_SHA = "f" * 64


def _bar() -> QuoteBar:
    ts = datetime(2019, 1, 2, 8, 0, tzinfo=timezone.utc)
    return QuoteBar(
        timestamp_utc=ts,
        symbol="EURUSD",
        bid_open=1.1000,
        bid_high=1.1005,
        bid_low=1.0995,
        bid_close=1.1002,
        ask_open=1.1002,
        ask_high=1.1007,
        ask_low=1.0997,
        ask_close=1.1004,
    )


def _loaded(research_range) -> LoadedRetrospectiveBars:
    return LoadedRetrospectiveBars(
        bars=(_bar(),),
        excluded_incomplete_count=0,
        eligible_utc_dates=(date(2019, 1, 2),),
        evidence_label=PHASE8A_RETROSPECTIVE_LABEL,
        start=research_range.start,
        end_exclusive=research_range.end_exclusive,
        processed_manifest_sha256="e" * 64,
        opened_artifact_months=("2019-01",),
    )


def _cell_rows(
    *,
    split_name: str,
    core_pass_fingerprints: set[str],
    low_sample_fingerprints: set[str] | None = None,
) -> dict[str, object]:
    low_sample_fingerprints = low_sample_fingerprints or set()
    records = [
        item
        for item in build_opening_range_momentum_challengers(code_commit=COMMIT)
        if item.strategy.symbol == "EURUSD"
        and item.strategy.timeframe == "15m"
    ]
    rows = []
    for record in records:
        for slippage in (0.2, 0.5, 1.0):
            passing = (
                record.strategy.fingerprint in core_pass_fingerprints
                and slippage in (0.2, 0.5)
            )
            trade_count = 120 if split_name == "development" else 70
            if (
                slippage == 0.2
                and record.strategy.fingerprint in low_sample_fingerprints
            ):
                trade_count = 20
            rows.append(
                {
                    "strategy_fingerprint": record.strategy.fingerprint,
                    "parameters_json": record.strategy.parameters_json,
                    "slippage_pips": slippage,
                    "candidate_sha256": "c" * 64,
                    "metrics": {
                        "trade_count": trade_count,
                        "phase3_metrics": {
                            "net_return": 0.01 if passing else -0.01,
                            "expectancy_usd": 2.0 if passing else -2.0,
                            "profit_factor": 1.10 if passing else 0.90,
                            "max_drawdown_fraction": 0.02,
                        },
                    },
                }
            )
    return {
        "protocol": EXP013_STAGE_A_CELL_PROTOCOL,
        "experiment_id": "EXP-20260922-013",
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "symbol": "EURUSD",
        "timeframe": "15m",
        "split_name": split_name,
        "runner_code_commit": COMMIT,
        "strategy_source_sha256": SOURCE_SHA,
        "strategy_identity_count": 4,
        "scenario_run_count": 12,
        "rows": rows,
    }


class Phase8AChallengerRound1Tests(unittest.TestCase):
    def test_stage_a_cell_runs_exact_four_configs_three_costs_with_one_data_load(self) -> None:
        load_calls = []
        run_calls = []

        def loader(**kwargs):
            load_calls.append(kwargs)
            return _loaded(kwargs["research_range"])

        def fake_runner(**kwargs):
            plan = kwargs["plan"]
            run_calls.append(plan)
            return {
                "strategy_fingerprint": plan.strategy.fingerprint,
                "processed_manifest_sha256": "e" * 64,
                "candidate_sha256": "c" * 64,
                "slippage_pips": plan.slippage_pips,
                "run_identity": {"code_commit": plan.runner_code_commit},
                "metrics": {
                    "trade_count": 10,
                    "phase3_metrics": {
                        "net_return": 0.0,
                        "expectancy_usd": 0.0,
                        "profit_factor": None,
                        "max_drawdown_fraction": 0.0,
                    },
                },
            }

        result = run_exp013_stage_a_cell(
            dataset_root=Path("/unused"),
            manifest_path=Path("/unused"),
            symbol="EURUSD",
            timeframe="15m",
            split_name="development",
            code_commit=COMMIT,
            bars_loader=loader,
            strategy_runner=fake_runner,
        )

        self.assertEqual(result["protocol"], EXP013_STAGE_A_CELL_PROTOCOL)
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["untouched_oos"])
        self.assertEqual(result["strategy_identity_count"], 4)
        self.assertEqual(result["scenario_run_count"], 12)
        self.assertEqual(len(load_calls), 1)
        self.assertEqual(len(run_calls), 12)
        self.assertEqual(
            {plan.research_range.start for plan in run_calls},
            {date(2015, 1, 1)},
        )
        self.assertEqual(
            {plan.research_range.end_exclusive for plan in run_calls},
            {date(2021, 1, 1)},
        )
        self.assertEqual(
            {plan.slippage_pips for plan in run_calls},
            {0.2, 0.5, 1.0},
        )

    def test_stage_a_runner_rejects_confirmation_split_before_source_io(self) -> None:
        touched = False

        def loader(**kwargs):
            nonlocal touched
            touched = True
            return _loaded(kwargs["research_range"])

        with self.assertRaises(ValueError):
            run_exp013_stage_a_cell(
                dataset_root=Path("/unused"),
                manifest_path=Path("/unused"),
                symbol="EURUSD",
                timeframe="15m",
                split_name="confirmation",
                code_commit=COMMIT,
                bars_loader=loader,
            )
        self.assertFalse(touched)

    def test_isolated_winner_is_rejected_by_neighbor_rule(self) -> None:
        records = [
            item
            for item in build_opening_range_momentum_challengers(code_commit=COMMIT)
            if item.strategy.symbol == "EURUSD"
            and item.strategy.timeframe == "15m"
        ]
        a = next(
            item
            for item in records
            if json.loads(item.strategy.parameters_json)
            == {"body_fraction_threshold": 0.5, "target_r_multiple": 1.0}
        )
        development = _cell_rows(
            split_name="development",
            core_pass_fingerprints={a.strategy.fingerprint},
        )
        validation = _cell_rows(
            split_name="validation",
            core_pass_fingerprints={a.strategy.fingerprint},
        )
        result = evaluate_exp013_stage_a_cell_pair(
            development=development,
            validation=validation,
        )
        self.assertEqual(result["survivor_fingerprints"], [])
        gate = result["config_gates"][a.strategy.fingerprint]
        self.assertTrue(gate["mandatory_profitability_drawdown_pass"])
        self.assertFalse(gate["neighbor_pass"])
        self.assertFalse(gate["stage_a_survivor"])

    def test_neighbor_can_support_survivor_even_if_neighbor_itself_fails_sample_gate(self) -> None:
        records = [
            item
            for item in build_opening_range_momentum_challengers(code_commit=COMMIT)
            if item.strategy.symbol == "EURUSD"
            and item.strategy.timeframe == "15m"
        ]
        a = next(
            item
            for item in records
            if json.loads(item.strategy.parameters_json)
            == {"body_fraction_threshold": 0.5, "target_r_multiple": 1.0}
        )
        b = next(
            item
            for item in records
            if json.loads(item.strategy.parameters_json)
            == {"body_fraction_threshold": 0.7, "target_r_multiple": 1.0}
        )
        passing = {a.strategy.fingerprint, b.strategy.fingerprint}
        development = _cell_rows(
            split_name="development",
            core_pass_fingerprints=passing,
            low_sample_fingerprints={b.strategy.fingerprint},
        )
        validation = _cell_rows(
            split_name="validation",
            core_pass_fingerprints=passing,
            low_sample_fingerprints={b.strategy.fingerprint},
        )
        result = evaluate_exp013_stage_a_cell_pair(
            development=development,
            validation=validation,
        )

        self.assertEqual(result["survivor_fingerprints"], [a.strategy.fingerprint])
        self.assertTrue(result["config_gates"][a.strategy.fingerprint]["neighbor_pass"])
        self.assertTrue(result["config_gates"][a.strategy.fingerprint]["sample_pass"])
        self.assertFalse(result["config_gates"][b.strategy.fingerprint]["sample_pass"])
        self.assertFalse(result["config_gates"][b.strategy.fingerprint]["stage_a_survivor"])


if __name__ == "__main__":
    unittest.main()
