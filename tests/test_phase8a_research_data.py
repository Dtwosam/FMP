from datetime import date, datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import polars as pl

from fmp.portfolio.research_data import (
    PHASE8A_RETROSPECTIVE_END_EXCLUSIVE,
    PHASE8A_RETROSPECTIVE_LABEL,
    PHASE8A_RETROSPECTIVE_START,
    RetrospectiveRange,
    load_phase8a_retrospective_bars,
)


def _frame(symbol: str, timestamps: list[datetime], *, complete: list[bool] | None = None) -> pl.DataFrame:
    complete = complete or [True] * len(timestamps)
    rows = []
    for ts, is_complete in zip(timestamps, complete):
        price = 150.0 if symbol == "USDJPY" else 1.1
        spread = 0.02 if symbol == "USDJPY" else 0.0002
        rows.append(
            {
                "timestamp_utc": ts,
                "symbol": symbol,
                "bid_open": price - spread / 2,
                "bid_high": price + spread / 2,
                "bid_low": price - spread / 2,
                "bid_close": price - spread / 2,
                "ask_open": price + spread / 2,
                "ask_high": price + spread,
                "ask_low": price,
                "ask_close": price + spread / 2,
                "is_complete": is_complete,
            }
        )
    return pl.DataFrame(rows)


