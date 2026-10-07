from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2022_runtime_authorization_install_receipt import (
    review_2022_runtime_authorization_install,
    validate_2022_runtime_authorization_install_receipt,
    validate_2022_runtime_authorization_install_receipt_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

ACTION_JSON = r"""
{
  "action_count": 2,
  "actions": [
    {
      "content_source_blob_sha": "ecb21dc7106e7bd43447f4135c3a696251a75e05",
      "content_source_path": "docs/superpowers/templates/annual_pattern_catalogue_2022_runtime_authorization.py.disabled",
      "expected_result_blob_sha": "ecb21dc7106e7bd43447f4135c3a696251a75e05",
      "expected_target_absent": true,
      "operation": "create",
      "order": 1,
      "target_path": "src/fmp/discovery/annual_pattern_catalogue_2022_runtime_authorization.py"
    },
    {
      "content_source_blob_sha": "f2734c7ea32355b1024d1097812578b23fc4409d",
      "content_source_path": "docs/superpowers/templates/annual_pattern_catalogue_runtime_with_2022_authorization.py.disabled",
      "expected_current_blob_sha": "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
      "expected_result_blob_sha": "f2734c7ea32355b1024d1097812578b23fc4409d",
      "operation": "update",
      "order": 2,
      "target_path": "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
    }
  ],
  "activation_condition": "validated_concrete_dec594_preflight_and_unchanged_runtime_on_exact_main",
  "annual_segment_label": "2022",
  "annual_workflow_dispatch_authorized": false,
  "authorization_basis": "standing_operator_autonomous_build_authorization",
  "broker_mutation_authorized": false,
  "cross_year_comparison_authorized": false,
  "cross_year_result_production_authorized": false,
  "decision": "DEC-595",
  "demo_order_authorized": false,
  "expected_head_sha": "1351125bb903f7d7b636d945c4446ad815a2efb1",
  "expected_run_attempt": 1,
  "expected_run_number": 384,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_action_fingerprint_sha256": "3352e4254ce62247d56c9fd16c9eb6972c3c7210dce7e08d6582f4c46c5e4a51",
  "install_preflight_source_blob_sha": "8d1fce9c947fd7a579a6ab581d605293a02329a3",
  "live_order_authorized": false,
  "next_gate": "APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC595",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "previous_annual_freeze_run_id": 37531960014,
  "promotion_authorized": false,
  "protected_history_access_authorized": false,
  "real_money_authorized": false,
  "replacement_run_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "repository_mutation_authorized": true,
  "rerun_authorized": false,
  "retry_authorized": false,
  "run_385_or_later_authorized": false,
  "runtime_authorization_installed": false,
  "runtime_gate_active": false,
  "source_preflight_artifact_digest": "sha256:17334ae595a45bfb8174b7bcb41cab169b4185064ca33c05a79dcaa548fdafd1",
  "source_preflight_artifact_id": 11480120937,
  "source_preflight_canonical_sha256": "6927206445b32ea2cd8a1e78b0511f70e9815a9204d771712c5976a5d79af4e4",
  "source_preflight_decision": "DEC-594",
  "source_preflight_expected_head_sha": "ae0949d54a55d2a71a7cd78f153c391be0c6ff23",
  "source_preflight_fingerprint_sha256": "56c3ff244ed7ad47a07ab64efbea68e41acb61cfdba24303f2d265a2e690b08c",
  "source_preflight_workflow_head_sha": "ae0949d54a55d2a71a7cd78f153c391be0c6ff23",
  "source_preflight_workflow_run_id": 37616348059,
  "stage": "ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_ACTION_READY",
  "strategy_v1_synthesis_authorized": false,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2022-runtime-authorization-install-action-v1"
}
"""


def _action() -> dict[str, object]:
    value = json.loads(ACTION_JSON)
    assert isinstance(value, dict)
    return value


class AnnualPatternCatalogue2022RuntimeAuthorizationInstallReceiptTests(
    unittest.TestCase
):
    def test_sources_pin_concrete_dec595_action(self) -> None:
        value = validate_2022_runtime_authorization_install_receipt_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            value["install_action_source_blob_sha"],
            "90fbc26b51d50d019e39c467d461bd7ba6b4f22b",
        )

    def test_receipt_binds_exact_two_file_install_without_dispatch(self) -> None:
        value = review_2022_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                (
                    "src/fmp/discovery/"
                    "annual_pattern_catalogue_2022_runtime_authorization.py"
                ),
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha=(
                "ecb21dc7106e7bd43447f4135c3a696251a75e05"
            ),
            installed_runtime_blob_sha=(
                "f2734c7ea32355b1024d1097812578b23fc4409d"
            ),
        )
        self.assertIs(
            validate_2022_runtime_authorization_install_receipt(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-596")
        self.assertEqual(value["source_action_workflow_run_id"], 37618517412)
        self.assertEqual(value["source_action_artifact_id"], 11480463531)
        self.assertEqual(
            value["source_action_fingerprint_sha256"],
            "3352e4254ce62247d56c9fd16c9eb6972c3c7210dce7e08d6582f4c46c5e4a51",
        )
        self.assertEqual(
            value["source_action_canonical_sha256"],
            "2b99a8b914ee01d27902daa626d2ca01e31384e17de1b3a63b99fcbb1c90070c",
        )
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["install_action_consumed"])
        self.assertEqual(value["expected_run_number"], 384)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37531960014)
        for field in (
            "annual_workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
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
        self.assertEqual(
            value["next_gate"],
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2022_DISPATCH_PREFLIGHT",
        )

    def test_changed_file_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "changed-file inventory"):
            review_2022_runtime_authorization_install(
                _action(),
                repository_root=REPOSITORY_ROOT,
                install_commit_sha="c" * 40,
                changed_files=[
                    "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
                ],
                installed_gate_blob_sha=(
                    "ecb21dc7106e7bd43447f4135c3a696251a75e05"
                ),
                installed_runtime_blob_sha=(
                    "f2734c7ea32355b1024d1097812578b23fc4409d"
                ),
            )

    def test_nonconcrete_action_fingerprint_is_rejected(self) -> None:
        action = _action()
        action["install_action_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            ValueError,
            "install action fingerprint mismatch|source action fingerprint mismatch",
        ):
            review_2022_runtime_authorization_install(
                action,
                repository_root=REPOSITORY_ROOT,
                install_commit_sha="c" * 40,
                changed_files=[
                    (
                        "src/fmp/discovery/"
                        "annual_pattern_catalogue_2022_runtime_authorization.py"
                    ),
                    "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
                ],
                installed_gate_blob_sha=(
                    "ecb21dc7106e7bd43447f4135c3a696251a75e05"
                ),
                installed_runtime_blob_sha=(
                    "f2734c7ea32355b1024d1097812578b23fc4409d"
                ),
            )

    def test_receipt_tampering_fails_closed(self) -> None:
        value = review_2022_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                (
                    "src/fmp/discovery/"
                    "annual_pattern_catalogue_2022_runtime_authorization.py"
                ),
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha=(
                "ecb21dc7106e7bd43447f4135c3a696251a75e05"
            ),
            installed_runtime_blob_sha=(
                "f2734c7ea32355b1024d1097812578b23fc4409d"
            ),
        )
        tampered = copy.deepcopy(value)
        tampered["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            validate_2022_runtime_authorization_install_receipt(tampered)

    def test_cli_is_review_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/"
            "phase8a_annual_pattern_catalogue_2022_runtime_authorization_install_receipt.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("review")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
