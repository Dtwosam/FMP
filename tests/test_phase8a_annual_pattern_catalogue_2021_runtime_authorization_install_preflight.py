from __future__ import annotations

import copy
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2021_runtime_authorization_install_preflight import (
    build_2021_runtime_authorization_install_preflight,
    validate_2021_runtime_authorization_install_preflight,
    validate_2021_runtime_authorization_install_preflight_sources,
)
from fmp.discovery.annual_pattern_catalogue_2021_runtime_authorization_plan import (
    build_2021_runtime_authorization_plan,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40


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
        "prior_segment_label": "2021",
        "promotion_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "run_384_or_later_authorized": False,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "runtime_source_blob_sha": "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
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


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-583 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2021RuntimeAuthorizationInstallPreflightTests(
    unittest.TestCase
):
    def _plan(self) -> dict[str, object]:
        return build_2021_runtime_authorization_plan(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
        )

    def test_sources_pin_dec568_dec569_and_dormant_targets(self) -> None:
        source = validate_2021_runtime_authorization_install_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "3e086e82201ed0bea85226c115ae7a09e7d95983",
        )
        self.assertEqual(
            source["runtime_authorization_plan_source_blob_sha"],
            "de1643991d85cd63e5505401b871e3c02315e0e9",
        )

    def test_preflight_is_read_only_and_exact_run383(self) -> None:
        value = build_2021_runtime_authorization_install_preflight(
            _authorization(),
            self._plan(),
            repository_root=REPOSITORY_ROOT,
            main_branch={"name": "main", "commit": {"sha": HEAD}},
            expected_head_sha=HEAD,
        )
        self.assertIs(
            validate_2021_runtime_authorization_install_preflight(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-583")
        self.assertEqual(value["source_plan_workflow_run_id"], 37473293705)
        self.assertEqual(value["source_plan_artifact_id"], 11416884894)
        self.assertEqual(
            value["source_plan_artifact_digest"],
            "sha256:cfc8580df9318eeebfdae9e446fa92603e5f2e408ec0066a05945845654743b0",
        )
        self.assertEqual(
            value["source_plan_canonical_sha256"],
            "ea0244c3ef60cfa21dc90567faeff680bca856afc68acc96e9e74c19fafd54f1",
        )
        self.assertEqual(value["expected_run_number"], 383)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37443770076)
        self.assertEqual(value["activation_mutation_file_count"], 2)
        self.assertEqual(
            value["expected_current_runtime_source_blob_sha"],
            "4e124365430672fa63825b272001937c60151644",
        )
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        )
        self.assertEqual(
            value["next_gate"],
            (
                "EXACT_ANNUAL_PATTERN_CATALOGUE_2021_RUNTIME_"
                "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC583"
            ),
        )
        self.assertTrue(value["authorization_contract_validated"])
        self.assertTrue(value["runtime_plan_validated"])
        self.assertTrue(value["runtime_install_preflight_ready"])
        self.assertTrue(value["preflight_read_only"])
        for field in (
            "repository_mutation_authorized",
            "runtime_authorization_installed",
            "runtime_gate_active",
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

    def test_plan_mutation_authority_tamper_is_rejected(self) -> None:
        plan = copy.deepcopy(self._plan())
        plan["repository_mutation_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "repository_mutation_authorized mismatch",
        ):
            build_2021_runtime_authorization_install_preflight(
                _authorization(),
                plan,
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": HEAD}},
                expected_head_sha=HEAD,
            )

    def test_wrong_main_head_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2021_runtime_authorization_install_preflight(
                _authorization(),
                self._plan(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
