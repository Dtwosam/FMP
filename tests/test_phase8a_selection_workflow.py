from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8a-exp014-selection.yml"


class Dec042SelectionWorkflowTests(unittest.TestCase):
    def test_selection_workflow_freezes_preflight_before_source_download(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("stage_c_run_id:", text)
        self.assertIn("phase8a-exp015-stage-c", text)
        self.assertIn("scripts/phase8a_selection.py preflight", text)
        self.assertIn("scripts/phase8a_selection.py run", text)
        self.assertIn("phase8a-exp014-selection-preflight-${{ github.sha }}", text)
        self.assertIn("actions/upload-artifact@v6", text)
        self.assertIn("actions/download-artifact@v6", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)

        preflight_index = text.index("Freeze exact DEC-042 pool and set universe")
        upload_index = text.index("Upload DEC-042 preflight before selection data")
        source_index = text.index("Download required accepted Phase 2 artifacts")
        run_index = text.index("Run frozen DEC-042 selection")
        self.assertLess(preflight_index, upload_index)
        self.assertLess(upload_index, source_index)
        self.assertLess(source_index, run_index)

    def test_workflow_uses_exact_range_costs_and_nonpromotion_boundary(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("'2019-01-01'", text)
        self.assertIn("'2026-08-21'", text)
        self.assertIn("[0.2, 0.5, 1.0]", text)
        self.assertIn("set_universe_sha256", text)
        self.assertIn("selected_strategy_fingerprints", text)
        self.assertIn("shadow_candidate_authorized", text)
        self.assertIn("promotion_authorized", text)
        self.assertIn("PORTFOLIO_SELECTION_PASS", text)
        self.assertIn("NO_PORTFOLIO_SELECTED", text)
        self.assertNotIn("phase8b", text.lower())
        self.assertNotIn("mt5", text.lower())

        for artifact_id, digest in (
            ("10325737935", "db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3"),
            ("10326096831", "fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2"),
            ("10327600628", "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72"),
        ):
            self.assertIn(artifact_id, text)
            self.assertIn(digest, text)


if __name__ == "__main__":
    unittest.main()
