from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zoneinfo import ZoneInfo

from fmp.shadow.campaign import register_campaign
from fmp.shadow.evidence import finalize_existing_segment
from fmp.shadow.gates import Phase8ReviewOutcome, review_campaign
from fmp.shadow.qualification import practice_boundary_audit


UTC = timezone.utc
LONDON = ZoneInfo("Europe/London")
CODE_COMMIT = "c" * 40
FINGERPRINT = "f" * 64
DECISION_ID = "SB-USDJPY-20260916-15m-B5-R1p5-LONG"
REFERENCE = {
    "method_version": "fmp-phase8-spread-reference-v1",
    "phase7_checkpoint_tag": "fmp-v1-phase7-walk-forward",
    "phase7_checkpoint_sha": "b6fb0176555b071fef6d1070edf3407b03cd60c9",
    "phase7_experiment": "EXP-20260915-008",
    "phase7_outcome": "PASS / PROMOTE",
    "phase7_stage2_run_id": 35015277625,
    "phase2_artifact_id": 10327600628,
    "phase2_zip_sha256": "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72",
    "processed_manifest_sha256": "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
    "code_commit": CODE_COMMIT,
    "strategy": {
        "id": "session_breakout",
        "symbol": "USDJPY",
        "timeframe": "15m",
        "buffer_pips": 5,
        "target_range_multiple": 1.5,
    },
    "historical_slippage_pips": 0.2,
    "stage2_windows": [
        "2024-01_to_2024-03",
        "2024-04_to_2024-06",
        "2024-07_to_2024-09",
        "2024-10_to_2024-12",
        "2024-H1",
        "2024-H2",
        "2024-full",
    ],
    "trade_count": 40,
    "entry_spread_pips": {"count": 40, "median": 0.3, "p95": 0.5, "p95_method": "nearest_rank"},
    "exit_spread_pips": {"count": 40, "median": 0.4, "p95": 0.6, "p95_method": "nearest_rank"},
    "trades": [],
}


def _canonical(record: object) -> bytes:
    return (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _write_json(path: Path, record: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical(record))


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(_canonical(record) for record in records))


def _timestamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _quote(value: datetime, *, bid: float, ask: float) -> dict[str, object]:
    return {
        "source_time_utc": _timestamp(value),
        "received_at_utc": _timestamp(value),
        "receive_monotonic_ns": 1,
        "symbol": "USDJPY",
        "bid": bid,
        "ask": ask,
        "tradeable": True,
    }


def _bar(label_utc: datetime) -> dict[str, object]:
    return {
        "timeframe": "15m",
        "bar": {
            "timestamp_utc": _timestamp(label_utc),
            "symbol": "USDJPY",
            "bid_open": 140.0,
            "bid_high": 140.1,
            "bid_low": 139.9,
            "bid_close": 140.05,
            "ask_open": 140.003,
            "ask_high": 140.103,
            "ask_low": 139.903,
            "ask_close": 140.053,
        },
    }


def _trade(*, scenario: float, entry: datetime, exit_: datetime) -> dict[str, object]:
    net = {0.2: 100.0, 0.5: 90.0, 1.0: 70.0}[scenario]
    after = 100000.0 + net
    return {
        "trade_id": DECISION_ID,
        "decision_id": DECISION_ID,
        "symbol": "USDJPY",
        "direction": "LONG",
        "units": 1000,
        "entry_timestamp_utc": _timestamp(entry),
        "exit_timestamp_utc": _timestamp(exit_),
        "entry_reference_price": 140.003,
        "exit_reference_price": 140.100,
        "entry_price": 140.003 + scenario * 0.01,
        "exit_price": 140.100 - scenario * 0.01,
        "stop_price": 139.5,
        "target_price": 140.5,
        "exit_reason": "TIME_EXIT",
        "intrabar_ambiguous": False,
        "gross_pnl_usd": net,
        "slippage_cost_usd": 0.0,
        "commission_cost_usd": 0.0,
        "financing_cost_usd": 0.0,
        "net_pnl_usd": net,
        "risk_equity_before_usd": 100000.0,
        "risk_equity_after_usd": after,
    }


