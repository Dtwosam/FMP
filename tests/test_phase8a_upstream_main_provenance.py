from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "phase8a-exp013-stage-b.yml": (
        ".github/workflows/phase8a-exp013-stage-a.yml",
    ),
    "phase8a-exp015-stage-b.yml": (
        ".github/workflows/phase8a-exp015-stage-a.yml",
    ),
    "phase8a-exp015-stage-c.yml": (
        ".github/workflows/phase8a-exp015-stage-a.yml",
        ".github/workflows/phase8a-exp015-stage-b.yml",
    ),
    "phase8a-exp014-selection.yml": (
        ".github/workflows/phase8a-exp015-stage-c.yml",
    ),
}


class Phase8AUpstreamMainProvenanceTests(unittest.TestCase):
    def test_downstream_workflows_require_main_upstream_provenance(self) -> None:
        for name, upstream_paths in EXPECTED.items():
            with self.subTest(workflow=name):
                text = (ROOT / ".github" / "workflows" / name).read_text(
                    encoding="utf-8"
                )
                self.assertIn("workflow_dispatch:", text)
                self.assertIn("head_branch", text)
                self.assertIn("main", text)
                self.assertIn("path", text)
                for upstream_path in upstream_paths:
                    self.assertIn(upstream_path, text)

    def test_upstream_provenance_is_checked_before_artifact_download(self) -> None:
        for name in EXPECTED:
            with self.subTest(workflow=name):
                text = (ROOT / ".github" / "workflows" / name).read_text(
                    encoding="utf-8"
                )
                if name == "phase8a-exp014-selection.yml":
                    verify_marker = "Verify EXP-015 Stage C workflow run"
                elif name == "phase8a-exp015-stage-c.yml":
                    verify_marker = "Verify Stage A and Stage B workflow runs"
                else:
                    verify_marker = "Verify Stage A workflow run identity"
                self.assertLess(
                    text.index(verify_marker),
                    text.index("actions/download-artifact@v6"),
                    name,
                )


if __name__ == "__main__":
    unittest.main()
