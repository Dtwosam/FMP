"""DEC-1376: Cross-check TWO COMMITTED SOURCE BLOBS, never real artifacts.

This uses git show and ast.literal_eval only. No FMP module is imported,
no GitHub API is called, and no protected historic evidence is opened.
"""
from __future__ import annotations

import ast
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


def tracked(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", "HEAD:" + path], cwd=ROOT, text=True
    )


def matrix_rows(source: str) -> list[dict[str, str]]:
    block = source.split("        dataset:\n", 1)[1].split("\n    steps:\n", 1)[0]
    rows = []
    for chunk in re.split(r"(?m)^          - symbol: ", block)[1:]:
        symbol, _, remainder = chunk.partition("\n")
        fields = re.findall(r"(?m)^            ([a-z0-9_]+): (.+)$", remainder)
        row = {"symbol": symbol.strip()}
        for name, raw in fields:
            if name in row:
                raise ValueError("duplicate annual matrix field")
            row[name] = raw.strip().strip('"')
        rows.append(row)
    return rows


def artifact_pins(source: str) -> tuple[dict, dict, dict]:
    tree = ast.parse(source)
    wanted = {
        "_CELL_SOURCE_ARTIFACTS", "FEATURE_EVIDENCE_ARTIFACT",
        "OUTCOME_EVIDENCE_ARTIFACT",
    }
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in wanted:
                found[target.id] = ast.literal_eval(node.value)
    if set(found) != wanted:
        raise ValueError("missing tracked EXP-044 source pin")
    return (
        found["_CELL_SOURCE_ARTIFACTS"],
        found["FEATURE_EVIDENCE_ARTIFACT"],
        found["OUTCOME_EVIDENCE_ARTIFACT"],
    )


def mismatched_pairs(rows: list[dict[str, str]], pins: dict) -> tuple:
    bad = []
    expected_fields = {
        "feature_artifact_id": ("feature_id", int),
        "outcome_artifact_id": ("outcome_id", int),
        "feature_zip_sha256": ("feature_digest", lambda x: "sha256:" + x),
        "outcome_zip_sha256": ("outcome_digest", lambda x: "sha256:" + x),
    }
    for row in rows:
        key = (row.get("symbol"), row.get("timeframe"))
        expected = pins.get(key)
        if expected is None:
            bad.append((key, "missing_source_pair"))
            continue
        for field, (target, converter) in expected_fields.items():
            try:
                observed = converter(row[field])
            except (KeyError, ValueError, TypeError):
                bad.append((key, field))
                continue
            if observed != expected[target]:
                bad.append((key, field))
    return tuple(bad)


class AnnualSourcePinsMustNotBeConfusedWithExternalAuthenticity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.annual = tracked(".github/workflows/phase8a-annual-pattern-catalogue.yml")
        source = tracked("src/fmp/discovery/workflow_source.py")
        cls.pins, cls.feature_evidence, cls.outcome_evidence = artifact_pins(source)
        cls.rows = matrix_rows(cls.annual)
        cls.cell = cls.annual.split("  annual_cell:\n", 1)[1].split(
            "  annual_freeze:\n", 1)[0]

    def test_nine_source_pairs_and_eighteen_annual_cells(self):
        self.assertEqual(len(self.pins), 9)
        self.assertEqual(len(self.rows), 18)

    def test_source_pair_universe_exactly_matches_matrix_pairs(self):
        self.assertEqual(
            set(self.pins),
            {(r["symbol"], r["timeframe"]) for r in self.rows},
        )

    def test_every_cell_feature_source_id_matches_upstream_inventory(self):
        for row in self.rows:
            with self.subTest(row=row["symbol"] + row["timeframe"] + row["horizon"]):
                pin = self.pins[(row["symbol"], row["timeframe"])]
                self.assertEqual(int(row["feature_artifact_id"]), pin["feature_id"])

    def test_every_cell_feature_sha256_matches_upstream_inventory(self):
        for row in self.rows:
            pin = self.pins[(row["symbol"], row["timeframe"])]
            self.assertEqual("sha256:" + row["feature_zip_sha256"],
                             pin["feature_digest"])

    def test_every_cell_outcome_id_matches_upstream_inventory(self):
        for row in self.rows:
            pin = self.pins[(row["symbol"], row["timeframe"])]
            self.assertEqual(int(row["outcome_artifact_id"]), pin["outcome_id"])

    def test_every_cell_outcome_sha256_matches_upstream_inventory(self):
        for row in self.rows:
            pin = self.pins[(row["symbol"], row["timeframe"])]
            self.assertEqual("sha256:" + row["outcome_zip_sha256"],
                             pin["outcome_digest"])

    def test_evidence_ids_match_tracked_exp044_source_inventory(self):
        for role, pin in (("FEATURE", self.feature_evidence),
                          ("OUTCOME", self.outcome_evidence)):
            name = role + "_EVIDENCE_ARTIFACT_ID"
            match = re.search(r"(?m)^          " + name + r': "([0-9]+)"$', self.cell)
            self.assertIsNotNone(match, name)
            self.assertEqual(int(match.group(1)), pin["id"])

    def test_evidence_sha256_values_match_exp044_source_inventory(self):
        for role, pin in (("FEATURE", self.feature_evidence),
                          ("OUTCOME", self.outcome_evidence)):
            name = role + "_EVIDENCE_ZIP_SHA256"
            match = re.search(r"(?m)^          " + name + r': ([0-9a-f]{64})$', self.cell)
            self.assertIsNotNone(match, name)
            self.assertEqual("sha256:" + match.group(1), pin["digest"])

    def test_every_matrix_pair_horizon_agrees_with_source_inventory(self):
        self.assertEqual(mismatched_pairs(self.rows, self.pins), ())

    def test_offline_single_digest_or_id_mutation_is_detected(self):
        changed = [dict(x) for x in self.rows]
        changed[0]["feature_zip_sha256"] = "0" * 64
        changed[1]["outcome_artifact_id"] = "999999999"
        bad = mismatched_pairs(changed, self.pins)
        self.assertIn((("EURUSD", "5m"), "feature_zip_sha256"), bad)
        self.assertIn((("EURUSD", "5m"), "outcome_artifact_id"), bad)
