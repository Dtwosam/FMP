from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2022_dispatch_authorization import (
    build_2022_dispatch_authorization,
    validate_2022_dispatch_authorization,
    validate_2022_dispatch_authorization_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION_HEAD = "a" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _preflight() -> dict[str, object]:
    return {
        "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        "annual_segment_label": "2022",
        "annual_workflow_dispatch_authorized": False,
        "annual_workflow_run_count": 9,
        "broker_mutation_authorized": False,
        "cross_year_comparison_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-597",
        "demo_order_authorized": False,
        "dispatch_command_present": False,
        "expected_head_sha": "1fafdacab1df0bc2df24b6fa8cd822b031e5cda8",
        "expected_run_attempt": 1,
        "expected_run_number": 384,
        "failed_run_1_id": 37126711695,
        "failed_run_376_id": 37191637168,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "install_receipt_source_blob_sha": "8f7891820c91bcac1fec5627c7b93ee967ab3754",
        "installed_gate_blob_sha": "ecb21dc7106e7bd43447f4135c3a696251a75e05",
        "installed_runtime_blob_sha": "f2734c7ea32355b1024d1097812578b23fc4409d",
        "live_order_authorized": False,
        "next_gate": "ANNUAL_PATTERN_CATALOGUE_2022_DISPATCH_AUTHORIZATION_BEFORE_RUN",
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "preflight_fingerprint_sha256": "090b8c7e9a1e835387bb7e1579d6db902d359e537c67caa1357a1d96ff938c92",
        "preflight_read_only": True,
        "previous_annual_freeze_run_id": 37531960014,
        "promotion_authorized": False,
        "protected_history_access_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "repository_full_name": "Dtwosam/FMP",
        "rerun_authorized": False,
        "retry_authorized": False,
        "run_385_or_later_authorized": False,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "source_install_artifact_digest": "sha256:704fa463bbd6d23fea6a829be3db9d84b8789fb09df1dd924e526040e4d53112",
        "source_install_artifact_id": 11489650716,
        "source_install_commit_sha": "df6da8cb52578c82e36c6206714a0452496614d9",
        "source_install_receipt_canonical_sha256": "79ebf56af148c5976734976e5332b3a16b314c8a42916223c771a3fd32b78de4",
        "source_install_receipt_decision": "DEC-596",
        "source_install_receipt_fingerprint_sha256": "99e99b92f74776694bdfcaab2499587b36129f6c371ef87c1696e3ba4ad3ecfd",
        "source_installer_workflow_head_sha": "68bdb581a89247b0a2e5046fe9a30f086260e498",
        "source_installer_workflow_run_id": 37635483891,
        "stage": "ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_READY",
        "strategy_v1_synthesis_authorized": False,
        "successful_2015_run_id": 37198002653,
        "successful_2016_run_id": 37206992367,
        "successful_2017_run_id": 37227536041,
        "successful_2018_run_id": 37237817538,
        "successful_2019_run_id": 37310525635,
        "successful_2020_run_id": 37443770076,
        "successful_2021_run_id": 37531960014,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2022-dispatch-preflight-v1",
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-598 requires installed 2022 annual runtime state",
)
class AnnualPatternCatalogue2022DispatchAuthorizationTests(unittest.TestCase):
    def test_sources_pin_dec597_and_installed_runtime(self) -> None:
        source = validate_2022_dispatch_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["dispatch_preflight_source_blob_sha"],
            "6680b571765622653bf53a006a1cb7126cf7ea80",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        )

    def test_authorization_is_source_only_and_exact_run384(self) -> None:
        value = build_2022_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        self.assertIs(validate_2022_dispatch_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-598")
        self.assertEqual(value["source_preflight_workflow_run_id"], 37643850671)
        self.assertEqual(value["source_preflight_artifact_id"], 11492114816)
        self.assertEqual(
            value["source_preflight_artifact_digest"],
            "sha256:440254694717b13d2fe346a0aae4b247beb02dd9cb18feab7ad6a947968d13d2",
        )
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "090b8c7e9a1e835387bb7e1579d6db902d359e537c67caa1357a1d96ff938c92",
        )
        self.assertEqual(
            value["source_preflight_canonical_sha256"],
            "015a894dca744889a6fdb56b64190e48c43a13e62c149363e248778660c53481",
        )
        self.assertEqual(value["authorization_head_sha"], AUTHORIZATION_HEAD)
        self.assertEqual(value["authorization_scope"], "2022_run_384_attempt_1_only")
        self.assertEqual(value["annual_segment_label"], "2022")
        self.assertEqual(value["prior_segment_label"], "2021")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37531960014)
        self.assertEqual(value["expected_run_number"], 384)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["authorization_contract_validated"])
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertTrue(value["source_only_authorization"])
        for field in (
            "dispatch_command_present",
            "dispatch_action_executed",
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

    def test_source_preflight_authority_tamper_is_rejected(self) -> None:
        preflight = copy.deepcopy(_preflight())
        preflight["annual_workflow_dispatch_authorized"] = True
        unsigned = dict(preflight)
        unsigned.pop("preflight_fingerprint_sha256", None)
        preflight["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaises(ValueError):
            build_2022_dispatch_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
                authorization_head_sha=AUTHORIZATION_HEAD,
            )

    def test_refingerprinted_run385_authority_is_rejected(self) -> None:
        value = build_2022_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["run_385_or_later_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "run_385_or_later_authorized mismatch",
        ):
            validate_2022_dispatch_authorization(tampered)

    def test_cli_is_authorize_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2022_dispatch_authorization.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("authorize")', script)
        for forbidden in (
            'subparsers.add_parser("dispatch")',
            'subparsers.add_parser("run")',
            'subparsers.add_parser("execute")',
            "gh workflow run ",
        ):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
