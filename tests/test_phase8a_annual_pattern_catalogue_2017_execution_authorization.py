from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2017_execution_authorization import (
    build_2017_execution_authorization,
    validate_2017_execution_authorization,
    validate_2017_execution_authorization_sources,
)


HEAD = "23231c82360da824e3b9eedbd4e2a5edcffd0d45"


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _preflight() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-534",
        "version": "fmp-annual-catalogue-2017-execution-preflight-v2",
        "runtime_binding_source_blob_sha": (
            "ad182ce30d32aff985558f3b2fd9370ca1141cc2"
        ),
        "active_workflow_blob_sha": (
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
        ),
        "annual_workflow_run_count": 4,
        "failed_first_run_id": 37126711695,
        "failed_run376_id": 37191637168,
        "successful_2015_run_id": 37198002653,
        "successful_2015_run_number": 377,
        "successful_2015_run_attempt": 1,
        "successful_2015_run_head_sha": (
            "a89db974be9a94481e7ed0990476bc661012f1e4"
        ),
        "successful_2016_run_id": 37206992367,
        "successful_2016_run_number": 378,
        "successful_2016_run_attempt": 1,
        "successful_2016_run_head_sha": (
            "2524fde355349581c9440a172d0384c3cbce31ed"
        ),
        "source_runtime_binding_decision": "DEC-522",
        "source_runtime_binding_version": (
            "fmp-annual-catalogue-2016-run378-evidence-review-v1"
        ),
        "source_runtime_binding_fingerprint_sha256": (
            "c95d28505fab6a8c55c9889ba5da6565be3b63cb98321eea58d26196b60a2b40"
        ),
        "source_runtime_binding_artifact_id": 11305284883,
        "source_runtime_binding_artifact_digest": (
            "sha256:6282a6765f659a5a5801e2b1c8804d0dd23b96c4f235a770cd8e0e6053caab8c"
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2017_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": HEAD,
        "annual_segment_label": "2017",
        "prior_segment_required": True,
        "prior_segment_label": "2016",
        "previous_annual_freeze_run_id": 37206992367,
        "previous_runtime_binding_fingerprint_sha256": (
            "c95d28505fab6a8c55c9889ba5da6565be3b63cb98321eea58d26196b60a2b40"
        ),
        "previous_annual_freeze_evidence_fingerprint_sha256": (
            "01e15f5081523136af12af7ccc443b79c44d102732a31cb9075a29ea67e80b99"
        ),
        "expected_next_run_number": 379,
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
            "ANNUAL_PATTERN_CATALOGUE_2017_EXECUTION_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


class AnnualPatternCatalogue2017ExecutionAuthorizationTests(unittest.TestCase):
    def test_sources_pin_concrete_preflight_runtime_and_workflow(self) -> None:
        source = validate_2017_execution_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "7e6e6a54d4111a44a68218e551c379fa342d3e27",
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            "b564f5a26fdef146fc6080962e7c4762b0b5949a",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_authorization_is_exact_run379_and_runtime_inactive(self) -> None:
        value = build_2017_execution_authorization(
            _preflight(),
            repository_root=Path("."),
        )
        self.assertIs(validate_2017_execution_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-535")
        self.assertEqual(value["annual_segment_label"], "2017")
        self.assertEqual(value["prior_segment_label"], "2016")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37206992367)
        self.assertEqual(value["expected_run_number"], 379)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["source_preflight_workflow_run_id"], 37210041270)
        self.assertEqual(value["source_preflight_artifact_id"], 11306121033)
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertTrue(value["authorization_contract_validated"])
        self.assertTrue(value["source_only_authorization"])
        self.assertFalse(value["runtime_authorization_installed"])
        self.assertFalse(value["runtime_gate_active"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertFalse(value["run_380_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_refingerprinted_runtime_activation_tamper_is_rejected(self) -> None:
        value = build_2017_execution_authorization(
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
            "runtime_gate_active mismatch",
        ):
            validate_2017_execution_authorization(tampered)

    def test_wrong_run_number_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["expected_next_run_number"] = 380
        unsigned = dict(preflight)
        unsigned.pop("preflight_fingerprint_sha256", None)
        preflight["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "expected_next_run_number mismatch",
        ):
            build_2017_execution_authorization(
                preflight,
                repository_root=Path("."),
            )

    def test_current_runtime_has_no_2017_route(self) -> None:
        runtime = Path(
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('segment == "2017"', runtime)
        self.assertNotIn("require_2017_execution_authorized", runtime)


if __name__ == "__main__":
    unittest.main()
