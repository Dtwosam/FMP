from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2021_runtime_authorization_install_receipt import (
    review_2021_runtime_authorization_install,
    validate_2021_runtime_authorization_install_receipt,
    validate_2021_runtime_authorization_install_receipt_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

ACTION_JSON = r"""
{
  "action_count": 2,
  "actions": [
    {
      "content_source_blob_sha": "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
      "content_source_path": "docs/superpowers/templates/annual_pattern_catalogue_2021_runtime_authorization.py.disabled",
      "expected_result_blob_sha": "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
      "expected_target_absent": true,
      "operation": "create",
      "order": 1,
      "target_path": "src/fmp/discovery/annual_pattern_catalogue_2021_runtime_authorization.py"
    },
    {
      "content_source_blob_sha": "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
      "content_source_path": "docs/superpowers/templates/annual_pattern_catalogue_runtime_with_2021_authorization.py.disabled",
      "expected_current_blob_sha": "4e124365430672fa63825b272001937c60151644",
      "expected_result_blob_sha": "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
      "operation": "update",
      "order": 2,
      "target_path": "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
    }
  ],
  "activation_condition": "validated_concrete_dec583_preflight_and_unchanged_runtime_on_exact_main",
  "annual_segment_label": "2021",
  "annual_workflow_dispatch_authorized": false,
  "authorization_basis": "standing_operator_autonomous_build_authorization",
  "broker_mutation_authorized": false,
  "cross_year_result_production_authorized": false,
  "decision": "DEC-584",
  "demo_order_authorized": false,
  "expected_head_sha": "32927e836fcf6888a7f8567b28f5ba2fd0b48315",
  "expected_run_attempt": 1,
  "expected_run_number": 383,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_action_fingerprint_sha256": "bffb48b795c1fc76f792aa8b00f5b8b94d23554cbc958bf3d11249eaa1058b04",
  "install_preflight_source_blob_sha": "b8ba899634fe1b45ee7a50dc13da97440c3d45d0",
  "live_order_authorized": false,
  "next_gate": "APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2021_RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC584",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "previous_annual_freeze_run_id": 37443770076,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "repository_mutation_authorized": true,
  "runtime_authorization_installed": false,
  "runtime_gate_active": false,
  "source_preflight_artifact_digest": "sha256:4a9de7f416f2297ce315b43f6869a17db34341686c12deced02000fda5342e79",
  "source_preflight_artifact_id": 11423396654,
  "source_preflight_decision": "DEC-559",
  "source_preflight_expected_head_sha": "bb1c7901d1b5859bec97a383716166e9024a6022",
  "source_preflight_fingerprint_sha256": "54bb157ee055a5c625f1cb05094e7c4f8228f48766ccdfb163e4d2b07223d575",
  "source_preflight_workflow_head_sha": "bb1c7901d1b5859bec97a383716166e9024a6022",
  "source_preflight_workflow_run_id": 37486048003,
  "stage": "ANNUAL_CATALOGUE_2021_RUNTIME_AUTHORIZATION_INSTALL_ACTION_READY",
  "strategy_v1_synthesis_authorized": false,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2021-runtime-authorization-install-action-v1"
}
"""


def _action() -> dict[str, object]:
    value = json.loads(ACTION_JSON)
    assert isinstance(value, dict)
    return value


class AnnualPatternCatalogue2021RuntimeAuthorizationInstallReceiptTests(
    unittest.TestCase
):
    def test_sources_pin_concrete_dec560_action(self) -> None:
        value = validate_2021_runtime_authorization_install_receipt_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            value["install_action_source_blob_sha"],
            "9ea8f4574ed1a85cbf0b95031a7450cc4f7fa705",
        )

    def test_receipt_binds_exact_two_file_install_without_dispatch(self) -> None:
        value = review_2021_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                (
                    "src/fmp/discovery/"
                    "annual_pattern_catalogue_2021_runtime_authorization.py"
                ),
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha=(
                "cac68c905bedf3105aa7e766eaa968c87bff6ce9"
            ),
            installed_runtime_blob_sha=(
                "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"
            ),
        )
        self.assertIs(
            validate_2021_runtime_authorization_install_receipt(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-585")
        self.assertEqual(value["source_action_workflow_run_id"], 37490417862)
        self.assertEqual(value["source_action_artifact_id"], 11425666284)
        self.assertEqual(
            value["source_action_fingerprint_sha256"],
            "bffb48b795c1fc76f792aa8b00f5b8b94d23554cbc958bf3d11249eaa1058b04",
        )
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["install_action_consumed"])
        self.assertEqual(value["expected_run_number"], 383)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37443770076)
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_changed_file_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "changed-file inventory"):
            review_2021_runtime_authorization_install(
                _action(),
                repository_root=REPOSITORY_ROOT,
                install_commit_sha="c" * 40,
                changed_files=[
                    "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
                ],
                installed_gate_blob_sha=(
                    "cac68c905bedf3105aa7e766eaa968c87bff6ce9"
                ),
                installed_runtime_blob_sha=(
                    "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"
                ),
            )

    def test_nonconcrete_action_fingerprint_is_rejected(self) -> None:
        action = _action()
        action["install_action_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "install action fingerprint mismatch|source action fingerprint mismatch"):
            review_2021_runtime_authorization_install(
                action,
                repository_root=REPOSITORY_ROOT,
                install_commit_sha="c" * 40,
                changed_files=[
                    (
                        "src/fmp/discovery/"
                        "annual_pattern_catalogue_2021_runtime_authorization.py"
                    ),
                    "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
                ],
                installed_gate_blob_sha=(
                    "cac68c905bedf3105aa7e766eaa968c87bff6ce9"
                ),
                installed_runtime_blob_sha=(
                    "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"
                ),
            )

    def test_receipt_tampering_fails_closed(self) -> None:
        value = review_2021_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                (
                    "src/fmp/discovery/"
                    "annual_pattern_catalogue_2021_runtime_authorization.py"
                ),
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha=(
                "cac68c905bedf3105aa7e766eaa968c87bff6ce9"
            ),
            installed_runtime_blob_sha=(
                "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"
            ),
        )
        tampered = copy.deepcopy(value)
        tampered["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            validate_2021_runtime_authorization_install_receipt(tampered)

    def test_cli_is_review_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/"
            "phase8a_annual_pattern_catalogue_2021_runtime_authorization_install_receipt.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("review")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
