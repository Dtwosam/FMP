"""DEC-1368: source-only cell artifact/staging bindings; NEVER annual work.

All inspection operates on committed text loaded locally from git show HEAD.
No workflow dispatch, artifact reads, historical annual CLI run or trading.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
BLOB = "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED = (
    ('FEATURE_ARTIFACT_ID', 'FEATURE_ZIP_SHA256', '.downloads/feature.zip'),
    ('OUTCOME_ARTIFACT_ID', 'OUTCOME_ZIP_SHA256', '.downloads/outcome.zip'),
    ('FEATURE_EVIDENCE_ARTIFACT_ID', 'FEATURE_EVIDENCE_ZIP_SHA256',
     '.downloads/feature-evidence.zip'),
    ('OUTCOME_EVIDENCE_ARTIFACT_ID', 'OUTCOME_EVIDENCE_ZIP_SHA256',
     '.downloads/outcome-evidence.zip'),
)


def download_binding_problems(cell: str) -> tuple[str, ...]:
    problems = []
    for artifact, digest, destination in EXPECTED:
        expected = 'download_exact "$' + artifact + '" "$' + digest + '" ' + destination
        if cell.count(expected) != 1:
            problems.append("ABSENT_OR_DUPLICATE_DOWNLOAD_" + artifact)
    for destination, extract in (
        ('.downloads/feature.zip', '.feature'),
        ('.downloads/outcome.zip', '.outcome'),
        ('.downloads/feature-evidence.zip', '.feature-evidence'),
        ('.downloads/outcome-evidence.zip', '.outcome-evidence'),
    ):
        if cell.count(f'unzip -q {destination} -d {extract}') != 1:
            problems.append("ABSENT_OR_DUPLICATE_UNZIP_" + destination)
    return tuple(problems)


class CellEvidenceArchivesRemainSourceOnlyNotOSIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = subprocess.check_output(["git", "show", BLOB],
                                         cwd=ROOT, text=True)
        cls.cell = source.split("  annual_cell:\n", 1)[1].split(
            "  annual_freeze:\n", 1)[0]

    def test_four_download_id_digest_destination_bindings_are_unique(self):
        self.assertEqual(download_binding_problems(self.cell), ())

    def test_archive_digest_checker_precedes_any_extraction(self):
        s = self.cell
        self.assertLess(s.index('"repos/$GITHUB_REPOSITORY/actions/artifacts/$artifact_id/zip"'),
                        s.index('actual_sha="$(sha256sum "$destination"'))
        self.assertLess(s.index('actual_sha="$(sha256sum "$destination"'),
                        s.index('test "$actual_sha" = "$expected_sha"'))
        self.assertLess(s.index('test "$actual_sha" = "$expected_sha"'),
                        s.index('unzip -q .downloads/feature.zip'))

    def test_four_artifacts_download_before_first_unzip(self):
        first_extract = self.cell.index("unzip -q .downloads/feature.zip")
        for artifact, digest, destination in EXPECTED:
            with self.subTest(destination=destination):
                call = 'download_exact "$' + artifact + '" "$' + digest + '" ' + destination
                self.assertLess(self.cell.index(call), first_extract)

    def test_evidence_artifact_id_and_sha_literals_are_configured(self):
        for name in ('FEATURE_EVIDENCE_ARTIFACT_ID', 'OUTCOME_EVIDENCE_ARTIFACT_ID'):
            match = re.search(r'(?m)^\s+' + name + r': "([0-9]+)"$', self.cell)
            self.assertIsNotNone(match, name)
            self.assertGreater(int(match.group(1)), 0)
        for name in ('FEATURE_EVIDENCE_ZIP_SHA256',
                     'OUTCOME_EVIDENCE_ZIP_SHA256'):
            match = re.search(r'(?m)^\s+' + name + r': ([0-9a-f]{64})$', self.cell)
            self.assertIsNotNone(match, name)

    def test_archive_extract_destinations_are_four_distinct_relative_paths(self):
        self.assertIn(
            "mkdir -p .downloads .feature .outcome .feature-evidence .outcome-evidence",
            self.cell)
        for _artifact, _digest, destination in EXPECTED:
            self.assertTrue(destination.startswith(".downloads/"))
        self.assertEqual(len({row[2] for row in EXPECTED}), 4)

    def test_resolver_finds_exactly_one_manifest_and_evidence_file_each(self):
        s = self.cell.split("- name: Resolve exact extracted source roots", 1)[1].split(
            "- name: Run frozen annual catalogue cell", 1)[0]
        for target in ('find .feature -type f -name manifest.json',
                       'find .outcome -type f -name manifest.json',
                       "find .feature-evidence -type f -name 'feature-evidence.json'",
                       "find .outcome-evidence -type f -name 'outcome-evidence.json'"):
            with self.subTest(target=target):
                self.assertIn(target, s)
        self.assertGreaterEqual(s.count('= "1"'), 4)

    def test_downstream_cell_receives_resolved_roots_and_evidence_variables(self):
        s = self.cell
        for value in ('steps.roots.outputs.feature_root',
                      'steps.roots.outputs.outcome_root',
                      'steps.roots.outputs.feature_evidence',
                      'steps.roots.outputs.outcome_evidence'):
            with self.subTest(value=value):
                self.assertIn(value, s)

    def test_cell_output_remains_checkout_relative_not_an_os_proof(self):
        s = self.cell
        self.assertIn("mkdir -p .result", s)
        self.assertIn("--evidence-out .result/cell-evidence.json", s)
        self.assertIn("--catalogue-out .result/catalogue-payload.json", s)
        self.assertIn("path: .result", s)
        self.assertIn("uses: actions/upload-artifact@v6", s)

    def test_cell_sha_argument_is_ci_sha_not_approved_external_dispatch_sha(self):
        s = self.cell
        self.assertIn('--code-commit "$GITHUB_SHA"', s)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', s)
        self.assertNotIn("independent_approved_dispatch_sha", s)

    def test_swapped_and_missing_download_bindings_are_detected_offline(self):
        s = self.cell
        tampered = s.replace(
            'download_exact "$FEATURE_ARTIFACT_ID" "$FEATURE_ZIP_SHA256" .downloads/feature.zip',
            'download_exact "$OUTCOME_ARTIFACT_ID" "$FEATURE_ZIP_SHA256" .downloads/feature.zip',
            1)
        self.assertIn("ABSENT_OR_DUPLICATE_DOWNLOAD_FEATURE_ARTIFACT_ID",
                      download_binding_problems(tampered))
        removed = s.replace('unzip -q .downloads/outcome.zip -d .outcome', '', 1)
        self.assertIn("ABSENT_OR_DUPLICATE_UNZIP_.downloads/outcome.zip",
                      download_binding_problems(removed))
