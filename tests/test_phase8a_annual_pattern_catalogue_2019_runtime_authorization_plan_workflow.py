from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2019-runtime-authorization-plan.yml"
)


class AnnualPatternCatalogue2019RuntimeAuthorizationPlanWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-runtime-authorization-plan",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-2019-runtime-authorization-plan.yml",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_concrete_dec546_evidence_and_templates(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37241812968",
            "eb72a2ab8639da62d6c6e4a084a6b11470b72bf1",
            "11317224241",
            "ecdbb57924cf74945e9e8bba12dcaae2d869ef264813ef012d21ba175c5ef52e",
            "c785127b20f57210e60ebd681d7b0e48a66f419fa8fbbbdd9cdd8fa560b464f9",
            "837b984e1ccb101c125ec21d9be062a969a002e3",
            "c29a37e70eed0e31f22a7c715e80555c44bf27a5",
            "3f7f71882195e373940d922a451f426011728063",
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_run381_is_absent(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("set(by_number) == {1, 376, 377, 378, 379, 380}", text)
        self.assertIn('by_number[380]["conclusion"] == "success"', text)
        self.assertIn('row["run_number"] >= 381', text)
        self.assertIn('value["expected_run_number"] == 381', text)
        self.assertIn(
            'value["expected_previous_annual_freeze_run_id"] == 37237817538',
            text,
        )

    def test_workflow_cannot_dispatch_or_mutate(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)
        self.assertNotIn("annual-catalogue-2018-dec557", text)
        self.assertNotIn('annual_segment_label\' "$RUNNER_TEMP/dec557-2019-execution-authorization.json")" = "2018"', text)
        self.assertIn('value["plan_source_only"] is True', text)
        self.assertIn('"trading_authorized",', text)


if __name__ == "__main__":
    unittest.main()
