from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2022_dispatch_authorization import (
    build_2022_dispatch_authorization,
)
from fmp.discovery.annual_pattern_catalogue_2022_dispatch_action_preflight import (
    build_2022_dispatch_action_preflight,
    validate_2022_dispatch_action_preflight,
    validate_2022_dispatch_action_preflight_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "e" * 40
AUTHORIZATION_HEAD = "a6bd637f55e356a948378f6a85e99443ee287a4f"

PREFLIGHT_JSON = r"""
{
  "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
  "annual_segment_label": "2022",
  "annual_workflow_dispatch_authorized": false,
  "annual_workflow_run_count": 9,
  "broker_mutation_authorized": false,
  "cross_year_comparison_authorized": false,
  "cross_year_result_production_authorized": false,
  "decision": "DEC-597",
  "demo_order_authorized": false,
  "dispatch_command_present": false,
  "expected_head_sha": "1fafdacab1df0bc2df24b6fa8cd822b031e5cda8",
  "expected_run_attempt": 1,
  "expected_run_number": 384,
  "failed_run_1_id": 37126711695,
  "failed_run_376_id": 37191637168,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_receipt_source_blob_sha": "8f7891820c91bcac1fec5627c7b93ee967ab3754",
  "installed_gate_blob_sha": "ecb21dc7106e7bd43447f4135c3a696251a75e05",
  "installed_runtime_blob_sha": "f2734c7ea32355b1024d1097812578b23fc4409d",
  "live_order_authorized": false,
  "next_gate": "ANNUAL_PATTERN_CATALOGUE_2022_DISPATCH_AUTHORIZATION_BEFORE_RUN",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "preflight_fingerprint_sha256": "090b8c7e9a1e835387bb7e1579d6db902d359e537c67caa1357a1d96ff938c92",
  "preflight_read_only": true,
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
  "source_install_artifact_digest": "sha256:704fa463bbd6d23fea6a829be3db9d84b8789fb09df1dd924e526040e4d53112",
  "source_install_artifact_id": 11489650716,
  "source_install_commit_sha": "df6da8cb52578c82e36c6206714a0452496614d9",
  "source_install_receipt_canonical_sha256": "79ebf56af148c5976734976e5332b3a16b314c8a42916223c771a3fd32b78de4",
  "source_install_receipt_decision": "DEC-596",
  "source_install_receipt_fingerprint_sha256": "99e99b92f74776694bdfcaab2499587b36129f6c371ef87c1696e3ba4ad3ecfd",
  "source_installer_workflow_head_sha": "68bdb581a89247b0a2e5046fe9a30f086260e498",
  "source_installer_workflow_run_id": 37635483891,
  "stage": "ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_READY",
  "strategy_v1_synthesis_authorized": false,
  "successful_2015_run_id": 37198002653,
  "successful_2016_run_id": 37206992367,
  "successful_2017_run_id": 37227536041,
  "successful_2018_run_id": 37237817538,
  "successful_2019_run_id": 37310525635,
  "successful_2020_run_id": 37443770076,
  "successful_2021_run_id": 37531960014,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2022-dispatch-preflight-v1"
}
"""


def _preflight() -> dict[str, object]:
    value = json.loads(PREFLIGHT_JSON)
    assert isinstance(value, dict)
    return value


def _authorization() -> dict[str, object]:
    value = build_2022_dispatch_authorization(
        _preflight(),
        repository_root=REPOSITORY_ROOT,
        authorization_head_sha=AUTHORIZATION_HEAD,
    )
    assert value["authorization_fingerprint_sha256"] == (
        "4b6dbbb1c02b0806828c19748f50bc2e06aa75b6a9baee88d6716a7e35900270"
    )
    return value


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _runs() -> dict[str, object]:
    common = {
        "name": "phase8a-annual-pattern-catalogue",
        "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "run_attempt": 1,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "status": "completed",
    }
    return {
        "workflow_runs": [
            {
                **common,
                "id": 37126711695,
                "run_number": 1,
                "head_sha": "fd85a886d07234ad584dcca08692b37e6af54b2e",
                "conclusion": "failure",
            },
            {
                **common,
                "id": 37191637168,
                "run_number": 376,
                "head_sha": "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3",
                "conclusion": "failure",
            },
            {
                **common,
                "id": 37198002653,
                "run_number": 377,
                "head_sha": "a89db974be9a94481e7ed0990476bc661012f1e4",
                "conclusion": "success",
            },
            {
                **common,
                "id": 37206992367,
                "run_number": 378,
                "head_sha": "2524fde355349581c9440a172d0384c3cbce31ed",
                "conclusion": "success",
            },
            {
                **common,
                "id": 37227536041,
                "run_number": 379,
                "head_sha": "7b4c1ef8573e280c067443b72f1534d9091d5b7f",
                "conclusion": "success",
            },
            {
                **common,
                "id": 37237817538,
                "run_number": 380,
                "head_sha": "30971a996f514670a6f836d8e45cf80137197a4f",
                "conclusion": "success",
            },
            {
                **common,
                "id": 37310525635,
                "run_number": 381,
                "head_sha": "8bcee3a7a834743f08bd9ad73109bfc09609a2fe",
                "conclusion": "success",
            },
            {
                **common,
                "id": 37443770076,
                "run_number": 382,
                "head_sha": "681e81e021d4970a67b18370142d55b17ec68864",
                "conclusion": "success",
            },
            {
                **common,
                "id": 37531960014,
                "run_number": 383,
                "head_sha": "a1e194907c273a2fcdddfb4c24d64a96cfd8d263",
                "conclusion": "success",
            },
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-599 requires the current installed 2022 runtime state",
)
class AnnualPatternCatalogue2022DispatchActionPreflightTests(unittest.TestCase):
    def test_sources_pin_concrete_authorization_and_runtime(self) -> None:
        source = validate_2022_dispatch_action_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["authorization_source_blob_sha"],
            "34a805b3ab9038e847097f51a3fcc1d5c1806a53",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        )

    def test_exact_state_freezes_run384_parameters_read_only(self) -> None:
        value = build_2022_dispatch_action_preflight(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2022_dispatch_action_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-599")
        self.assertEqual(value["annual_workflow_run_count"], 9)
        self.assertEqual(value["annual_segment_label"], "2022")
        self.assertEqual(value["prior_segment_label"], "2021")
        self.assertEqual(value["successful_2021_run_id"], 37531960014)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37531960014)
        self.assertEqual(value["expected_run_number"], 384)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["dispatch_ref"], "main")
        self.assertEqual(value["dispatch_input_annual_segment_label"], "2022")
        self.assertEqual(
            value["dispatch_input_previous_annual_freeze_run_id"],
            "37531960014",
        )
        self.assertTrue(value["dispatch_parameters_frozen"])
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["run_385_or_later_authorized"])
        self.assertFalse(value["protected_history_access_authorized"])
        self.assertFalse(value["cross_year_comparison_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_unexpected_run384_is_rejected(self) -> None:
        runs = _runs()
        rows = list(runs["workflow_runs"])
        rows.append(
            {
                "id": 99999999999,
                "name": "phase8a-annual-pattern-catalogue",
                "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
                "run_number": 384,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": HEAD,
                "status": "completed",
                "conclusion": "success",
            }
        )
        with self.assertRaisesRegex(
            ValueError,
            "exactly eight prior annual workflow runs",
        ):
            build_2022_dispatch_action_preflight(
                _authorization(),
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=HEAD,
            )

    def test_run382_head_drift_is_rejected(self) -> None:
        runs = _runs()
        rows = [dict(row) for row in runs["workflow_runs"]]
        rows[7]["head_sha"] = "d" * 40
        with self.assertRaisesRegex(
            ValueError,
            "annual run 382 head_sha mismatch",
        ):
            build_2022_dispatch_action_preflight(
                _authorization(),
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=HEAD,
            )

    def test_concrete_authorization_head_drift_is_rejected(self) -> None:
        authorization = copy.deepcopy(_authorization())
        authorization["authorization_head_sha"] = "f" * 40
        unsigned = dict(authorization)
        unsigned.pop("authorization_fingerprint_sha256", None)
        import hashlib
        authorization["authorization_fingerprint_sha256"] = hashlib.sha256(
            (
                json.dumps(
                    unsigned,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "source authorization head mismatch",
        ):
            build_2022_dispatch_action_preflight(
                authorization,
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2022_dispatch_action_preflight(
                _authorization(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "c" * 40}},
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2022_dispatch_action_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
