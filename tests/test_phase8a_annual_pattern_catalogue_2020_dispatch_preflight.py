from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2020_dispatch_preflight import (
    build_2020_dispatch_preflight,
    validate_2020_dispatch_preflight,
    validate_2020_dispatch_preflight_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40

INSTALL_RECEIPT_JSON = r"""
{
  "annual_segment_label": "2020",
  "annual_workflow_dispatch_authorized": false,
  "broker_mutation_authorized": false,
  "changed_files": [
    "src/fmp/discovery/annual_pattern_catalogue_2020_runtime_authorization.py",
    "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
  ],
  "cross_year_result_production_authorized": false,
  "decision": "DEC-572",
  "demo_order_authorized": false,
  "expected_run_attempt": 1,
  "expected_run_number": 382,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_action_consumed": true,
  "install_action_source_blob_sha": "98043c92240d00a343087e4d5fcef56575ba319e",
  "install_commit_sha": "3ee648808bc2982c02dd1cb10fd45911f6379dcb",
  "install_receipt_fingerprint_sha256": "1f77559f7aadfb83e338e467148d86b2a99850d69909e689f04604fa19c3e7b4",
  "installed_gate_blob_sha": "695a50b418da752e1bd37d6302f209033ab611f5",
  "installed_runtime_blob_sha": "4e124365430672fa63825b272001937c60151644",
  "live_order_authorized": false,
  "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_DISPATCH_PREFLIGHT",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "previous_annual_freeze_run_id": 37310525635,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "runtime_authorization_installed": true,
  "runtime_gate_active": true,
  "source_action_artifact_digest": "sha256:082c09ed64042f2c63252676be1d63aab6553c3cd92e3995256498ac4744b423",
  "source_action_artifact_id": 11352259131,
  "source_action_decision": "DEC-571",
  "source_action_fingerprint_sha256": "0d617a5261a25d1fbdcc661fcc9518be63081ca442fb2ac068a2206f875e6939",
  "source_action_workflow_head_sha": "4ed1da1cdc5a8df1272fb1f06a803a57a8043427",
  "source_action_workflow_run_id": 37327905209,
  "stage": "ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALLED",
  "strategy_v1_synthesis_authorized": false,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2020-runtime-authorization-install-receipt-v1"
}
"""


def _install_receipt() -> dict[str, object]:
    value = json.loads(INSTALL_RECEIPT_JSON)
    assert isinstance(value, dict)
    return value


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _run(
    *,
    run_id: int,
    number: int,
    head_sha: str,
    conclusion: str,
) -> dict[str, object]:
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
    return {
        "workflow_runs": [
            _run(
                run_id=37310525635,
                number=381,
                head_sha="8bcee3a7a834743f08bd9ad73109bfc09609a2fe",
                conclusion="success",
            ),
            _run(
                run_id=37237817538,
                number=380,
                head_sha="30971a996f514670a6f836d8e45cf80137197a4f",
                conclusion="success",
            ),
            _run(
                run_id=37227536041,
                number=379,
                head_sha="7b4c1ef8573e280c067443b72f1534d9091d5b7f",
                conclusion="success",
            ),
            _run(
                run_id=37206992367,
                number=378,
                head_sha="2524fde355349581c9440a172d0384c3cbce31ed",
                conclusion="success",
            ),
            _run(
                run_id=37198002653,
                number=377,
                head_sha="a89db974be9a94481e7ed0990476bc661012f1e4",
                conclusion="success",
            ),
            _run(
                run_id=37191637168,
                number=376,
                head_sha="4c14fa7db6eb812b89ecb79201f7e298fa9c04f3",
                conclusion="failure",
            ),
            _run(
                run_id=37126711695,
                number=1,
                head_sha="fd85a886d07234ad584dcca08692b37e6af54b2e",
                conclusion="failure",
            ),
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-573 requires installed annual workflow and 2020 runtime state",
)
class AnnualPatternCatalogue2020DispatchPreflightTests(unittest.TestCase):
    def test_sources_pin_installed_runtime_and_dec561_receipt(self) -> None:
        value = validate_2020_dispatch_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            value["install_receipt_source_blob_sha"],
            "7bcf5c20c5dce845901bca200e299b8dfeb364b3",
        )
        self.assertEqual(
            value["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            value["installed_gate_blob_sha"],
            "695a50b418da752e1bd37d6302f209033ab611f5",
        )
        self.assertEqual(
            value["installed_runtime_blob_sha"],
            "4e124365430672fa63825b272001937c60151644",
        )

    def test_preflight_freezes_run382_without_authorizing_dispatch(self) -> None:
        value = build_2020_dispatch_preflight(
            _install_receipt(),
            repository_root=REPOSITORY_ROOT,
            main_branch=_main(),
            annual_workflow_runs=_annual_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2020_dispatch_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-573")
        self.assertEqual(value["source_installer_workflow_run_id"], 37361230835)
        self.assertEqual(value["source_install_artifact_id"], 11367191085)
        self.assertEqual(
            value["source_install_receipt_fingerprint_sha256"],
            "1f77559f7aadfb83e338e467148d86b2a99850d69909e689f04604fa19c3e7b4",
        )
        self.assertEqual(value["expected_run_number"], 382)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37310525635)
        self.assertEqual(value["annual_workflow_run_count"], 7)
        self.assertEqual(value["successful_2019_run_id"], 37310525635)
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_run382_already_present_fails_closed(self) -> None:
        runs = _annual_runs()
        rows = runs["workflow_runs"]
        assert isinstance(rows, list)
        rows.insert(
            0,
            _run(
                run_id=999999,
                number=382,
                head_sha="d" * 40,
                conclusion="failure",
            ),
        )
        with self.assertRaisesRegex(ValueError, "exactly seven prior"):
            build_2020_dispatch_preflight(
                _install_receipt(),
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs=runs,
                expected_head_sha=HEAD,
            )

    def test_install_receipt_tampering_fails_closed(self) -> None:
        receipt = copy.deepcopy(_install_receipt())
        receipt["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_2020_dispatch_preflight(
                receipt,
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs=_annual_runs(),
                expected_head_sha=HEAD,
            )

    def test_main_drift_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "current main head mismatch"):
            build_2020_dispatch_preflight(
                _install_receipt(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "c" * 40}},
                annual_workflow_runs=_annual_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        text = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2020_dispatch_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn('subparsers.add_parser("dispatch")', text)


if __name__ == "__main__":
    unittest.main()
