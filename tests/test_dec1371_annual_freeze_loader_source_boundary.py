"""DEC-1371 source-only freeze review: no CLI invocation or protected reads."""
from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


def committed(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", "HEAD:" + path], cwd=ROOT, text=True
    )


class AnnualFreezeSourceDoesNotProveProtectedAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cli = committed("scripts/phase8a_annual_pattern_catalogue.py")
        cls.workflow = committed(
            ".github/workflows/phase8a-annual-pattern-catalogue.yml"
        )
        module = ast.parse(cls.cli)
        cls.functions = {
            node.name: ast.get_source_segment(cls.cli, node)
            for node in module.body if isinstance(node, ast.FunctionDef)
        }
        cls.freeze_job = cls.workflow.split("  annual_freeze:\n", 1)[1]

    def test_loader_functions_present_without_runtime_import(self):
        self.assertIn("_load_validated_cell_summaries", self.functions)
        self.assertIn("_cmd_freeze", self.functions)

    def test_loader_enforces_expected_cell_evidence_count(self):
        s = self.functions["_load_validated_cell_summaries"]
        self.assertIn('rglob("cell-evidence.json")', s)
        self.assertIn("len(paths) != EXPECTED_CELLS_PER_SEGMENT", s)
        self.assertIn("raise ValueError(", s)

    def test_loader_requires_companion_payload(self):
        s = self.functions["_load_validated_cell_summaries"]
        self.assertIn('evidence_path.with_name("catalogue-payload.json")', s)
        self.assertIn('if not payload_path.is_file():', s)
        self.assertLess(s.index('if not payload_path.is_file():'),
                        s.index('payload_path.read_bytes()'))

    def test_loader_validates_evidence_payload_pairs(self):
        s = self.functions["_load_validated_cell_summaries"]
        for token in ("validated_cell_summary(", "_read_json(evidence_path)",
                      "payload_path.read_bytes()", "return summaries"):
            self.assertIn(token, s)

    def test_freeze_runtime_gate_precedes_result_tree_scan(self):
        s = self.functions["_cmd_freeze"]
        self.assertLess(s.index("require_historical_catalogue_execution_authorized("),
                        s.index("_load_validated_cell_summaries(args.result_root)"))

    def test_freeze_binds_commit_and_segment_to_compilation(self):
        s = self.functions["_cmd_freeze"]
        self.assertIn("code_commit=args.code_commit", s)
        self.assertIn("annual_segment_label=args.annual_segment_label", s)
        self.assertIn("compile_annual_segment_freeze(", s)

    def test_freeze_validates_before_result_output(self):
        s = self.functions["_cmd_freeze"]
        self.assertLess(s.index("validate_annual_segment_freeze(evidence)"),
                        s.index("_write_json(args.out, evidence)"))

    def test_workflow_downloads_patterned_cell_artifacts_relative_to_checkout(self):
        s = self.freeze_job
        for token in ("uses: actions/download-artifact@v6",
                      "pattern: phase8a-annual-catalogue-cell-",
                      "-*-*-*m-", "path: .cell-results",
                      "merge-multiple: false", "--result-root .cell-results"):
            self.assertIn(token, s)

    def test_job_setup_precedes_execution_recheck(self):
        s = self.freeze_job
        self.assertLess(s.index("- name: Checkout"),
                        s.index("Install pinned annual catalogue runtime"))
        self.assertLess(s.index("Install pinned annual catalogue runtime"),
                        s.index("Recheck separately authorized annual catalogue execution"))

    def test_upload_remains_checkout_relative_and_not_external_sink_proof(self):
        s = self.freeze_job
        for token in ("--out .annual-freeze/annual-freeze.json",
                      "uses: actions/upload-artifact@v6",
                      "path: .annual-freeze/annual-freeze.json",
                      "if-no-files-found: error", "include-hidden-files: true"):
            self.assertIn(token, s)
