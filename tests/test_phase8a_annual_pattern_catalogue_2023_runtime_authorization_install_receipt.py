from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_runtime_authorization_install_receipt import (
    review_2023_runtime_authorization_install,
    validate_2023_runtime_authorization_install_receipt,
    validate_2023_runtime_authorization_install_receipt_sources,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

ACTION_JSON = r'''{
  "action_count": 2,
  "actions": [
    {
      "content_source_blob_sha": "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
      "content_source_path": "docs/superpowers/templates/annual_pattern_catalogue_2023_runtime_authorization.py.disabled",
      "expected_result_blob_sha": "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
      "expected_target_absent": true,
      "operation": "create",
      "order": 1,
      "target_path": "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py"
    },
    {
      "content_source_blob_sha": "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
      "content_source_path": "docs/superpowers/templates/annual_pattern_catalogue_runtime_with_2023_authorization.py.disabled",
      "expected_current_blob_sha": "f2734c7ea32355b1024d1097812578b23fc4409d",
      "expected_result_blob_sha": "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
      "operation": "update",
      "order": 2,
      "target_path": "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
    }
  ],
  "activation_condition": "validated_concrete_dec605_preflight_and_unchanged_runtime_on_exact_main",
  "annual_segment_label": "2023",
  "annual_workflow_dispatch_authorized": false,
  "authorization_basis": "standing_operator_autonomous_build_authorization",
  "broker_mutation_authorized": false,
  "cross_year_comparison_authorized": false,
  "cross_year_result_production_authorized": false,
  "decision": "DEC-606",
  "demo_order_authorized": false,
  "expected_head_sha": "14478b3d8e6026a834d4e5d5d34bdf0b0d0dfd30",
  "expected_run_attempt": 1,
  "expected_run_number": 385,
  "governing_method_decision": "DEC-469",
  "governing_protocol_decision": "DEC-470",
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_action_fingerprint_sha256": "585af9488ef0a2f6df018bc86051979fc68d151810a0575cc5091f051f18e763",
  "install_preflight_source_blob_sha": "614784849bca811cbd822cd2243eec19f26163d1",
  "live_order_authorized": false,
  "next_gate": "APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2023_RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC606",
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
  "repository_mutation_authorized": true,
  "rerun_authorized": false,
  "retry_authorized": false,
  "run_386_or_later_authorized": false,
  "runtime_authorization_installed": false,
  "runtime_gate_active": false,
  "source_authorization_protected_history_access_authorized": true,
  "source_preflight_artifact_digest": "sha256:0cc56948730d68dc76f21fdc5d99dad97218640f3ddabd62b77062d1acb0e00b",
  "source_preflight_artifact_id": 11513856300,
  "source_preflight_canonical_sha256": "85c8ac47a4e98d296b4423be1dd551286f82187dc5ec1f0c4c9eadf2fd316599",
  "source_preflight_decision": "DEC-605",
  "source_preflight_expected_head_sha": "81ffd195079d853d7bcd7a49ac34720d563f1a49",
  "source_preflight_fingerprint_sha256": "08d7d79adb7f1fabbe156851923adb4f1f907f2dacd54ddbd82e33063116de76",
  "source_preflight_workflow_head_sha": "81ffd195079d853d7bcd7a49ac34720d563f1a49",
  "source_preflight_workflow_run_id": 37691460323,
  "stage": "ANNUAL_CATALOGUE_2023_RUNTIME_AUTHORIZATION_INSTALL_ACTION_READY",
  "strategy_v1_synthesis_authorized": false,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2023-runtime-authorization-install-action-v1"
}'''

def _action() -> dict[str, object]:
    value = json.loads(ACTION_JSON)
    assert isinstance(value, dict)
    return value

class AnnualPatternCatalogue2023RuntimeAuthorizationInstallReceiptTests(unittest.TestCase):
    def test_sources_pin_concrete_dec606_action(self) -> None:
        value = validate_2023_runtime_authorization_install_receipt_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            value["install_action_source_blob_sha"],
            "42477932452d07a445d7c85650a01b3692fa755c",
        )

    def test_receipt_binds_exact_two_file_install_without_dispatch(self) -> None:
        value = review_2023_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py",
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha="cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
            installed_runtime_blob_sha="0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        )
        self.assertIs(validate_2023_runtime_authorization_install_receipt(value), value)
        self.assertEqual(value["decision"], "DEC-607")
        self.assertEqual(value["source_action_workflow_run_id"], 37693786078)
        self.assertEqual(value["source_action_artifact_id"], 11514552382)
        self.assertEqual(
            value["source_action_fingerprint_sha256"],
            "585af9488ef0a2f6df018bc86051979fc68d151810a0575cc5091f051f18e763",
        )
        self.assertEqual(
            value["source_action_canonical_sha256"],
            "927c05ce7d59782a10e148d7345a3a93bedc6587e3acb0632c9dcd531eb262b4",
        )
        self.assertTrue(value["source_authorization_protected_history_access_authorized"])
        self.assertTrue(value["protected_catalogue_segment"])
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["install_action_consumed"])
        self.assertEqual(value["expected_run_number"], 385)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37663157285)
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
        self.assertEqual(
            value["next_gate"],
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2023_DISPATCH_PREFLIGHT",
        )

    def test_changed_file_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "changed-file inventory"):
            review_2023_runtime_authorization_install(
                _action(),
                repository_root=REPOSITORY_ROOT,
                install_commit_sha="c" * 40,
                changed_files=["src/fmp/discovery/annual_pattern_catalogue_runtime.py"],
                installed_gate_blob_sha="cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
                installed_runtime_blob_sha="0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
            )

    def test_receipt_tampering_fails_closed(self) -> None:
        value = review_2023_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py",
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha="cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
            installed_runtime_blob_sha="0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        )
        tampered = copy.deepcopy(value)
        tampered["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            validate_2023_runtime_authorization_install_receipt(tampered)

    def test_cli_is_review_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2023_runtime_authorization_install_receipt.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("review")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn("gh workflow run ", script)

if __name__ == "__main__":
    unittest.main()