class Phase8ARetrospectiveDataTests(unittest.TestCase):
    def test_range_is_explicitly_retrospective_and_bounded_to_accepted_snapshot(self) -> None:
        research_range = RetrospectiveRange(
            start=date(2024, 1, 1),
            end_exclusive=PHASE8A_RETROSPECTIVE_END_EXCLUSIVE,
        )
        self.assertEqual(research_range.evidence_label, PHASE8A_RETROSPECTIVE_LABEL)
        self.assertEqual(PHASE8A_RETROSPECTIVE_START, date(2015, 1, 1))
        self.assertEqual(PHASE8A_RETROSPECTIVE_END_EXCLUSIVE, date(2026, 8, 21))

        with self.assertRaises(ValueError):
            RetrospectiveRange(start=date(2014, 12, 31), end_exclusive=date(2015, 1, 2))
        with self.assertRaises(ValueError):
            RetrospectiveRange(start=date(2026, 8, 20), end_exclusive=date(2026, 8, 22))
        with self.assertRaises(ValueError):
            RetrospectiveRange(start=date(2026, 8, 20), end_exclusive=date(2026, 8, 20))

    def test_invalid_range_fails_before_manifest_io(self) -> None:
        with self.assertRaisesRegex(ValueError, "accepted Phase 8A snapshot"):
            load_phase8a_retrospective_bars(
                dataset_root=Path("/definitely/missing"),
                manifest_path=Path("/definitely/missing/manifest.json"),
                symbol="EURUSD",
                timeframe="15m",
                research_range=RetrospectiveRange.__new__(RetrospectiveRange),
            )

    def test_loader_can_read_previously_opened_2024_2026_history_without_using_phase4_split_escape(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            parquet = root / "processed" / "USDJPY-15m-2026-08.parquet"
            parquet.parent.mkdir(parents=True)
            parquet.touch()
            manifest = root / "USDJPY.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": "fmp-canonical-1m-v1",
                        "symbol": "USDJPY",
                        "artifacts": {
                            "15m:2026-08": {"path": "processed/USDJPY-15m-2026-08.parquet"}
                        },
                    }
                ),
                encoding="utf-8",
            )

            timestamps = [
                datetime(2026, 8, 19, 0, 0, tzinfo=timezone.utc),
                datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc),
            ]
            loaded = load_phase8a_retrospective_bars(
                dataset_root=root,
                manifest_path=manifest,
                symbol="USDJPY",
                timeframe="15m",
                research_range=RetrospectiveRange(
                    start=date(2026, 8, 19),
                    end_exclusive=date(2026, 8, 21),
                ),
                parquet_reader=lambda _: _frame("USDJPY", timestamps),
            )

            self.assertEqual(len(loaded.bars), 2)
            self.assertEqual(loaded.evidence_label, PHASE8A_RETROSPECTIVE_LABEL)
            self.assertEqual(loaded.start, date(2026, 8, 19))
            self.assertEqual(loaded.end_exclusive, date(2026, 8, 21))
            self.assertEqual(loaded.opened_artifact_months, ("2026-08",))
            self.assertEqual(loaded.excluded_incomplete_count, 0)
            self.assertEqual(loaded.eligible_utc_dates, (date(2026, 8, 19), date(2026, 8, 20)))

    def test_loader_filters_exact_requested_range_and_excludes_incomplete_bars(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            parquet = root / "m.parquet"
            parquet.touch()
            manifest = root / "EURUSD.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": "fmp-canonical-1m-v1",
                        "symbol": "EURUSD",
                        "artifacts": {"5m:2023-12": {"path": "m.parquet"}},
                    }
                ),
                encoding="utf-8",
            )
            timestamps = [
                datetime(2023, 12, 30, 0, 0, tzinfo=timezone.utc),
                datetime(2023, 12, 31, 0, 0, tzinfo=timezone.utc),
                datetime(2023, 12, 31, 0, 5, tzinfo=timezone.utc),
                datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
            ]
            loaded = load_phase8a_retrospective_bars(
                dataset_root=root,
                manifest_path=manifest,
                symbol="EURUSD",
                timeframe="5m",
                research_range=RetrospectiveRange(
                    start=date(2023, 12, 31),
                    end_exclusive=date(2024, 1, 1),
                ),
                parquet_reader=lambda _: _frame(
                    "EURUSD",
                    timestamps,
                    complete=[True, True, False, True],
                ),
            )
            self.assertEqual(len(loaded.bars), 1)
            self.assertEqual(loaded.excluded_incomplete_count, 1)
            self.assertEqual(loaded.bars[0].timestamp_utc, timestamps[1])


    def test_phase8a_loader_accepts_1m_for_execution_data_role(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            parquet = root / "EURUSD-1m-2024-01.parquet"
            parquet.touch()
            manifest = root / "EURUSD.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": "fmp-canonical-1m-v1",
                        "symbol": "EURUSD",
                        "artifacts": {"1m:2024-01": {"path": parquet.name}},
                    }
                ),
                encoding="utf-8",
            )
            ts = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
            loaded = load_phase8a_retrospective_bars(
                dataset_root=root,
                manifest_path=manifest,
                symbol="EURUSD",
                timeframe="1m",
                research_range=RetrospectiveRange(
                    start=date(2024, 1, 2),
                    end_exclusive=date(2024, 1, 3),
                ),
                parquet_reader=lambda _: _frame("EURUSD", [ts]),
            )
            self.assertEqual(len(loaded.bars), 1)
            self.assertEqual(loaded.bars[0].timestamp_utc, ts)

    def test_loader_rejects_manifest_symbol_mismatch_and_duplicate_bar_identity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            parquet = root / "m.parquet"
            parquet.touch()
            manifest = root / "bad.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": "fmp-canonical-1m-v1",
                        "symbol": "GBPUSD",
                        "artifacts": {"15m:2020-01": {"path": "m.parquet"}},
                    }
                ),
                encoding="utf-8",
            )
            research_range = RetrospectiveRange(start=date(2020, 1, 1), end_exclusive=date(2020, 1, 2))
            with self.assertRaisesRegex(ValueError, "symbol"):
                load_phase8a_retrospective_bars(
                    dataset_root=root,
                    manifest_path=manifest,
                    symbol="EURUSD",
                    timeframe="15m",
                    research_range=research_range,
                    parquet_reader=lambda _: _frame(
                        "EURUSD",
                        [datetime(2020, 1, 1, tzinfo=timezone.utc)],
                    ),
                )

            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": "fmp-canonical-1m-v1",
                        "symbol": "EURUSD",
                        "artifacts": {"15m:2020-01": {"path": "m.parquet"}},
                    }
                ),
                encoding="utf-8",
            )
            duplicate = datetime(2020, 1, 1, tzinfo=timezone.utc)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_phase8a_retrospective_bars(
                    dataset_root=root,
                    manifest_path=manifest,
                    symbol="EURUSD",
                    timeframe="15m",
                    research_range=research_range,
                    parquet_reader=lambda _: _frame("EURUSD", [duplicate, duplicate]),
                )


if __name__ == "__main__":
    unittest.main()
