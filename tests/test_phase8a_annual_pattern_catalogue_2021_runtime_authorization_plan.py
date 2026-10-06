from __future__ import annotations

import copy
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2021_runtime_authorization_plan import (
    build_2021_runtime_authorization_plan,
    validate_2021_runtime_authorization_plan,
    validate_2021_runtime_authorization_plan_sources,
)


ROOT = Path(__file__).resolve().parents[1]


def _authorization() -> dict[str, object]:
    return {
        "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        "annual_segment_label": "2021",
        "annual_workflow_dispatch_authorized": True,
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_contract_validated": True,
        "authorization_fingerprint_sha256": (
            "56226545935b649e24077b1e108e17b865a65bbdbee36fb73a9605d4f766d6d6"
        ),
        "authorization_scope": "2021_run_383_attempt_1_only",
        "broker_mutation_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-581",
        "demo_order_authorized": False,
        "dispatch_action_executed": False,
        "dispatch_command_present": False,
        "execution_preflight_source_blob_sha": (
            "981309374459ed6b99030f66d08ac5fc0e707dcc"
        ),
        "expected_run_attempt": 1,
        "expected_run_number": 383,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "live_order_authorized": False,
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2021_RUNTIME_AUTHORIZATION_PLAN",
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "previous_annual_freeze_evidence_fingerprint_sha256": (
            "53cd4475b2e9f70252bc4962666ce421daf7795d3e78defbb38ec948448e1c3c"
        ),
        "previous_annual_freeze_run_id": 37443770076,
        "previous_runtime_binding_fingerprint_sha256": (
            "ebde4b5ee78421cc2afb4c12c4ff2603b6d01f1990fbfe683aed11d00653a76c"
        ),
        "prior_segment_label": "2020",
        "promotion_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "run_384_or_later_authorized": False,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "runtime_source_blob_sha": "4e124365430672fa63825b272001937c60151644",
        "source_only_authorization": True,
        "source_preflight_artifact_digest": (
            "sha256:f408d6cdd389bb9f25e84d6aec110a502a0ac9d8a1098d92c8709aab879f6f62"
        ),
        "source_preflight_artifact_id": 11407570779,
        "source_preflight_canonical_sha256": (
            "cafb8a5f1e6513e8d9b3896a2275aea78a88853cd8268e676aff58ad637aa69f"
        ),
        "source_preflight_decision": "DEC-580",
        "source_preflight_fingerprint_sha256": (
            "42582ae521d339a1a1df7b46fae7675fd5bce6cc98669bdbaa211d3bd864129e"
        ),
        "source_preflight_version": "fmp-annual-catalogue-2021-execution-preflight-v1",
        "source_preflight_workflow_head_sha": (
            "5b775915dc14c9f14aac34ac8dc98643a24841d8"
        ),
        "source_preflight_workflow_run_id": 37452889764,
        "stage": "ANNUAL_CATALOGUE_2021_EXECUTION_AUTHORIZED_RUNTIME_NOT_INSTALLED",
        "strategy_v1_synthesis_authorized": False,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2021-execution-authorization-v1",
    }


class AnnualPatternCatalogue2021RuntimeAuthorizationPlanTests(unittest.TestCase):
    def test_sources_pin_installed_runtime_and_dormant_targets(self) -> None:
        source = validate_2021_runtime_authorization_plan_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "3e086e82201ed0bea85226c115ae7a09e7d95983",
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "981309374459ed6b99030f66d08ac5fc0e707dcc",
        )
        self.assertEqual(
            source["current_runtime_source_blob_sha"],
            "4e124365430672fa63825b272001937c60151644",
        )
        self.assertEqual(
            source["dormant_2021_gate_template_blob_sha"],
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
        )
        self.assertEqual(
            source["dormant_runtime_target_template_blob_sha"],
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        )

    def test_valid_authorization_builds_read_only_dormant_plan(self) -> None:
        value = build_2021_runtime_authorization_plan(
            _authorization(),
            repository_root=ROOT,
        )
        self.assertIs(validate_2021_runtime_authorization_plan(value), value)
        self.assertEqual(value["decision"], "DEC-582")
        self.assertEqual(value["annual_segment_label"], "2021")
        self.assertEqual(value["expected_run_number"], 383)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(
            value["expected_previous_annual_freeze_run_id"],
            37443770076,
        )
        self.assertEqual(
            value["source_authorization_workflow_run_id"],
            37460105363,
        )
        self.assertEqual(
            value["source_authorization_artifact_id"],
            11411376869,
        )
        self.assertEqual(
            value["source_authorization_fingerprint_sha256"],
            "56226545935b649e24077b1e108e17b865a65bbdbee36fb73a9605d4f766d6d6",
        )
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        )
        self.assertFalse(value["runtime_authorization_installed"])
        self.assertFalse(value["runtime_gate_active"])
        self.assertFalse(value["repository_mutation_authorized"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertTrue(value["plan_source_only"])
        self.assertEqual(
            value["next_gate"],
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2021_RUNTIME_"
            "AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC582",
        )

    def test_wrong_run_number_is_rejected(self) -> None:
        value = copy.deepcopy(_authorization())
        value["expected_run_number"] = 384
        with self.assertRaisesRegex(ValueError, "DEC-581 authorization fingerprint mismatch"):
            build_2021_runtime_authorization_plan(value, repository_root=ROOT)

    def test_wrong_authorization_fingerprint_is_rejected(self) -> None:
        value = copy.deepcopy(_authorization())
        value["authorization_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "DEC-581 authorization fingerprint mismatch"):
            build_2021_runtime_authorization_plan(value, repository_root=ROOT)

    def test_current_runtime_has_no_2021_route_and_target_gate_is_absent(self) -> None:
        runtime = (
            ROOT / "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn(
            "annual_pattern_catalogue_2021_runtime_authorization",
            runtime,
        )
        self.assertNotIn('segment == "2021"', runtime)
        self.assertFalse(
            (
                ROOT
                / "src/fmp/discovery/"
                "annual_pattern_catalogue_2021_runtime_authorization.py"
            ).exists()
        )

    def test_dormant_runtime_preserves_2020_and_adds_only_2021_route(self) -> None:
        target = (
            ROOT
            / "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2021_authorization.py.disabled"
        ).read_text(encoding="utf-8")
        self.assertIn("require_2021_execution_authorized", target)
        self.assertIn(
            'segment == "2021" and effective_run_number == 383',
            target,
        )
        self.assertIn("require_2020_execution_authorized", target)
        self.assertIn(
            'segment == "2020" and effective_run_number == 382',
            target,
        )

    def test_cli_is_plan_only(self) -> None:
        script = (
            ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2021_runtime_authorization_plan.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("install")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
