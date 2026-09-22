from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
STAGE_B = ROOT / ".github" / "workflows" / "phase8a-exp015-stage-b.yml"
STAGE_C = ROOT / ".github" / "workflows" / "phase8a-exp015-stage-c.yml"


class Exp015StageBCWorkflowTests(unittest.TestCase):
    def test_stage_b_is_manual_and_validates_upstream_before_source_download(self) -> None:
        text = STAGE_B.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("stage_a_run_id:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("phase8a-exp015-stage-a", text)
        self.assertIn("validate_exp015_stage_a_authorization", text)
        self.assertIn("scripts/phase8a_exp015.py stage-b-run", text)
        self.assertIn("'2019-01-01'", text)
        self.assertIn("'2023-01-01'", text)
        self.assertNotIn("stage-c-run", text)
        self.assertNotIn("finalize", text)
        self.assertNotIn("phase8a_joint.py", text)

        validate_index = text.index(
            "Validate Stage A authorization before source download"
        )
        source_index = text.index("Download required accepted Phase 2 artifacts")
        self.assertLess(validate_index, source_index)

        for artifact_id, digest in (
            ("10325737935", "db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3"),
            ("10326096831", "fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2"),
            ("10327600628", "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72"),
        ):
            self.assertIn(artifact_id, text)
            self.assertIn(digest, text)

    def test_stage_c_validates_both_upstreams_before_source_and_finalizes_only_after_stage_c(self) -> None:
        text = STAGE_C.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("stage_a_run_id:", text)
        self.assertIn("stage_b_run_id:", text)
        self.assertIn("phase8a-exp015-stage-a", text)
        self.assertIn("phase8a-exp015-stage-b", text)
        self.assertIn("validate_exp015_stage_b_evidence", text)
        self.assertIn("scripts/phase8a_exp015.py stage-c-run", text)
        self.assertIn("scripts/phase8a_exp015.py finalize", text)
        self.assertIn("'2023-01-01'", text)
        self.assertIn("'2026-08-21'", text)
        self.assertIn("historical_qualified_count", text)
        self.assertIn("lifecycle_dispositions", text)
        self.assertNotIn("phase8a_joint.py", text)
        self.assertNotIn("portfolio-selection", text)

        validate_index = text.index(
            "Validate upstream evidence before Stage C source download"
        )
        source_index = text.index("Download required accepted Phase 2 artifacts")
        run_index = text.index("Run frozen EXP-015 Stage C")
        finalize_index = text.index("Finalize frozen EXP-015 shortlist")
        self.assertLess(validate_index, source_index)
        self.assertLess(source_index, run_index)
        self.assertLess(run_index, finalize_index)

        for cap in (
            "historical_qualified_count'] <= 11",
            "value <= 4",
            "value <= 3",
            "value <= 2",
        ):
            self.assertIn(cap, text)


if __name__ == "__main__":
    unittest.main()
