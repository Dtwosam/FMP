from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

WORKFLOWS = (
    "phase8a-exp013-stage-a.yml",
    "phase8a-exp013-stage-b.yml",
    "phase8a-exp015-stage-a.yml",
    "phase8a-exp015-stage-b.yml",
    "phase8a-exp015-stage-c.yml",
    "phase8a-exp014-selection.yml",
)


class Phase8ADispatchRefGuardTests(unittest.TestCase):
    def test_all_authoritative_manual_workflows_fail_closed_off_main(self) -> None:
        for name in WORKFLOWS:
            with self.subTest(workflow=name):
                text = (ROOT / ".github" / "workflows" / name).read_text(
                    encoding="utf-8"
                )
                self.assertIn("workflow_dispatch:", text)
                self.assertNotIn("pull_request:", text)
                self.assertIn("Require main workflow dispatch", text)
                self.assertIn('if [ "${GITHUB_REF}" != "refs/heads/main" ]; then', text)
                self.assertIn(
                    "Phase 8A historical workflows must be dispatched from refs/heads/main",
                    text,
                )

    def test_main_guard_precedes_any_historical_source_download(self) -> None:
        for name in WORKFLOWS:
            with self.subTest(workflow=name):
                text = (ROOT / ".github" / "workflows" / name).read_text(
                    encoding="utf-8"
                )
                guard_index = text.index("Require main workflow dispatch")
                source_markers = (
                    "Download and verify accepted Phase 2 artifact",
                    "Download required accepted Phase 2 artifacts",
                )
                present = [
                    text.index(marker)
                    for marker in source_markers
                    if marker in text
                ]
                self.assertTrue(present, name)
                self.assertLess(guard_index, min(present), name)


if __name__ == "__main__":
    unittest.main()
