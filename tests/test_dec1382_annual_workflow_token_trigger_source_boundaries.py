"""DEC-1382: offline source-only GitHub Actions token/trigger boundaries.

No GitHub API, workflow execution, protected artifacts, credential material
or FMP imports. All mutations are in-memory strings.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


def source_diagnostics(source: object) -> tuple[str, ...]:
    if type(source) is not str:
        return ("NON_TEXT",)
    if source.count("\njobs:\n") != 1 or source.count("\npermissions:\n") != 1:
        return ("MALFORMED_TOP_LEVEL",)
    header, jobs = source.split("\njobs:\n", 1)
    if header.count("\non:\n") > 1:
        return ("DUPLICATED_TRIGGER_SOURCE",)
    event_block = header.split("\non:\n", 1)
    if len(event_block) != 2:
        return ("MISSING_TRIGGER",)
    event = event_block[1].split("\npermissions:\n", 1)[0]
    names = re.findall(r"(?m)^  ([a-z_]+):$", event)
    problems = []
    if names != ["workflow_dispatch"]:
        problems.append("NOT_EXCLUSIVE_MANUAL_DISPATCH_SOURCE")
    perms = header.split("\npermissions:\n", 1)[1]
    permission_pairs = re.findall(r"(?m)^  (contents|actions): (read|write|none)$",
                                  perms)
    if permission_pairs != [("contents", "read"), ("actions", "read")]:
        problems.append("TOKEN_SCOPE_NOT_EXACT_READONLY_SOURCE")
    if re.search(r"(?m)^    permissions:", jobs):
        problems.append("JOB_SCOPED_PERMISSION_OVERRIDE_SOURCE")
    job_names = re.findall(r"(?m)^  ([a-z_][a-z0-9_-]*):$", jobs)
    if job_names != ["annual_preflight", "annual_cell", "annual_freeze"]:
        problems.append("JOB_INVENTORY_OR_ORDER_DRIFT")
    if source.count("GH_TOKEN: " + "$" + "{{ github.token }}") != 3:
        problems.append("WORKFLOW_TOKEN_SOURCE_BINDINGS_DRIFT")
    return tuple(problems)


class ReadOnlyGitHubTokenSourceIsNotReadOnlyFilesystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )

    def test_actual_trigger_is_manual_workflow_dispatch_only(self):
        s = self.source.split("\non:\n", 1)[1].split("\npermissions:\n", 1)[0]
        self.assertEqual(re.findall(r"(?m)^  ([a-z_]+):$", s),
                         ["workflow_dispatch"])

    def test_root_token_source_has_only_contents_and_actions_read(self):
        self.assertIn(
            "\npermissions:\n  contents: read\n  actions: read\n", self.source
        )

    def test_three_actual_jobs_have_no_permission_escalation_source(self):
        jobs = self.source.split("\njobs:\n", 1)[1]
        self.assertNotRegex(jobs, r"(?m)^    permissions:")
        self.assertEqual(
            re.findall(r"(?m)^  (annual_preflight|annual_cell|annual_freeze):$",
                       jobs),
            ["annual_preflight", "annual_cell", "annual_freeze"],
        )

    def test_workflow_token_binding_occurs_three_times(self):
        self.assertEqual(
            self.source.count("GH_TOKEN: " + "$" + "{{ github.token }}"), 3
        )

    def test_actual_source_has_no_token_or_trigger_shape_diagnostics(self):
        self.assertEqual(source_diagnostics(self.source), ())

    def test_actions_write_mutation_is_rejected_in_memory(self):
        tampered = self.source.replace("  actions: read\n",
                                       "  actions: write\n", 1)
        self.assertIn("TOKEN_SCOPE_NOT_EXACT_READONLY_SOURCE",
                      source_diagnostics(tampered))

    def test_automatic_push_trigger_mutation_is_rejected_in_memory(self):
        tampered = self.source.replace(
            "on:\n  workflow_dispatch:\n", "on:\n  push:\n  workflow_dispatch:\n", 1
        )
        self.assertIn("NOT_EXCLUSIVE_MANUAL_DISPATCH_SOURCE",
                      source_diagnostics(tampered))

    def test_job_scoped_escalation_mutation_is_rejected_in_memory(self):
        tampered = self.source.replace(
            "  annual_preflight:\n",
            "  annual_preflight:\n    permissions:\n      actions: write\n",
            1,
        )
        self.assertIn("JOB_SCOPED_PERMISSION_OVERRIDE_SOURCE",
                      source_diagnostics(tampered))

    def test_non_text_and_missing_trigger_are_rejected(self):
        self.assertIn("NON_TEXT", source_diagnostics({}))
        tampered = self.source.replace("\non:\n", "\nremoved_on:\n", 1)
        self.assertIn("MISSING_TRIGGER", source_diagnostics(tampered))

    def test_readonly_token_does_not_suppress_always_upload_source(self):
        self.assertIn("if: always()", self.source)
        self.assertIn("path: .preflight", self.source)
        self.assertIn("include-hidden-files: true", self.source)
        # A GitHub API read token is not an independent OS no-write mount.

    def test_unreviewed_fourth_job_is_rejected_in_memory(self):
        mutated = self.source.replace(
            "  annual_freeze:\n",
            "  unreviewed_job:\n    runs-on: ubuntu-latest\n  annual_freeze:\n",
            1,
        )
        self.assertIn("JOB_INVENTORY_OR_ORDER_DRIFT",
                      source_diagnostics(mutated))

    def test_duplicate_top_level_trigger_is_rejected_in_memory(self):
        mutated = self.source.replace(
            "\npermissions:\n",
            "\non:\n  push:\n\npermissions:\n",
            1,
        )
        self.assertIn("DUPLICATED_TRIGGER_SOURCE",
                      source_diagnostics(mutated))
