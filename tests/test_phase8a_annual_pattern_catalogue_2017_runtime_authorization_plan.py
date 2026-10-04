from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2017_runtime_authorization_plan import (
    build_2017_runtime_authorization_plan,
    validate_2017_runtime_authorization_plan,
    validate_2017_runtime_authorization_plan_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _authorization() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-535",
        "version": "fmp-annual-catalogue-2017-execution-authorization-v1",
        "execution_preflight_source_blob_sha": (
            "7e6e6a54d4111a44a68218e551c379fa342d3e27"
        ),
        "runtime_source_blob_sha": (
            "b564f5a26fdef146fc6080962e7c4762b0b5949a"
        ),
        "active_workflow_blob_sha": (
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
        ),
        "source_preflight_decision": "DEC-534",
        "source_preflight_version": (
            "fmp-annual-catalogue-2017-execution-preflight-v2"
        ),
        "source_preflight_workflow_run_id": 37210041270,
        "source_preflight_workflow_head_sha": (
            "23231c82360da824e3b9eedbd4e2a5edcffd0d45"
        ),
        "source_preflight_artifact_id": 11306121033,
        "source_preflight_artifact_digest": (
            "sha256:531c468e36ac80f6c0c24620c14b78d2b2faad869d53be098efe7a2b31425e04"
        ),
        "source_preflight_fingerprint_sha256": "1" * 64,
        "source_preflight_canonical_sha256": "2" * 64,
        "stage": (
            "ANNUAL_CATALOGUE_2017_EXECUTION_AUTHORIZED_"
            "RUNTIME_NOT_INSTALLED"
        ),
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_scope": "2017_run_379_attempt_1_only",
        "annual_segment_label": "2017",
        "prior_segment_label": "2016",
        "previous_annual_freeze_run_id": 37206992367,
        "previous_runtime_binding_fingerprint_sha256": "3" * 64,
        "previous_annual_freeze_evidence_fingerprint_sha256": "4" * 64,
        "expected_run_number": 379,
        "expected_run_attempt": 1,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "authorization_contract_validated": True,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_380_or_later_authorized": False,
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
        "source_only_authorization": True,
        "next_gate": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_RUNTIME_AUTHORIZATION_PLAN"
        ),
    }
    value["authorization_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


class AnnualPatternCatalogue2017RuntimeAuthorizationPlanTests(unittest.TestCase):
    def test_sources_pin_authorization_runtime_workflow_and_templates(self) -> None:
        source = validate_2017_runtime_authorization_plan_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "ef70a0aec215943a2d992a484fd95feb390c6e07",
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "7e6e6a54d4111a44a68218e551c379fa342d3e27",
        )
        self.assertEqual(
            source["current_runtime_source_blob_sha"],
            "b564f5a26fdef146fc6080962e7c4762b0b5949a",
        )
        self.assertEqual(
            source["dormant_2017_gate_template_blob_sha"],
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
        )
        self.assertEqual(
            source["dormant_runtime_target_template_blob_sha"],
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
        )

    def test_plan_is_dormant_and_exact_run379(self) -> None:
        value = build_2017_runtime_authorization_plan(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
        )
        self.assertIs(validate_2017_runtime_authorization_plan(value), value)
        self.assertEqual(value["decision"], "DEC-536")
        self.assertEqual(value["annual_segment_label"], "2017")
        self.assertEqual(value["expected_run_number"], 379)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(
            value["expected_previous_annual_freeze_run_id"],
            37206992367,
        )
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
        )
        self.assertTrue(value["plan_source_only"])
        self.assertFalse(value["runtime_authorization_installed"])
        self.assertFalse(value["runtime_gate_active"])
        self.assertFalse(value["repository_mutation_authorized"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_artifact_read_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["historical_result_production_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_dormant_gate_is_exact_and_later_runs_locked(self) -> None:
        text = (
            REPOSITORY_ROOT
            / "docs/superpowers/templates/"
            "annual_pattern_catalogue_2017_runtime_authorization.py.disabled"
        ).read_text(encoding="utf-8")
        self.assertIn('AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2017"', text)
        self.assertIn("EXPECTED_RUN_NUMBER = 379", text)
        self.assertIn("EXPECTED_RUN_ATTEMPT = 1", text)
        self.assertIn(
            "EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37206992367",
            text,
        )
        self.assertIn("RUN_380_OR_LATER_AUTHORIZED = False", text)
        self.assertIn("TRADING_AUTHORIZED = False", text)
        self.assertNotIn("gh workflow run ", text)

    def test_runtime_target_adds_only_2017_route_and_preserves_history(self) -> None:
        text = (
            REPOSITORY_ROOT
            / "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2017_authorization.py.disabled"
        ).read_text(encoding="utf-8")
        self.assertIn("require_2017_execution_authorized", text)
        self.assertIn(
            'segment == "2017" and effective_run_number == 379',
            text,
        )
        self.assertIn(
            'segment == "2016" and effective_run_number == 378',
            text,
        )
        self.assertIn("if effective_run_number == 377:", text)
        self.assertIn("if effective_run_number == 376:", text)
        self.assertNotIn('segment == "2018"', text)

    def test_refingerprinted_active_authorization_is_rejected(self) -> None:
        authorization = _authorization()
        tampered = copy.deepcopy(authorization)
        tampered["runtime_gate_active"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "runtime_gate_active mismatch"):
            build_2017_runtime_authorization_plan(
                tampered,
                repository_root=REPOSITORY_ROOT,
            )


if __name__ == "__main__":
    unittest.main()
