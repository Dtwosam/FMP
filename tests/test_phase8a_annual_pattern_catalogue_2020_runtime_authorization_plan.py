from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest
from fmp.discovery.annual_pattern_catalogue_2020_runtime_authorization_plan import (
    build_2020_runtime_authorization_plan,
    validate_2020_runtime_authorization_plan,
    validate_2020_runtime_authorization_plan_sources,
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
        "annual_segment_label": "2020",
        "annual_workflow_dispatch_authorized": True,
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_contract_validated": True,
        "authorization_fingerprint_sha256": "cfd43db91d2703e743132e61540ed95acec11fc9d4f6f89d8a8c011345a95f55",
        "authorization_scope": "2020_run_382_attempt_1_only",
        "broker_mutation_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-568",
        "demo_order_authorized": False,
        "dispatch_action_executed": False,
        "dispatch_command_present": False,
        "execution_preflight_source_blob_sha": "e045b3e82d2f16e870c77b5b107d8d46fcf96f85",
        "expected_run_attempt": 1,
        "expected_run_number": 382,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "live_order_authorized": False,
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_RUNTIME_AUTHORIZATION_PLAN",
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "previous_annual_freeze_evidence_fingerprint_sha256": "6935506f20d6d46054fabed5200ba6cec33ea4f10b00d839cc1cfc7f1b92b918",
        "previous_annual_freeze_run_id": 37310525635,
        "previous_runtime_binding_fingerprint_sha256": "a7063417dfb917f9b9019eb97c9a2803f50b4163ea524ea52c64b28a387720a2",
        "prior_segment_label": "2019",
        "promotion_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "run_383_or_later_authorized": False,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "runtime_source_blob_sha": "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        "source_only_authorization": True,
        "source_preflight_artifact_digest": "sha256:182be0b68d721e3267a84bab37c5a3bcb5c25b84b546ba9565c20b6c2ee1f1b0",
        "source_preflight_artifact_id": 11346985812,
        "source_preflight_canonical_sha256": "597cbe83fccd3770172b54fa2f40a479e65cc6f4a366b541d727ad431fe70a80",
        "source_preflight_decision": "DEC-567",
        "source_preflight_fingerprint_sha256": "bfccf190a7abad8464bafbf96a039305a8034f754fdc7cd05f5825c65398204f",
        "source_preflight_version": "fmp-annual-catalogue-2020-execution-preflight-v1",
        "source_preflight_workflow_head_sha": "35115a69cae452d0afd922549fe41b4b8e404fd7",
        "source_preflight_workflow_run_id": 37313687059,
        "stage": "ANNUAL_CATALOGUE_2020_EXECUTION_AUTHORIZED_RUNTIME_NOT_INSTALLED",
        "strategy_v1_synthesis_authorized": False,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2020-execution-authorization-v1",
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-569 requires the installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2020RuntimeAuthorizationPlanTests(unittest.TestCase):
    def test_sources_pin_authorization_runtime_workflow_and_templates(self) -> None:
        source = validate_2020_runtime_authorization_plan_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "270fea87dd298888f224f605a88e66215ae06911",
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "e045b3e82d2f16e870c77b5b107d8d46fcf96f85",
        )
        self.assertEqual(
            source["current_runtime_source_blob_sha"],
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        )
        self.assertEqual(
            source["dormant_2020_gate_template_blob_sha"],
            "695a50b418da752e1bd37d6302f209033ab611f5",
        )
        self.assertEqual(
            source["dormant_runtime_target_template_blob_sha"],
            "4e124365430672fa63825b272001937c60151644",
        )

    def test_plan_is_dormant_and_exact_run382(self) -> None:
        value = build_2020_runtime_authorization_plan(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
        )
        self.assertIs(validate_2020_runtime_authorization_plan(value), value)
        self.assertEqual(value["decision"], "DEC-569")
        self.assertEqual(value["annual_segment_label"], "2020")
        self.assertEqual(value["expected_run_number"], 382)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(
            value["expected_previous_annual_freeze_run_id"],
            37310525635,
        )
        self.assertEqual(
            value["source_authorization_workflow_run_id"],
            37315889656,
        )
        self.assertEqual(value["source_authorization_artifact_id"], 11346849851)
        self.assertEqual(
            value["source_authorization_artifact_digest"],
            "sha256:a03cd0d85672e8ae760b8490982fe93f541738c68b733860f10bb16caf968308",
        )
        self.assertEqual(
            value["source_authorization_fingerprint_sha256"],
            "cfd43db91d2703e743132e61540ed95acec11fc9d4f6f89d8a8c011345a95f55",
        )
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "695a50b418da752e1bd37d6302f209033ab611f5",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "4e124365430672fa63825b272001937c60151644",
        )
        self.assertTrue(value["plan_source_only"])
        for field in (
            "runtime_authorization_installed",
            "runtime_gate_active",
            "repository_mutation_authorized",
            "annual_workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "next_segment_execution_authorized",
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

    def test_dormant_gate_is_exact_and_later_runs_locked(self) -> None:
        text = (
            REPOSITORY_ROOT
            / "docs/superpowers/templates/"
            "annual_pattern_catalogue_2020_runtime_authorization.py.disabled"
        ).read_text(encoding="utf-8")
        self.assertIn('AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2020"', text)
        self.assertIn("EXPECTED_RUN_NUMBER = 382", text)
        self.assertIn("EXPECTED_RUN_ATTEMPT = 1", text)
        self.assertIn(
            "EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37310525635",
            text,
        )
        self.assertIn("RUN_383_OR_LATER_AUTHORIZED = False", text)
        self.assertIn("TRADING_AUTHORIZED = False", text)
        self.assertIn('"run_383_or_later_authorized"', text)
        self.assertNotIn("gh workflow run ", text)

    def test_runtime_target_adds_only_2020_route_and_preserves_history(self) -> None:
        text = (
            REPOSITORY_ROOT
            / "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2020_authorization.py.disabled"
        ).read_text(encoding="utf-8")
        for needle in (
            "require_2020_execution_authorized",
            'segment == "2020" and effective_run_number == 382',
            "require_2019_execution_authorized",
            'segment == "2019" and effective_run_number == 381',
            "require_2018_execution_authorized",
            'segment == "2018" and effective_run_number == 380',
            "require_2017_execution_authorized",
            'segment == "2017" and effective_run_number == 379',
            "require_2016_execution_authorized",
            'segment == "2016" and effective_run_number == 378',
            "if effective_run_number == 377:",
            "if effective_run_number == 376:",
        ):
            self.assertIn(needle, text)
        self.assertNotIn('segment == "2021"', text)

    def test_refingerprinted_active_authorization_is_rejected(self) -> None:
        tampered = copy.deepcopy(_authorization())
        tampered["runtime_gate_active"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "runtime_gate_active mismatch"):
            build_2020_runtime_authorization_plan(
                tampered,
                repository_root=REPOSITORY_ROOT,
            )


if __name__ == "__main__":
    unittest.main()
