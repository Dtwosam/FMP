from __future__ import annotations

from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"scripts"/"dec1330_synthetic_annual_gate_proof_nonauthorizing.py"
DENIED_IDENTIFIERS=(
    "dec1330_synthetic_annual_gate_proof_nonauthorizing",
    "assess_synthetic_claims",
)


class SyntheticReviewEntrypointMustStayInert(unittest.TestCase):
    def _negative_source_inventory(self, paths):
        inspected=0
        for path in paths:
            with self.subTest(source=path.relative_to(ROOT).as_posix()):
                body=path.read_text(encoding="utf-8")
                for marker in DENIED_IDENTIFIERS:
                    self.assertNotIn(marker,body,
                                     "inert reviewer must not run in another source")
                inspected+=1
        self.assertGreater(inspected,0,"do not silently accept an empty scope")

    def test_other_repository_scripts_do_not_invoke_the_synthetic_reviewer(self):
        folder=ROOT/"scripts"
        self.assertTrue(folder.is_dir())
        self._negative_source_inventory(
            sorted(p for p in folder.rglob("*.py")
                   if p.is_file() and p != SOURCE))

    def test_supabase_edge_functions_do_not_expose_the_reviewer(self):
        folder=ROOT/"supabase"
        self.assertTrue(folder.is_dir())
        self._negative_source_inventory(
            sorted(p for p in folder.rglob("*")
                   if p.is_file() and p.suffix in (".ts",".js",".toml")))

    def test_dependency_requirement_files_do_not_reference_reviewer(self):
        folder=ROOT/"requirements"
        self.assertTrue(folder.is_dir())
        self._negative_source_inventory(
            sorted(p for p in folder.rglob("*.txt") if p.is_file()))

    def test_no_repository_script_runs_protected_annual_dispatch_by_alias(self):
        # This additional, narrowly scoped check prevents the REVIEWER's
        # own source from gaining a subprocess/host API action. This does
        # not purport to vet every other legitimate maintenance script.
        body=SOURCE.read_text(encoding="utf-8")
        for forbidden in (
            "workflow_dispatch","subprocess","requests.",
            "urllib.", "gh api", "GenUI", "place_order",
            "send_order","broker_api",
        ):
            with self.subTest(token=forbidden):
                self.assertNotIn(forbidden,body)
