from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2018_dispatch_authorization import (
    build_2018_dispatch_authorization,
    validate_2018_dispatch_authorization,
    validate_2018_dispatch_authorization_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION_HEAD = "a" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _preflight() -> dict[str, object]:
    value: dict[str, object] = {
        "active_workflow_blob_sha": (
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
        ),
        "annual_segment_label": "2018",
        "annual_workflow_dispatch_authorized": False,
        "annual_workflow_run_count": 5,
        "broker_mutation_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-551",
        "demo_order_authorized": False,
        "dispatch_command_present": False,
        "expected_head_sha": "35263ec4c59bae4733507c53b080f3ea07ff1325",
        "expected_run_attempt": 1,
        "expected_run_number": 380,
        "failed_run_1_id": 37126711695,
        "failed_run_376_id": 37191637168,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "install_receipt_source_blob_sha": (
            "a2a07003fdcef2a4202594286becc562ee6fc718"
        ),
        "installed_gate_blob_sha": (
            "cd50f50156cf74c34cd97d69d24291dc373b390f"
        ),
        "installed_runtime_blob_sha": (
            "410180c34a9e3500bbbb42310a5253b993ac7785"
        ),
        "live_order_authorized": False,
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2018_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "preflight_read_only": True,
        "previous_annual_freeze_run_id": 37227536041,
        "promotion_authorized": False,
        "real_money_authorized": False,
        "repository_full_name": "Dtwosam/FMP",
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "source_install_artifact_digest": (
            "sha256:8b9732b24a5ef6163d8ab54f34d058eecd9e1c4ce1a68c79a88306178933df2d"
        ),
        "source_install_artifact_id": 11314488545,
        "source_install_commit_sha": (
            "1fc73dfc1e102996cecd5b9ffcb75d3ab4fa3ade"
        ),
        "source_install_receipt_decision": "DEC-550",
        "source_install_receipt_fingerprint_sha256": (
            "5759024fded487649284109550a0d54d4a92332b963804e196b2cad15984dc27"
        ),
        "source_installer_workflow_head_sha": (
            "11048bd278bbf8f3697571aaff40c27656449a6c"
        ),
        "source_installer_workflow_run_id": 37233054691,
        "stage": "ANNUAL_CATALOGUE_2018_DISPATCH_PREFLIGHT_READY",
        "strategy_v1_synthesis_authorized": False,
        "successful_2015_run_id": 37198002653,
        "successful_2016_run_id": 37206992367,
        "successful_2017_run_id": 37227536041,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2018-dispatch-preflight-v1",
    }
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    assert (
        value["preflight_fingerprint_sha256"]
        == "f756088f404f77220b366eaffdfd36cfe805f9fcd91a274ef7c5a364994893c8"
    )
    return value


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-552 requires the installed DEC-550 runtime and active annual workflow",
)
class AnnualPatternCatalogue2018DispatchAuthorizationTests(unittest.TestCase):
    def test_sources_pin_dec551_and_installed_runtime(self) -> None:
        source = validate_2018_dispatch_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["dispatch_preflight_source_blob_sha"],
            "171056b861bf3e795271cd04631b4f8fdba7a827",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        )

    def test_exact_preflight_yields_source_only_run380_authorization(self) -> None:
        value = build_2018_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        self.assertIs(validate_2018_dispatch_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-552")
        self.assertEqual(value["source_preflight_workflow_run_id"], 37233894381)
        self.assertEqual(value["source_preflight_artifact_id"], 11314757055)
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "f756088f404f77220b366eaffdfd36cfe805f9fcd91a274ef7c5a364994893c8",
        )
        self.assertEqual(value["authorization_head_sha"], AUTHORIZATION_HEAD)
        self.assertEqual(value["annual_segment_label"], "2018")
        self.assertEqual(value["prior_segment_label"], "2017")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37227536041)
        self.assertEqual(value["expected_run_number"], 380)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["authorization_contract_validated"])
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertTrue(value["source_only_authorization"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertFalse(value["run_381_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_source_preflight_dispatch_tamper_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["annual_workflow_dispatch_authorized"] = True
        unsigned = dict(preflight)
        unsigned.pop("preflight_fingerprint_sha256", None)
        preflight["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "preflight fingerprint mismatch|annual_workflow_dispatch_authorized",
        ):
            build_2018_dispatch_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
                authorization_head_sha=AUTHORIZATION_HEAD,
            )

    def test_wrong_run_number_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["expected_run_number"] = 381
        unsigned = dict(preflight)
        unsigned.pop("preflight_fingerprint_sha256", None)
        preflight["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "preflight fingerprint mismatch|expected run number mismatch",
        ):
            build_2018_dispatch_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
                authorization_head_sha=AUTHORIZATION_HEAD,
            )

    def test_refingerprinted_later_run_authority_is_rejected(self) -> None:
        value = build_2018_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["run_381_or_later_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "run_381_or_later_authorized mismatch",
        ):
            validate_2018_dispatch_authorization(tampered)

    def test_cli_is_authorize_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2018_dispatch_authorization.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("authorize")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
