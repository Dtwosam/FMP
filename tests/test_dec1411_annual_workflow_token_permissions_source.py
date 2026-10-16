"""DEC-1411: source-only GitHub token permissions inventory.

Never dispatch workflows, request secrets, edit GitHub settings, run the annual
CLI, or access historical artifacts. A checked-in permissions stanza is not
an admin-policy witness and does not bind a future workflow_dispatch to a SHA.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
JOBS = ("annual_preflight", "annual_cell", "annual_freeze")
EXPECTED_SCOPES = ("  contents: read", "  actions: read")


def scope_source_review(source: object) -> tuple[str, ...]:
    if type(source) is not str:
        return ("NON_TEXT",)
    if "\njobs:\n" not in source:
        return ("WORKFLOW_JOBS_SHAPE_UNREVIEWED",)
    pre, jobs = source.split("\njobs:\n", 1)
    issues = []
    if pre.count("permissions:\n") != 1 or not re.search(
            r"(?m)^permissions:$", pre):
        issues.append("ROOT_PERMISSIONS_SHAPE_UNREVIEWED")
    else:
        body = pre.split("permissions:\n", 1)[1]
        lines = []
        for line in body.splitlines():
            if not line.strip():
                break
            lines.append(line)
        if tuple(lines) != EXPECTED_SCOPES:
            issues.append("ROOT_PERMISSION_SCOPE_DRIFT")
        if len(lines) != len(set(lines)):
            issues.append("ROOT_PERMISSION_DUPLICATE_SCOPE")
    for index, name in enumerate(JOBS):
        marker = "  " + name + ":\n"
        if jobs.count(marker) != 1:
            issues.append("JOB_SHAPE_UNREVIEWED_" + name)
            continue
        part = jobs.split(marker, 1)[1]
        if index + 1 < len(JOBS):
            next_marker = "  " + JOBS[index + 1] + ":\n"
            if next_marker not in part:
                issues.append("JOB_SHAPE_UNREVIEWED_" + name)
                continue
            part = part.split(next_marker, 1)[0]
        if re.search(r"(?m)^    permissions\s*:", part):
            issues.append("JOB_PERMISSION_OVERRIDE_UNREVIEWED_" + name)
    return tuple(sorted(set(issues)))


class CheckedInTokenScopesAreNotRealAdminAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )

    def test_current_source_has_expected_read_only_scopes(self):
        self.assertEqual(scope_source_review(self.source), ())

    def test_both_scopes_are_explicitly_named_read(self):
        self.assertIn("permissions:\n  contents: read\n  actions: read\n",
                      self.source)

    def test_contents_write_scope_requires_review(self):
        changed = self.source.replace("  contents: read\n",
                                      "  contents: write\n", 1)
        self.assertIn("ROOT_PERMISSION_SCOPE_DRIFT",
                      scope_source_review(changed))

    def test_actions_write_scope_requires_review(self):
        changed = self.source.replace("  actions: read\n",
                                      "  actions: write\n", 1)
        self.assertIn("ROOT_PERMISSION_SCOPE_DRIFT",
                      scope_source_review(changed))

    def test_explicit_id_token_write_requires_review(self):
        changed = self.source.replace(
            "  actions: read\n",
            "  actions: read\n  id-token: write\n", 1)
        self.assertIn("ROOT_PERMISSION_SCOPE_DRIFT",
                      scope_source_review(changed))

    def test_any_new_scope_requires_review(self):
        changed = self.source.replace(
            "  actions: read\n", "  actions: read\n  pull-requests: read\n", 1)
        self.assertIn("ROOT_PERMISSION_SCOPE_DRIFT",
                      scope_source_review(changed))

    def test_removed_actions_read_requires_review(self):
        changed = self.source.replace("  actions: read\n", "", 1)
        self.assertIn("ROOT_PERMISSION_SCOPE_DRIFT",
                      scope_source_review(changed))

    def test_duplicate_yaml_permission_scope_is_rejected(self):
        changed = self.source.replace(
            "  actions: read\n", "  actions: read\n  actions: read\n", 1)
        self.assertIn("ROOT_PERMISSION_DUPLICATE_SCOPE",
                      scope_source_review(changed))

    def test_duplicate_root_permissions_block_is_rejected(self):
        changed = self.source.replace(
            "\njobs:\n",
            "\npermissions:\n  contents: read\n  actions: read\n\njobs:\n", 1)
        self.assertIn("ROOT_PERMISSIONS_SHAPE_UNREVIEWED",
                      scope_source_review(changed))

    def test_shorthand_permission_policy_requires_review(self):
        changed = self.source.replace(
            "permissions:\n  contents: read\n  actions: read\n",
            "permissions: write-all\n", 1)
        self.assertIn("ROOT_PERMISSIONS_SHAPE_UNREVIEWED",
                      scope_source_review(changed))

    def test_preflight_job_local_override_requires_review(self):
        changed = self.source.replace(
            "  annual_preflight:\n",
            "  annual_preflight:\n    permissions:\n      actions: write\n",
            1)
        self.assertIn("JOB_PERMISSION_OVERRIDE_UNREVIEWED_annual_preflight",
                      scope_source_review(changed))

    def test_cell_job_local_override_requires_review(self):
        changed = self.source.replace(
            "  annual_cell:\n",
            "  annual_cell:\n    permissions:\n      contents: write\n",
            1)
        self.assertIn("JOB_PERMISSION_OVERRIDE_UNREVIEWED_annual_cell",
                      scope_source_review(changed))

    def test_freeze_job_local_override_requires_review(self):
        changed = self.source.replace(
            "  annual_freeze:\n",
            "  annual_freeze:\n    permissions: write-all\n", 1)
        self.assertIn("JOB_PERMISSION_OVERRIDE_UNREVIEWED_annual_freeze",
                      scope_source_review(changed))

    def test_nontext_review_input_is_rejected(self):
        self.assertEqual(scope_source_review({}), ("NON_TEXT",))
