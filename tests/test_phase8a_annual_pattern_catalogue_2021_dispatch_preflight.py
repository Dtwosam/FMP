from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2021_dispatch_preflight import (
    build_2021_dispatch_preflight,
    validate_2021_dispatch_preflight,
    validate_2021_dispatch_preflight_sources,
)


ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40

INSTALL_RECEIPT_JSON = r"""
{
  "annual_segment_label": "2021",
  "annual_workflow_dispatch_authorized": false,
  "broker_mutation_authorized": false,
  "changed_files": [
    "src/fmp/discovery/annual_pattern_catalogue_2021_runtime_authorization.py",
    "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
  ],
  "cross_year_result_production_authorized": false,
  "decision": "DEC-585",
  "demo_order_authorized": false,
  "expected_run_attempt": 1,
  "expected_run_number": 383,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_action_consumed": true,
  "install_action_source_blob_sha": "9ea8f4574ed1a85cbf0b95031a7450cc4f7fa705",
  "install_commit_sha": "4833c86f74af3febfc2592048916d9ce20aa051a",
  "install_receipt_fingerprint_sha256": "6fcbfeb2d2f7a8154925ac7fb5d08d68050a0ea2f2bbf2b3612015fd08b422c5",
  "installed_gate_blob_sha": "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
  "installed_runtime_blob_sha": "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
  "live_order_authorized": false,
  "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2021_DISPATCH_PREFLIGHT",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "previous_annual_freeze_run_id": 37443770076,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "runtime_authorization_installed": true,
  "runtime_gate_active": true,
  "source_action_artifact_digest": "sha256:d8e77b482e83250a56aafc99e4e6d2b81d94d1adb1227abbd1a0e49397e45ebe",
  "source_action_artifact_id": 11425666284,
  "source_action_decision": "DEC-584",
  "source_action_fingerprint_sha256": "bffb48b795c1fc76f792aa8b00f5b8b94d23554cbc958bf3d11249eaa1058b04",
  "source_action_workflow_head_sha": "32927e836fcf6888a7f8567b28f5ba2fd0b48315",
  "source_action_workflow_run_id": 37490417862,
  "stage": "ANNUAL_CATALOGUE_2021_RUNTIME_AUTHORIZATION_INSTALLED",
  "strategy_v1_synthesis_authorized": false,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2021-runtime-authorization-install-receipt-v1"
}
"""


def _receipt() -> dict[str, object]:
    value = json.loads(INSTALL_RECEIPT_JSON)
    assert isinstance(value, dict)
    return value


def _run(run_id: int, number: int, head_sha: str, conclusion: str) -> dict[str, object]:
    return {
        "id": run_id,
        "name": "phase8a-annual-pattern-catalogue",
        "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "run_number": number,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": conclusion,
    }


def _annual_runs() -> dict[str, object]:
    return {"workflow_runs": [
        _run(37443770076, 382, "681e81e021d4970a67b18370142d55b17ec68864", "success"),
        _run(37310525635, 381, "8bcee3a7a834743f08bd9ad73109bfc09609a2fe", "success"),
        _run(37237817538, 380, "30971a996f514670a6f836d8e45cf80137197a4f", "success"),
        _run(37227536041, 379, "7b4c1ef8573e280c067443b72f1534d9091d5b7f", "success"),
        _run(37206992367, 378, "2524fde355349581c9440a172d0384c3cbce31ed", "success"),
        _run(37198002653, 377, "a89db974be9a94481e7ed0990476bc661012f1e4", "success"),
        _run(37191637168, 376, "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3", "failure"),
        _run(37126711695, 1, "fd85a886d07234ad584dcca08692b37e6af54b2e", "failure"),
    ]}


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-586 requires installed 2021 runtime state",
)
class AnnualPatternCatalogue2021DispatchPreflightTests(unittest.TestCase):
    def test_sources_pin_dec585_install(self) -> None:
        value = validate_2021_dispatch_preflight_sources(repository_root=ROOT)
        self.assertEqual(value["install_receipt_source_blob_sha"], "b088a8483ea555b28107462e88b8c16ec72b66b8")
        self.assertEqual(value["active_workflow_blob_sha"], "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1")
        self.assertEqual(value["installed_gate_blob_sha"], "cac68c905bedf3105aa7e766eaa968c87bff6ce9")
        self.assertEqual(value["installed_runtime_blob_sha"], "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6")

    def test_preflight_freezes_run383_without_authorizing_dispatch(self) -> None:
        value = build_2021_dispatch_preflight(
            _receipt(),
            repository_root=ROOT,
            main_branch={"name": "main", "commit": {"sha": HEAD}},
            annual_workflow_runs=_annual_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2021_dispatch_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-586")
        self.assertEqual(value["source_installer_workflow_run_id"], 37496446082)
        self.assertEqual(value["source_install_artifact_id"], 11427632507)
        self.assertEqual(value["source_install_commit_sha"], "4833c86f74af3febfc2592048916d9ce20aa051a")
        self.assertEqual(value["source_install_receipt_fingerprint_sha256"], "6fcbfeb2d2f7a8154925ac7fb5d08d68050a0ea2f2bbf2b3612015fd08b422c5")
        self.assertEqual(value["expected_run_number"], 383)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37443770076)
        self.assertEqual(value["annual_workflow_run_count"], 8)
        self.assertEqual(value["successful_2020_run_id"], 37443770076)
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_run383_already_present_fails_closed(self) -> None:
        runs = _annual_runs()
        rows = runs["workflow_runs"]
        assert isinstance(rows, list)
        rows.insert(0, _run(999999, 383, "d" * 40, "failure"))
        with self.assertRaisesRegex(ValueError, "exactly eight prior"):
            build_2021_dispatch_preflight(
                _receipt(), repository_root=ROOT,
                main_branch={"name": "main", "commit": {"sha": HEAD}},
                annual_workflow_runs=runs, expected_head_sha=HEAD,
            )

    def test_receipt_tampering_fails_closed(self) -> None:
        receipt = copy.deepcopy(_receipt())
        receipt["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_2021_dispatch_preflight(
                receipt, repository_root=ROOT,
                main_branch={"name": "main", "commit": {"sha": HEAD}},
                annual_workflow_runs=_annual_runs(), expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        text = (ROOT / "scripts/phase8a_annual_pattern_catalogue_2021_dispatch_preflight.py").read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn('subparsers.add_parser("dispatch")', text)


if __name__ == "__main__":
    unittest.main()
