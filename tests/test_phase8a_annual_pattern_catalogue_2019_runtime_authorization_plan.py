from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2019_runtime_authorization_plan import (
    build_2019_runtime_authorization_plan,
    validate_2019_runtime_authorization_plan,
    validate_2019_runtime_authorization_plan_sources,
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
        "annual_segment_label": "2019",
        "annual_workflow_dispatch_authorized": True,
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_contract_validated": True,
        "authorization_fingerprint_sha256": "c785127b20f57210e60ebd681d7b0e48a66f419fa8fbbbdd9cdd8fa560b464f9",
        "authorization_scope": "2019_run_381_attempt_1_only",
        "broker_mutation_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-557",
        "demo_order_authorized": False,
        "dispatch_action_executed": False,
        "dispatch_command_present": False,
        "execution_preflight_source_blob_sha": "a813a8db59927eaf9108e010a5db84f6c6dafa27",
        "expected_run_attempt": 1,
        "expected_run_number": 381,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "live_order_authorized": False,
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_RUNTIME_AUTHORIZATION_PLAN",
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "previous_annual_freeze_evidence_fingerprint_sha256": "355a1e5ca9282300a7a38e24dd3009ebe8470d1f029e62c38860bf710ac80559",
        "previous_annual_freeze_run_id": 37237817538,
        "previous_runtime_binding_fingerprint_sha256": "09950f6bfb577c4abe17a2466e466a08585fbcd05359ad5fa6c4bad16cce5fda",
        "prior_segment_label": "2018",
        "promotion_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "run_381_or_later_authorized": False,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "runtime_source_blob_sha": "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        "source_only_authorization": True,
        "source_preflight_artifact_digest": "sha256:09be3f1d11e77ab6da407a67346a6ff4d4ce631f4acb6265575da6db64eeb202",
        "source_preflight_artifact_id": 11317461212,
        "source_preflight_canonical_sha256": "4bd0f016f8ce968c7bcce2c959daa10f6371926ed3462e763195a32f6814110e",
        "source_preflight_decision": "DEC-556",
        "source_preflight_fingerprint_sha256": "3d311b8d8d387aca00f079bdab6b0531cf17aefc36913165cfb5eb265ad50421",
        "source_preflight_version": "fmp-annual-catalogue-2019-execution-preflight-v1",
        "source_preflight_workflow_head_sha": "9fa3446b389cbbe1c8429968032ae573198e78b2",
        "source_preflight_workflow_run_id": 37240728378,
        "stage": "ANNUAL_CATALOGUE_2018_EXECUTION_AUTHORIZED_RUNTIME_NOT_INSTALLED",
        "strategy_v1_synthesis_authorized": False,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2019-execution-authorization-v1",
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-558 requires the installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2019RuntimeAuthorizationPlanTests(unittest.TestCase):
    def test_sources_pin_authorization_runtime_workflow_and_templates(self) -> None:
        source = validate_2019_runtime_authorization_plan_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "084fa62c7fd4855fc561038d991e1215df2ff73b",
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "a813a8db59927eaf9108e010a5db84f6c6dafa27",
        )
        self.assertEqual(
            source["current_runtime_source_blob_sha"],
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        )
        self.assertEqual(
            source["dormant_2018_gate_template_blob_sha"],
            "3f7f71882195e373940d922a451f426011728063",
        )
        self.assertEqual(
            source["dormant_runtime_target_template_blob_sha"],
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        )

    def test_plan_is_dormant_and_exact_run381(self) -> None:
        value = build_2019_runtime_authorization_plan(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
        )
        self.assertIs(validate_2019_runtime_authorization_plan(value), value)
        self.assertEqual(value["decision"], "DEC-558")
        self.assertEqual(value["annual_segment_label"], "2018")
        self.assertEqual(value["expected_run_number"], 381)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(
            value["expected_previous_annual_freeze_run_id"],
            37237817538,
        )
        self.assertEqual(value["source_authorization_workflow_run_id"], 37241812968)
        self.assertEqual(value["source_authorization_artifact_id"], 11317224241)
        self.assertEqual(
            value["source_authorization_artifact_digest"],
            "sha256:ecdbb57924cf74945e9e8bba12dcaae2d869ef264813ef012d21ba175c5ef52e",
        )
        self.assertEqual(
            value["source_authorization_fingerprint_sha256"],
            "c785127b20f57210e60ebd681d7b0e48a66f419fa8fbbbdd9cdd8fa560b464f9",
        )
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "3f7f71882195e373940d922a451f426011728063",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
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
            "annual_pattern_catalogue_2019_runtime_authorization.py.disabled"
        ).read_text(encoding="utf-8")
        self.assertIn('AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2018"', text)
        self.assertIn("EXPECTED_RUN_NUMBER = 381", text)
        self.assertIn("EXPECTED_RUN_ATTEMPT = 1", text)
        self.assertIn(
            "EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37237817538",
            text,
        )
        self.assertIn("RUN_382_OR_LATER_AUTHORIZED = False", text)
        self.assertIn("TRADING_AUTHORIZED = False", text)
        self.assertNotIn("gh workflow run ", text)

    def test_runtime_target_adds_only_2018_route_and_preserves_history(self) -> None:
        text = (
            REPOSITORY_ROOT
            / "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2019_authorization.py.disabled"
        ).read_text(encoding="utf-8")
        self.assertIn("require_2018_execution_authorized", text)
        self.assertIn(
            'segment == "2019" and effective_run_number == 381',
            text,
        )
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
        self.assertNotIn('segment == "2020"', text)

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
            build_2019_runtime_authorization_plan(
                tampered,
                repository_root=REPOSITORY_ROOT,
            )


if __name__ == "__main__":
    unittest.main()
