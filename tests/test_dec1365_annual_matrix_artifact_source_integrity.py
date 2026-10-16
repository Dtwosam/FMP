"""DEC-1365: offline tests of the committed annual workflow matrix, no dispatch.

This reads only git show HEAD:...; it never fetches historical artifacts,
invokes the annual CLI, or decides that annual execution is authorized.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import product
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"
REQUIRED = frozenset((
    "symbol", "timeframe", "horizon", "feature_artifact_id",
    "feature_zip_sha256", "outcome_artifact_id", "outcome_zip_sha256",
))
SYMBOLS = frozenset(("EURUSD", "GBPUSD", "USDJPY"))
TIMEFRAMES = frozenset(("5m", "15m", "1h"))
HORIZONS = frozenset(("60", "240"))


def parse_committed_matrix(source: str) -> list[dict[str, str]]:
    """A deliberately narrow parser for the reviewed YAML source structure."""
    matrix = source.split("        dataset:\n", 1)[1].split("\n    steps:\n", 1)[0]
    parts = re.split(r"(?m)^          - symbol: ", matrix)
    rows = []
    for fragment in parts[1:]:
        symbol, _, tail = fragment.partition("\n")
        row = {"symbol": symbol.strip()}
        fields = re.findall(r"(?m)^            ([a-z_]+): (.+)$", tail)
        for name, value in fields:
            if name in row:
                raise ValueError("duplicate matrix field")
            row[name] = value.strip().strip('"')
        rows.append(row)
    return rows


def matrix_violations(rows: list[dict[str, str]]) -> tuple[str, ...]:
    """Non-authorizing diagnostics for this exact, tracked matrix shape."""
    problems = []
    if len(rows) != 18:
        problems.append("WRONG_ROW_COUNT")
    expected = set(product(SYMBOLS, TIMEFRAMES, HORIZONS))
    actual = []
    by_pair = defaultdict(list)
    for row in rows:
        if set(row) != REQUIRED:
            problems.append("MISSING_OR_EXTRA_FIELDS")
            continue
        key = (row["symbol"], row["timeframe"], row["horizon"])
        actual.append(key)
        by_pair[key[:2]].append(row)
        for field in ("feature_artifact_id", "outcome_artifact_id"):
            value = row[field]
            if not value.isascii() or not value.isdecimal() or int(value) <= 0:
                problems.append("INVALID_ARTIFACT_ID")
        for field in ("feature_zip_sha256", "outcome_zip_sha256"):
            if re.fullmatch("[0-9a-f]{64}", row[field]) is None:
                problems.append("INVALID_DIGEST")
    if len(actual) != len(set(actual)) or set(actual) != expected:
        problems.append("INCOMPLETE_OR_DUPLICATED_MATRIX")
    for pair, group in by_pair.items():
        for field in (
            "feature_artifact_id", "outcome_artifact_id",
            "feature_zip_sha256", "outcome_zip_sha256",
        ):
            if len({row[field] for row in group}) > 1:
                problems.append("CONFLICTING_PAIR_SOURCE_" + field)
    return tuple(sorted(set(problems)))


class AnnualCellMatrixArtifactSourceCannotAuthorizeExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = subprocess.check_output(
            ["git", "show", WORKFLOW], cwd=ROOT, text=True
        )
        cls.rows = parse_committed_matrix(cls.source)

    def test_exact_eighteen_cell_rows(self):
        self.assertEqual(len(self.rows), 18)
        self.assertEqual(matrix_violations(self.rows), ())

    def test_all_three_symbols_three_timeframes_two_horizons(self):
        actual = {(r["symbol"], r["timeframe"], r["horizon"])
                  for r in self.rows}
        self.assertEqual(actual, set(product(SYMBOLS, TIMEFRAMES, HORIZONS)))

    def test_all_fields_are_present_without_extras(self):
        for i, row in enumerate(self.rows):
            with self.subTest(i=i):
                self.assertEqual(set(row), REQUIRED)

    def test_feature_source_id_and_digest_do_not_change_with_horizon(self):
        groups = defaultdict(set)
        for row in self.rows:
            groups[(row["symbol"], row["timeframe"])].add(
                (row["feature_artifact_id"], row["feature_zip_sha256"]))
        self.assertEqual(len(groups), 9)
        self.assertTrue(all(len(v) == 1 for v in groups.values()))

    def test_outcome_source_id_and_digest_do_not_change_with_horizon(self):
        groups = defaultdict(set)
        for row in self.rows:
            groups[(row["symbol"], row["timeframe"])].add(
                (row["outcome_artifact_id"], row["outcome_zip_sha256"]))
        self.assertEqual(len(groups), 9)
        self.assertTrue(all(len(v) == 1 for v in groups.values()))

    def test_every_digest_is_lowercase_sha256_shape(self):
        for i, row in enumerate(self.rows):
            for field in ("feature_zip_sha256", "outcome_zip_sha256"):
                with self.subTest(i=i, field=field):
                    self.assertRegex(row[field], r"\A[0-9a-f]{64}\Z")

    def test_artifact_identifiers_are_positive_decimal_strings(self):
        for row in self.rows:
            for field in ("feature_artifact_id", "outcome_artifact_id"):
                with self.subTest(symbol=row["symbol"], field=field):
                    value = row[field]
                    self.assertTrue(value.isascii() and value.isdecimal())
                    self.assertGreater(int(value), 0)

    def test_duplicate_matrix_entry_fails_source_shape_review(self):
        changed = [dict(row) for row in self.rows]
        changed[0] = dict(changed[1])
        self.assertIn("INCOMPLETE_OR_DUPLICATED_MATRIX",
                      matrix_violations(changed))

    def test_missing_matrix_entry_fails_source_shape_review(self):
        self.assertIn("WRONG_ROW_COUNT", matrix_violations(self.rows[:-1]))

    def test_swapped_digest_for_one_horizon_fails_pair_binding(self):
        changed = [dict(row) for row in self.rows]
        changed[0]["feature_zip_sha256"] = changed[2]["feature_zip_sha256"]
        self.assertIn("CONFLICTING_PAIR_SOURCE_feature_zip_sha256",
                      matrix_violations(changed))

    def test_missing_or_invalid_digest_fails_source_shape_review(self):
        changed = [dict(row) for row in self.rows]
        changed[0]["outcome_zip_sha256"] = "NOT_SHA256"
        self.assertIn("INVALID_DIGEST", matrix_violations(changed))
        del changed[0]["feature_artifact_id"]
        self.assertIn("MISSING_OR_EXTRA_FIELDS", matrix_violations(changed))

    def test_workflow_checks_archive_digest_before_unzip(self):
        cell = self.source.split("  annual_cell:\n", 1)[1].split(
            "  annual_freeze:\n", 1)[0]
        self.assertLess(cell.index('actual_sha="$(sha256sum "$destination"'),
                        cell.index('test "$actual_sha" = "$expected_sha"'))
        self.assertLess(cell.index('test "$actual_sha" = "$expected_sha"'),
                        cell.index("unzip -q .downloads/feature.zip"))
        self.assertIn('download_exact "$FEATURE_ARTIFACT_ID" "$FEATURE_ZIP_SHA256"', cell)
        self.assertIn('download_exact "$OUTCOME_ARTIFACT_ID" "$OUTCOME_ZIP_SHA256"', cell)
