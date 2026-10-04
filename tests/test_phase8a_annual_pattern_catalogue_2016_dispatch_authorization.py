from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2016_dispatch_authorization import (
    build_2016_dispatch_authorization,
    validate_2016_dispatch_authorization,
    validate_2016_dispatch_authorization_sources,
)


HEAD = "e" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _preflight() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-509",
        "version": "fmp-annual-catalogue-2016-dispatch-preflight-v1",
        "install_receipt_source_blob_sha": "7da956910e24e788a2f2a60834c04048a660bc75",
        "runtime_binding_source_blob_sha": "bbb3bba32c3677d3bd971a2744eb93498868433b",
        "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        "annual_workflow_run_count": 3,
        "failed_first_run_id": 37126711695,
        "successful_2015_run_id": 424242,
        "successful_2015_run_number": 377,
        "successful_2015_run_attempt": 1,
        "successful_2015_run_head_sha": "b" * 40,
        "source_install_receipt_decision": "DEC-508",
        "source_install_receipt_version": (
            "fmp-annual-catalogue-2016-runtime-authorization-install-receipt-v1"
        ),
        "source_install_receipt_fingerprint_sha256": "1" * 64,
        "previous_runtime_binding_fingerprint_sha256": "2" * 64,
        "previous_runtime_freeze_fingerprint_sha256": "3" * 64,
        "previous_annual_freeze_evidence_fingerprint_sha256": "4" * 64,
        "stage": (
            "ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_"
            "INSTALLED_RUNTIME_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": HEAD,
        "install_commit_sha": HEAD,
        "annual_segment_label": "2016",
        "prior_segment_label": "2015",
        "previous_annual_freeze_run_id": 424242,
        "expected_run_number": 378,
        "expected_run_attempt": 1,
        "install_action_consumed": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
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
        "dispatch_command_present": False,
        "preflight_read_only": True,
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


def _refingerprint(value: dict[str, object]) -> dict[str, object]:
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(unsigned)
    ).hexdigest()
    return value


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-510 requires the DEC-509 source state",
)
class AnnualPatternCatalogue2016DispatchAuthorizationTests(unittest.TestCase):
    def test_sources_pin_dispatch_preflight_and_workflow(self) -> None:
        source = validate_2016_dispatch_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dispatch_preflight_source_blob_sha"],
            "e4afa2047cba8fbb066c755033e35e9b185c07a9",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_exact_preflight_yields_source_only_run3_authorization(self) -> None:
        value = build_2016_dispatch_authorization(
            _preflight(),
            repository_root=Path("."),
        )
        self.assertIs(validate_2016_dispatch_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-510")
        self.assertEqual(value["annual_segment_label"], "2016")
        self.assertEqual(value["expected_run_number"], 378)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["successful_2015_run_head_sha"], "b" * 40)
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["authorization_contract_validated"])
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["retry_authorized"])
        self.assertFalse(value["fourth_or_later_run_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertTrue(value["source_only_authorization"])

    def test_source_preflight_dispatch_tamper_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["annual_workflow_dispatch_authorized"] = True
        _refingerprint(preflight)
        with self.assertRaisesRegex(
            ValueError,
            "annual_workflow_dispatch_authorized mismatch",
        ):
            build_2016_dispatch_authorization(
                preflight,
                repository_root=Path("."),
            )

    def test_source_preflight_run_number_drift_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["expected_run_number"] = 379
        _refingerprint(preflight)
        with self.assertRaisesRegex(
            ValueError,
            "expected_run_number mismatch",
        ):
            build_2016_dispatch_authorization(
                preflight,
                repository_root=Path("."),
            )

    def test_refingerprinted_later_run_authority_tamper_is_rejected(self) -> None:
        value = build_2016_dispatch_authorization(
            _preflight(),
            repository_root=Path("."),
        )
        tampered = copy.deepcopy(value)
        tampered["fourth_or_later_run_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "fourth_or_later_run_authorized mismatch",
        ):
            validate_2016_dispatch_authorization(tampered)

    def test_cli_is_authorize_only(self) -> None:
        script = Path(
            "scripts/phase8a_annual_pattern_catalogue_2016_dispatch_authorization.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("authorize")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
