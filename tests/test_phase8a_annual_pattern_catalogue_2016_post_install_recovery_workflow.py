from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2016-post-install-recovery.yml"
)


class AnnualCatalogue2016PostInstallRecoveryWorkflowTests(unittest.TestCase):
    def test_workflow_is_exact_one_shot_push_recovery(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2016-post-install-recovery",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)

    def test_workflow_reconstructs_historical_dec508_from_exact_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("37205141103", text)
        self.assertIn("11304088642", text)
        self.assertIn(
            "cd455bfae7a1c91f114d9a4e35b81fcd46d7921740f0c04ff27d79978ab93231",
            text,
        )
        self.assertIn("dec507-install-action.json", text)
        self.assertIn("runtime-binding.json", text)
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2016_runtime_authorization_install_receipt.py",
            text,
        )
        self.assertIn("525386dd68955e9f02909f9692987968ab15e516", text)

    def test_workflow_dispatches_only_exact_run378(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-annual-pattern-catalogue.yml"
        self.assertEqual(text.count(command), 1)
        self.assertIn("-f annual_segment_label=2016", text)
        self.assertIn('test "$previous_run_id" = "37198002653"', text)
        self.assertIn('row.get("run_number") == 378', text)
        self.assertIn('row.get("run_number") >= 379', text)
        self.assertIn("DEC-532", text)
        self.assertIn("run_379_or_later_authorized", text)
        self.assertIn('"trading_authorized": False', text)

    def test_workflow_never_mutates_repository_or_broker(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for forbidden in (
            "git push",
            "git commit",
            "git add ",
            "contents: write",
            "order_send(",
            "MetaTrader5",
            "mt5.",
            "broker_order",
            "live_order(",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
