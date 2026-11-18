from __future__ import annotations

import json
import unittest
from pathlib import Path

from fmp.research.trial_inventory import (
    ELIGIBLE_FOR_BY_ADJUSTMENT,
    INSUFFICIENT_STATISTICAL_EVIDENCE,
    INSUFFICIENT_TRIAL_CENSUS,
    VERIFIED,
    build_inventory,
    family_correction_status,
    inventory_json,
)
from fmp.research.trial_ledger import LEDGER_PATH

ROOT = Path(__file__).resolve().parents[1]


def _ledger_line(**overrides: object) -> str:
    record = {
        "trial_id": "EXP-20260101-001",
        "recorded_on": "2026-01-01",
        "hypothesis": "A stated rule was evaluated.",
        "version": "grid",
        "parameters": {},
        "data_exposure": {"overlaps_2015_2022": True, "untouched_validation": False},
        "cost_assumptions": "bid/ask",
        "source_commit": "abc1234",
        "outcome": "recorded",
        "statistical_evidence": {
            "available": True,
            "trial_count": 4,
            "result_rows": 8,
            "note": "4 configurations were evaluated. This is not the programme-wide count.",
        },
    }
    record.update(overrides)
    return json.dumps(record, sort_keys=True) + "\n"


class TrialInventoryTests(unittest.TestCase):
    def test_printed_grid_separates_trials_from_result_rows(self) -> None:
        root = Path(self._tmp())
        log = root / "docs" / "experiment-log.md"
        log.parent.mkdir(parents=True)
        log.write_text(
            "# Log\n\n"
            "### EXP-20260101-001 — Example grid\n\n"
            "- Code commit: `abc1234abcdef`\n"
            "- Pair(s): EURUSD, GBPUSD, USDJPY\n"
            "- Timeframe(s): 5m, 15m, 1h\n"
            "- Data range: 2015-01-01 through 2023-12-31\n"
            "- Train period: 2015-01-01 through 2020-12-31\n"
            "- Validation period: 2021-01-01 through 2023-12-31\n"
            "- Final-test touched?: NO\n"
            "- Parameters/search space: exactly 4 configurations per pair/timeframe.\n"
            "- Result summary: 8/8 rows independently verified. zero of 4 pair/timeframe/buffer points passed.\n",
            encoding="utf-8",
        )
        (root / "docs" / "trial-ledger.jsonl").write_text("", encoding="utf-8")
        inventory = build_inventory(root)
        row = inventory["records"][0]
        self.assertEqual(row["configuration_count"]["value"], 4)
        self.assertEqual(row["configuration_count"]["status"], VERIFIED)
        self.assertEqual(row["result_row_count"]["value"], 8)
        self.assertEqual(row["executed_trial_count"]["value"], 4)
        self.assertEqual(row["configurations_per_pair_timeframe"]["value"], 4)
        self.assertEqual(row["configurations_per_pair_timeframe"]["status"], "partially_supported")
        self.assertIsNone(inventory["programme_trial_count"])
        self.assertTrue(row["data_exposure"]["overlaps_2015_2022"])
        self.assertIs(row["data_exposure"]["untouched_validation"], False)

    def test_same_trial_in_two_documents_is_one_record(self) -> None:
        root = self._write(
            "### EXP-20260101-001 — Same grid\n\n"
            "- Result summary: 8/8 rows independently verified. zero of 4 pair/timeframe/buffer points passed.\n",
            _ledger_line(),
        )
        inventory = build_inventory(root)
        matches = [row for row in inventory["records"] if row["experiment_id"] == "EXP-20260101-001"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["configuration_count"]["value"], 4)
        self.assertEqual(matches[0]["evidence_locations"], ["docs/experiment-log.md", "trial-ledger"])

    def test_conflicting_counts_stay_unresolved(self) -> None:
        evidence = {
            "available": True,
            "trial_count": 9,
            "note": "9 configurations were evaluated.",
        }
        root = self._write(
            "### EXP-20260101-001 — Conflict\n\n"
            "- Result summary: zero of 4 pair/timeframe/buffer points passed.\n",
            _ledger_line(statistical_evidence=evidence),
        )
        row = build_inventory(root)["records"][0]
        self.assertEqual(row["configuration_count"]["status"], "conflicted")
        self.assertIsNone(row["configuration_count"]["value"])
        self.assertEqual(row["correction_blocker"], INSUFFICIENT_TRIAL_CENSUS)

    def test_duplicate_ids_are_not_summed(self) -> None:
        text = (
            "### EXP-20260101-009 — DEC-1 workflow preflight proof\n\n"
            "- Protocol decisions: workflow freeze.\n\n"
            "### EXP-20260101-009 — DEC-2 runtime authorization proof\n\n"
            "- Protocol decisions: another workflow freeze.\n"
        )
        root = self._write(text, "")
        inventory = build_inventory(root)
        self.assertEqual(inventory["duplicate_experiment_ids"], ["EXP-20260101-009"])
        self.assertEqual(len(inventory["records"]), 2)
        self.assertTrue(all(row["role"] == "engineering_or_governance" for row in inventory["records"]))
        self.assertTrue(all(row["executed_trial_count"]["value"] is None for row in inventory["records"]))
        self.assertIsNone(inventory["programme_trial_count"])

    def test_missing_evidence_and_malformed_ledger(self) -> None:
        root = self._write("### EXP-20260101-003 — Untitled note\n\nNo counts here.\n", "")
        row = build_inventory(root)["records"][0]
        self.assertEqual(row["configuration_count"]["status"], "unavailable")
        self.assertIn("No single printed configuration total.", row["missing_information"])
        ledger = root / "docs" / "trial-ledger.jsonl"
        ledger.write_text('{"trial_id": "x"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            build_inventory(root)

    def test_output_order_is_stable_and_reread_does_not_change_the_ledger(self) -> None:
        text = (
            "### EXP-20260101-002 — Later\n\n- Status: note\n\n"
            "### EXP-20260101-001 — Earlier\n\n- Status: note\n"
        )
        root = self._write(text, _ledger_line(trial_id="CENSUS-1", version="not-a-trial",
                                               statistical_evidence={"available": False, "trial_count": None}))
        ledger = root / "docs" / "trial-ledger.jsonl"
        before = ledger.read_bytes()
        first = build_inventory(root)
        second = build_inventory(root)
        self.assertEqual(inventory_json(first), inventory_json(second))
        self.assertEqual(ledger.read_bytes(), before)
        self.assertEqual(
            [row["experiment_id"] for row in first["records"]],
            ["CENSUS-1", "EXP-20260101-001", "EXP-20260101-002"],
        )
        self.assertIsNone(first["programme_trial_count"])

    def test_incomplete_family_is_not_sent_to_adjustment(self) -> None:
        refused = family_correction_status(family_id="partial", closed=False, members=({
            "hypothesis_id": "a",
            "count_status": VERIFIED,
            "p_value": 0.01,
        },))
        self.assertEqual(refused["status"], INSUFFICIENT_TRIAL_CENSUS)
        self.assertIsNone(refused["adjustment"])
        no_p = family_correction_status(family_id="closed-without-p", closed=True, members=({
            "hypothesis_id": "a",
            "count_status": VERIFIED,
            "p_value": None,
        },))
        self.assertEqual(no_p["status"], INSUFFICIENT_STATISTICAL_EVIDENCE)
        ready = family_correction_status(family_id="closed-synthetic", closed=True, members=(
            {"hypothesis_id": "a", "count_status": VERIFIED, "p_value": 0.001},
            {"hypothesis_id": "b", "count_status": VERIFIED, "p_value": 0.5},
        ))
        self.assertEqual(ready["status"], ELIGIBLE_FOR_BY_ADJUSTMENT)
        self.assertEqual(ready["eligible_for_statistical_correction"], "yes")
        self.assertEqual(ready["adjustment"]["total_hypotheses"], 2)
        duplicate_members = family_correction_status(family_id="repeated", closed=True, members=(
            {"hypothesis_id": "a", "count_status": VERIFIED, "p_value": 0.01},
            {"hypothesis_id": "a", "count_status": VERIFIED, "p_value": 0.02},
        ))
        self.assertEqual(duplicate_members["status"], INSUFFICIENT_TRIAL_CENSUS)
        self.assertIsNone(duplicate_members["adjustment"])
        blank_family = family_correction_status(family_id="  ", closed=True, members=(
            {"hypothesis_id": "a", "count_status": VERIFIED, "p_value": 0.01},
        ))
        self.assertEqual(blank_family["status"], INSUFFICIENT_TRIAL_CENSUS)
        invalid_p = family_correction_status(family_id="invalid-p", closed=True, members=(
            {"hypothesis_id": "a", "count_status": VERIFIED, "p_value": 1.5},
        ))
        self.assertEqual(invalid_p["status"], INSUFFICIENT_STATISTICAL_EVIDENCE)
        self.assertIsNone(invalid_p["adjustment"])

    def test_repository_documents_keep_the_programme_total_unknown(self) -> None:
        before = LEDGER_PATH.read_bytes()
        inventory = build_inventory(ROOT)
        self.assertEqual(LEDGER_PATH.read_bytes(), before)
        self.assertIsNone(inventory["programme_trial_count"])
        self.assertGreater(inventory["experiment_heading_count"], inventory["unique_experiment_ids_in_log"])
        self.assertIn("EXP-20260927-062", inventory["duplicate_experiment_ids"])
        by_id = {row["record_id"]: row for row in inventory["records"]}
        session = by_id["EXP-20260914-001#1"]
        self.assertEqual(
            session["source_commits"],
            ["cc01929b80cbd1d5619de8476caa8f3d3410262e"],
        )
        self.assertEqual(session["configuration_count"]["value"], 81)
        self.assertEqual(session["result_row_count"]["value"], 486)
        self.assertEqual(session["executed_trial_count"]["value"], 81)
        trend = by_id["EXP-20260914-002#1"]
        self.assertIsNone(trend["configuration_count"]["value"])
        self.assertEqual(trend["configurations_per_pair_timeframe"]["value"], 6)
        self.assertEqual(trend["result_row_count"]["value"], 324)
        self.assertIsNone(trend["executed_trial_count"]["value"])
        mean = by_id["EXP-20260914-003#1"]
        self.assertEqual(mean["configuration_count"]["value"], 54)
        self.assertEqual(mean["result_row_count"]["value"], 324)
        declared = by_id["EXP-20260922-013#1"]
        self.assertEqual(declared["configuration_count"]["value"], 36)
        self.assertEqual(declared["role"], "declared_search_not_executed")
        self.assertIsNone(declared["executed_trial_count"]["value"])
        phase7 = by_id["EXP-20260915-008#1"]
        self.assertIs(phase7["data_exposure"]["untouched_validation"], False)
        self.assertTrue(phase7["data_exposure"]["scored_2024_through_2026"])
        self.assertIsNone(phase7["configuration_count"]["value"])
        self.assertIn(
            "not the earlier",
            " ".join(item["quote"] for item in phase7["configuration_count"]["provenance"]),
        )
        self.assertEqual(inventory["historical_family_correction"]["status"], INSUFFICIENT_TRIAL_CENSUS)
        self.assertTrue(all(
            row["eligible_for_statistical_correction"] != "yes"
            for row in inventory["records"]
        ))
        grids = {item["name"]: item["declared_parameter_count"] for item in inventory["source_declared_grids"]}
        self.assertEqual(grids["SESSION_BREAKOUT_GRID"], 9)
        self.assertEqual(grids["MEAN_REVERSION_GRID"], 6)

    def _tmp(self) -> str:
        import tempfile
        path = tempfile.mkdtemp()
        self.addCleanup(lambda: None)
        return path

    def _write(self, body: str, ledger: str) -> Path:
        import tempfile
        root = Path(tempfile.mkdtemp())
        docs = root / "docs"
        docs.mkdir()
        (docs / "experiment-log.md").write_text("# Log\n\n" + body, encoding="utf-8")
        (docs / "trial-ledger.jsonl").write_text(ledger, encoding="utf-8")
        return root


if __name__ == "__main__":
    unittest.main()
