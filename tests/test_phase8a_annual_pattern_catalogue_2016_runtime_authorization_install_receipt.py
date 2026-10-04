from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2016_execution_authorization import (
    build_2016_execution_authorization,
)
from fmp.discovery.annual_pattern_catalogue_2016_runtime_authorization_install_action import (
    compile_2016_runtime_authorization_install_action,
)
from fmp.discovery.annual_pattern_catalogue_2016_runtime_authorization_install_preflight import (
    build_2016_runtime_authorization_install_preflight,
)
from fmp.discovery.annual_pattern_catalogue_2016_runtime_authorization_install_receipt import (
    review_2016_runtime_authorization_install,
    validate_2016_runtime_authorization_install_receipt,
    validate_2016_runtime_authorization_install_receipt_sources,
)


HEAD = "c" * 40
INSTALL_COMMIT = "d" * 40
GATE_BLOB = "4bb008eedc2ca0676cf25dd3cfcebba5eac0eaff"
RUNTIME_BLOB = "b564f5a26fdef146fc6080962e7c4762b0b5949a"
GATE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2016_runtime_authorization.py"
)
RUNTIME_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"


def _source_preflight() -> dict[str, object]:
    return {
        "decision": "DEC-503",
        "version": "fmp-annual-catalogue-2016-execution-preflight-v1",
        "runtime_binding_source_blob_sha": "400e9715a6e3b2dab413ce2ecff0fbce8c46f6b0",
        "runtime_source_blob_sha": "f1fa50e7c862354931d919fe7da241de863f6834",
        "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        "annual_workflow_run_count": 3,
        "failed_first_run_id": 37126711695,
        "successful_2015_run_id": 424242,
        "successful_2015_run_number": 377,
        "successful_2015_run_attempt": 1,
        "successful_2015_run_head_sha": "b" * 40,
        "stage": (
            "ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": HEAD,
        "annual_segment_label": "2016",
        "prior_segment_required": True,
        "prior_segment_label": "2015",
        "previous_annual_freeze_run_id": 424242,
        "previous_runtime_binding_fingerprint": "1" * 64,
        "previous_runtime_freeze_fingerprint": "2" * 64,
        "previous_annual_freeze_evidence_fingerprint": "3" * 64,
        "expected_next_run_number": 378,
        "expected_next_run_attempt": 1,
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
        "preflight_read_only": True,
        "next_gate": "ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_AUTHORIZATION_BEFORE_RUN",
    }


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _install_action() -> dict[str, object]:
    authorization = build_2016_execution_authorization(
        _source_preflight(),
        repository_root=Path("."),
    )
    preflight = build_2016_runtime_authorization_install_preflight(
        authorization,
        repository_root=Path("."),
        main_branch=_main(),
        expected_head_sha=HEAD,
    )
    return compile_2016_runtime_authorization_install_action(
        preflight,
        repository_root=Path("."),
        main_branch=_main(),
        expected_head_sha=HEAD,
    )


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-508 requires the future 2016 install-action source state",
)
class AnnualPatternCatalogue2016RuntimeAuthorizationInstallReceiptTests(
    unittest.TestCase
):
    def test_sources_pin_exact_dec507(self) -> None:
        source = validate_2016_runtime_authorization_install_receipt_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["install_action_source_blob_sha"],
            "0545f0474bdead4e479c07b9af889db842bf00dd",
        )

    def test_exact_two_file_install_yields_dispatch_locked_receipt(self) -> None:
        value = review_2016_runtime_authorization_install(
            _install_action(),
            repository_root=Path("."),
            install_commit_sha=INSTALL_COMMIT,
            changed_files=[GATE_PATH, RUNTIME_PATH],
            installed_gate_blob_sha=GATE_BLOB,
            installed_runtime_blob_sha=RUNTIME_BLOB,
        )
        self.assertIs(
            validate_2016_runtime_authorization_install_receipt(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-508")
        self.assertEqual(value["changed_file_count"], 2)
        self.assertTrue(value["install_action_consumed"])
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_artifact_read_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["historical_result_production_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_extra_changed_file_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "changed-file inventory mismatch",
        ):
            review_2016_runtime_authorization_install(
                _install_action(),
                repository_root=Path("."),
                install_commit_sha=INSTALL_COMMIT,
                changed_files=[GATE_PATH, RUNTIME_PATH, "unexpected"],
                installed_gate_blob_sha=GATE_BLOB,
                installed_runtime_blob_sha=RUNTIME_BLOB,
            )

    def test_wrong_runtime_blob_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "installed runtime blob mismatch"):
            review_2016_runtime_authorization_install(
                _install_action(),
                repository_root=Path("."),
                install_commit_sha=INSTALL_COMMIT,
                changed_files=[GATE_PATH, RUNTIME_PATH],
                installed_gate_blob_sha=GATE_BLOB,
                installed_runtime_blob_sha="0" * 40,
            )

    def test_refingerprinted_dispatch_authority_tamper_is_rejected(self) -> None:
        value = review_2016_runtime_authorization_install(
            _install_action(),
            repository_root=Path("."),
            install_commit_sha=INSTALL_COMMIT,
            changed_files=[GATE_PATH, RUNTIME_PATH],
            installed_gate_blob_sha=GATE_BLOB,
            installed_runtime_blob_sha=RUNTIME_BLOB,
        )
        tampered = copy.deepcopy(value)
        tampered["annual_workflow_dispatch_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("receipt_fingerprint_sha256", None)
        tampered["receipt_fingerprint_sha256"] = hashlib.sha256(
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
            "annual_workflow_dispatch_authorized must remain false",
        ):
            validate_2016_runtime_authorization_install_receipt(tampered)

    def test_cli_is_review_only(self) -> None:
        script = Path(
            "scripts/"
            "phase8a_annual_pattern_catalogue_2016_runtime_authorization_install_receipt.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("review")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
