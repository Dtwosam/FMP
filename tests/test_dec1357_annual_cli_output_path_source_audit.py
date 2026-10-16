from __future__ import annotations

from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/"scripts"/"phase8a_annual_pattern_catalogue.py"
WORKFLOW=ROOT/".github"/"workflows"/"phase8a-annual-pattern-catalogue.yml"


class AnnualCliOutputLocationsRequireSeparateTrustedScratch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cli=CLI.read_text(encoding="utf-8")
        cls.workflow=WORKFLOW.read_text(encoding="utf-8")

    def test_cli_json_writer_creates_parent_and_writes_destination(self):
        self.assertIn("def _write_json(path: Path,",self.cli)
        self.assertIn("destination.parent.mkdir(parents=True, exist_ok=True)",
                      self.cli)
        self.assertIn("destination.write_text(payload, encoding=\"utf-8\")",
                      self.cli)

    def test_cli_byte_writer_creates_parent_and_writes_destination(self):
        self.assertIn("def _write_bytes(path: Path,",self.cli)
        self.assertIn("destination.write_bytes(value)",self.cli)
        self.assertIn("_write_bytes(args.catalogue_out,",self.cli)

    def test_preflight_current_workflow_uses_relative_checkout_outputs(self):
        for snippet in (
            "mkdir -p .preflight",
            "--out .preflight/preflight.json",
            "mkdir -p .prior-freeze/artifact",
            "--out .preflight/prior-freeze.json",
        ):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet,self.workflow)

    def test_cell_current_workflow_stages_and_writes_relative_directories(self):
        for snippet in (
            "mkdir -p .downloads .feature .outcome .feature-evidence .outcome-evidence",
            "mkdir -p .result",
            "--evidence-out .result/cell-evidence.json",
            "--catalogue-out .result/catalogue-payload.json",
            "download_exact \"$FEATURE_ARTIFACT_ID\"",
            "unzip -q .downloads/feature.zip -d .feature",
        ):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet,self.workflow)

    def test_freeze_job_downloads_cells_and_writes_checkout_relative_output(self):
        for snippet in (
            "path: .cell-results",
            "--result-root .cell-results",
            "--out .annual-freeze/annual-freeze.json",
            "path: .annual-freeze/annual-freeze.json",
        ):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet,self.workflow)

    def test_cli_freeze_requires_gate_before_result_read_but_after_job_setup(self):
        command=self.cli.split("def _cmd_freeze(",1)[1].split(
            "\ndef build_parser(",1)[0]
        self.assertLess(
            command.index("require_historical_catalogue_execution_authorized("),
            command.index("_load_validated_cell_summaries("))
        workflow_freeze=self.workflow.split("  annual_freeze:",1)[1]
        self.assertLess(workflow_freeze.index("Install pinned annual catalogue runtime"),
                        workflow_freeze.index("Recheck separately authorized annual catalogue execution"))
