"""DEC-1378: source-only calendar and market matrix coherence checks.

No FMP imports, annual jobs, historical artifact reads, network requests or
production changes. Only tracked Git text and AST literal values.
"""
from __future__ import annotations

import ast
from itertools import product
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ".github/workflows/phase8a-annual-pattern-catalogue.yml"


def tracked(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", "HEAD:" + path], cwd=ROOT, text=True
    )


def literal(source: str, name: str):
    nodes = [
        node.value
        for node in ast.parse(source).body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == name
    ]
    if len(nodes) != 1:
        raise ValueError("missing or duplicated literal: " + name)
    return ast.literal_eval(nodes[0])


def matrix_cells(source: str) -> list[tuple[str, str, int]]:
    fragment = source.split("        dataset:\n", 1)[1].split(
        "\n    steps:\n", 1
    )[0]
    rows = []
    for part in re.split(r"(?m)^          - symbol: ", fragment)[1:]:
        lines = part.splitlines()
        fields = dict(re.findall(
            r"(?m)^            (timeframe|horizon): ([0-9a-z]+)$", part
        ))
        if len(fields) != 2 or "timeframe" not in fields or "horizon" not in fields:
            raise ValueError("missing workflow matrix identity fields")
        rows.append((lines[0].strip(), fields["timeframe"],
                     int(fields["horizon"])))
    return rows


def annual_labels(source: str) -> list[str]:
    fragment = source.split("        options:\n", 1)[1].split(
        "      previous_annual_freeze_run_id:\n", 1
    )[0]
    return re.findall(r'(?m)^          - "([^"]+)"$', fragment)


class AnnualCalendarAndMarketMatrixRemainSourceOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = tracked(WORKFLOW)
        cls.protocol = tracked("src/fmp/discovery/pattern_protocol.py")
        cls.method = tracked(
            "src/fmp/discovery/annual_pattern_catalogue_method.py"
        )
        cls.plan = tracked(
            "src/fmp/discovery/annual_pattern_catalogue_workflow_plan.py"
        )
        cls.symbols = literal(cls.protocol, "SYMBOLS")
        cls.timeframes = literal(cls.protocol, "TIMEFRAMES")
        cls.horizons = literal(cls.protocol, "HORIZONS_MINUTES")
        cls.cells = matrix_cells(cls.workflow)
        cls.labels = annual_labels(cls.workflow)

    def test_market_universe_uses_three_pinned_symbols(self):
        self.assertEqual(self.symbols, ("EURUSD", "GBPUSD", "USDJPY"))

    def test_market_universe_uses_three_timeframes_two_horizons(self):
        self.assertEqual(self.timeframes, ("5m", "15m", "1h"))
        self.assertEqual(self.horizons, (60, 240))

    def test_workflow_cells_equal_frozen_cartesian_market_universe(self):
        self.assertEqual(len(self.cells), 18)
        self.assertEqual(
            set(self.cells),
            set(product(self.symbols, self.timeframes, self.horizons)),
        )

    def test_workflow_has_no_duplicate_cells(self):
        self.assertEqual(len(self.cells), len(set(self.cells)))

    def test_workflow_lists_exactly_twelve_annual_segments(self):
        expected = [str(n) for n in range(2015, 2026)]
        expected.append("2026_YTD_TO_2026_08_20")
        self.assertEqual(self.labels, expected)

    def test_tracked_method_marks_partial_2026_end_boundary(self):
        self.assertIn("COLLECTION_START = date(2015, 1, 1)", self.method)
        self.assertIn("COLLECTION_END_INCLUSIVE = date(2026, 8, 20)",
                      self.method)
        self.assertIn('label="2026_YTD_TO_2026_08_20"', self.method)

    def test_plan_counts_match_three_by_three_by_two_cells(self):
        self.assertIn(
            "CELLS_PER_SEGMENT = len(SYMBOLS) * len(TIMEFRAMES) * len(HORIZONS_MINUTES)",
            self.plan,
        )
        self.assertIn("JOBS_PER_SEGMENT_RUN = CELLS_PER_SEGMENT + 2", self.plan)
        self.assertIn("ARTIFACTS_PER_SEGMENT_RUN = CELLS_PER_SEGMENT + 2",
                      self.plan)
        self.assertIn("FULL_COLLECTION_CELL_COUNT = SEGMENT_COUNT * CELLS_PER_SEGMENT",
                      self.plan)
        self.assertEqual(len(self.labels) * len(self.cells), 216)

    def test_freeze_job_uses_cell_dependency_without_cross_year_trading(self):
        self.assertIn("  annual_cell:\n    needs: annual_preflight",
                      self.workflow)
        self.assertIn("  annual_freeze:\n    needs: annual_cell",
                      self.workflow)
        self.assertIn("STRATEGY_V1_SYNTHESIS_AUTHORIZED = False", self.method)
        self.assertIn("TRADING_AUTHORIZED = False", self.method)

    def test_offline_matrix_mutations_do_not_preserve_exact_inventory(self):
        altered = list(self.cells)
        altered[0] = ("EURUSD", "5m", 999)
        self.assertNotEqual(set(altered),
                            set(product(self.symbols, self.timeframes, self.horizons)))
        dropped = self.cells[:-1]
        self.assertNotEqual(len(dropped), 18)

    def test_offline_annual_segment_mutations_do_not_preserve_calendar(self):
        labels = list(self.labels)
        labels[-1] = "2026"
        expected = [str(n) for n in range(2015, 2026)]
        expected.append("2026_YTD_TO_2026_08_20")
        self.assertNotEqual(labels, expected)
        self.assertNotEqual(len(self.labels[:-1]), 12)
