from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import polars as pl

from fmp.features.engine import build_feature_frame
from fmp.market_learning.contracts import MARKET_FEATURE_SET_VERSION
from fmp.market_learning.labels import label_market_outcome
from fmp.market_learning.outcomes import (
    MARKET_OUTCOME_SET_VERSION,
    OUTCOME_COLUMNS,
    OUTCOME_FEATURE_IDENTITY_COLUMNS,
    build_market_outcome_grid,
    build_market_outcome_grid_from_identity,
    write_market_outcome_artifacts,
)
from tests.phase5_helpers import make_bars


UTC = timezone.utc


def _feature_rows(
    *,
    symbol: str = "EURUSD",
    timeframe: str = "5m",
    start: datetime = datetime(2024, 1, 2, 10, 0, tzinfo=UTC),
    count: int = 8,
) -> pl.DataFrame:
    source = make_bars(
        symbol=symbol,
        timeframe=timeframe,
        start=start,
        count=count,
    )
    return build_feature_frame(
        source,
        symbol=symbol,
        timeframe=timeframe,
        processed_manifest_sha256="a" * 64,
    ).with_columns(
        pl.lit(MARKET_FEATURE_SET_VERSION).alias("feature_set_version")
    )


def _minute_quotes(
    *,
    symbol: str = "EURUSD",
    start: datetime,
    count: int,
    base: float | None = None,
    step: float | None = None,
    spread: float | None = None,
) -> pl.DataFrame:
    frame = make_bars(
        symbol=symbol,
        timeframe="5m",
        start=start,
        count=count,
        base=base,
        step=step,
        spread=spread,
    )
    timestamps = [start + timedelta(minutes=i) for i in range(count)]
    return frame.with_columns(
        pl.Series("timestamp_utc", timestamps),
        pl.lit("1m").alias("timeframe"),
        pl.lit(1).alias("source_minutes"),
        pl.lit(1).alias("expected_open_minutes"),
    )


