from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_dispatch_preflight import (
    build_2023_dispatch_preflight,
    validate_2023_dispatch_preflight,
    validate_2023_dispatch_preflight_sources,
)


ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40

INSTALL_RECEIPT_JSON = r"""
{
  "annual_segment_label": "2023",
  "annual_workflow_dispatch_authorized": false,
  "broker_mutation_authorized": false,
  "changed_files": [
    "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py",
    "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
  ],
  "cross_year_comparison_authorized": false,
  "cross_year_result_production_authorized": false,
  "decision": "DEC-607",
  "demo_order_authorized": false,
  "expected_run_attempt": 1,
  "expected_run_number": 385,
  "governing_method_decision": "DEC-469",
  "governing_protocol_decision": "DEC-470",
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_action_consumed": true,
  "install_action_source_blob_sha": "42477932452d07a445d7c85650a01b3692fa755c",
  "install_commit_sha": "3eb688a0e69afba4a04d2b91a61fa7189135eeab",
  "install_receipt_fingerprint_sha256": "1a13067292e6e52eff69d606e968b15e362ef19e8a14278d80cd594a64f5fc9c",
  "installed_gate_blob_sha": "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
  "installed_runtime_blob_sha": "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
  "live_order_authorized": false,
  "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2023_DISPATCH_PREFLIGHT",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "previous_annual_freeze_run_id": 37663157285,
  "promotion_authorized": false,
  "protected_catalogue_segment": true,
  "protected_history_access_authorized": false,
  "protocol_2023_2026_catalogue_use_authorized": true,
  "protocol_full_collection_catalogue_use_authorized": true,
  "real_money_authorized": false,
  "replacement_run_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "rerun_authorized": false,
  "retry_authorized": false,
  "run_386_or_later_authorized": false,
  "runtime_authorization_installed": true,
  "runtime_gate_active": true,
  "source_action_artifact_digest": "sha256:9ef098ec8f9e91ad640ce1e08c94b0942b5a18115a4b0257269845688d06fdde",
  "source_action_artifact_id": 11514552382,
  "source_action_canonical_sha256": "927c05ce7d59782a10e148d7345a3a93bedc6587e3acb0632c9dcd531eb262b4",
  "source_action_decision": "DEC-606",
  "source_action_fingerprint_sha256": "585af9488ef0a2f6df018bc86051979fc68d151810a0575cc5091f051f18e763",
  "source_action_workflow_head_sha": "14478b3d8e6026a834d4e5d5d34bdf0b0d0dfd30",
  "source_action_workflow_run_id": 37693786078,
  "source_authorization_protected_history_access_authorized": true,
  "stage": "ANNUAL_CATALOGUE_2023_RUNTIME_AUTHORIZATION_INSTALLED",
  "strategy_v1_synthesis_authorized": false,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2023-runtime-authorization-install-receipt-v1"
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
        _run(37663157285, 384, "dd79687adc4ec179c56f91939cb600e6746fab5d", "success"),
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
    "DEC-608 requires installed 2023 runtime state",
)
class AnnualPatternCatalogue2023DispatchPreflightTests(unittest.TestCase):
    def test_sources_pin_dec607_install(self) -> None:
        value = validate_2023_dispatch_preflight_sources(repository_root=ROOT)
        self.assertEqual(
            value["install_receipt_source_blob_sha"],
            "a8cc32730ab16e9d876725363ddc6d53fa09890a",
        )
        self.assertEqual(
            value["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            value["installed_gate_blob_sha"],
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
        )
        self.assertEqual(
            value["installed_runtime_blob_sha"],
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        )

    def test_preflight_freezes_run385_without_authorizing_dispatch(self) -> None:
        value = build_2023_dispatch_preflight(
            _receipt(),
            repository_root=ROOT,
            main_branch={"name": "main", "commit": {"sha": HEAD}},
            annual_workflow_runs=_annual_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2023_dispatch_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-608")
        self.assertEqual(value["source_installer_workflow_run_id"], 37763604645)
        self.assertEqual(value["source_install_artifact_id"], 11542709585)
        self.assertEqual(
            value["source_install_artifact_digest"],
            "sha256:e055c0e1d6727451c52c4cc3d3f7530fa6afc65faf87cf0d6e95e013f1b2eef8",
        )
        self.assertEqual(
            value["source_install_commit_sha"],
            "3eb688a0e69afba4a04d2b91a61fa7189135eeab",
        )
        self.assertEqual(
            value["source_install_receipt_fingerprint_sha256"],
            "1a13067292e6e52eff69d606e968b15e362ef19e8a14278d80cd594a64f5fc9c",
        )
        self.assertEqual(
            value["source_install_receipt_canonical_sha256"],
            "dde50dd5d4a7ad7d0fb92cc69eda83090f08958c391706b283cef9796dbfcaef",
        )
        self.assertEqual(value["expected_run_number"], 385)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37663157285)
        self.assertEqual(value["annual_workflow_run_count"], 10)
        self.assertEqual(value["successful_2021_run_id"], 37531960014)
        self.assertEqual(value["successful_2022_run_id"], 37663157285)
        self.assertTrue(value["source_authorization_protected_history_access_authorized"])
        self.assertTrue(value["protected_catalogue_segment"])
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
            "run_386_or_later_authorized",
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

    def test_run385_already_present_fails_closed(self) -> None:
        runs = _annual_runs()
        rows = runs["workflow_runs"]
        assert isinstance(rows, list)
        rows.insert(0, _run(999999, 385, "d" * 40, "failure"))
        with self.assertRaisesRegex(ValueError, "exactly ten prior"):
            build_2023_dispatch_preflight(
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
            build_2023_dispatch_preflight(
                receipt,
                repository_root=ROOT,
                main_branch={"name": "main", "commit": {"sha": HEAD}},
                annual_workflow_runs=_annual_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        text = (
            ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_dispatch_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn('subparsers.add_parser("dispatch")', text)


if __name__ == "__main__":
    unittest.main()
