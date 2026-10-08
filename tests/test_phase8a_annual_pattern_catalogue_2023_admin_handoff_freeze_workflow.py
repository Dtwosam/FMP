from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase8a-annual-catalogue-2023-admin-handoff-freeze.yml"


class AnnualCatalogue2023AdminHandoffFreezeWorkflowTests(unittest.TestCase):
    def test_only_first_main_push_with_read_only_permissions(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for token in (
            "name: phase8a-annual-catalogue-2023-admin-handoff-freeze",
            "  push:",
            "      - main",
            "  contents: read",
            "  actions: read",
            'test "$GITHUB_REPOSITORY" = "Dtwosam/FMP"',
            'test "$GITHUB_EVENT_NAME" = "push"',
            'test "$GITHUB_REF" = "refs/heads/main"',
            'test "$GITHUB_RUN_NUMBER" = "1"',
            'test "$GITHUB_RUN_ATTEMPT" = "1"',
            'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"',
            "if-no-files-found: error",
        ):
            self.assertIn(token, text)
        for forbidden in (
            "  actions: write", "  contents: write",
            "  workflow_dispatch:", "  schedule:",
            "gh workflow run ", "gh run rerun",
            "gh api --method POST", "gh api -X POST",
            "git push", "git commit",
        ):
            self.assertNotIn(forbidden, text)

    def test_upstream_provenance_frozen_and_bounded_landing(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "29a47639d80caf5e02fe33586c1fa5718603c614",
            "895b9ad311bd5159b2591dcfc8da714191574d00",
            "37791444781",
            "11555414803",
            "48b4512002af76c4fe88a256cff8ddc558d185d18411f2f9d8fd9b32fba80bf3",
            "cc89cf90e820341a48d41cdd5518105dd99f3c867c9ec43b8c7d989a2535d0c5",
            "d9555c20a7d7a5a2d4bc79f9dd621e7a6d73e1ac9340cfec81348dc4e5f6a787",
            "6de695a5ea0c27f4fb16b5eae3289c0014155e3b",
            "cb17f4fba2eccd19077a8a057d5781bf81950759",
            "e4c76ef4993f03d51200139dee708250cf40e80f",
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "git diff --name-only",
            "assert actual == expected",
            "dec614-2023-admin-lock-handoff.json",
        ):
            self.assertIn(value, text)

    def test_handoff_does_not_upgrade_research_or_trading_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "assert len(rows) == 10",
            "assert not any(r.get(\"run_number\", 0) >= 385 for r in rows)",
            'assert value["decision"] == "DEC-613"',
            'assert value["expected_head_sha"] == os.environ["GITHUB_SHA"]',
            'assert value["expected_run_number"] == 385',
            'assert value["expected_run_attempt"] == 1',
            'assert value["admin_evidence_gathered_by_this_packet"] is False',
            'assert value["human_proof_required"] is True',
            'assert value["dispatch_blocked"] is True',
            'assert value["dispatch_action_executed"] is False',
            'assert value["main_exclusive_lock_proven"] is False',
            'assert value["annual_workflow_dispatch_authorized"] is False',
            'assert value["trading_authorized"] is False',
        ):
            self.assertIn(required, text)

    def test_source_writes_only_runner_temp_and_read_only_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("--out \"$RUNNER_TEMP/dec614-2023-admin-lock-handoff.json\"", text)
        self.assertEqual(text.count("actions/upload-artifact@v6"), 1)
        self.assertEqual(text.count("actions/checkout@v6"), 1)
        self.assertIn("validate_2023_admin_lock_handoff(value)", text)


if __name__ == "__main__":
    unittest.main()
