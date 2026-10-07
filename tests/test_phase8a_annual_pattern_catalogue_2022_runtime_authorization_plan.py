from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2022_runtime_authorization_plan import (
    build_2022_runtime_authorization_plan,
    validate_2022_runtime_authorization_plan,
    validate_2022_runtime_authorization_plan_sources,
)


ROOT = Path(__file__).resolve().parents[1]
PREINSTALL_SNAPSHOT = os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1"


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
    PREINSTALL_SNAPSHOT,
    "DEC-593 requires installed DEC-592/runtime sources",
)
class AnnualCatalogue2022RuntimeAuthorizationPlanTests(unittest.TestCase):
    def test_sources_pin_templates_and_installed_runtime(self) -> None:
        value = validate_2022_runtime_authorization_plan_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            value["execution_authorization_source_blob_sha"],
            "e68e9f1ee41ca89f0ae3d7758d59b4ce8c5823bb",
        )
        self.assertEqual(
            value["current_runtime_source_blob_sha"],
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        )
        self.assertEqual(
            value["dormant_2022_gate_template_blob_sha"],
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
        )
        self.assertEqual(
            value["dormant_runtime_target_template_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        )

    def test_valid_authorization_builds_dormant_source_only_plan(self) -> None:
        authorization = _authorization()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2022_runtime_authorization_plan."
            "validate_2022_execution_authorization",
            return_value=authorization,
        ):
            value = build_2022_runtime_authorization_plan(
                authorization,
                repository_root=ROOT,
            )
        self.assertIs(validate_2022_runtime_authorization_plan(value), value)
        self.assertEqual(value["decision"], "DEC-593")
        self.assertEqual(value["annual_segment_label"], "2022")
        self.assertEqual(value["expected_run_number"], 384)
        self.assertEqual(value["expected_previous_annual_freeze_run_id"], 37531960014)
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
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
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(value[field], field)

    def test_wrong_run_is_rejected(self) -> None:
        authorization = _authorization()
        authorization["expected_run_number"] = 385
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2022_runtime_authorization_plan."
            "validate_2022_execution_authorization",
            return_value=authorization,
        ):
            with self.assertRaisesRegex(ValueError, "expected run number mismatch"):
                build_2022_runtime_authorization_plan(
                    authorization,
                    repository_root=ROOT,
                )

    def test_cli_is_plan_only(self) -> None:
        text = (
            ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2022_runtime_authorization_plan.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', text)
        self.assertNotIn('subparsers.add_parser("install")', text)
        self.assertNotIn("gh workflow run ", text)


if __name__ == "__main__":
    unittest.main()
