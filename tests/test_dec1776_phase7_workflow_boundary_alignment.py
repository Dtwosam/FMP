"""DEC-1776: offline cross-file boundary check for *historic* Phase7 only.

This parses text and source declarations; it never executes workflow code,
fetches artifacts, validates actual market bars, or authorizes later research.
"""
import ast
from datetime import date, timedelta
import hashlib
from pathlib import Path
import re
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".github" / "workflows" / "phase7-walk-forward.yml"
REPLAY = ROOT / "scripts" / "dec1764_phase7_historical_cost_stress.py"
FROZEN_WORKFLOW_GIT_BLOB = "2ab8bd26a82a4561a24e6efc179552df8b919284"


def frozen_stage2_windows_from_workflow(source_text):
    """Extract a static literal, never eval/execute YAML or a workflow."""
    prefix = "          expected_windows = [\n"
    suffix = "\n          ]"
    if source_text.count(prefix) != 1:
        raise ValueError("expected a single historic Stage2 window declaration")
    rest = source_text.split(prefix, 1)[1]
    if suffix not in rest:
        raise ValueError("historic window literal was truncated")
    literal = "[" + rest.split(suffix, 1)[0] + "]"
    try:
        rows = ast.literal_eval(literal)
    except (SyntaxError, ValueError, TypeError) as exc:
        raise ValueError("historic Stage2 window declaration is not a literal") from exc
    if type(rows) is not list or len(rows) != 7 or any(
        type(item) is not tuple
        or len(item) != 3
        or any(type(p) is not str for p in item) for item in rows
    ):
        raise ValueError("historic Stage2 requires seven literal triples")
    return rows


class HistoricPhase7WorkflowDateAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_bytes = SOURCE.read_bytes()
        cls.source = cls.source_bytes.decode("utf-8")
        cls.workflow_windows = frozen_stage2_windows_from_workflow(cls.source)
        cls.replay_module = runpy.run_path(str(REPLAY))
        cls.history = cls.replay_module["replay_phase7_cost_evidence"]()
        cls.documented = cls.history["published_historical_window_schedule"]

    def test_frozen_documentary_workflow_source_identity(self):
        payload = self.source_bytes
        git_blob = hashlib.sha1(
            b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload
        ).hexdigest()
        self.assertEqual(git_blob, FROZEN_WORKFLOW_GIT_BLOB)

    def test_workflow_date_literals_match_frozen_historical_report(self):
        actual = [
            (
                row["window"],
                row["scored_start_inclusive"] + "T00:00:00Z",
                row["scored_end_exclusive"] + "T00:00:00Z",
            )
            for row in self.documented
        ]
        self.assertEqual(self.workflow_windows, actual)
        self.assertEqual(len(actual), 7)
        self.assertEqual(actual[-1][2], "2026-08-21T00:00:00Z")

    def test_original_source_checks_warmup_and_partition_access(self):
        for snippet in (
            "assert warmup_end == scored_start",
            "assert warmup_start == scored_start - timedelta(days=7)",
            "assert row['opened_partition_keys'] == expected_partition_keys(",
            "assert scored_end <= parse_utc('2026-08-21T00:00:00Z')",
            "if actual_windows != expected_windows:",
            "recomputed_gate = stage2_gate(rows_for_gate)",
        ):
            with self.subTest(assertion=snippet):
                self.assertIn(snippet, self.source)

    def test_declared_scored_ranges_are_consecutive_utc_exclusive(self):
        for index, (_, start, end) in enumerate(self.workflow_windows):
            self.assertTrue(start.endswith("T00:00:00Z"))
            self.assertTrue(end.endswith("T00:00:00Z"))
            parsed_start = date.fromisoformat(start[:10])
            parsed_end = date.fromisoformat(end[:10])
            self.assertLess(parsed_start, parsed_end)
            self.assertEqual(
                self.documented[index]["reported_warmup_start_inclusive"],
                (parsed_start - timedelta(days=7)).isoformat(),
            )
            if index:
                self.assertEqual(start, self.workflow_windows[index-1][2])

    def test_synthetic_bad_workflow_cutoff_fails_historical_alignment(self):
        changed = self.source.replace(
            "'2026-08-21T00:00:00Z'),",
            "'2026-08-22T00:00:00Z'),",
            1,
        )
        self.assertNotEqual(changed, self.source)
        parsed = frozen_stage2_windows_from_workflow(changed)
        self.assertNotEqual(parsed, self.workflow_windows)
        self.assertNotEqual(
            parsed[-1][2],
            self.documented[-1]["scored_end_exclusive"] + "T00:00:00Z",
        )

    def test_workflow_literal_parser_refuses_nonliteral_code(self):
        altered = self.source.replace(
            "('2025-Q1', '2025-01-01T00:00:00Z', '2025-04-01T00:00:00Z')",
            "('2025-Q1', __import__('os').getcwd(), '2025-04-01T00:00:00Z')",
            1,
        )
        self.assertNotEqual(altered, self.source)
        with self.assertRaisesRegex(ValueError, "not a literal"):
            frozen_stage2_windows_from_workflow(altered)

    def test_historical_workflow_alignment_is_not_live_runner_proof(self):
        self.assertTrue(
            self.history["historic_schedule_is_documentary_not_data_leakage_witness"])
        self.assertIs(
            self.history["phase8a_strategy_v1_edge_proven"], False)
        self.assertIs(
            self.history["protected_2023_run385_authorized"], False)
        self.assertIsNone(
            self.history["external_current_provenance_witness"])
        self.assertEqual(self.history["allowed_actions"], [])
