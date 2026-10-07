from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/phase8a-annual-catalogue-2023-execution-preflight.yml"
)


class AnnualCatalogue2023ExecutionPreflightWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_one_shot_preflight(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2023-execution-preflight",
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
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn("Install pinned preflight dependencies", text)
        self.assertIn("scikit-learn==1.9.1", text)

    def test_workflow_pins_exact_dec601_recovery_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37670106681",
            "a08512973deb127f16e199c6ecd2876e0fc8d8e0",
            "11504596272",
            "sha256:45e4436ce5536c7df7ed8a3af99d9dc911025ec441a554de627d4adf8de1f755",
            "7e36345fc0ca8592e5f5ede41b9afcfdc9becff72d2415b7e6741ed2352923ac",
            "926832634d5836b158d780e21886692e762709104a6d0048c54a75c77ad2f352",
            "d7e0823bc0d7513b6d7ee27a02fb5b519bc4818b",
            "11ef1e46a8242455fc5eeff3d596b705951969a5",
            "7048781474ce74b8bbed0fd380f8edf4ec51491d",
            "d7486296c2e953d6b4e7602c753c5529ccf5eef2",
            "5ddd987cc480e6e31c0cd45328eba16cf690dee9",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "2d0160338a7791cc98e4aaed22c49ee6541f8c33",
        ):
            self.assertIn(value, text)
        self.assertIn(
            '"name": "phase8a-annual-catalogue-2022-run384-runtime-evidence"',
            text,
        )
        self.assertIn(
            '"annual-catalogue-2022-dec601-runtime-binding-37663157285"',
            text,
        )
        self.assertIn("runtime-binding-2022.json", text)

    def test_workflow_requires_exact_ten_run_history(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 10", text)
        self.assertIn(
            "assert set(by_number) == "
            "{1, 376, 377, 378, 379, 380, 381, 382, 383, 384}",
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
            "37663157285",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            '384: (37663157285, "success", '
            '"dd79687adc4ec179c56f91939cb600e6746fab5d")',
            text,
        )
        self.assertIn(
            'assert not any(row["run_number"] >= 385 for row in rows)',
            text,
        )

    def test_workflow_supersedes_terminal_claim_without_opening_protected_access(
        self,
    ) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'assert value["source_final_required_annual_segment_bound_claim"] is True',
            text,
        )
        self.assertIn(
            'assert value["source_terminal_successor_claim_superseded_by_dec469_dec470"] is True',
            text,
        )
        self.assertIn('assert value["governing_method_decision"] == "DEC-469"', text)
        self.assertIn('assert value["governing_protocol_decision"] == "DEC-470"', text)
        self.assertIn('assert value["protected_catalogue_segment"] is True', text)
        self.assertIn(
            'assert value["protocol_2023_2026_catalogue_use_authorized"] is True',
            text,
        )
        self.assertIn('assert value["annual_segment_label"] == "2023"', text)
        self.assertIn('assert value["prior_segment_label"] == "2022"', text)
        self.assertIn(
            'assert value["previous_annual_freeze_run_id"] == 37663157285',
            text,
        )
        self.assertIn('assert value["expected_next_run_number"] == 385', text)
        self.assertIn('assert value["preflight_read_only"] is True', text)
        self.assertIn('"protected_history_access_authorized",', text)
        self.assertIn('"run_386_or_later_authorized",', text)
        self.assertIn(
            "annual-catalogue-2023-dec602-execution-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
