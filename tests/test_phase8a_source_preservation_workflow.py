from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8a-exp044-preserve-phase2.yml"


class Phase2PreservationWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_main_only_with_required_permissions(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', text)
        self.assertIn("contents: write", text)
        self.assertIn("actions: read", text)

    def test_workflow_preserves_exact_existing_source_identities(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = (
            (
                "10325737935",
                "db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3",
                "182037581",
                "fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a",
            ),
            (
                "10326096831",
                "fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2",
                "190706384",
                "a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94",
            ),
            (
                "10327600628",
                "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72",
                "160033414",
                "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
            ),
        )
        for values in expected:
            for value in values:
                self.assertIn(value, text)
        self.assertIn("34782357048", text)
        self.assertIn("158c1c121655867b7fb2886fe755585dfcd682ec", text)

    def test_release_is_verified_as_draft_before_publication(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("--draft", text)
        self.assertIn("phase8a_phase2_preservation.py verify-release", text)
        self.assertIn("--draft=false", text)
        self.assertLess(
            text.index("phase8a_phase2_preservation.py verify-release"),
            text.index("--draft=false"),
        )
        self.assertNotIn("--clobber", text)

    def test_workflow_performs_no_new_data_acquisition_or_trading(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("does not reacquire market data", text)
        self.assertIn("authorizes no model fit", text)
        self.assertNotIn("dukascopy.com", text.lower())
        self.assertNotIn("order_send", text)
        self.assertNotIn("mt5", text.lower())


if __name__ == "__main__":
    unittest.main()
