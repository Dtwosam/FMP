from __future__ import annotations

import copy
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2022_runtime_authorization_install_preflight import (
    build_2022_runtime_authorization_install_preflight,
    validate_2022_runtime_authorization_install_preflight,
    validate_2022_runtime_authorization_install_preflight_sources,
)
from fmp.discovery.annual_pattern_catalogue_2022_runtime_authorization_plan import (
    build_2022_runtime_authorization_plan,
)


ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40


def _authorization() -> dict[str, object]:
    return {
        "decision": "DEC-592",
        "authorization_fingerprint_sha256": (
            "5365ca95855d97df7ad28ff7d4e6f5c2ec51183899da7f88048d78b5d381bf54"
        ),
        "annual_segment_label": "2022",
        "expected_run_number": 384,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37531960014,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "dispatch_action_executed": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_385_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "protected_history_access_authorized": False,
        "cross_year_comparison_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "source_preflight_workflow_run_id": 37603215074,
        "source_preflight_artifact_id": 11474170578,
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-594 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2022RuntimeAuthorizationInstallPreflightTests(
    unittest.TestCase
):
    def _plan(self) -> dict[str, object]:
        authorization = _authorization()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2022_runtime_authorization_plan."
            "validate_2022_execution_authorization",
            return_value=authorization,
        ):
            return build_2022_runtime_authorization_plan(
                authorization,
                repository_root=ROOT,
            )

    def _build(
        self,
        authorization: dict[str, object] | None = None,
        plan: dict[str, object] | None = None,
        *,
        main_sha: str = HEAD,
    ) -> dict[str, object]:
        authorization = authorization or _authorization()
        plan = plan or self._plan()
        with patch(
            "fmp.discovery."
            "annual_pattern_catalogue_2022_runtime_authorization_install_preflight."
            "validate_2022_execution_authorization",
            return_value=authorization,
        ):
            return build_2022_runtime_authorization_install_preflight(
                authorization,
                plan,
                repository_root=ROOT,
                main_branch={"name": "main", "commit": {"sha": main_sha}},
                expected_head_sha=HEAD,
            )

    def test_sources_pin_dec592_dec593_and_dormant_targets(self) -> None:
        source = validate_2022_runtime_authorization_install_preflight_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "e68e9f1ee41ca89f0ae3d7758d59b4ce8c5823bb",
        )
        self.assertEqual(
            source["runtime_authorization_plan_source_blob_sha"],
            "d7710ab16dde2eea6b0d93dc6387c6cc489b30d7",
        )

    def test_preflight_is_read_only_and_exact_run384(self) -> None:
        value = self._build()
        self.assertIs(
            validate_2022_runtime_authorization_install_preflight(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-594")
        self.assertEqual(value["source_plan_workflow_run_id"], 37611869958)
        self.assertEqual(value["source_plan_artifact_id"], 11477773270)
        self.assertEqual(
            value["source_plan_artifact_digest"],
            "sha256:ff974250ff9a09069e77f8c61e96649c9318e83dfcccab74e8dfd3dd07fed420",
        )
        self.assertEqual(
            value["source_plan_canonical_sha256"],
            "2ed8681de71e27f9767f75a9e47861044c81c3886639195e412495613acd09fd",
        )
        self.assertEqual(value["expected_run_number"], 384)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37531960014)
        self.assertEqual(value["activation_mutation_file_count"], 2)
        self.assertEqual(
            value["expected_current_runtime_source_blob_sha"],
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        )
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        )
        self.assertEqual(
            value["next_gate"],
            (
                "EXACT_ANNUAL_PATTERN_CATALOGUE_2022_RUNTIME_"
                "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC594"
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
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "run_385_or_later_authorized",
            "next_segment_execution_authorized",
            "protected_history_access_authorized",
            "cross_year_comparison_authorized",
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
            self._build(plan=plan)

    def test_wrong_main_head_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            self._build(main_sha="b" * 40)


if __name__ == "__main__":
    unittest.main()
