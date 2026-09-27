from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.nan_null_repair_workflow_source import (
    source_artifacts_for_cell,
    validate_workflow_source_dependencies,
    workflow_source_payload,
    require_historical_execution_authorized,
)


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (
    ROOT
    / "docs/superpowers/templates/"
    "phase8a-exp062-discovery.yml.disabled"
)
CLI = ROOT / "scripts/phase8a_exp062.py"
ACTIVE = ROOT / ".github/workflows/phase8a-exp062-discovery.yml"


class Exp062DormantWorkflowSourceTests(unittest.TestCase):
    def test_dependencies_bind_exact_repair_stack(self) -> None:
        report = validate_workflow_source_dependencies(
            repository_root=ROOT,
        )
        self.assertEqual(report["decision"], "DEC-295")
        self.assertEqual(
            report["source_blobs"]["dec294_run_contract"],
            "0d1532e6a747e2dd9f0e70cd395e97433e6320ce",
        )
        self.assertEqual(
            report["source_blobs"]["dec293_repaired_adapter"],
            "53f85d99bad42decb673e9fa2ff0f771150e17db",
        )
        self.assertFalse(report["workflow_template_install_authorized"])
        self.assertFalse(report["workflow_dispatch_authorized"])
        self.assertFalse(report["historical_discovery_execution_authorized"])
        self.assertFalse(report["discovery_result_authorized"])
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_workflow_payload_is_eighteen_cells_and_fully_locked(self) -> None:
        value = workflow_source_payload(code_commit="a" * 40)
        self.assertEqual(value["decision"], "DEC-295")
        self.assertEqual(len(value["cells"]), 18)
        self.assertEqual(
            value["dormant_workflow_template_path"],
            "docs/superpowers/templates/"
            "phase8a-exp062-discovery.yml.disabled",
        )
        self.assertEqual(
            value["reserved_active_workflow_path"],
            ".github/workflows/phase8a-exp062-discovery.yml",
        )
        self.assertEqual(value["accepted_feature_run_id"], 35867307338)
        self.assertEqual(value["accepted_outcome_run_id"], 35876715434)
        for field in (
            "workflow_template_install_authorized",
            "workflow_dispatch_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
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
            self.assertFalse(value[field], field)

    def test_source_artifacts_are_exact_accepted_exp044_inputs(self) -> None:
        eurusd_5m = source_artifacts_for_cell("EURUSD", "5m")
        self.assertEqual(eurusd_5m["feature_id"], 10752009633)
        self.assertEqual(eurusd_5m["outcome_id"], 10759485253)

        usdjpy_1h = source_artifacts_for_cell("USDJPY", "1h")
        self.assertEqual(usdjpy_1h["feature_id"], 10752752044)
        self.assertEqual(usdjpy_1h["outcome_id"], 10757692733)

    def test_execution_gate_always_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            PermissionError,
            "execution is not authorized by DEC-295",
        ):
            require_historical_execution_authorized(
                code_commit="a" * 40,
            )

    def test_active_workflow_is_not_installed(self) -> None:
        self.assertTrue(TEMPLATE.is_file())
        self.assertFalse(ACTIVE.exists())

    def test_cli_gates_before_historical_reads(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        cell_start = text.index("def _cmd_cell")
        aggregate_start = text.index("def _cmd_aggregate")

        cell_gate = text.index(
            "require_historical_execution_authorized",
            cell_start,
        )
        cell_loader = text.index(
            "load_verified_exp061_cell_from_indexes",
            cell_start,
        )
        self.assertLess(cell_gate, cell_loader)

        aggregate_gate = text.index(
            "require_historical_execution_authorized",
            aggregate_start,
        )
        aggregate_read = text.index(
            "_load_cell_evidence",
            aggregate_start,
        )
        self.assertLess(aggregate_gate, aggregate_read)

        self.assertIn(
            "from fmp.discovery.nan_null_repair_adapter import (",
            text,
        )
        self.assertIn(
            "from fmp.discovery.nan_null_repair_run_contract import (",
            text,
        )

    def test_dormant_template_gates_before_source_downloads_and_results(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-exp062-discovery", text)
        self.assertIn("requirements/exp062-discovery-run.txt", text)
        self.assertIn("scripts/phase8a_exp062.py", text)
        self.assertNotIn("phase8a_exp061.py", text)
        self.assertIn("Require separately authorized EXP-062 execution", text)
        self.assertIn("Recheck separately authorized EXP-062 execution", text)

        first_recheck = text.index(
            "Recheck separately authorized EXP-062 execution"
        )
        first_download = text.index(
            "Download exact frozen feature/outcome/evidence artifacts"
        )
        self.assertLess(first_recheck, first_download)

        aggregate_job = text.index("name: exp062-aggregate")
        aggregate_gate = text.index(
            "Recheck separately authorized EXP-062 execution",
            aggregate_job,
        )
        aggregate_download = text.index(
            "Download all 18 EXP-062 cell artifacts",
            aggregate_job,
        )
        self.assertLess(aggregate_gate, aggregate_download)

    def test_dormant_template_has_exact_eighteen_matrix_cells(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(text.count("          - symbol:"), 18)
        self.assertEqual(
            text.count("feature_artifact_id:"),
            18,
        )
        self.assertEqual(
            text.count("outcome_artifact_id:"),
            18,
        )


if __name__ == "__main__":
    unittest.main()
