from __future__ import annotations

import copy
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2020_runtime_authorization_install_preflight import (
    build_2020_runtime_authorization_install_preflight,
    validate_2020_runtime_authorization_install_preflight,
    validate_2020_runtime_authorization_install_preflight_sources,
)
from fmp.discovery.annual_pattern_catalogue_2020_runtime_authorization_plan import (
    build_2020_runtime_authorization_plan,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40


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
    "DEC-570 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2020RuntimeAuthorizationInstallPreflightTests(
    unittest.TestCase
):
    def _plan(self) -> dict[str, object]:
        return build_2020_runtime_authorization_plan(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
        )

    def test_sources_pin_dec568_dec569_and_dormant_targets(self) -> None:
        source = validate_2020_runtime_authorization_install_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "270fea87dd298888f224f605a88e66215ae06911",
        )
        self.assertEqual(
            source["runtime_authorization_plan_source_blob_sha"],
            "cd420419cb149c23056edfcaf650d4d7e2d3775a",
        )

    def test_preflight_is_read_only_and_exact_run382(self) -> None:
        value = build_2020_runtime_authorization_install_preflight(
            _authorization(),
            self._plan(),
            repository_root=REPOSITORY_ROOT,
            main_branch={"name": "main", "commit": {"sha": HEAD}},
            expected_head_sha=HEAD,
        )
        self.assertIs(
            validate_2020_runtime_authorization_install_preflight(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-570")
        self.assertEqual(value["source_plan_workflow_run_id"], 37318488687)
        self.assertEqual(value["source_plan_artifact_id"], 11349042014)
        self.assertEqual(
            value["source_plan_artifact_digest"],
            "sha256:855375a850fe4e90475f5f5b9dd4d4721fba5bbac6ce8162d3c9d6d3854bbc7f",
        )
        self.assertEqual(
            value["source_plan_canonical_sha256"],
            "794ea5631bee374ec7a2e05c5efcb33e35f008d188114c879f7d2e68be72a7b0",
        )
        self.assertEqual(value["expected_run_number"], 382)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37310525635)
        self.assertEqual(value["activation_mutation_file_count"], 2)
        self.assertEqual(
            value["expected_current_runtime_source_blob_sha"],
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        )
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "695a50b418da752e1bd37d6302f209033ab611f5",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "4e124365430672fa63825b272001937c60151644",
        )
        self.assertEqual(
            value["next_gate"],
            (
                "EXACT_ANNUAL_PATTERN_CATALOGUE_2020_RUNTIME_"
                "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC570"
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
            build_2020_runtime_authorization_install_preflight(
                _authorization(),
                plan,
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": HEAD}},
                expected_head_sha=HEAD,
            )

    def test_wrong_main_head_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2020_runtime_authorization_install_preflight(
                _authorization(),
                self._plan(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
