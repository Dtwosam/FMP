from __future__ import annotations

from pathlib import Path
import inspect
import unittest
from unittest.mock import patch

from fmp.discovery import annual_pattern_catalogue_runtime as runtime
from fmp.discovery.annual_pattern_catalogue_runtime import (
    require_historical_catalogue_execution_authorized,
    run_locked_annual_catalogue_cell,
    runtime_wiring_contract_payload,
)


CODE_COMMIT = "a" * 40


class AnnualPatternCatalogueRuntimeWiringTests(unittest.TestCase):
    def test_execution_gate_is_hard_closed_before_historical_reads(self) -> None:
        self.assertFalse(runtime.HISTORICAL_ARTIFACT_READ_AUTHORIZED)
        self.assertFalse(runtime.HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED)
        self.assertFalse(runtime.HISTORICAL_RESULT_PRODUCTION_AUTHORIZED)

        with patch.object(
            runtime,
            "load_verified_annual_catalogue_segment_from_indexes",
        ) as loader:
            with self.assertRaisesRegex(
                PermissionError,
                "historical artifact reads remain locked",
            ):
                run_locked_annual_catalogue_cell(
                    feature_root=Path("feature-root"),
                    outcome_root=Path("outcome-root"),
                    feature_evidence_path=Path("feature-evidence.json"),
                    outcome_evidence_path=Path("outcome-evidence.json"),
                    annual_segment_label="2015",
                    symbol="EURUSD",
                    timeframe="5m",
                    horizon_minutes=60,
                    code_commit=CODE_COMMIT,
                )
            loader.assert_not_called()

    def test_gate_validates_code_commit_without_opening_authority(self) -> None:
        with self.assertRaisesRegex(ValueError, "40-character Git commit"):
            require_historical_catalogue_execution_authorized(code_commit="bad")

        with self.assertRaisesRegex(
            PermissionError,
            "historical artifact reads remain locked",
        ):
            require_historical_catalogue_execution_authorized(
                code_commit=CODE_COMMIT,
            )

    def test_source_order_keeps_gate_before_loader(self) -> None:
        source = inspect.getsource(run_locked_annual_catalogue_cell)
        gate = source.index("require_historical_catalogue_execution_authorized")
        loader = source.index("load_verified_annual_catalogue_segment_from_indexes")
        adapter = source.index("adapt_verified_annual_catalogue_segment")
        miner = source.index("mine_annual_catalogue_cell")
        evidence = source.index("compile_cell_evidence")

        self.assertLess(gate, loader)
        self.assertLess(loader, adapter)
        self.assertLess(adapter, miner)
        self.assertLess(miner, evidence)

    def test_runtime_contract_exposes_locked_call_graph_only(self) -> None:
        payload = runtime_wiring_contract_payload()

        self.assertEqual(payload["decision"], "DEC-475")
        self.assertEqual(payload["source_adapter_decision"], "DEC-474")
        self.assertEqual(
            payload["call_order"],
            [
                "require_historical_catalogue_execution_authorized",
                "load_verified_annual_catalogue_segment_from_indexes",
                "adapt_verified_annual_catalogue_segment",
                "mine_annual_catalogue_cell",
                "compile_cell_evidence",
            ],
        )
        self.assertTrue(payload["authorization_gate_precedes_historical_read"])
        self.assertEqual(
            payload["unit_of_work"],
            "annual_segment_x_symbol_x_timeframe_x_horizon",
        )
        self.assertFalse(payload["workflow_installed"])
        self.assertFalse(payload["workflow_dispatch_authorized"])
        self.assertEqual(
            payload["next_gate"],
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_PLAN",
        )
        for field in (
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(payload[field], field)


if __name__ == "__main__":
    unittest.main()