def _setup_phase8(root: Path) -> tuple[Path, Path]:
    phase8 = root / "phase8"
    reference = phase8 / "reference"
    campaign = phase8 / "campaign"
    qualification = phase8 / "qualification"
    payload = _canonical(REFERENCE)
    digest = hashlib.sha256(payload).hexdigest()
    reference.mkdir(parents=True)
    (reference / "reference.json").write_bytes(payload)
    (reference / "reference.sha256").write_text(digest + "\n", encoding="ascii")
    register_campaign(
        reference_dir=reference,
        campaign_dir=campaign,
        code_commit=CODE_COMMIT,
        campaign_start_utc=datetime(2026, 9, 16, 0, 0, tzinfo=UTC),
    )
    _write_json(
        qualification / "qualification.json",
        {
            "outcome": "PASS",
            "account_fingerprint": FINGERPRINT,
            "started_at_utc": "2026-09-15T23:45:00Z",
            "ended_at_utc": "2026-09-15T23:50:00Z",
            "elapsed_seconds": 300.0,
            "price_count": 100,
            "heartbeat_count": 6,
            "max_liveness_gap_seconds": 10.0,
            "boundary_audit": practice_boundary_audit(),
            "rejection_codes": [],
        },
    )
    return phase8, campaign


def _verified_segment(campaign: Path) -> Path:
    session_date = datetime(2026, 9, 16, tzinfo=LONDON).date()
    signal_local = datetime(2026, 9, 16, 8, 0, tzinfo=LONDON)
    signal_bar = signal_local.astimezone(UTC)
    signal_known = (signal_local + timedelta(minutes=15)).astimezone(UTC)
    entry = signal_known + timedelta(seconds=3)
    scheduled_exit = datetime(2026, 9, 16, 16, 0, tzinfo=LONDON).astimezone(UTC)
    exit_ = scheduled_exit + timedelta(seconds=2)
    run_start = datetime(2026, 9, 16, 6, 50, tzinfo=UTC)
    run_end = exit_ + timedelta(minutes=1)
    segment = campaign / "segment-20260916T065000.000000Z"
    segment.mkdir(parents=True)

    _write_jsonl(segment / "raw.jsonl", [])
    _write_jsonl(
        segment / "normalized.jsonl",
        [
            _quote(entry, bid=140.000, ask=140.003),
            _quote(exit_, bid=140.100, ask=140.104),
        ],
    )
    labels: list[dict[str, object]] = []
    local = datetime(2026, 9, 16, 0, 0, tzinfo=LONDON)
    while local <= signal_local:
        labels.append(_bar(local.astimezone(UTC)))
        local += timedelta(minutes=15)
    _write_jsonl(segment / "bars.jsonl", labels)
    _write_jsonl(
        segment / "decisions.jsonl",
        [
            {
                "event": "strategy_decision",
                "candidate": {
                    "candidate_id": DECISION_ID,
                    "symbol": "USDJPY",
                    "observation_bar_timestamp_utc": _timestamp(signal_bar),
                    "signal_known_timestamp_utc": _timestamp(signal_known),
                    "direction": "LONG",
                    "stop_price": 139.5,
                    "target_price": 140.5,
                    "latest_exit_timestamp_utc": _timestamp(scheduled_exit),
                    "reason_code": "BREAKOUT_LONG",
                    "metadata": {"session_date": session_date.isoformat()},
                },
                "decision": {
                    "decision_id": DECISION_ID,
                    "symbol": "USDJPY",
                    "decision_timestamp_utc": _timestamp(signal_bar),
                    "direction": "LONG",
                    "earliest_executable_timestamp_utc": _timestamp(signal_known),
                    "requested_risk_fraction": 0.0025,
                    "stop_price": 139.5,
                    "target_price": 140.5,
                    "reason_code": "BREAKOUT_LONG",
                    "reason_text": None,
                },
                "scheduled_exit": {
                    "decision_id": DECISION_ID,
                    "symbol": "USDJPY",
                    "timestamp_utc": _timestamp(scheduled_exit),
                },
            }
        ],
    )
    scenario_records: list[dict[str, object]] = []
    for scenario in (0.2, 0.5, 1.0):
        trade = _trade(scenario=scenario, entry=entry, exit_=exit_)
        scenario_records.extend(
            [
                {
                    "event": "trade_completed",
                    "slippage_pips": scenario,
                    "decision_id": DECISION_ID,
                    "trade": trade,
                },
                {
                    "event": "outcome",
                    "slippage_pips": scenario,
                    "decision_id": DECISION_ID,
                    "outcome": "COMPLETED",
                },
                {
                    "event": "financial_metrics",
                    "slippage_pips": scenario,
                    "metrics": {
                        "trade_count": 999,
                        "net_return": 99.0,
                        "expectancy_usd": 99.0,
                        "profit_factor": 99.0,
                        "max_drawdown_fraction": 0.0,
                    },
                },
            ]
        )
    _write_jsonl(segment / "scenarios.jsonl", scenario_records)
    _write_jsonl(
        segment / "operational.jsonl",
        [
            {
                "event": "segment_start",
                "timestamp_utc": _timestamp(run_start),
                "code_commit": CODE_COMMIT,
                "account_fingerprint_sha256": FINGERPRINT,
            },
            {"event": "connect", "timestamp_utc": _timestamp(run_start)},
            {
                "event": "normalized_append_latency",
                "timestamp_utc": _timestamp(entry),
                "source_time_utc": _timestamp(entry),
                "receive_monotonic_ns": 1_000_000_000,
                "append_completed_monotonic_ns": 1_020_000_000,
                "processing_latency_ms": 20.0,
            },
            {
                "event": "normalized_append_latency",
                "timestamp_utc": _timestamp(exit_),
                "source_time_utc": _timestamp(exit_),
                "receive_monotonic_ns": 2_000_000_000,
                "append_completed_monotonic_ns": 2_040_000_000,
                "processing_latency_ms": 40.0,
            },
            {"event": "disconnect", "timestamp_utc": _timestamp(run_end), "reason": "stream_end"},
        ],
    )
    digest = "d" * 64
    manifest = finalize_existing_segment(
        segment,
        code_commit=CODE_COMMIT,
        account_fingerprint_sha256=FINGERPRINT,
        run_start_utc=run_start,
        run_end_utc=run_end,
        replay_result_digest=digest,
    )
    derived = ("normalized.jsonl", "bars.jsonl", "decisions.jsonl", "scenarios.jsonl")
    _write_json(
        segment / "replay.json",
        {
            "protocol": "fmp-phase8-shadow-replay-v1",
            "match": True,
            "compared_files": list(derived),
            "semantic_files": ["bars.jsonl", "decisions.jsonl", "scenarios.jsonl"],
            "mismatched_files": [],
            "live_file_sha256": {name: manifest["file_sha256"][name] for name in derived},
            "replay_file_sha256": {name: manifest["file_sha256"][name] for name in derived},
            "replay_result_digest": digest,
        },
    )
    return segment


