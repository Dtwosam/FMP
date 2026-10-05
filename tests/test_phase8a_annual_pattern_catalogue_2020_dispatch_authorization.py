from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2020_dispatch_authorization import (
    build_2020_dispatch_authorization,
    validate_2020_dispatch_authorization,
    validate_2020_dispatch_authorization_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION_HEAD = "a" * 40

PREFLIGHT_JSON = r"""
{
  "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
  "annual_segment_label": "2020",
  "annual_workflow_dispatch_authorized": false,
  "annual_workflow_run_count": 7,
  "broker_mutation_authorized": false,
  "cross_year_result_production_authorized": false,
  "decision": "DEC-573",
  "demo_order_authorized": false,
  "dispatch_command_present": false,
  "expected_head_sha": "46aa484cc4729ff662122fb629576a6a40c1530f",
  "expected_run_attempt": 1,
  "expected_run_number": 382,
  "failed_run_1_id": 37126711695,
  "failed_run_376_id": 37191637168,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_receipt_source_blob_sha": "7bcf5c20c5dce845901bca200e299b8dfeb364b3",
  "installed_gate_blob_sha": "695a50b418da752e1bd37d6302f209033ab611f5",
  "installed_runtime_blob_sha": "4e124365430672fa63825b272001937c60151644",
  "live_order_authorized": false,
  "next_gate": "ANNUAL_PATTERN_CATALOGUE_2020_DISPATCH_AUTHORIZATION_BEFORE_RUN",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "preflight_fingerprint_sha256": "54ad1c4e693545ace92aed406140005ef8b609971247d1cf5b4240931dc7987e",
  "preflight_read_only": true,
  "previous_annual_freeze_run_id": 37310525635,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "runtime_authorization_installed": true,
  "runtime_gate_active": true,
  "source_install_artifact_digest": "sha256:5f0f9862b411a9da4f0c383259ef78dc9df842be4a58ee06c43374a0b774d716",
  "source_install_artifact_id": 11367191085,
  "source_install_commit_sha": "3ee648808bc2982c02dd1cb10fd45911f6379dcb",
  "source_install_receipt_decision": "DEC-572",
  "source_install_receipt_fingerprint_sha256": "1f77559f7aadfb83e338e467148d86b2a99850d69909e689f04604fa19c3e7b4",
  "source_installer_workflow_head_sha": "2d57ea571111845cd58a34a0c25a89eabe233bcb",
  "source_installer_workflow_run_id": 37361230835,
  "stage": "ANNUAL_CATALOGUE_2020_DISPATCH_PREFLIGHT_READY",
  "strategy_v1_synthesis_authorized": false,
  "successful_2015_run_id": 37198002653,
  "successful_2016_run_id": 37206992367,
  "successful_2017_run_id": 37227536041,
  "successful_2018_run_id": 37237817538,
  "successful_2019_run_id": 37310525635,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2020-dispatch-preflight-v1"
}
"""


def _preflight() -> dict[str, object]:
    value = json.loads(PREFLIGHT_JSON)
    assert isinstance(value, dict)
    return value


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-574 requires installed 2020 runtime and active annual workflow",
)
class AnnualPatternCatalogue2020DispatchAuthorizationTests(unittest.TestCase):
    def test_sources_pin_dec573_and_installed_runtime(self) -> None:
        source = validate_2020_dispatch_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["dispatch_preflight_source_blob_sha"],
            "0e796623ddc8b95e62db9d841d658d2b1898eac0",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "695a50b418da752e1bd37d6302f209033ab611f5",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "4e124365430672fa63825b272001937c60151644",
        )

    def test_exact_preflight_yields_source_only_run382_authorization(self) -> None:
        value = build_2020_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        self.assertIs(validate_2020_dispatch_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-574")
        self.assertEqual(value["source_preflight_workflow_run_id"], 37367592757)
        self.assertEqual(value["source_preflight_artifact_id"], 11368966845)
        self.assertEqual(
            value["source_preflight_artifact_digest"],
            "sha256:bba88547a36138109e6178936fd632e9bc61e81f8725e12124d739477916c5fa",
        )
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "54ad1c4e693545ace92aed406140005ef8b609971247d1cf5b4240931dc7987e",
        )
        self.assertEqual(value["authorization_head_sha"], AUTHORIZATION_HEAD)
        self.assertEqual(value["annual_segment_label"], "2020")
        self.assertEqual(value["prior_segment_label"], "2019")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37310525635)
        self.assertEqual(value["expected_run_number"], 382)
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
        self.assertFalse(value["run_383_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_source_preflight_dispatch_tamper_is_rejected(self) -> None:
        preflight = copy.deepcopy(_preflight())
        preflight["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "preflight fingerprint mismatch|annual_workflow_dispatch_authorized",
        ):
            build_2020_dispatch_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
                authorization_head_sha=AUTHORIZATION_HEAD,
            )

    def test_wrong_run_number_is_rejected(self) -> None:
        preflight = copy.deepcopy(_preflight())
        preflight["expected_run_number"] = 383
        with self.assertRaisesRegex(
            ValueError,
            "preflight fingerprint mismatch|expected_run_number mismatch|expected run number mismatch",
        ):
            build_2020_dispatch_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
                authorization_head_sha=AUTHORIZATION_HEAD,
            )

    def test_refingerprinted_later_run_authority_is_rejected(self) -> None:
        value = build_2020_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["run_383_or_later_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
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
            "run_383_or_later_authorized mismatch",
        ):
            validate_2020_dispatch_authorization(tampered)

    def test_cli_is_authorize_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2020_dispatch_authorization.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("authorize")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
