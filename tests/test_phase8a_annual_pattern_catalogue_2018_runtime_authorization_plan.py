from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2018_runtime_authorization_plan import (
    build_2018_runtime_authorization_plan,
    validate_2018_runtime_authorization_plan,
    validate_2018_runtime_authorization_plan_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _authorization() -> dict[str, object]:
    return {
        "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        "annual_segment_label": "2018",
        "annual_workflow_dispatch_authorized": True,
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_contract_validated": True,
        "authorization_fingerprint_sha256": "34fe76b3bd30d054853b43f660f996757e8bdb30793c03ad6937cc3078b427a0",
        "authorization_scope": "2018_run_380_attempt_1_only",
        "broker_mutation_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-546",
        "demo_order_authorized": False,
        "dispatch_action_executed": False,
        "dispatch_command_present": False,
        "execution_preflight_source_blob_sha": "ed71113733ae0034d81914d4c0ab37efb5c4ce6e",
        "expected_run_attempt": 1,
        "expected_run_number": 380,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "live_order_authorized": False,
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_RUNTIME_AUTHORIZATION_PLAN",
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "previous_annual_freeze_evidence_fingerprint_sha256": "ed579f80f947f9a04731b4a20e675c98e2101884c874fa385df5999ef419ff8b",
        "previous_annual_freeze_run_id": 37227536041,
        "previous_runtime_binding_fingerprint_sha256": "a454e3eef8a51260cc07f9103a7de0208f5408a18686bb1249ad05e349edd9ae",
        "prior_segment_label": "2017",
        "promotion_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "run_381_or_later_authorized": False,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "runtime_source_blob_sha": "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
        "source_only_authorization": True,
        "source_preflight_artifact_digest": "sha256:36f76bba9cd3cef5fd1b3236f3bc80ad62029edf9c493ce10d946b7bcadf18a4",
        "source_preflight_artifact_id": 11313083318,
        "source_preflight_canonical_sha256": "4bd0f016f8ce968c7bcce2c959daa10f6371926ed3462e763195a32f6814110e",
        "source_preflight_decision": "DEC-545",
        "source_preflight_fingerprint_sha256": "55b9378a78f54a99a9055da1ac0294e73c5e02434fc4ad17d38acea7ac5c6315",
        "source_preflight_version": "fmp-annual-catalogue-2018-execution-preflight-v1",
        "source_preflight_workflow_head_sha": "24fa329cbcf88192cdc19e63173edd55b3aa7eb5",
        "source_preflight_workflow_run_id": 37229319220,
        "stage": "ANNUAL_CATALOGUE_2018_EXECUTION_AUTHORIZED_RUNTIME_NOT_INSTALLED",
        "strategy_v1_synthesis_authorized": False,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2018-execution-authorization-v1",
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-547 requires the installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2018RuntimeAuthorizationPlanTests(unittest.TestCase):
    def test_sources_pin_authorization_runtime_workflow_and_templates(self) -> None:
        source = validate_2018_runtime_authorization_plan_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "c50f1480ae6b39764f75974182830f149fc820fc",
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "ed71113733ae0034d81914d4c0ab37efb5c4ce6e",
        )
        self.assertEqual(
            source["current_runtime_source_blob_sha"],
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
        )
        self.assertEqual(
            source["dormant_2018_gate_template_blob_sha"],
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
        )
        self.assertEqual(
            source["dormant_runtime_target_template_blob_sha"],
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        )

    def test_plan_is_dormant_and_exact_run380(self) -> None:
        value = build_2018_runtime_authorization_plan(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
        )
        self.assertIs(validate_2018_runtime_authorization_plan(value), value)
        self.assertEqual(value["decision"], "DEC-547")
        self.assertEqual(value["annual_segment_label"], "2018")
        self.assertEqual(value["expected_run_number"], 380)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(
            value["expected_previous_annual_freeze_run_id"],
            37227536041,
        )
        self.assertEqual(value["source_authorization_workflow_run_id"], 37229862532)
        self.assertEqual(value["source_authorization_artifact_id"], 11313482812)
        self.assertEqual(
            value["source_authorization_artifact_digest"],
            "sha256:79e9bd2485160dd59fbb88a2d50f32a52b6cfd573f80555a8716fde4ea18c71e",
        )
        self.assertEqual(
            value["source_authorization_fingerprint_sha256"],
            "34fe76b3bd30d054853b43f660f996757e8bdb30793c03ad6937cc3078b427a0",
        )
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "410180c34a9e3500bbbb42310a5253b993ac7785",
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
            "annual_pattern_catalogue_2018_runtime_authorization.py.disabled"
        ).read_text(encoding="utf-8")
        self.assertIn('AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2018"', text)
        self.assertIn("EXPECTED_RUN_NUMBER = 380", text)
        self.assertIn("EXPECTED_RUN_ATTEMPT = 1", text)
        self.assertIn(
            "EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37227536041",
            text,
        )
        self.assertIn("RUN_381_OR_LATER_AUTHORIZED = False", text)
        self.assertIn("TRADING_AUTHORIZED = False", text)
        self.assertNotIn("gh workflow run ", text)

    def test_runtime_target_adds_only_2018_route_and_preserves_history(self) -> None:
        text = (
            REPOSITORY_ROOT
            / "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2018_authorization.py.disabled"
        ).read_text(encoding="utf-8")
        self.assertIn("require_2018_execution_authorized", text)
        self.assertIn(
            'segment == "2018" and effective_run_number == 380',
            text,
        )
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
        self.assertNotIn('segment == "2019"', text)

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
            build_2018_runtime_authorization_plan(
                tampered,
                repository_root=REPOSITORY_ROOT,
            )


if __name__ == "__main__":
    unittest.main()
