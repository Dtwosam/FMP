from __future__ import annotations

import copy
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2018_runtime_authorization_install_preflight import (
    build_2018_runtime_authorization_install_preflight,
    validate_2018_runtime_authorization_install_preflight,
    validate_2018_runtime_authorization_install_preflight_sources,
)
from fmp.discovery.annual_pattern_catalogue_2018_runtime_authorization_plan import (
    build_2018_runtime_authorization_plan,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40


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
    "DEC-548 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2018RuntimeAuthorizationInstallPreflightTests(
    unittest.TestCase
):
    def _plan(self) -> dict[str, object]:
        return build_2018_runtime_authorization_plan(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
        )

    def test_sources_pin_dec546_dec547_and_dormant_targets(self) -> None:
        source = validate_2018_runtime_authorization_install_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "c50f1480ae6b39764f75974182830f149fc820fc",
        )
        self.assertEqual(
            source["runtime_authorization_plan_source_blob_sha"],
            "543752e5ecad05fed0b368170663a9329b0405aa",
        )

    def test_preflight_is_read_only_and_exact_run380(self) -> None:
        value = build_2018_runtime_authorization_install_preflight(
            _authorization(),
            self._plan(),
            repository_root=REPOSITORY_ROOT,
            main_branch={"name": "main", "commit": {"sha": HEAD}},
            expected_head_sha=HEAD,
        )
        self.assertIs(
            validate_2018_runtime_authorization_install_preflight(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-548")
        self.assertEqual(value["source_plan_workflow_run_id"], 37231060551)
        self.assertEqual(value["source_plan_artifact_id"], 11314500352)
        self.assertEqual(
            value["source_plan_artifact_digest"],
            "sha256:633476f0bab6a5e1f3165cab44be176c05c01f955569ff0018cae957006ab56c",
        )
        self.assertEqual(value["expected_run_number"], 380)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37227536041)
        self.assertEqual(value["activation_mutation_file_count"], 2)
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "410180c34a9e3500bbbb42310a5253b993ac7785",
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
            build_2018_runtime_authorization_install_preflight(
                _authorization(),
                plan,
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": HEAD}},
                expected_head_sha=HEAD,
            )

    def test_wrong_main_head_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2018_runtime_authorization_install_preflight(
                _authorization(),
                self._plan(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
