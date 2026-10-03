from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_proof_workflow_dispatch_preflight import (
    EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA,
    EXPECTED_INSTALL_RECEIPT_BLOB_SHA,
    build_proof_workflow_dispatch_preflight,
    validate_proof_workflow_dispatch_preflight,
    validate_proof_workflow_dispatch_preflight_sources,
)


HEAD = "a" * 40


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _run() -> dict[str, object]:
    return {
        "id": 50000000001,
        "name": "phase8a-annual-catalogue-workflow-install-preflight-proof",
        "path": (
            ".github/workflows/"
            "phase8a-annual-catalogue-workflow-install-preflight-proof.yml"
        ),
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": 1,
        "run_attempt": 1,
        "status": "queued",
        "conclusion": None,
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-486 current-state tests require the installed proof workflow",
)
class AnnualPatternCatalogueProofWorkflowDispatchPreflightTests(unittest.TestCase):
    def test_sources_pin_receipt_and_active_workflow(self) -> None:
        source = validate_proof_workflow_dispatch_preflight_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["install_receipt_blob_sha"],
            EXPECTED_INSTALL_RECEIPT_BLOB_SHA,
        )
        self.assertEqual(
            source["active_proof_workflow_blob_sha"],
            EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA,
        )

    def test_zero_run_inventory_is_read_only_ready(self) -> None:
        value = build_proof_workflow_dispatch_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            proof_workflow_runs={"workflow_runs": []},
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_proof_workflow_dispatch_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-486")
        self.assertTrue(value["active_proof_workflow_present"])
        self.assertTrue(value["proof_workflow_installed"])
        self.assertTrue(value["proof_workflow_available"])
        self.assertEqual(value["proof_workflow_run_count"], 0)
        self.assertFalse(value["proof_workflow_dispatch_authorized"])
        self.assertFalse(value["annual_workflow_install_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_existing_proof_run_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "zero proof-workflow runs"):
            build_proof_workflow_dispatch_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                proof_workflow_runs={"workflow_runs": [_run()]},
                expected_head_sha=HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_proof_workflow_dispatch_preflight(
                repository_root=Path("."),
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                proof_workflow_runs={"workflow_runs": []},
                expected_head_sha=HEAD,
            )

    def test_non_main_metadata_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires main branch metadata"):
            build_proof_workflow_dispatch_preflight(
                repository_root=Path("."),
                main_branch={"name": "dev", "commit": {"sha": HEAD}},
                proof_workflow_runs={"workflow_runs": []},
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        text = Path(
            "scripts/phase8a_annual_pattern_catalogue_"
            "proof_workflow_dispatch_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', text)
        self.assertNotIn('add_parser("dispatch")', text)
        self.assertNotIn('add_parser("execute")', text)
        self.assertNotIn('add_parser("run")', text)
        self.assertNotIn("gh workflow run ", text)


if __name__ == "__main__":
    unittest.main()
