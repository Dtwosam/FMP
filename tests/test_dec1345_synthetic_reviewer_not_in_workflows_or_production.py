from __future__ import annotations

from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MARKERS=(
    "dec1330_synthetic_annual_gate_proof_nonauthorizing",
    "assess_synthetic_claims",
)


class SyntheticAnnualReviewerMustNeverBecomeExecutionGate(unittest.TestCase):
    def _assert_no_production_reference(self, files):
        inspected=0
        for path in files:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                content=path.read_text(encoding="utf-8")
                for marker in MARKERS:
                    self.assertNotIn(marker,content,
                                     "SOURCE-ONLY reviewer must remain inert")
                inspected+=1
        self.assertGreater(inspected,0,"scope must not pass on empty file set")

    def test_installed_github_workflow_sources_do_not_use_synthetic_reviewer(self):
        workflows=ROOT/".github"/"workflows"
        self.assertTrue(workflows.is_dir())
        self._assert_no_production_reference(
            sorted(p for p in workflows.iterdir()
                   if p.is_file() and p.suffix in (".yml",".yaml")))

    def test_packaged_python_runtime_does_not_import_synthetic_reviewer(self):
        source=ROOT/"src"
        self.assertTrue(source.is_dir())
        self._assert_no_production_reference(
            sorted(p for p in source.rglob("*.py") if p.is_file()))

    def test_package_entrypoint_spec_does_not_expose_synthetic_reviewer(self):
        pyproject=ROOT/"pyproject.toml"
        self.assertTrue(pyproject.is_file())
        self._assert_no_production_reference((pyproject,))
