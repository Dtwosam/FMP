from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2019-execution-preflight.yml"
)


class AnnualCatalogue2019ExecutionPreflightWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_one_shot_preflight(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-execution-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_workflow_pins_exact_recovered_dec555_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37240186365",
            "b0de575d0ba564de523ba8e23ed05f052ae756a3",
            "11317140969",
            "sha256:2d158ae5dc2040570c1738c6700b96d34d05820abe3cd71f91b3389c469094b5",
            "09950f6bfb577c4abe17a2466e466a08585fbcd05359ad5fa6c4bad16cce5fda",
            "355a1e5ca9282300a7a38e24dd3009ebe8470d1f029e62c38860bf710ac80559",
            "a813a8db59927eaf9108e010a5db84f6c6dafa27",
            "277cf9d2c8df3a341c747546496ff712535d07af",
            "c44123cb04a8f476cf3efdb635bd1efb1d072df1",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_exact_six_run_history(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 6", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380}",
            text,
        )
        for run_id in (
            "37126711695",
            "37191637168",
            "37198002653",
            "37206992367",
            "37227536041",
            "37237817538",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            'assert not any(row["run_number"] >= 381 for row in rows)',
            text,
        )

    def test_workflow_freezes_2019_at_run381_without_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'assert value["annual_segment_label"] == "2019"',
            text,
        )
        self.assertIn(
            'assert value["previous_annual_freeze_run_id"] == 37237817538',
            text,
        )
        self.assertIn(
            'assert value["expected_next_run_number"] == 381',
            text,
        )
        self.assertIn(
            'assert value["expected_next_run_attempt"] == 1',
            text,
        )
        self.assertIn('assert value["preflight_read_only"] is True', text)
        self.assertIn("assert value[field] is False, field", text)
        self.assertIn(
            "annual-catalogue-2019-dec556-execution-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
