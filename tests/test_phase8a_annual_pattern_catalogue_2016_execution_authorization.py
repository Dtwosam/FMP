from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2016_execution_authorization import (
    build_2016_execution_authorization,
    validate_2016_execution_authorization,
    validate_2016_execution_authorization_sources,
)


HEAD = "c" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _preflight() -> dict[str, object]:
    return {
        "decision": "DEC-503",
        "version": "fmp-annual-catalogue-2016-execution-preflight-v1",
        "runtime_binding_source_blob_sha": "505e9dcbfc518e7fc00b603cafef44077d105cfa",
        "runtime_source_blob_sha": "ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b",
        "active_workflow_blob_sha": "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        "annual_workflow_run_count": 2,
        "failed_first_run_id": 37126711695,
        "successful_2015_run_id": 424242,
        "successful_2015_run_number": 2,
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
        "expected_next_run_number": 3,
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
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_AUTHORIZATION_BEFORE_RUN"
        ),
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-504 requires the 2016 preflight source state",
)
class AnnualPatternCatalogue2016ExecutionAuthorizationTests(unittest.TestCase):
    def test_sources_pin_preflight_runtime_and_workflow(self) -> None:
        source = validate_2016_execution_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "00b0df00f15e1d983c799e8991a88e03e010d2e3",
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            "ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        )

    def test_authorization_receipt_is_scoped_but_runtime_inactive(self) -> None:
        value = build_2016_execution_authorization(
            _preflight(),
            repository_root=Path("."),
        )
        self.assertIs(validate_2016_execution_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-504")
        self.assertEqual(
            value["authorization_basis"],
            "standing_operator_autonomous_build_authorization",
        )
        self.assertEqual(value["annual_segment_label"], "2016")
        self.assertEqual(value["prior_segment_label"], "2015")
        self.assertEqual(value["previous_annual_freeze_run_id"], 424242)
        self.assertEqual(value["expected_run_number"], 3)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertTrue(value["authorization_contract_validated"])
        self.assertFalse(value["runtime_authorization_installed"])
        self.assertFalse(value["runtime_gate_active"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_refingerprinted_runtime_activation_tamper_is_rejected(self) -> None:
        value = build_2016_execution_authorization(
            _preflight(),
            repository_root=Path("."),
        )
        tampered = copy.deepcopy(value)
        tampered["runtime_gate_active"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "runtime_gate_active must remain false",
        ):
            validate_2016_execution_authorization(tampered)

    def test_wrong_preflight_run_number_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["expected_next_run_number"] = 4
        with self.assertRaisesRegex(ValueError, "next run number mismatch"):
            build_2016_execution_authorization(
                preflight,
                repository_root=Path("."),
            )

    def test_cli_is_authorize_only_and_has_no_dispatch_surface(self) -> None:
        script = Path(
            "scripts/phase8a_annual_pattern_catalogue_2016_execution_authorization.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("authorize")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
