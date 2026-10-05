from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2020-execution-preflight.yml"
)


class AnnualCatalogue2020ExecutionPreflightWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_one_shot_preflight(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-execution-preflight",
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
        self.assertNotIn("gh run rerun", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_workflow_pins_exact_recovered_dec566_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37312368068",
            "ae724ba3e59c17440a8cf222242316a9462bf98f",
            "11345528676",
            "sha256:800e06ce5026efa517853db32edf424ade527dc3fa7f2b95d9d2edd128237700",
            "a7063417dfb917f9b9019eb97c9a2803f50b4163ea524ea52c64b28a387720a2",
            "6935506f20d6d46054fabed5200ba6cec33ea4f10b00d839cc1cfc7f1b92b918",
            "e045b3e82d2f16e870c77b5b107d8d46fcf96f85",
            "b468378dfc784a0eca032dd799c132d6874f2ab2",
            "9eec5e2ea74fc15b5d2686aa426bcaaddae5c14b",
            "833242440600799ebe6ada7a83f4e9cb84481213",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_exact_seven_run_history(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 7", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381}",
            text,
        )
        for run_id in (
            "37126711695",
            "37191637168",
            "37198002653",
            "37206992367",
            "37227536041",
            "37237817538",
            "37310525635",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            'assert not any(row["run_number"] >= 382 for row in rows)',
            text,
        )

    def test_workflow_freezes_2020_at_run382_without_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'assert value["annual_segment_label"] == "2020"',
            text,
        )
        self.assertIn(
            'assert value["prior_segment_label"] == "2019"',
            text,
        )
        self.assertIn(
            'assert value["previous_annual_freeze_run_id"] == 37310525635',
            text,
        )
        self.assertIn(
            'assert value["expected_next_run_number"] == 382',
            text,
        )
        self.assertIn(
            'assert value["expected_next_run_attempt"] == 1',
            text,
        )
        self.assertIn('assert value["preflight_read_only"] is True', text)
        self.assertIn("assert value[field] is False, field", text)
        self.assertIn(
            "annual-catalogue-2020-dec567-execution-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
