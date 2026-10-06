from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT / ".github/workflows/phase8a-annual-catalogue-2021-dispatch-preflight.yml"
)


class AnnualPatternCatalogue2021DispatchPreflightWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: phase8a-annual-catalogue-2021-dispatch-preflight", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)

    def test_workflow_pins_exact_dec585_install_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37496446082",
            "3f128ce83dc8d88b3951d5e4b17312f3139d9100",
            "11427632507",
            "0eec90cdfdd9b4ab68fd4989e7114d3d40baf41fc7e5f1129bd6cac182f48d74",
            "4833c86f74af3febfc2592048916d9ce20aa051a",
            "6fcbfeb2d2f7a8154925ac7fb5d08d68050a0ea2f2bbf2b3612015fd08b422c5",
            "2aac3060fad9a5d3f538a46c09a0ece58a41c3b863b34ca670593675a0175f2e",
            "a2454464ad9445dfd3ac788797f1c7633b67e116",
            "469f7e56e6a9051971e55bb78bcf6a489c03937c",
            "b088a8483ea555b28107462e88b8c16ec72b66b8",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_installed_state_and_run383_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("cac68c905bedf3105aa7e766eaa968c87bff6ce9", text)
        self.assertIn("d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6", text)
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382}",
            text,
        )
        self.assertIn('row["run_number"] >= 383', text)
        self.assertIn(
            'git merge-base --is-ancestor "$DEC585_INSTALL_COMMIT_SHA" "$GITHUB_SHA"',
            text,
        )

    def test_workflow_emits_read_only_dec586_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-586"', text)
        self.assertIn('value["expected_run_number"] == 383', text)
        self.assertIn('value["expected_run_attempt"] == 1', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37443770076',
            text,
        )
        self.assertIn('value["annual_workflow_run_count"] == 8', text)
        self.assertIn('value["successful_2020_run_id"] == 37443770076', text)
        self.assertIn('value["dispatch_command_present"] is False', text)
        self.assertIn('value["preflight_read_only"] is True', text)
        self.assertIn('"annual_workflow_dispatch_authorized",', text)
        self.assertIn('"trading_authorized",', text)
        self.assertIn(
            "annual-catalogue-2021-dec586-dispatch-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
