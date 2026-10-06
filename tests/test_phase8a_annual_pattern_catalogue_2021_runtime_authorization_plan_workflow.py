from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2021-runtime-authorization-plan.yml"
)


class AnnualPatternCatalogue2021RuntimeAuthorizationPlanWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_first_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2021-runtime-authorization-plan",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("gh api --method POST", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_workflow_pins_recovered_dec581_run2(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37460105363",
            "cde122a5b70032733dc5699cb2258ed40defbc4d",
            "11411376869",
            "sha256:233cdabf39d23016a6ba73915abeac7a5af333661c91b68752cfb61f9db513e4",
            "56226545935b649e24077b1e108e17b865a65bbdbee36fb73a9605d4f766d6d6",
        ):
            self.assertIn(value, text)
        self.assertIn('"run_number": 2', text)
        self.assertIn('"run_attempt": 1', text)
        self.assertIn('"conclusion": "success"', text)

    def test_workflow_pins_exact_sources_and_dormant_templates(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "de1643991d85cd63e5505401b871e3c02315e0e9",
            "84285fec29f71096ff0f71bfd73ff2a5c39f508e",
            "3e086e82201ed0bea85226c115ae7a09e7d95983",
            "981309374459ed6b99030f66d08ac5fc0e707dcc",
            "4e124365430672fa63825b272001937c60151644",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        ):
            self.assertIn(value, text)
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2021_runtime_authorization.py",
            text,
        )

    def test_workflow_requires_run383_slot_unconsumed(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 8", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382}",
            text,
        )
        self.assertIn(
            'assert not any(row["run_number"] >= 383 for row in rows)',
            text,
        )

    def test_workflow_emits_only_dormant_dec582_plan(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert value["decision"] == "DEC-582"', text)
        self.assertIn('assert value["expected_run_number"] == 383', text)
        self.assertIn(
            'assert value["runtime_authorization_installed"] is False',
            text,
        )
        self.assertIn('assert value["runtime_gate_active"] is False', text)
        self.assertIn(
            'assert value["repository_mutation_authorized"] is False',
            text,
        )
        self.assertIn(
            'assert value["annual_workflow_dispatch_authorized"] is False',
            text,
        )
        self.assertIn('assert value["trading_authorized"] is False', text)
        self.assertIn(
            "annual-catalogue-2021-dec582-runtime-authorization-plan-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
