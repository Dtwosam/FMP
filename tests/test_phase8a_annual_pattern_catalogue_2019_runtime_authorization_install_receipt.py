from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2019_runtime_authorization_install_receipt import (
    review_2019_runtime_authorization_install,
    validate_2019_runtime_authorization_install_receipt,
    validate_2019_runtime_authorization_install_receipt_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

ACTION_JSON = r"""
{
  "action_count": 2,
  "actions": [
    {
      "content_source_blob_sha": "d87fe85a5b426fa92caf7d6cc165445590f4097c",
      "content_source_path": "docs/superpowers/templates/annual_pattern_catalogue_2019_runtime_authorization.py.disabled",
      "expected_result_blob_sha": "d87fe85a5b426fa92caf7d6cc165445590f4097c",
      "expected_target_absent": true,
      "operation": "create",
      "order": 1,
      "target_path": "src/fmp/discovery/annual_pattern_catalogue_2019_runtime_authorization.py"
    },
    {
      "content_source_blob_sha": "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
      "content_source_path": "docs/superpowers/templates/annual_pattern_catalogue_runtime_with_2019_authorization.py.disabled",
      "expected_current_blob_sha": "410180c34a9e3500bbbb42310a5253b993ac7785",
      "expected_result_blob_sha": "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
      "operation": "update",
      "order": 2,
      "target_path": "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
    }
  ],
  "activation_condition": "validated_concrete_dec559_preflight_and_unchanged_runtime_on_exact_main",
  "annual_segment_label": "2019",
  "annual_workflow_dispatch_authorized": false,
  "authorization_basis": "standing_operator_autonomous_build_authorization",
  "broker_mutation_authorized": false,
  "cross_year_result_production_authorized": false,
  "decision": "DEC-560",
  "demo_order_authorized": false,
  "expected_head_sha": "bacb20c1d1541ac0b46076cef8ca9fe898559339",
  "expected_run_attempt": 1,
  "expected_run_number": 381,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_action_fingerprint_sha256": "c68df812693da1edfc5ab568afef50b2e70797a04b4c44cf22de7c3fc15bea35",
  "install_preflight_source_blob_sha": "a3b087419f9b9dd8980139f5dc47db4de3f657fd",
  "live_order_authorized": false,
  "next_gate": "APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC560",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "previous_annual_freeze_run_id": 37237817538,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "repository_mutation_authorized": true,
  "runtime_authorization_installed": false,
  "runtime_gate_active": false,
  "source_preflight_artifact_digest": "sha256:3d8b6933a1949c77a4e6b29df5bd86896a140d0011ba6859187d412df24cc8f9",
  "source_preflight_artifact_id": 11338796649,
  "source_preflight_decision": "DEC-559",
  "source_preflight_expected_head_sha": "bb1c7901d1b5859bec97a381716166e9024a6022",
  "source_preflight_fingerprint_sha256": "1c585ad2a2a0bdf3a0fc811376d1fa5701b293b2fd888abca30ea5c13fcf3861",
  "source_preflight_workflow_head_sha": "bb1c7901d1b5859bec97a381716166e9024a6022",
  "source_preflight_workflow_run_id": 37295798286,
  "stage": "ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_ACTION_READY",
  "strategy_v1_synthesis_authorized": false,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2019-runtime-authorization-install-action-v1"
}
"""


def _action() -> dict[str, object]:
    value = json.loads(ACTION_JSON)
    assert isinstance(value, dict)
    return value


class AnnualPatternCatalogue2019RuntimeAuthorizationInstallReceiptTests(
    unittest.TestCase
):
    def test_sources_pin_concrete_dec560_action(self) -> None:
        value = validate_2019_runtime_authorization_install_receipt_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            value["install_action_source_blob_sha"],
            "15cc0c8e3b93453ecaf6ba1dfd635133279acb6c",
        )

    def test_receipt_binds_exact_two_file_install_without_dispatch(self) -> None:
        value = review_2019_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                (
                    "src/fmp/discovery/"
                    "annual_pattern_catalogue_2019_runtime_authorization.py"
                ),
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha=(
                "d87fe85a5b426fa92caf7d6cc165445590f4097c"
            ),
            installed_runtime_blob_sha=(
                "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e"
            ),
        )
        self.assertIs(
            validate_2019_runtime_authorization_install_receipt(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-561")
        self.assertEqual(value["source_action_workflow_run_id"], 37299664787)
        self.assertEqual(value["source_action_artifact_id"], 11341025756)
        self.assertEqual(
            value["source_action_fingerprint_sha256"],
            "c68df812693da1edfc5ab568afef50b2e70797a04b4c44cf22de7c3fc15bea35",
        )
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["install_action_consumed"])
        self.assertEqual(value["expected_run_number"], 381)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37237817538)
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_changed_file_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "changed-file inventory"):
            review_2019_runtime_authorization_install(
                _action(),
                repository_root=REPOSITORY_ROOT,
                install_commit_sha="c" * 40,
                changed_files=[
                    "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
                ],
                installed_gate_blob_sha=(
                    "d87fe85a5b426fa92caf7d6cc165445590f4097c"
                ),
                installed_runtime_blob_sha=(
                    "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e"
                ),
            )

    def test_nonconcrete_action_fingerprint_is_rejected(self) -> None:
        action = _action()
        action["install_action_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "install action fingerprint mismatch|source action fingerprint mismatch"):
            review_2019_runtime_authorization_install(
                action,
                repository_root=REPOSITORY_ROOT,
                install_commit_sha="c" * 40,
                changed_files=[
                    (
                        "src/fmp/discovery/"
                        "annual_pattern_catalogue_2019_runtime_authorization.py"
                    ),
                    "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
                ],
                installed_gate_blob_sha=(
                    "d87fe85a5b426fa92caf7d6cc165445590f4097c"
                ),
                installed_runtime_blob_sha=(
                    "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e"
                ),
            )

    def test_receipt_tampering_fails_closed(self) -> None:
        value = review_2019_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                (
                    "src/fmp/discovery/"
                    "annual_pattern_catalogue_2019_runtime_authorization.py"
                ),
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha=(
                "d87fe85a5b426fa92caf7d6cc165445590f4097c"
            ),
            installed_runtime_blob_sha=(
                "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e"
            ),
        )
        tampered = copy.deepcopy(value)
        tampered["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            validate_2019_runtime_authorization_install_receipt(tampered)

    def test_cli_is_review_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/"
            "phase8a_annual_pattern_catalogue_2019_runtime_authorization_install_receipt.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("review")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
