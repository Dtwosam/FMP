from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2017_runtime_authorization_plan import (
    build_2017_runtime_authorization_plan,
    validate_2017_runtime_authorization_plan_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GATE_TEMPLATE = (
    REPOSITORY_ROOT
    / "docs/superpowers/templates/"
    "annual_pattern_catalogue_2017_runtime_authorization.py.disabled"
)
RUNTIME_TEMPLATE = (
    REPOSITORY_ROOT
    / "docs/superpowers/templates/"
    "annual_pattern_catalogue_runtime_with_2017_authorization.py.disabled"
)


class AnnualPatternCatalogue2017RuntimeAuthorizationPlanTests(unittest.TestCase):
    def test_sources_pin_dec523_dec524_workflow_and_templates(self) -> None:
        source = validate_2017_runtime_authorization_plan_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "e7c1b20516cff69e6ab177d255b64c95616f9533",
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "e800a24b6ab50fdd11ff3c907fe0cc5d647beff9",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            source["base_runtime_source_blob_sha"],
            "995bb46ddd95563f904243c78ae4fc3cf3308968",
        )
        self.assertEqual(
            source["dormant_2017_gate_template_blob_sha"],
            "9016baaee0d3fd8915590a399eb8d242a954dfee",
        )
        self.assertEqual(
            source["dormant_runtime_target_template_blob_sha"],
            "2ac50ccbdfb40d2971c06711e98e464badd9f1fc",
        )

    def test_plan_is_dormant_and_non_mutating(self) -> None:
        value = build_2017_runtime_authorization_plan(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(value["decision"], "DEC-525")
        self.assertEqual(value["annual_segment_label"], "2017")
        self.assertEqual(value["expected_run_number"], 378)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(
            value["expected_current_runtime_source_blob_sha"],
            "995bb46ddd95563f904243c78ae4fc3cf3308968",
        )
        self.assertTrue(value["previous_annual_freeze_run_required"])
        self.assertTrue(value["plan_source_only"])
        self.assertFalse(value["repository_mutation_authorized"])
        self.assertFalse(value["runtime_authorization_installed"])
        self.assertFalse(value["runtime_gate_active"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_dormant_gate_is_exact_run378_attempt1_and_predecessor_bound(self) -> None:
        gate = GATE_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn('AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2017"', gate)
        self.assertIn("EXPECTED_RUN_NUMBER = 378", gate)
        self.assertIn("EXPECTED_RUN_ATTEMPT = 1", gate)
        self.assertIn("previous_annual_freeze_run_id", gate)
        self.assertIn(
            "DEC-525 authorizes only annual workflow run number 378",
            gate,
        )
        self.assertIn("TRADING_AUTHORIZED = False", gate)

    def test_runtime_target_adds_only_2017_route_and_preserves_prior_routes(self) -> None:
        runtime = RUNTIME_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("require_2017_execution_authorized", runtime)
        self.assertIn(
            'segment == "2017" and effective_run_number == 378',
            runtime,
        )
        self.assertIn(
            'segment == "2016" and effective_run_number == 377',
            runtime,
        )
        self.assertIn("if effective_run_number == 376:", runtime)
        self.assertIn(
            "DEC-525 2017 execution requires previous annual freeze run id",
            runtime,
        )
        self.assertNotIn(
            'segment == "2018" and effective_run_number == 379',
            runtime,
        )

    def test_templates_have_no_broker_or_order_execution_surface(self) -> None:
        text = (
            GATE_TEMPLATE.read_text(encoding="utf-8")
            + RUNTIME_TEMPLATE.read_text(encoding="utf-8")
        )
        for forbidden in (
            "order_send(",
            "MetaTrader5",
            "mt5.",
            "broker_order",
            "live_order(",
            "gh workflow run ",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
