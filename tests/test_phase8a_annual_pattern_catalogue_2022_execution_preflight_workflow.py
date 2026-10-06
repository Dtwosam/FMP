from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2022-execution-preflight.yml"
)


class AnnualCatalogue2022ExecutionPreflightWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_one_shot_preflight(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-execution-preflight",
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
        self.assertNotIn("gh api --method POST", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "2"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn("37539005579", text)
        self.assertIn("112527115635", text)
        self.assertIn(
            "Require exact second DEC-591 landing run after missing dependency failure",
            text,
        )
        self.assertIn("Install pinned preflight dependencies", text)
        self.assertIn("requirements/exp061-discovery-run.txt", text)
        self.assertIn("scikit-learn==1.9.1", text)
        self.assertIn("assert artifacts == []", text)

    def test_workflow_pins_exact_dec590_recovery_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37536632065",
            "2798003636d1858da38c564adbb70227cbb41e76",
            "11446806853",
            "sha256:3b4ac4827390c2262b35bf38e28a0b82140b792c7e2f9eb2575122ecd1e37eda",
            "7ea6ac7ec5a780bbd41fad754d3dce212d2d6e2e198ffe88cf9d85381133c683",
            "09aa36f87de239f692c90ae8aa5f41f6a3d5dd3015445979195a9dd9e9df2dfc",
            "a52661d8abd910856bc5260898a7f21cc4958f94",
            "c926a123133c6ffea080ad9674737648d8439bcf",
            "542ace21e77c2bbdf5fec5312556c58d9e641da7",
            "d7486296c2e953d6b4e7602c753c5529ccf5eef2",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "5b91918b4a57a3c9518b4321c07e0e8eb1c74c88",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_exact_nine_run_history(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 9", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
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
            "37443770076",
            "37531960014",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            'assert not any(row["run_number"] >= 384 for row in rows)',
            text,
        )

    def test_workflow_supersedes_terminal_claim_without_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'assert value["source_final_required_annual_segment_bound_claim"] is True',
            text,
        )
        self.assertIn(
            'assert value["source_terminal_successor_claim_superseded_by_dec469"] is True',
            text,
        )
        self.assertIn('assert value["governing_method_decision"] == "DEC-469"', text)
        self.assertIn('assert value["collection_segment_count"] == 12', text)
        self.assertIn('assert value["annual_segment_label"] == "2022"', text)
        self.assertIn('assert value["prior_segment_label"] == "2021"', text)
        self.assertIn(
            'assert value["previous_annual_freeze_run_id"] == 37531960014',
            text,
        )
        self.assertIn('assert value["expected_next_run_number"] == 384', text)
        self.assertIn('assert value["preflight_read_only"] is True', text)
        self.assertIn("assert value[field] is False, field", text)
        self.assertIn(
            "annual-catalogue-2022-dec591-execution-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
