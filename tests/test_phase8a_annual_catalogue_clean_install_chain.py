from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ".github/workflows/phase8a-annual-catalogue-2015-replacement-executor-recovery.yml",
    ".github/workflows/phase8a-annual-catalogue-2015-replacement-runtime-evidence.yml",
    ".github/workflows/phase8a-annual-catalogue-2016-activation-plan.yml",
    ".github/workflows/phase8a-annual-catalogue-2016-runtime-install-executor.yml",
    ".github/workflows/phase8a-annual-catalogue-2016-run377-runtime-evidence.yml",
)


class AnnualCatalogueCleanInstallChainTests(unittest.TestCase):
    def test_live_successor_workflows_do_not_use_editable_installs(self) -> None:
        for relative in WORKFLOWS:
            with self.subTest(workflow=relative):
                text = (REPOSITORY_ROOT / relative).read_text(encoding="utf-8")
                self.assertNotIn("-e .", text)
                self.assertIn(
                    "-r requirements/exp061-discovery-run.txt",
                    text,
                )
                self.assertIn("scikit-learn==1.9.1", text)
                self.assertIn('git status --porcelain', text)

    def test_recovery_v3_preserves_failed_run376_provenance(self) -> None:
        text = (REPOSITORY_ROOT / WORKFLOWS[0]).read_text(encoding="utf-8")
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "3"', text)
        self.assertIn("37191637168", text)
        self.assertIn("4c14fa7db6eb812b89ecb79201f7e298fa9c04f3", text)
        self.assertIn("build_2015_run376_failure_receipt", text)
        self.assertIn("build_2015_run377_execution_authorization", text)
        self.assertIn('"conclusion": "failure"', text)
        self.assertEqual(
            text.count("gh workflow run phase8a-annual-pattern-catalogue.yml"),
            1,
        )
        self.assertIn('row.get("run_number") == 377', text)
        self.assertIn('row["run_number"] >= 378', text)


if __name__ == "__main__":
    unittest.main()
