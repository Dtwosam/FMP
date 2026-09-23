from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from fmp.phase8b.campaign_close import (
    PHASE8B_CAMPAIGN_PROGRESS_AVAILABLE,
    PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS,
    preview_phase8b_campaign_progress_directory,
)


UTC = timezone.utc
COMMIT = "c" * 40


def _preflight() -> dict[str, object]:
    return {
        "capture_preflight_fingerprint": "1" * 64,
        "champion_set_fingerprint": "2" * 64,
    }


def _write_preflight(root: Path) -> None:
    (root / "capture-preflight.json").write_text(
        json.dumps(_preflight()),
        encoding="utf-8",
    )


def _aggregate(*, open_ids=None, pending_ids=None, completed=12):
    open_ids = [] if open_ids is None else list(open_ids)
    pending_ids = [] if pending_ids is None else list(pending_ids)
    scenario = {
        "completed_trades": [
            {"decision_id": f"d{i}"} for i in range(completed)
        ],
        "open_decision_ids": open_ids,
        "pending_decision_ids": pending_ids,
    }
    return {
        "scenarios": {
            "0.2": dict(scenario),
            "0.5": dict(scenario),
            "1.0": dict(scenario),
        }
    }


class Phase8BCampaignProgressTests(unittest.TestCase):
    def test_empty_campaign_reports_no_closed_segments_and_writes_nothing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_preflight(root)
            before = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
            with (
                patch(
                    "fmp.phase8b.campaign_close.validate_phase8b_capture_preflight"
                ),
                patch(
                    "fmp.phase8b.campaign_close._load_bundles",
                    side_effect=ValueError(
                        "Phase 8B campaign has no closed prospective segments"
                    ),
                ),
            ):
                result = preview_phase8b_campaign_progress_directory(
                    campaign_dir=root,
                    code_commit=COMMIT,
                )
            after = sorted(str(p.relative_to(root)) for p in root.rglob("*"))

        self.assertEqual(result["outcome"], PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS)
        self.assertEqual(result["eligible_closed_segment_count"], 0)
        self.assertFalse(result["minimum_evidence"]["all_minimums_pass"])
        self.assertFalse(result["currently_closeable"])
        self.assertEqual(before, after)

    def test_progress_uses_dec051_minimums_and_remaining_amounts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_preflight(root)
            bundles = (SimpleNamespace(), SimpleNamespace(), SimpleNamespace())
            first = datetime(2026, 1, 1, tzinfo=UTC)
            last = datetime(2026, 2, 12, tzinfo=UTC)  # exactly 6 weeks
            with (
                patch(
                    "fmp.phase8b.campaign_close.validate_phase8b_capture_preflight"
                ),
                patch(
                    "fmp.phase8b.campaign_close._load_bundles",
                    return_value=(bundles, 2),
                ),
                patch(
                    "fmp.phase8b.campaign_close._compile_aggregate_segment",
                    return_value=(_aggregate(completed=12), []),
                ),
                patch(
                    "fmp.phase8b.campaign_close._build_replay",
                    return_value={"match": True},
                ),
                patch(
                    "fmp.phase8b.campaign_close._received_bounds",
                    return_value=(first, last),
                ),
                patch(
                    "fmp.phase8b.campaign_close._denominator_dates",
                    return_value=[f"2026-01-{i:02d}" for i in range(1, 21)],
                ),
                patch(
                    "fmp.phase8b.campaign_close._segment_intervals",
                    return_value=(),
                ),
                patch(
                    "fmp.phase8b.campaign_close._complete_dates",
                    return_value=[f"2026-01-{i:02d}" for i in range(1, 19)],
                ),
                patch(
                    "fmp.phase8b.campaign_close._representation",
                    return_value=(["family-a"], ["EURUSD"]),
                ),
            ):
                result = preview_phase8b_campaign_progress_directory(
                    campaign_dir=root,
                    code_commit=COMMIT,
                )

        self.assertEqual(result["outcome"], PHASE8B_CAMPAIGN_PROGRESS_AVAILABLE)
        minimums = result["minimum_evidence"]
        self.assertEqual(minimums["elapsed_weeks"], 6.0)
        self.assertEqual(minimums["elapsed_weeks_required"], 8)
        self.assertEqual(minimums["elapsed_weeks_remaining"], 2.0)
        self.assertEqual(minimums["complete_london_dates"], 18)
        self.assertEqual(minimums["complete_london_dates_remaining"], 12)
        self.assertEqual(minimums["completed_trade_count_0_2"], 12)
        self.assertEqual(minimums["completed_trade_count_remaining"], 28)
        self.assertEqual(minimums["represented_strategy_family_count"], 1)
        self.assertEqual(minimums["represented_strategy_family_count_remaining"], 1)
        self.assertEqual(minimums["represented_pair_count"], 1)
        self.assertEqual(minimums["represented_pair_count_remaining"], 1)
        self.assertFalse(minimums["all_minimums_pass"])
        self.assertEqual(result["eligible_closed_segment_count"], 3)
        self.assertEqual(result["unclosed_segment_directory_count"], 2)
        self.assertTrue(result["aggregate_replay_match"])
        self.assertTrue(result["currently_closeable"])

    def test_open_or_pending_decision_makes_preview_not_closeable(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_preflight(root)
            with (
                patch(
                    "fmp.phase8b.campaign_close.validate_phase8b_capture_preflight"
                ),
                patch(
                    "fmp.phase8b.campaign_close._load_bundles",
                    return_value=((SimpleNamespace(),), 0),
                ),
                patch(
                    "fmp.phase8b.campaign_close._compile_aggregate_segment",
                    return_value=(
                        _aggregate(open_ids=["open-1"], completed=40),
                        [],
                    ),
                ),
                patch(
                    "fmp.phase8b.campaign_close._build_replay",
                    return_value={"match": True},
                ),
                patch(
                    "fmp.phase8b.campaign_close._received_bounds",
                    return_value=(
                        datetime(2026, 1, 1, tzinfo=UTC),
                        datetime(2026, 3, 5, tzinfo=UTC),
                    ),
                ),
                patch(
                    "fmp.phase8b.campaign_close._denominator_dates",
                    return_value=["x"] * 45,
                ),
                patch(
                    "fmp.phase8b.campaign_close._segment_intervals",
                    return_value=(),
                ),
                patch(
                    "fmp.phase8b.campaign_close._complete_dates",
                    return_value=["x"] * 30,
                ),
                patch(
                    "fmp.phase8b.campaign_close._representation",
                    return_value=(
                        ["family-a", "family-b"],
                        ["EURUSD", "USDJPY"],
                    ),
                ),
            ):
                result = preview_phase8b_campaign_progress_directory(
                    campaign_dir=root,
                    code_commit=COMMIT,
                )

        self.assertTrue(result["minimum_evidence"]["all_minimums_pass"])
        self.assertFalse(result["currently_closeable"])

    def test_progress_authorizes_nothing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_preflight(root)
            with (
                patch(
                    "fmp.phase8b.campaign_close.validate_phase8b_capture_preflight"
                ),
                patch(
                    "fmp.phase8b.campaign_close._load_bundles",
                    side_effect=ValueError(
                        "Phase 8B campaign has no segment directory"
                    ),
                ),
            ):
                result = preview_phase8b_campaign_progress_directory(
                    campaign_dir=root,
                    code_commit=COMMIT,
                )

        for field in (
            "acceptance_authorized",
            "promotion_authorized",
            "shadow_validation_authorized",
            "demo_order_authorized",
            "live_order_authorized",
            "broker_mutation_authorized",
            "real_money_authorized",
            "phase9_authorized",
        ):
            self.assertFalse(result[field])


if __name__ == "__main__":
    unittest.main()
