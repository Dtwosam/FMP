"""DEC-1372: source-only annual CLI entrypoint check.

No CLI import, call, job dispatch, protected data read, or GitHub API use.
"""
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


class AnnualCliSourceEntrypointsDoNotGrantPreAdmissionAuthority(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = committed("scripts/phase8a_annual_pattern_catalogue.py")
        module = ast.parse(source)
        cls.functions = {
            n.name: ast.get_source_segment(source, n)
            for n in module.body if isinstance(n, ast.FunctionDef)
        }
        flow = committed(".github/workflows/phase8a-annual-pattern-catalogue.yml")
        cls.preflight_job = flow.split("  annual_preflight:\n", 1)[1].split(
            "  annual_cell:\n", 1)[0]

    def test_preflight_cli_has_no_direct_execution_authorization_call(self):
        body = self.functions["_cmd_preflight"]
        self.assertNotIn("require_historical_catalogue_execution_authorized(", body)
        self.assertIn("validate_annual_segment_label(", body)

    def test_preflight_reads_four_snapshot_metadata_inputs_before_output(self):
        body = self.functions["_cmd_preflight"]
        for name in ("feature_run_json", "feature_artifacts_json",
                     "outcome_run_json", "outcome_artifacts_json"):
            with self.subTest(name=name):
                self.assertIn("_read_json(args." + name + ")", body)
        self.assertLess(body.index("validate_source_snapshots("),
                        body.index("_write_json(args.out, value)"))

    def test_preflight_embeds_source_report_and_install_receipt_before_writing(self):
        body = self.functions["_cmd_preflight"]
        self.assertIn("workflow_source_payload(", body)
        self.assertIn("validate_corrected_annual_workflow_install_receipt_sources(", body)
        self.assertLess(
            body.index("validate_corrected_annual_workflow_install_receipt_sources("),
            body.index("_write_json(args.out, value)"),
        )

    def test_status_command_reports_checked_in_source_without_execution_gate(self):
        body = self.functions["_cmd_status"]
        self.assertIn("workflow_source_payload(", body)
        self.assertIn("print(json.dumps(", body)
        self.assertNotIn("require_historical_catalogue_execution_authorized(", body)

    def test_prior_freeze_cli_reads_optional_input_json_without_direct_gate(self):
        body = self.functions["_cmd_require_prior_freeze"]
        for term in ("_read_json(args.previous_run_json)",
                     "_read_json(args.previous_freeze_evidence)",
                     "validate_prior_segment_freeze("):
            self.assertIn(term, body)
        self.assertNotIn("require_historical_catalogue_execution_authorized(", body)

    def test_prior_freeze_cli_reports_to_caller_chosen_output_path(self):
        body = self.functions["_cmd_require_prior_freeze"]
        self.assertIn("expected_previous_run_id=args.expected_previous_run_id", body)
        self.assertIn("_write_json(args.out, report)", body)

    def test_require_execution_entrypoint_calls_runtime_gate(self):
        body = self.functions["_cmd_require_execution"]
        self.assertIn("require_historical_catalogue_execution_authorized(", body)
        self.assertIn("code_commit=args.code_commit", body)

    def test_workflow_preflight_metadata_access_precedes_separate_entrypoint(self):
        body = self.preflight_job
        self.assertLess(
            body.index("- name: Fetch exact accepted EXP-044 source snapshots"),
            body.index("- name: Require separately authorized annual catalogue execution"),
        )
        self.assertLess(
            body.index("- name: Validate exact accepted EXP-044 source snapshots"),
            body.index("- name: Require separately authorized annual catalogue execution"),
        )

    def test_always_upload_is_downstream_but_remains_available_after_failure(self):
        body = self.preflight_job
        upload = body.split("- name: Upload annual catalogue preflight evidence", 1)[1]
        self.assertIn("if: always()", upload)
        self.assertIn("path: .preflight", upload)
        self.assertIn("include-hidden-files: true", upload)
        self.assertLess(
            body.index("- name: Require separately authorized annual catalogue execution"),
            body.index("- name: Upload annual catalogue preflight evidence"),
        )