class MarketOutcomeGridTests(unittest.TestCase):
    def test_vectorized_grid_matches_row_label_economics(self) -> None:
        features = _feature_rows(count=4)
        first_available = features["available_at_utc"][0]
        quotes = _minute_quotes(
            start=first_available,
            count=300,
            base=1.1000,
            step=0.00001,
            spread=0.0002,
        )

        build = build_market_outcome_grid(
            features,
            quotes,
            symbol="EURUSD",
            timeframe="5m",
        )
        self.assertEqual(build.source_feature_rows, features.height)
        self.assertEqual(
            tuple(build.frame.columns),
            OUTCOME_COLUMNS,
        )
        self.assertEqual(
            set(build.frame["outcome_set_version"].to_list()),
            {MARKET_OUTCOME_SET_VERSION},
        )

        row = build.frame.filter(
            (pl.col("bar_start_utc") == features["bar_start_utc"][0])
            & (pl.col("horizon_minutes") == 60)
        ).row(0, named=True)

        from fmp.contracts import QuoteBar
        from fmp.market_learning.contracts import MarketObservation

        feature = features.row(0, named=True)
        entry_ts = feature["available_at_utc"]
        exit_ts = entry_ts + timedelta(minutes=60)
        quote_by_ts = {
            item["timestamp_utc"]: item
            for item in quotes.to_dicts()
        }
        def qb(ts: datetime) -> QuoteBar:
            q = quote_by_ts[ts]
            return QuoteBar(
                timestamp_utc=ts,
                symbol="EURUSD",
                bid_open=q["bid_open"],
                bid_high=q["bid_high"],
                bid_low=q["bid_low"],
                bid_close=q["bid_close"],
                ask_open=q["ask_open"],
                ask_high=q["ask_high"],
                ask_low=q["ask_low"],
                ask_close=q["ask_close"],
            )

        observation = MarketObservation(
            symbol="EURUSD",
            timeframe="5m",
            bar_start_utc=feature["bar_start_utc"],
            available_at_utc=entry_ts,
        )
        scalar = label_market_outcome(
            observation,
            (qb(entry_ts), qb(exit_ts)),
            horizon_minutes=60,
            slippage_pips=0.2,
        )
        assert scalar.label is not None
        self.assertAlmostEqual(
            row["future_mid_move_pips"],
            scalar.label.future_mid_move_pips,
        )
        self.assertAlmostEqual(
            row["long_net_pips_0p2"],
            scalar.label.long_net_pips,
        )
        self.assertAlmostEqual(
            row["short_net_pips_0p2"],
            scalar.label.short_net_pips,
        )
        self.assertEqual(
            row["best_direction_0p2"],
            scalar.label.best_direction.value,
        )

    def test_identity_projection_matches_full_feature_outcome_grid(self) -> None:
        features = _feature_rows(count=5)
        quotes = _minute_quotes(
            start=features["available_at_utc"][0],
            count=400,
            base=1.1000,
            step=0.00001,
            spread=0.0002,
        )
        full = build_market_outcome_grid(
            features,
            quotes,
            symbol="EURUSD",
            timeframe="5m",
        )
        projected = build_market_outcome_grid_from_identity(
            features.select(list(OUTCOME_FEATURE_IDENTITY_COLUMNS)),
            quotes,
            symbol="EURUSD",
            timeframe="5m",
        )
        self.assertEqual(full.frame.to_dicts(), projected.frame.to_dicts())
        self.assertEqual(full.source_feature_rows, projected.source_feature_rows)
        self.assertEqual(
            full.labeled_rows_by_horizon,
            projected.labeled_rows_by_horizon,
        )
        self.assertEqual(
            full.missing_entry_rows_by_horizon,
            projected.missing_entry_rows_by_horizon,
        )
        self.assertEqual(
            full.missing_exit_rows_by_horizon,
            projected.missing_exit_rows_by_horizon,
        )

    def test_exact_timestamp_gaps_are_counted_and_never_shifted(self) -> None:
        features = _feature_rows(count=2)
        start = features["available_at_utc"][0]
        quotes = _minute_quotes(
            start=start,
            count=300,
        )
        missing_entry = features["available_at_utc"][0]
        missing_exit = features["available_at_utc"][1] + timedelta(minutes=60)
        quotes = quotes.filter(
            ~pl.col("timestamp_utc").is_in([missing_entry, missing_exit])
        )

        build = build_market_outcome_grid(
            features,
            quotes,
            symbol="EURUSD",
            timeframe="5m",
        )
        self.assertGreaterEqual(build.missing_entry_rows_by_horizon[60], 1)
        self.assertGreaterEqual(build.missing_exit_rows_by_horizon[60], 1)
        forbidden = build.frame.filter(
            (pl.col("bar_start_utc") == features["bar_start_utc"][0])
        )
        self.assertEqual(forbidden.height, 0)

    def test_usdjpy_pip_scaling_and_cost_scenarios(self) -> None:
        features = _feature_rows(
            symbol="USDJPY",
            timeframe="15m",
            count=3,
        )
        start = features["available_at_utc"][0]
        quotes = _minute_quotes(
            symbol="USDJPY",
            start=start,
            count=400,
            base=150.00,
            step=0.001,
            spread=0.02,
        )
        build = build_market_outcome_grid(
            features,
            quotes,
            symbol="USDJPY",
            timeframe="15m",
        )
        row = build.frame.filter(pl.col("horizon_minutes") == 60).row(0, named=True)
        self.assertGreater(row["future_mid_move_pips"], 0)
        self.assertAlmostEqual(
            row["long_net_pips_0p2"] - row["long_net_pips_1p0"],
            1.6,
        )
        self.assertAlmostEqual(
            row["short_net_pips_0p2"] - row["short_net_pips_1p0"],
            1.6,
        )

    def test_artifact_writer_requires_verified_feature_evidence_fingerprint(self) -> None:
        features = _feature_rows(count=3)
        quotes = _minute_quotes(
            start=features["available_at_utc"][0],
            count=400,
        )
        build = build_market_outcome_grid(
            features,
            quotes,
            symbol="EURUSD",
            timeframe="5m",
        )
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "feature_evidence_fingerprint"):
                write_market_outcome_artifacts(
                    build=build,
                    output_root=Path(tmp),
                    symbol="EURUSD",
                    timeframe="5m",
                    code_commit="b" * 40,
                    feature_manifest_sha256="c" * 64,
                    feature_evidence_fingerprint="not-verified",
                    processed_manifest_sha256="a" * 64,
                )

    def test_artifact_writer_rejects_targets_beyond_accepted_history(self) -> None:
        features = _feature_rows(
            start=datetime(2026, 8, 20, 20, 0, tzinfo=UTC),
            count=3,
        )
        quotes = _minute_quotes(
            start=features["available_at_utc"][0],
            count=500,
        )
        build = build_market_outcome_grid(
            features,
            quotes,
            symbol="EURUSD",
            timeframe="5m",
        )
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "beyond accepted history"):
                write_market_outcome_artifacts(
                    build=build,
                    output_root=Path(tmp),
                    symbol="EURUSD",
                    timeframe="5m",
                    code_commit="b" * 40,
                    feature_manifest_sha256="c" * 64,
                    feature_evidence_fingerprint="d" * 64,
                    processed_manifest_sha256="a" * 64,
                )

    def test_artifact_writer_is_deterministic_and_keeps_model_fit_locked(self) -> None:
        features = _feature_rows(count=3)
        quotes = _minute_quotes(
            start=features["available_at_utc"][0],
            count=400,
        )
        build = build_market_outcome_grid(
            features,
            quotes,
            symbol="EURUSD",
            timeframe="5m",
        )
        kwargs = {
            "build": build,
            "symbol": "EURUSD",
            "timeframe": "5m",
            "code_commit": "b" * 40,
            "feature_manifest_sha256": "c" * 64,
            "feature_evidence_fingerprint": "d" * 64,
            "processed_manifest_sha256": "a" * 64,
        }
        with tempfile.TemporaryDirectory() as left_tmp, tempfile.TemporaryDirectory() as right_tmp:
            left = write_market_outcome_artifacts(
                output_root=Path(left_tmp),
                **kwargs,
            )
            right = write_market_outcome_artifacts(
                output_root=Path(right_tmp),
                **kwargs,
            )
            self.assertEqual(left, right)
            self.assertEqual(left["outcome_set_version"], MARKET_OUTCOME_SET_VERSION)
            self.assertEqual(left["feature_evidence_fingerprint"], "d" * 64)
            self.assertFalse(left["model_fit_authorized"])
            self.assertFalse(left["promotion_authorized"])
            self.assertEqual(left["horizons_minutes"], [60, 240])
            self.assertEqual(left["slippage_pips_per_fill"], [0.2, 0.5, 1.0])


if __name__ == "__main__":
    unittest.main()
