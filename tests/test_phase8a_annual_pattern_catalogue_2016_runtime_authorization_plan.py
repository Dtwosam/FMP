from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2016_runtime_authorization_plan import (
    build_2016_runtime_authorization_plan,
    validate_2016_runtime_authorization_plan_sources,
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-505 requires the post-DEC-504 source state",
)
class AnnualPatternCatalogue2016RuntimeAuthorizationPlanTests(unittest.TestCase):
    def test_sources_pin_authorization_preflight_runtime_workflow_and_templates(self) -> None:
        source = validate_2016_runtime_authorization_plan_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "f3d93ba4701a5d9d80005664445104d1105ff25f",
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "9c89eb64c1e0ecda56fd9cfe0b26516e4a20abc3",
        )
        self.assertEqual(
            source["current_runtime_source_blob_sha"],
            "ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            source["dormant_2016_gate_template_blob_sha"],
            "e6ef74733669ceb8cab13a1e0d25a236526266e3",
        )
        self.assertEqual(
            source["dormant_runtime_target_template_blob_sha"],
            "995bb46ddd95563f904243c78ae4fc3cf3308968",
        )

    def test_plan_is_dormant_and_non_authorizing(self) -> None:
        value = build_2016_runtime_authorization_plan(
            repository_root=Path("."),
        )
        self.assertEqual(value["decision"], "DEC-505")
        self.assertEqual(value["source_authorization_decision"], "DEC-504")
        self.assertEqual(value["source_preflight_decision"], "DEC-503")
        self.assertEqual(value["annual_segment_label"], "2016")
        self.assertEqual(value["expected_run_number"], 377)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertTrue(value["previous_annual_freeze_run_required"])
        self.assertFalse(value["runtime_authorization_installed"])
        self.assertFalse(value["runtime_gate_active"])
        self.assertFalse(value["repository_mutation_authorized"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_artifact_read_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["historical_result_production_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertEqual(
            value["next_gate"],
            (
                "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_"
                "AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC504"
            ),
        )

    def test_dormant_gate_is_exact_run3_attempt1_and_predecessor_bound(self) -> None:
        text = Path(
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_2016_runtime_authorization.py.disabled"
        ).read_text(encoding="utf-8")
        self.assertIn('AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2016"', text)
        self.assertIn("EXPECTED_RUN_NUMBER = 3", text)
        self.assertIn("EXPECTED_RUN_ATTEMPT = 1", text)
        self.assertIn("previous_annual_freeze_run_id", text)
        self.assertIn("TRADING_AUTHORIZED = False", text)

    def test_runtime_target_routes_only_2016_run3_to_new_gate(self) -> None:
        text = Path(
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2016_authorization.py.disabled"
        ).read_text(encoding="utf-8")
        self.assertIn("require_2016_execution_authorized", text)
        self.assertIn('segment == "2016" and effective_run_number == 377', text)
        self.assertIn(
            "DEC-505 2016 execution requires previous annual freeze run id",
            text,
        )
        self.assertIn("require_2015_replacement_execution_authorized", text)
        self.assertIn("require_2015_execution_authorized", text)


if __name__ == "__main__":
    unittest.main()
