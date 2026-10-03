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


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "c" * 40
RUN376_ID = 666666
RUN377_ID = 777777


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _preflight() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-523",
        "version": "fmp-annual-catalogue-2017-execution-preflight-v1",
        "runtime_binding_source_blob_sha": "b186c8049b045761ccd0f693feaf7637a4807e53",
        "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        "annual_workflow_run_count": 3,
        "failed_first_run_id": 37126711695,
        "successful_2015_run_id": RUN376_ID,
        "successful_2015_run_number": 376,
        "successful_2015_run_attempt": 1,
        "successful_2015_run_head_sha": "a" * 40,
        "successful_2016_run_id": RUN377_ID,
        "successful_2016_run_number": 377,
        "successful_2016_run_attempt": 1,
        "successful_2016_run_head_sha": "b" * 40,
        "source_runtime_binding_decision": "DEC-522",
        "source_runtime_binding_version": (
            "fmp-annual-catalogue-2016-run377-evidence-review-v1"
        ),
        "source_runtime_binding_fingerprint_sha256": "1" * 64,
        "stage": (
            "ANNUAL_CATALOGUE_2017_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": HEAD,
        "annual_segment_label": "2017",
        "prior_segment_required": True,
        "prior_segment_label": "2016",
        "previous_annual_freeze_run_id": RUN377_ID,
        "previous_runtime_binding_fingerprint_sha256": "1" * 64,
        "previous_annual_freeze_evidence_fingerprint_sha256": "2" * 64,
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
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2017_EXECUTION_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


def _refingerprint(value: dict[str, object]) -> None:
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(unsigned)
    ).hexdigest()


class AnnualPatternCatalogue2017ExecutionAuthorizationTests(unittest.TestCase):
    def test_sources_pin_dec523_and_corrected_workflow(self) -> None:
        source = validate_2017_execution_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "e800a24b6ab50fdd11ff3c907fe0cc5d647beff9",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_exact_preflight_yields_source_only_run378_authorization(self) -> None:
        value = build_2017_execution_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
        )
        self.assertIs(validate_2017_execution_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-524")
        self.assertEqual(value["authorization_scope"], "2017_run_378_attempt_1_only")
        self.assertEqual(value["annual_segment_label"], "2017")
        self.assertEqual(value["previous_annual_freeze_run_id"], RUN377_ID)
        self.assertEqual(value["expected_run_number"], 378)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertTrue(value["authorization_contract_validated"])
        self.assertFalse(value["runtime_authorization_installed"])
        self.assertFalse(value["runtime_gate_active"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertTrue(value["source_only_authorization"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_wrong_run_number_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["expected_next_run_number"] = 379
        _refingerprint(preflight)
        with self.assertRaisesRegex(ValueError, "expected_next_run_number mismatch"):
            build_2017_execution_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
            )

    def test_refingerprinted_runtime_activation_tamper_is_rejected(self) -> None:
        value = build_2017_execution_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
        )
        tampered = copy.deepcopy(value)
        tampered["runtime_gate_active"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "runtime_gate_active mismatch"):
            validate_2017_execution_authorization(tampered)

    def test_refingerprinted_later_segment_authority_tamper_is_rejected(self) -> None:
        value = build_2017_execution_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
        )
        tampered = copy.deepcopy(value)
        tampered["next_segment_execution_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "next_segment_execution_authorized mismatch",
        ):
            validate_2017_execution_authorization(tampered)

    def test_cli_is_authorize_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2017_execution_authorization.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("authorize")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
