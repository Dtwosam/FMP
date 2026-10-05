from __future__ import annotations

import copy
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2019_runtime_authorization_install_preflight import (
    build_2019_runtime_authorization_install_preflight,
    validate_2019_runtime_authorization_install_preflight,
    validate_2019_runtime_authorization_install_preflight_sources,
)
from fmp.discovery.annual_pattern_catalogue_2019_runtime_authorization_plan import (
    build_2019_runtime_authorization_plan,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40


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
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2019_RUNTIME_AUTHORIZATION_PLAN",
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
        "run_382_or_later_authorized": False,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "runtime_source_blob_sha": "410180c34a9e3500bbbb42310a5253b993ac7785",
        "source_only_authorization": True,
        "source_preflight_artifact_digest": "sha256:09be3f1d11e77ab6da407a67346a6ff4d4ce631f4acb6265575da6db64eeb202",
        "source_preflight_artifact_id": 11317461212,
        "source_preflight_canonical_sha256": "d55962b414ffa76cfa6c30ab5c717b540b1dbb91612f7e8cc993c08e036367db",
        "source_preflight_decision": "DEC-556",
        "source_preflight_fingerprint_sha256": "3d311b8d8d387aca00f079bdab6b0531cf17aefc36913165cfb5eb265ad50421",
        "source_preflight_version": "fmp-annual-catalogue-2019-execution-preflight-v1",
        "source_preflight_workflow_head_sha": "9fa3446b389cbbe1c8429968032ae573198e78b2",
        "source_preflight_workflow_run_id": 37240728378,
        "stage": "ANNUAL_CATALOGUE_2019_EXECUTION_AUTHORIZED_RUNTIME_NOT_INSTALLED",
        "strategy_v1_synthesis_authorized": False,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2019-execution-authorization-v1",
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-559 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2019RuntimeAuthorizationInstallPreflightTests(
    unittest.TestCase
):
    def _plan(self) -> dict[str, object]:
        return build_2019_runtime_authorization_plan(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
        )

    def test_sources_pin_dec557_dec558_and_dormant_targets(self) -> None:
        source = validate_2019_runtime_authorization_install_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "084fa62c7fd4855fc561038d991e1215df2ff73b",
        )
        self.assertEqual(
            source["runtime_authorization_plan_source_blob_sha"],
            "41e7adba8b5061028d8adc7ef93d1fc02424039e",
        )

    def test_preflight_is_read_only_and_exact_run381(self) -> None:
        value = build_2019_runtime_authorization_install_preflight(
            _authorization(),
            self._plan(),
            repository_root=REPOSITORY_ROOT,
            main_branch={"name": "main", "commit": {"sha": HEAD}},
            expected_head_sha=HEAD,
        )
        self.assertIs(
            validate_2019_runtime_authorization_install_preflight(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-559")
        self.assertEqual(value["source_plan_workflow_run_id"], 37294642532)
        self.assertEqual(value["source_plan_artifact_id"], 11337484835)
        self.assertEqual(
            value["source_plan_artifact_digest"],
            "sha256:7ee0dbfd168a8a63664419cce85e41a65fde46f9e492dbee65868386d74975a8",
        )
        self.assertEqual(
            value["source_plan_canonical_sha256"],
            "5e35a860916137118e6a1ca9d751045373c59ad9e5e0ac373545b20740ccd074",
        )
        self.assertEqual(value["expected_run_number"], 381)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37237817538)
        self.assertEqual(value["activation_mutation_file_count"], 2)
        self.assertEqual(
            value["expected_current_runtime_source_blob_sha"],
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        )
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
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
            build_2019_runtime_authorization_install_preflight(
                _authorization(),
                plan,
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": HEAD}},
                expected_head_sha=HEAD,
            )

    def test_wrong_main_head_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2019_runtime_authorization_install_preflight(
                _authorization(),
                self._plan(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
