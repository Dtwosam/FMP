from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2017_runtime_authorization_install_receipt import (
    review_2017_runtime_authorization_install,
    validate_2017_runtime_authorization_install_receipt,
    validate_2017_runtime_authorization_install_receipt_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _fingerprint(value: dict[str, object]) -> str:
    return hashlib.sha256(
        (
            json.dumps(
                value,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    ).hexdigest()


def _action() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-538",
        "version": "fmp-annual-catalogue-2017-runtime-authorization-install-action-v1",
        "install_preflight_source_blob_sha": "446fb95265ee222aa40ffa3f11ef869a1ede8090",
        "source_preflight_decision": "DEC-537",
        "source_preflight_workflow_run_id": 37215789401,
        "source_preflight_workflow_head_sha": "f8a8de09adc4b64b84b2129eacbc38d0eb00e645",
        "source_preflight_artifact_id": 11308490990,
        "source_preflight_artifact_digest": (
            "sha256:892512ac79d2b372372871a143d887f01e5c96d9ed60ea8243f1cbfb4b7cc6ea"
        ),
        "source_preflight_fingerprint_sha256": "1" * 64,
        "stage": "ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_INSTALL_ACTION_READY",
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "activation_condition": (
            "validated_concrete_dec537_preflight_and_unchanged_runtime_on_exact_main"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "source_preflight_expected_head_sha": (
            "f8a8de09adc4b64b84b2129eacbc38d0eb00e645"
        ),
        "expected_head_sha": "b" * 40,
        "annual_segment_label": "2017",
        "expected_run_number": 379,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37206992367,
        "action_count": 2,
        "actions": [
            {
                "order": 1,
                "operation": "create",
                "target_path": (
                    "src/fmp/discovery/"
                    "annual_pattern_catalogue_2017_runtime_authorization.py"
                ),
                "expected_target_absent": True,
                "content_source_path": (
                    "docs/superpowers/templates/"
                    "annual_pattern_catalogue_2017_runtime_authorization.py.disabled"
                ),
                "content_source_blob_sha": (
                    "c1853eeec55ee98b3155a6054f07cf360793ba9b"
                ),
                "expected_result_blob_sha": (
                    "c1853eeec55ee98b3155a6054f07cf360793ba9b"
                ),
            },
            {
                "order": 2,
                "operation": "update",
                "target_path": (
                    "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
                ),
                "expected_current_blob_sha": (
                    "b564f5a26fdef146fc6080962e7c4762b0b5949a"
                ),
                "content_source_path": (
                    "docs/superpowers/templates/"
                    "annual_pattern_catalogue_runtime_with_2017_authorization.py.disabled"
                ),
                "content_source_blob_sha": (
                    "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"
                ),
                "expected_result_blob_sha": (
                    "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"
                ),
            },
        ],
        "repository_mutation_authorized": True,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "annual_workflow_dispatch_authorized": False,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "next_segment_execution_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": (
            "APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2017_"
            "RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC538"
        ),
    }
    value["install_action_fingerprint_sha256"] = _fingerprint(value)
    return value


class AnnualPatternCatalogue2017RuntimeAuthorizationInstallReceiptTests(
    unittest.TestCase
):
    def test_sources_pin_concrete_dec538_action(self) -> None:
        value = validate_2017_runtime_authorization_install_receipt_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            value["install_action_source_blob_sha"],
            "b6fd22c5eca66ca373d0479e63af51cd39068ed9",
        )

    def test_receipt_binds_exact_two_file_install_without_dispatch(self) -> None:
        value = review_2017_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                (
                    "src/fmp/discovery/"
                    "annual_pattern_catalogue_2017_runtime_authorization.py"
                ),
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha=(
                "c1853eeec55ee98b3155a6054f07cf360793ba9b"
            ),
            installed_runtime_blob_sha=(
                "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"
            ),
        )
        self.assertIs(
            validate_2017_runtime_authorization_install_receipt(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-539")
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["install_action_consumed"])
        self.assertEqual(value["expected_run_number"], 379)
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_changed_file_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "changed-file inventory"):
            review_2017_runtime_authorization_install(
                _action(),
                repository_root=REPOSITORY_ROOT,
                install_commit_sha="c" * 40,
                changed_files=[
                    "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
                ],
                installed_gate_blob_sha=(
                    "c1853eeec55ee98b3155a6054f07cf360793ba9b"
                ),
                installed_runtime_blob_sha=(
                    "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"
                ),
            )

    def test_receipt_tampering_fails_closed(self) -> None:
        value = review_2017_runtime_authorization_install(
            _action(),
            repository_root=REPOSITORY_ROOT,
            install_commit_sha="c" * 40,
            changed_files=[
                (
                    "src/fmp/discovery/"
                    "annual_pattern_catalogue_2017_runtime_authorization.py"
                ),
                "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
            ],
            installed_gate_blob_sha=(
                "c1853eeec55ee98b3155a6054f07cf360793ba9b"
            ),
            installed_runtime_blob_sha=(
                "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"
            ),
        )
        tampered = copy.deepcopy(value)
        tampered["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            validate_2017_runtime_authorization_install_receipt(tampered)


if __name__ == "__main__":
    unittest.main()
