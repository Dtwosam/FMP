from __future__ import annotations

import unittest
from pathlib import Path

from tests.phase5_helpers import make_bars


class Phase5FeatureEngineTests(unittest.TestCase):
    def test_engine_emits_exact_frozen_schema_sorted_unique(self) -> None:
        from fmp.features.engine import build_feature_frame
        from fmp.features.schema import FEATURE_COLUMNS, FEATURE_VALUE_COLUMNS

        source = make_bars(timeframe="1h", count=30)
        out = build_feature_frame(
            source,
            symbol="EURUSD",
            timeframe="1h",
            processed_manifest_sha256="a" * 64,
        )
        self.assertEqual(tuple(out.columns), FEATURE_COLUMNS)
        self.assertEqual(len(FEATURE_VALUE_COLUMNS), 48)
        self.assertEqual(out.height, 30)
        self.assertEqual(
            out.select(["symbol", "timeframe", "bar_start_utc"]).unique().height,
            out.height,
        )
        starts = out["bar_start_utc"].to_list()
        self.assertEqual(starts, sorted(starts))
        self.assertEqual(set(out["feature_set_version"].to_list()), {"fmp-feature-v1"})
        self.assertEqual(set(out["processed_manifest_sha256"].to_list()), {"a" * 64})

    def test_schema_contains_all_eight_families_and_no_unapproved_fields(self) -> None:
        from fmp.features.schema import FEATURE_VALUE_COLUMNS

        expected = {
            "return_1bar", "realized_vol_8h", "sma_distance_8h_pips", "roc_8h",
            "body_to_range", "is_london_session", "prev_fx_day_high_dist_pips",
            "spread_close_pips",
        }
        self.assertTrue(expected.issubset(FEATURE_VALUE_COLUMNS))
        forbidden_fragments = ("label", "target", "future", "activity", "volume", "pair_join")
        for name in FEATURE_VALUE_COLUMNS:
            self.assertFalse(any(fragment in name for fragment in forbidden_fragments), name)

    def test_dictionary_matches_machine_feature_columns(self) -> None:
        from fmp.features.schema import FEATURE_VALUE_COLUMNS

        text = Path("docs/phase5-feature-dictionary.md").read_text(encoding="utf-8")
        self.assertIn("fmp-feature-v1", text)
        self.assertIn("available_at_utc", text)
        for column in FEATURE_VALUE_COLUMNS:
            self.assertIn(f"`{column}`", text, column)
        self.assertIn("no generic forward-fill", text.lower())
        self.assertIn("2024-01-01", text)


if __name__ == "__main__":
    unittest.main()