class Phase8ReviewAggregationTests(unittest.TestCase):
    def test_verified_segment_derives_campaign_metrics_timing_spreads_and_date_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            _, campaign = _setup_phase8(Path(tmp))
            _verified_segment(campaign)

            self.assertEqual(review_campaign(campaign), Phase8ReviewOutcome.NEED_MORE_DATA)
            evidence = json.loads((campaign / "review-evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(evidence["denominator_date_count"], 1)
            self.assertEqual(evidence["valid_date_count"], 1)
            self.assertEqual(evidence["fully_observed_london_dates"], 1)
            self.assertEqual(evidence["processing_latency_p99_ms"], 40.0)
            self.assertEqual(evidence["max_entry_quote_delay_seconds"], 3.0)
            self.assertEqual(evidence["max_time_exit_quote_delay_seconds"], 2.0)
            self.assertEqual(evidence["live_entry_spread"], {"median_pips": 0.3, "p95_pips": 0.3})
            self.assertEqual(evidence["live_exit_spread"], {"median_pips": 0.4, "p95_pips": 0.4})
            self.assertEqual(evidence["scenario_metrics"]["0.2"]["trade_count"], 1)
            self.assertAlmostEqual(evidence["scenario_metrics"]["0.2"]["net_return"], 0.001)
            self.assertEqual(evidence["scenario_metrics"]["0.2"]["expectancy_usd"], 100.0)
            self.assertNotEqual(evidence["scenario_metrics"]["0.2"]["trade_count"], 999)
            self.assertFalse(evidence["campaign_minimums_met"])
            self.assertTrue(evidence["replay_identical"])

    def test_tampered_stream_after_manifest_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            _, campaign = _setup_phase8(Path(tmp))
            segment = _verified_segment(campaign)
            with (segment / "scenarios.jsonl").open("ab") as handle:
                handle.write(b"{}\n")
            with self.assertRaisesRegex(ValueError, "digest|hash|manifest"):
                review_campaign(campaign)

    def test_replay_mismatch_records_frozen_safety_rejection(self) -> None:
        with TemporaryDirectory() as tmp:
            _, campaign = _setup_phase8(Path(tmp))
            segment = _verified_segment(campaign)
            replay = json.loads((segment / "replay.json").read_text(encoding="utf-8"))
            replay["match"] = False
            replay["mismatched_files"] = ["scenarios.jsonl"]
            _write_json(segment / "replay.json", replay)
            self.assertEqual(review_campaign(campaign), Phase8ReviewOutcome.REJECT_SAFETY)
            evidence = json.loads((campaign / "review-evidence.json").read_text(encoding="utf-8"))
            self.assertFalse(evidence["replay_identical"])


if __name__ == "__main__":
    unittest.main()
