from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2020_runtime_authorization_install_receipt import (
    review_2020_runtime_authorization_install,
    validate_2020_runtime_authorization_install_receipt,
    validate_2020_runtime_authorization_install_receipt_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

ACTION_JSON = r"""
{
  "action_count": 2,
  "actions": [
    {
      "content_source_blob_sha": "695a50b418da752e1bd37d6302f209033ab611f5",
      "content_source_path": "docs/superpowers/templates/annual_pattern_catalogue_2020_runtime_authorization.py.disabled",
      "expected_result_blob_sha": "695a50b418da752e1bd37d6302f209033ab611f5",
      "expected_target_absent": true,
      "operation": "create",
      "order": 1,
      "target_path": "src/fmp/discovery/annual_pattern_catalogue_2020_runtime_authorization.py"
    },
    {
      "content_source_blob_sha": "4e124365430672fa63825b272001937c60151644",
      "content_source_path": "docs/superpowers/templates/annual_pattern_catalogue_runtime_with_2020_authorization.py.disabled",
      "expected_current_blob_sha": "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
      "expected_result_blob_sha": "4e124365430672fa63825b272001937c60151644",
      "operation": "update",
      "order": 2,
      "target_path": "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
    }
  ],
  "activation_condition": "validated_concrete_dec570_preflight_and_unchanged_runtime_on_exact_main",
  "annual_segment_label": "2020",
  "annual_workflow_dispatch_authorized": false,
  "authorization_basis": "standing_operator_autonomous_build_authorization",
  "broker_mutation_authorized": false,
  "cross_year_result_production_authorized": false,
  "decision": "DEC-571",
  "demo_order_authorized": false,
  "expected_head_sha": "4ed1da1cdc5a8df1272fb1f06a803a57a8043427",
  "expected_run_attempt": 1,
  "expected_run_number": 382,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_action_fingerprint_sha256": "0d617a5261a25d1fbdcc661fcc9518be63081ca442fb2ac068a2206f875e6939",
  "install_preflight_source_blob_sha": "cb7df2aa6601c0ca81678ce700aad315a336ceaa",
  "live_order_authorized": false,
  "next_gate": "APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC571",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "previous_annual_freeze_run_id": 37310525635,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "repository_mutation_authorized": true,
  "runtime_authorization_installed": false,
  "runtime_gate_active": false,
  "source_preflight_artifact_digest": "sha256:97eee3d49aec78ebbc1f3aa7190159d4dfba62c861f221163bd03c2699fdad7c",
  "source_preflight_artifact_id": 11350136423,
  "source_preflight_decision": "DEC-570",
  "source_preflight_expected_head_sha": "6b8f0015a0d38276356b3370d73d4d6a26c9e644",
  "source_preflight_fingerprint_sha256": "367ec514057b011711ab9734a839f8cf03d1334125db336c947e979d923cab36",
  "source_preflight_workflow_head_sha": "6b8f0015a0d38276356b3370d73d4d6a26c9e644",
  "source_preflight_workflow_run_id": 37321690650,
  "stage": "ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_ACTION_READY",
  "strategy_v1_synthesis_authorized": false,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2020-runtime-authorization-install-action-v1"
}
"""


def _action() -> dict[str, object]:
    value = json.loads(ACTION_JSON)
    assert isinstance(value, dict)
    return value


class AnnualPatternCatalogue2020RuntimeAuthorizationInstallReceiptTests(
    unittest.TestCase
):
    def test_sources_pin_concrete_dec571_action(self) -> None:
        value = validate_2020_runtime_authorization_install_receipt_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            value["install_action_source_blob_sha"],
            "98043c92240d00a343087e4d5fcef56575ba319e",
        )

    def test_receipt_binds_exact_two_file_install_without_dispatch(self) -> None:
        value = review_2020_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                "src/fmp/discovery/annual_pattern_catalogue_2020_runtime_authorization.py",
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha="695a50b418da752e1bd37d6302f209033ab611f5",
            installed_runtime_blob_sha="4e124365430672fa63825b272001937c60151644",
        )
        self.assertIs(validate_2020_runtime_authorization_install_receipt(value), value)
        self.assertEqual(value["decision"], "DEC-572")
        self.assertEqual(value["source_action_workflow_run_id"], 37327905209)
        self.assertEqual(value["source_action_artifact_id"], 11352259131)
        self.assertEqual(
            value["source_action_fingerprint_sha256"],
            "0d617a5261a25d1fbdcc661fcc9518be63081ca442fb2ac068a2206f875e6939",
        )
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["install_action_consumed"])
        self.assertEqual(value["expected_run_number"], 382)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37310525635)
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_changed_file_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "changed-file inventory"):
            review_2020_runtime_authorization_install(
                _action(),
                repository_root=REPOSITORY_ROOT,
                install_commit_sha="c" * 40,
                changed_files=["src/fmp/discovery/annual_pattern_catalogue_runtime.py"],
                installed_gate_blob_sha="695a50b418da752e1bd37d6302f209033ab611f5",
                installed_runtime_blob_sha="4e124365430672fa63825b272001937c60151644",
            )

    def test_receipt_tampering_fails_closed(self) -> None:
        value = review_2020_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                "src/fmp/discovery/annual_pattern_catalogue_2020_runtime_authorization.py",
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha="695a50b418da752e1bd37d6302f209033ab611f5",
            installed_runtime_blob_sha="4e124365430672fa63825b272001937c60151644",
        )
        tampered = copy.deepcopy(value)
        tampered["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            validate_2020_runtime_authorization_install_receipt(tampered)

    def test_cli_is_review_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2020_runtime_authorization_install_receipt.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("review")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
