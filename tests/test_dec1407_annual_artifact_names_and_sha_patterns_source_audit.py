"""DEC-1407: committed annual artifact naming and match-pattern review.

All workflow parsing is read-only git show and pure in-memory text;
no Actions artifact is downloaded and no workflow is dispatched.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
LABEL = "$" + "{{ inputs.annual_segment_label }}"
SHA = "$" + "{{ github.sha }}"
SYMBOL = "$" + "{{ matrix.dataset.symbol }}"
TF = "$" + "{{ matrix.dataset.timeframe }}"
HORIZON = "$" + "{{ matrix.dataset.horizon }}"
PREFLIGHT = "phase8a-annual-catalogue-preflight-" + LABEL + "-" + SHA
CELL = ("phase8a-annual-catalogue-cell-" + LABEL + "-"
        + SYMBOL + "-" + TF + "-" + HORIZON + "m-" + SHA)
CELL_PATTERN = "phase8a-annual-catalogue-cell-" + LABEL + "-*-*-*m-" + SHA
FREEZE = "phase8a-annual-catalogue-freeze-" + LABEL + "-" + SHA
JOBS = ("annual_preflight", "annual_cell", "annual_freeze")


def source_steps(source: str, name: str) -> dict[str, str]:
    if name not in JOBS:
        raise ValueError("unrecognized annual job")
    fragment = source.split("  " + name + ":\n", 1)[1]
    idx = JOBS.index(name) + 1
    if idx < len(JOBS):
        fragment = fragment.split("  " + JOBS[idx] + ":\n", 1)[0]
    parts = re.split(r"(?m)^      - name: ([^\n]+)\n", fragment)
    names = parts[1::2]
    if len(names) != len(set(names)):
        raise ValueError("ambiguous duplicate job step")
    return dict(zip(names, parts[2::2]))


def artifact_pattern_problems(source: object) -> tuple[str, ...]:
    if type(source) is not str:
        return ("NON_TEXT_WORKFLOW",)
    try:
        pre = source_steps(source, "annual_preflight")[
            "Upload annual catalogue preflight evidence"
        ]
        cell = source_steps(source, "annual_cell")[
            "Upload annual catalogue cell product"
        ]
        freeze_steps = source_steps(source, "annual_freeze")
        download = freeze_steps["Download all 18 annual catalogue cell products"]
        freeze = freeze_steps["Upload annual segment freeze evidence"]
    except (KeyError, ValueError, IndexError):
        return ("REQUIRED_ARTIFACT_STEP_ABSENT_OR_AMBIGUOUS",)
    problems = []
    for name, chunk, expected in (
        ("PREFLIGHT", pre, PREFLIGHT),
        ("CELL", cell, CELL),
        ("FREEZE", freeze, FREEZE),
    ):
        actual = re.findall(r"(?m)^          name: ([^\n]+)$", chunk)
        if actual != [expected]:
            problems.append(name + "_ARTIFACT_IDENTITY_DRIFT")
    observed = re.findall(r"(?m)^          pattern: ([^\n]+)$", download)
    if observed != [CELL_PATTERN]:
        problems.append("FREEZE_CELL_SOURCE_PATTERN_DRIFT")
    if re.findall(r"(?m)^          path: ([^\n]+)$", download) != [".cell-results"]:
        problems.append("FREEZE_STAGING_ROOT_DRIFT")
    if re.findall(r"(?m)^          merge-multiple: ([^\n]+)$", download) != ["false"]:
        problems.append("FREEZE_MERGE_MULTIPLE_DRIFT")
    return tuple(problems)


class SourceArtifactNameEqualityIsNotServerOrOriginalProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )

    def test_committed_source_has_exact_name_and_download_pattern_contract(self):
        self.assertEqual(artifact_pattern_problems(self.source), ())

    def test_preflight_name_embeds_segment_and_current_github_sha(self):
        step = source_steps(self.source, "annual_preflight")[
            "Upload annual catalogue preflight evidence"
        ]
        self.assertIn("          name: " + PREFLIGHT, step)

    def test_cell_name_embeds_segment_matrix_dimensions_and_github_sha(self):
        step = source_steps(self.source, "annual_cell")[
            "Upload annual catalogue cell product"
        ]
        self.assertIn("          name: " + CELL, step)

    def test_freeze_download_pattern_matches_cell_dimensions_and_github_sha(self):
        step = source_steps(self.source, "annual_freeze")[
            "Download all 18 annual catalogue cell products"
        ]
        self.assertIn("          pattern: " + CELL_PATTERN, step)
        self.assertIn("          merge-multiple: false", step)

    def test_freeze_publication_name_embeds_segment_and_github_sha(self):
        step = source_steps(self.source, "annual_freeze")[
            "Upload annual segment freeze evidence"
        ]
        self.assertIn("          name: " + FREEZE, step)

    def test_preflight_name_mutated_to_github_ref_is_rejected(self):
        changed = self.source.replace(
            "          name: " + PREFLIGHT,
            "          name: " + PREFLIGHT.replace(SHA, "$" + "{{ github.ref }}"), 1
        )
        self.assertIn("PREFLIGHT_ARTIFACT_IDENTITY_DRIFT",
                      artifact_pattern_problems(changed))

    def test_cell_name_missing_horizon_is_rejected(self):
        changed = self.source.replace(
            "          name: " + CELL,
            "          name: " + CELL.replace("-" + HORIZON + "m-", "-"), 1,
        )
        self.assertIn("CELL_ARTIFACT_IDENTITY_DRIFT",
                      artifact_pattern_problems(changed))

    def test_freeze_download_wildcard_instead_of_sha_is_rejected(self):
        changed = self.source.replace(
            "          pattern: " + CELL_PATTERN,
            "          pattern: " + CELL_PATTERN.replace(SHA, "*"), 1,
        )
        self.assertIn("FREEZE_CELL_SOURCE_PATTERN_DRIFT",
                      artifact_pattern_problems(changed))

    def test_freeze_staging_path_mutation_is_rejected(self):
        changed = self.source.replace(
            "          path: .cell-results\n",
            "          path: .another-root\n", 1,
        )
        self.assertIn("FREEZE_STAGING_ROOT_DRIFT",
                      artifact_pattern_problems(changed))

    def test_merge_multiple_true_is_rejected(self):
        changed = self.source.replace(
            "          merge-multiple: false\n",
            "          merge-multiple: true\n", 1,
        )
        self.assertIn("FREEZE_MERGE_MULTIPLE_DRIFT",
                      artifact_pattern_problems(changed))

    def test_duplicate_artifact_name_property_is_rejected(self):
        marker = "          name: " + CELL + "\n"
        changed = self.source.replace(marker, marker + marker, 1)
        self.assertIn("CELL_ARTIFACT_IDENTITY_DRIFT",
                      artifact_pattern_problems(changed))

    def test_nontext_source_never_passes(self):
        self.assertEqual(artifact_pattern_problems({}),
                         ("NON_TEXT_WORKFLOW",))
