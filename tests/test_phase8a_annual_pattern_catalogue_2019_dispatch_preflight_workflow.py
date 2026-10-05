from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2019-dispatch-preflight.yml"
)


class AnnualPatternCatalogue2019DispatchPreflightWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-dispatch-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)

    def test_workflow_pins_exact_dec561_install_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37304310188",
            "0e23f87b5990961bcfe8d4e6998fef20282f6626",
            "11342593171",
            "9739dda98fe654435c9e58053b934cfba4f1cf8747ab79dcd7dcbe9e27e6492b",
            "ea3d63b5181fc592039c0c26d6decb358e43f7cc",
            "098d2d24fbce40943ccff16a9ae1374e77facc0804365fedbb15eb128b3ca7be",
            "4d1313ac3f79638e252c9d0e4f87844d387d73bc",
            "6b90fe9c45f1fbc10fd5749cbdfc2672831806a4",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_exact_installed_state_and_run381_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
            text,
        )
        self.assertIn(
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
            text,
        )
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380}",
            text,
        )
        self.assertIn('row["run_number"] >= 381', text)
        self.assertIn(
            'git merge-base --is-ancestor "$DEC561_INSTALL_COMMIT_SHA" "$GITHUB_SHA"',
            text,
        )

    def test_workflow_emits_read_only_dec562_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-562"', text)
        self.assertIn('value["expected_run_number"] == 381', text)
        self.assertIn('value["expected_run_attempt"] == 1', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37237817538',
            text,
        )
        self.assertIn('value["annual_workflow_run_count"] == 6', text)
        self.assertIn('value["dispatch_command_present"] is False', text)
        self.assertIn('value["preflight_read_only"] is True', text)
        self.assertIn('"annual_workflow_dispatch_authorized",', text)
        self.assertIn('"trading_authorized",', text)
        self.assertIn(
            "annual-catalogue-2019-dec562-dispatch-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
