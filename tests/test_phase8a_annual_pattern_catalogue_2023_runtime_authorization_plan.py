from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2023_runtime_authorization_plan import (
    build_2023_runtime_authorization_plan,
    validate_2023_runtime_authorization_plan,
    validate_2023_runtime_authorization_plan_sources,
)


ROOT = Path(__file__).resolve().parents[1]
PREINSTALL_SNAPSHOT = os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1"


def _authorization() -> dict[str, object]:
    return {
        "decision": "DEC-603",
        "authorization_fingerprint_sha256": (
            "dc1f6dc96e4bdbf527ffba49be9df175310389737bd7c70ca945bd260baf3946"
        ),
        "annual_segment_label": "2023",
        "expected_run_number": 385,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37663157285,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "dispatch_action_executed": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_386_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "protected_history_access_authorized": True,
        "protected_catalogue_segment": True,
        "governing_method_decision": "DEC-469",
        "governing_protocol_decision": "DEC-470",
        "protocol_full_collection_catalogue_use_authorized": True,
        "protocol_2023_2026_catalogue_use_authorized": True,
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
        "source_preflight_workflow_run_id": 37678209687,
        "source_preflight_artifact_id": 11507656390,
    }


@unittest.skipIf(
    PREINSTALL_SNAPSHOT,
    "DEC-604 requires installed DEC-603/runtime sources",
)
class AnnualCatalogue2023RuntimeAuthorizationPlanTests(unittest.TestCase):
    def test_sources_pin_templates_and_installed_runtime(self) -> None:
        value = validate_2023_runtime_authorization_plan_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            value["execution_authorization_source_blob_sha"],
            "2c4292abadbffb9dd87edaab67d9e32783facae7",
        )
        self.assertEqual(
            value["execution_preflight_source_blob_sha"],
            "d7e0823bc0d7513b6d7ee27a02fb5b519bc4818b",
        )
        self.assertEqual(
            value["current_runtime_source_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        )
        self.assertEqual(
            value["dormant_2023_gate_template_blob_sha"],
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
        )
        self.assertEqual(
            value["dormant_runtime_target_template_blob_sha"],
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        )

    def test_valid_authorization_builds_dormant_protected_plan(self) -> None:
        authorization = _authorization()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2023_runtime_authorization_plan."
            "validate_2023_execution_authorization",
            return_value=authorization,
        ):
            value = build_2023_runtime_authorization_plan(
                authorization,
                repository_root=ROOT,
            )
        self.assertIs(validate_2023_runtime_authorization_plan(value), value)
        self.assertEqual(value["decision"], "DEC-604")
        self.assertEqual(value["annual_segment_label"], "2023")
        self.assertEqual(value["expected_run_number"], 385)
        self.assertEqual(
            value["expected_previous_annual_freeze_run_id"],
            37663157285,
        )
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        )
        self.assertTrue(
            value["source_authorization_protected_history_access_authorized"]
        )
        self.assertTrue(value["protected_catalogue_segment"])
        self.assertTrue(value["protocol_full_collection_catalogue_use_authorized"])
        self.assertTrue(value["protocol_2023_2026_catalogue_use_authorized"])
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
            "run_386_or_later_authorized",
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

    def test_wrong_run_is_rejected(self) -> None:
        authorization = _authorization()
        authorization["expected_run_number"] = 386
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2023_runtime_authorization_plan."
            "validate_2023_execution_authorization",
            return_value=authorization,
        ):
            with self.assertRaisesRegex(ValueError, "expected run number mismatch"):
                build_2023_runtime_authorization_plan(
                    authorization,
                    repository_root=ROOT,
                )

    def test_missing_protected_source_authority_is_rejected(self) -> None:
        authorization = _authorization()
        authorization["protected_history_access_authorized"] = False
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2023_runtime_authorization_plan."
            "validate_2023_execution_authorization",
            return_value=authorization,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "protected-history authority missing",
            ):
                build_2023_runtime_authorization_plan(
                    authorization,
                    repository_root=ROOT,
                )

    def test_cli_is_plan_only(self) -> None:
        text = (
            ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2023_runtime_authorization_plan.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', text)
        self.assertNotIn('subparsers.add_parser("install")', text)
        self.assertNotIn("gh workflow run ", text)


if __name__ == "__main__":
    unittest.main()
