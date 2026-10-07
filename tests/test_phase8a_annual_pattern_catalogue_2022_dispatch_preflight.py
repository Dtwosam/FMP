from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2022_dispatch_preflight import (
    build_2022_dispatch_preflight,
    validate_2022_dispatch_preflight,
    validate_2022_dispatch_preflight_sources,
)


ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40

INSTALL_RECEIPT_JSON = r"""
{
  "annual_segment_label": "2022",
  "annual_workflow_dispatch_authorized": false,
  "broker_mutation_authorized": false,
  "changed_files": [
    "src/fmp/discovery/annual_pattern_catalogue_2022_runtime_authorization.py",
    "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
  ],
  "cross_year_comparison_authorized": false,
  "cross_year_result_production_authorized": false,
  "decision": "DEC-596",
  "demo_order_authorized": false,
  "expected_run_attempt": 1,
  "expected_run_number": 384,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_action_consumed": true,
  "install_action_source_blob_sha": "90fbc26b51d50d019e39c467d461bd7ba6b4f22b",
  "install_commit_sha": "df6da8cb52578c82e36c6206714a0452496614d9",
  "install_receipt_fingerprint_sha256": "99e99b92f74776694bdfcaab2499587b36129f6c371ef87c1696e3ba4ad3ecfd",
  "installed_gate_blob_sha": "ecb21dc7106e7bd43447f4135c3a696251a75e05",
  "installed_runtime_blob_sha": "f2734c7ea32355b1024d1097812578b23fc4409d",
  "live_order_authorized": false,
  "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2022_DISPATCH_PREFLIGHT",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "previous_annual_freeze_run_id": 37531960014,
  "promotion_authorized": false,
  "protected_history_access_authorized": false,
  "real_money_authorized": false,
  "replacement_run_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "rerun_authorized": false,
  "retry_authorized": false,
  "run_385_or_later_authorized": false,
  "runtime_authorization_installed": true,
  "runtime_gate_active": true,
  "source_action_artifact_digest": "sha256:6ff7996ac313a5437c0862cf58931a1246c5caf85251a6df4e0829602d9c07e8",
  "source_action_artifact_id": 11480463531,
  "source_action_canonical_sha256": "2b99a8b914ee01d27902daa626d2ca01e31384e17de1b3a63b99fcbb1c90070c",
  "source_action_decision": "DEC-595",
  "source_action_fingerprint_sha256": "3352e4254ce62247d56c9fd16c9eb6972c3c7210dce7e08d6582f4c46c5e4a51",
  "source_action_workflow_head_sha": "1351125bb903f7d7b636d945c4446ad815a2efb1",
  "source_action_workflow_run_id": 37618517412,
  "stage": "ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALLED",
  "strategy_v1_synthesis_authorized": false,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2022-runtime-authorization-install-receipt-v1"
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
        _run(37531960014, 383, "a1e194907c273a2fcdddfb4c24d64a96cfd8d263", "success"),
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
    "DEC-597 requires installed 2022 runtime state",
)
class AnnualPatternCatalogue2022DispatchPreflightTests(unittest.TestCase):
    def test_sources_pin_dec596_install(self) -> None:
        value = validate_2022_dispatch_preflight_sources(repository_root=ROOT)
        self.assertEqual(
            value["install_receipt_source_blob_sha"],
            "8f7891820c91bcac1fec5627c7b93ee967ab3754",
        )
        self.assertEqual(
            value["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            value["installed_gate_blob_sha"],
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
        )
        self.assertEqual(
            value["installed_runtime_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        )

    def test_preflight_freezes_run384_without_authorizing_dispatch(self) -> None:
        value = build_2022_dispatch_preflight(
            _receipt(),
            repository_root=ROOT,
            main_branch={"name": "main", "commit": {"sha": HEAD}},
            annual_workflow_runs=_annual_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2022_dispatch_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-597")
        self.assertEqual(value["source_installer_workflow_run_id"], 37635483891)
        self.assertEqual(value["source_install_artifact_id"], 11489650716)
        self.assertEqual(
            value["source_install_artifact_digest"],
            "sha256:704fa463bbd6d23fea6a829be3db9d84b8789fb09df1dd924e526040e4d53112",
        )
        self.assertEqual(
            value["source_install_commit_sha"],
            "df6da8cb52578c82e36c6206714a0452496614d9",
        )
        self.assertEqual(
            value["source_install_receipt_fingerprint_sha256"],
            "99e99b92f74776694bdfcaab2499587b36129f6c371ef87c1696e3ba4ad3ecfd",
        )
        self.assertEqual(
            value["source_install_receipt_canonical_sha256"],
            "79ebf56af148c5976734976e5332b3a16b314c8a42916223c771a3fd32b78de4",
        )
        self.assertEqual(value["expected_run_number"], 384)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37531960014)
        self.assertEqual(value["annual_workflow_run_count"], 9)
        self.assertEqual(value["successful_2021_run_id"], 37531960014)
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["dispatch_command_present"])
        for field in (
            "annual_workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "run_385_or_later_authorized",
            "next_segment_execution_authorized",
            "protected_history_access_authorized",
            "cross_year_comparison_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(value[field], field)

    def test_run384_already_present_fails_closed(self) -> None:
        runs = _annual_runs()
        rows = runs["workflow_runs"]
        assert isinstance(rows, list)
        rows.insert(0, _run(999999, 384, "d" * 40, "failure"))
        with self.assertRaisesRegex(ValueError, "exactly nine prior"):
            build_2022_dispatch_preflight(
                _receipt(),
                repository_root=ROOT,
                main_branch={"name": "main", "commit": {"sha": HEAD}},
                annual_workflow_runs=runs,
                expected_head_sha=HEAD,
            )

    def test_receipt_tampering_fails_closed(self) -> None:
        receipt = copy.deepcopy(_receipt())
        receipt["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_2022_dispatch_preflight(
                receipt,
                repository_root=ROOT,
                main_branch={"name": "main", "commit": {"sha": HEAD}},
                annual_workflow_runs=_annual_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        text = (
            ROOT / "scripts/phase8a_annual_pattern_catalogue_2022_dispatch_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn('subparsers.add_parser("dispatch")', text)


if __name__ == "__main__":
    unittest.main()
