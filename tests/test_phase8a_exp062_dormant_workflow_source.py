from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_workflow_source import (
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    RESERVED_ACTIVE_WORKFLOW_PATH,
    require_historical_execution_authorized,
    validate_exp062_workflow_source_dependencies,
    workflow_source_payload,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp062DormantWorkflowSourceTests(unittest.TestCase):
    def test_source_dependencies_bind_exact_repair_and_frozen_stack(self) -> None:
        report = validate_exp062_workflow_source_dependencies(
            repository_root=ROOT,
        )
        self.assertEqual(report["decision"], "DEC-299")
        self.assertEqual(report["experiment_id"], "EXP-20260927-062")
        blobs = report["source_blobs"]
        self.assertEqual(
            blobs["dec298_run_contract"],
            "d304c8fafcff64f967f6777b1c494819f69d4a03",
        )
        self.assertEqual(
            blobs["dec293_repaired_adapter"],
            "491ba8c92cb6e6e4c715bfb1ecb934b6949e1596",
        )
        self.assertEqual(
            blobs["exp061_miner"],
            "495a67699eb5014e52129f0238a2737049fe38e6",
        )
        self.assertEqual(
            blobs["exp061_loader"],
            "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea",
        )
        for field in (
            "template_install_authorized",
            "workflow_dispatch_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "trading_authorized",
        ):
            self.assertFalse(report[field], field)

    def test_payload_keeps_every_execution_and_trading_path_locked(self) -> None:
        value = workflow_source_payload(code_commit="a" * 40)
        self.assertEqual(value["decision"], "DEC-299")
        self.assertEqual(value["experiment_id"], "EXP-20260927-062")
        self.assertEqual(
            value["dormant_template_path"],
            DORMANT_WORKFLOW_TEMPLATE_PATH,
        )
        self.assertEqual(
            value["reserved_active_workflow_path"],
            RESERVED_ACTIVE_WORKFLOW_PATH,
        )
        self.assertEqual(len(value["expected_job_names"]), 20)
        self.assertEqual(len(value["expected_cell_artifacts"]), 18)
        auth = value["authorizations"]
        for field in (
            "template_install_authorized",
            "workflow_dispatch_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(auth[field], field)

    def test_execution_gate_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "DEC-299 historical EXP-062 discovery execution remains locked",
        ):
            require_historical_execution_authorized(code_commit="a" * 40)

    def test_dormant_template_exists_but_active_workflow_does_not(self) -> None:
        template = ROOT / DORMANT_WORKFLOW_TEMPLATE_PATH
        active = ROOT / RESERVED_ACTIVE_WORKFLOW_PATH
        self.assertTrue(template.is_file())
        self.assertFalse(active.exists())

        text = template.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-exp062-discovery", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn(
            "name: exp062-cell-${{ matrix.dataset.symbol }}-"
            "${{ matrix.dataset.timeframe }}-"
            "${{ matrix.dataset.horizon }}m",
            text,
        )
        self.assertEqual(text.count("- symbol:"), 18)
        self.assertEqual(text.count("horizon: 60"), 9)
        self.assertEqual(text.count("horizon: 240"), 9)
        self.assertIn(
            "python scripts/phase8a_exp062.py require-execution",
            text,
        )
        self.assertIn(
            "python scripts/phase8a_exp062.py cell",
            text,
        )
        self.assertIn(
            "python scripts/phase8a_exp062.py aggregate",
            text,
        )
        self.assertNotIn("phase8a_exp061.py cell", text)
        self.assertNotIn("phase8a_exp061.py aggregate", text)

    def test_cli_uses_repaired_adapter_and_exp062_evidence_contract(self) -> None:
        script = (
            ROOT / "scripts/phase8a_exp062.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "from fmp.discovery.exp062_nonfinite_feature_adapter import",
            script,
        )
        self.assertIn(
            "from fmp.discovery.exp062_run_contract import",
            script,
        )
        self.assertNotIn(
            "from fmp.discovery.market_learning_adapter import",
            script,
        )

    def test_cell_gate_precedes_loader_and_aggregate_gate_precedes_reads(self) -> None:
        script = (
            ROOT / "scripts/phase8a_exp062.py"
        ).read_text(encoding="utf-8")

        cell_start = script.index("def _cmd_cell")
        aggregate_start = script.index("def _cmd_aggregate")

        cell_gate = script.index(
            "require_historical_execution_authorized",
            cell_start,
        )
        cell_loader = script.index(
            "load_verified_exp061_cell_from_indexes",
            cell_start,
        )
        self.assertLess(cell_gate, cell_loader)

        aggregate_gate = script.index(
            "require_historical_execution_authorized",
            aggregate_start,
        )
        aggregate_read = script.index(
            "_load_cell_evidence",
            aggregate_start,
        )
        self.assertLess(aggregate_gate, aggregate_read)


if __name__ == "__main__":
    unittest.main()
