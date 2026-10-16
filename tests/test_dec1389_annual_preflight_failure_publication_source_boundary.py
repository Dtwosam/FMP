"""DEC-1389 — read-only, non-authorizing preflight step-boundary diagnostics.

No annual command is executed, no real artifact is fetched, and no Actions
token or protected data is used. Mutations affect in-memory YAML text only.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

FETCH = "Fetch exact accepted EXP-044 source snapshots"
VALIDATE = "Validate exact accepted EXP-044 source snapshots"
REQUIRE = "Require separately authorized annual catalogue execution"
UPLOAD = "Upload annual catalogue preflight evidence"


def preflight_review(source: object) -> tuple[str, ...]:
    if type(source) is not str:
        return ("SOURCE_NOT_TEXT",)
    try:
        body = source.split("  annual_preflight:\n", 1)[1].split(
            "  annual_cell:\n", 1
        )[0]
    except IndexError:
        return ("PREFLIGHT_JOB_MISSING",)
    parts = re.split(r"(?m)^      - name: ([^\n]+)\n", body)
    names = parts[1::2]
    chunks = parts[2::2]
    if (len(names) != len(set(names))
            or any(names.count(n) != 1 for n in (FETCH, VALIDATE, REQUIRE, UPLOAD))):
        return ("MISSING_OR_DUPLICATE_REVIEW_STEP",)
    spans = dict(zip(names, chunks))
    issues = []
    if names.index(FETCH) < names.index(REQUIRE):
        issues.append("METADATA_FETCH_BEFORE_EXECUTION_RECHECK")
    if names.index(VALIDATE) < names.index(REQUIRE):
        issues.append("PREFLIGHT_REPORT_BEFORE_EXECUTION_RECHECK")
    raw_metadata = (
        ".preflight/feature-run.json",
        ".preflight/feature-artifacts.json",
        ".preflight/outcome-run.json",
        ".preflight/outcome-artifacts.json",
    )
    if all(name in spans[FETCH] for name in raw_metadata):
        issues.append("SOURCE_METADATA_STAGED_IN_PREFLIGHT_TREE")
    upload = spans[UPLOAD]
    broad_path = re.search(r"(?m)^          path: \.preflight$", upload)
    always = re.search(r"(?m)^        if: always\(\)$", upload)
    if always and broad_path:
        issues.append("PREFLIGHT_ALWAYS_UPLOADS_TREE_ON_FAILURE")
        if re.search(r"(?m)^          include-hidden-files: true$", upload):
            issues.append("UPLOAD_INCLUDE_HIDDEN_SOURCE")
    return tuple(issues)


class SourceOnlyPreflightPublicationRiskIsNotActualLeakEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )

    def test_existing_preflight_has_separate_execution_recheck_after_metadata(self):
        self.assertIn("METADATA_FETCH_BEFORE_EXECUTION_RECHECK",
                      preflight_review(self.source))

    def test_existing_preflight_report_precedes_execution_recheck(self):
        self.assertIn("PREFLIGHT_REPORT_BEFORE_EXECUTION_RECHECK",
                      preflight_review(self.source))

    def test_four_raw_metadata_json_paths_are_staged_inside_preflight_tree(self):
        self.assertIn("SOURCE_METADATA_STAGED_IN_PREFLIGHT_TREE",
                      preflight_review(self.source))

    def test_existing_always_upload_can_attempt_publication_after_failure(self):
        self.assertIn("PREFLIGHT_ALWAYS_UPLOADS_TREE_ON_FAILURE",
                      preflight_review(self.source))

    def test_existing_preflight_upload_includes_hidden_files(self):
        self.assertIn("UPLOAD_INCLUDE_HIDDEN_SOURCE",
                      preflight_review(self.source))

    def test_removing_always_condition_changes_publication_risk_only(self):
        changed = self.source.replace(
            "- name: Upload annual catalogue preflight evidence\n"
            "        if: always()",
            "- name: Upload annual catalogue preflight evidence\n"
            "        if: success()",
            1,
        )
        self.assertNotIn("PREFLIGHT_ALWAYS_UPLOADS_TREE_ON_FAILURE",
                         preflight_review(changed))
        self.assertIn("METADATA_FETCH_BEFORE_EXECUTION_RECHECK",
                      preflight_review(changed))

    def test_narrower_upload_directory_does_not_remove_precheck_metadata_access(self):
        changed = self.source.replace(
            "          path: .preflight\n",
            "          path: .preflight/preflight.json\n",
            1,
        )
        self.assertNotIn("PREFLIGHT_ALWAYS_UPLOADS_TREE_ON_FAILURE",
                         preflight_review(changed))
        self.assertIn("METADATA_FETCH_BEFORE_EXECUTION_RECHECK",
                      preflight_review(changed))

    def test_missing_required_recheck_does_not_count_as_safe(self):
        changed = self.source.replace(
            "- name: Require separately authorized annual catalogue execution",
            "- name: Unknown check removed", 1,
        )
        self.assertIn("MISSING_OR_DUPLICATE_REVIEW_STEP",
                      preflight_review(changed))

    def test_duplicate_execution_recheck_does_not_count_as_safe(self):
        name = "      - name: " + REQUIRE + "\n"
        changed = self.source.replace(name, name + name, 1)
        self.assertIn("MISSING_OR_DUPLICATE_REVIEW_STEP",
                      preflight_review(changed))

    def test_nontext_source_never_passes_source_review(self):
        self.assertEqual(preflight_review({}), ("SOURCE_NOT_TEXT",))

    def test_suffixed_upload_path_is_not_the_full_preflight_directory(self):
        changed = self.source.replace(
            "          path: .preflight\n",
            "          path: .preflight/specific-report.json\n", 1,
        )
        self.assertNotIn("PREFLIGHT_ALWAYS_UPLOADS_TREE_ON_FAILURE",
                         preflight_review(changed))

    def test_fake_always_comment_does_not_pass_active_upload_condition(self):
        changed = self.source.replace(
            "        if: always()\n",
            "        if: success() # if: always()\n", 1,
        )
        self.assertNotIn("PREFLIGHT_ALWAYS_UPLOADS_TREE_ON_FAILURE",
                         preflight_review(changed))

    def test_trailing_path_suffix_comment_not_mistaken_for_exact_broad_root(self):
        changed = self.source.replace(
            "          path: .preflight\n",
            "          path: .preflight  # changed location\n", 1,
        )
        self.assertNotIn("PREFLIGHT_ALWAYS_UPLOADS_TREE_ON_FAILURE",
                         preflight_review(changed))

    def test_broad_directory_and_exact_always_still_flagged(self):
        self.assertIn("PREFLIGHT_ALWAYS_UPLOADS_TREE_ON_FAILURE",
                      preflight_review(self.source))
        self.assertIn("UPLOAD_INCLUDE_HIDDEN_SOURCE",
                      preflight_review(self.source))
