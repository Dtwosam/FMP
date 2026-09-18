from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fmp.shadow import campaign
from fmp.shadow.gates import Phase8ReviewOutcome, review_campaign
from fmp.shadow.qualification import mt5_boundary_audit


CODE_COMMIT = "c" * 40
FINGERPRINT = "f" * 64
QUALIFICATION_SESSION = "a" * 64
SERVER = "FPMarketsSC-Demo2"
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


def _canonical(record: dict[str, object]) -> bytes:
    return (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _write_json(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical(record))


class Phase8ReviewCompilerTests(unittest.TestCase):
    def test_review_never_trusts_operator_authored_review_evidence_without_campaign_sources(self) -> None:
        with TemporaryDirectory() as tmp:
            campaign_dir = Path(tmp) / "phase8" / "campaign"
            campaign_dir.mkdir(parents=True)
            _write_json(
                campaign_dir / "review-evidence.json",
                {
                    "structural_safety_ok": True,
                    "durable_artifacts_secret_free": True,
                    "qualification_pass": True,
                    "denominator_date_count": 40,
                    "valid_date_count": 40,
                    "fully_observed_london_dates": 40,
                    "malformed_silently_accepted_count": 0,
                    "stale_gap_financial_outcomes_count": 0,
                    "operational_events_complete": True,
                    "processing_latency_p99_ms": 1.0,
                    "max_entry_quote_delay_seconds": 1.0,
                    "max_time_exit_quote_delay_seconds": 1.0,
                    "historical_entry_spread": {"median_pips": 0.3, "p95_pips": 0.5},
                    "historical_exit_spread": {"median_pips": 0.4, "p95_pips": 0.6},
                    "live_entry_spread": {"median_pips": 0.3, "p95_pips": 0.5},
                    "live_exit_spread": {"median_pips": 0.4, "p95_pips": 0.6},
                    "scenario_metrics": {
                        "0.2": {"trade_count": 40, "net_return": 0.01, "expectancy_usd": 1.0, "profit_factor": 1.1, "max_drawdown_fraction": 0.01},
                        "0.5": {"trade_count": 40, "net_return": 0.01, "expectancy_usd": 1.0, "profit_factor": 1.1, "max_drawdown_fraction": 0.01},
                        "1.0": {"trade_count": 40, "net_return": 0.0, "expectancy_usd": 0.0, "profit_factor": 0.0, "max_drawdown_fraction": 0.0},
                    },
                    "campaign_minimums_met": True,
                    "replay_identical": True,
                },
            )
            with self.assertRaisesRegex(ValueError, "registration"):
                review_campaign(campaign_dir)

    def test_empty_registered_campaign_derives_need_more_data_and_persists_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            phase8 = Path(tmp) / "phase8"
            reference_dir = phase8 / "reference"
            campaign_dir = phase8 / "campaign"
            qualification_dir = phase8 / "qualification"

            reference_bytes = _canonical(REFERENCE)
            digest = hashlib.sha256(reference_bytes).hexdigest()
            reference_dir.mkdir(parents=True)
            (reference_dir / "reference.json").write_bytes(reference_bytes)
            (reference_dir / "reference.sha256").write_text(digest + "\n", encoding="ascii")

            with patch("fmp.shadow.campaign._load_reference", return_value=(REFERENCE, digest)):
                campaign.register_campaign(
                    reference_dir=reference_dir,
                    campaign_dir=campaign_dir,
                    code_commit=CODE_COMMIT,
                    campaign_start_utc=datetime(2026, 9, 16, 10, 0, tzinfo=timezone.utc),
                )

            _write_json(
                qualification_dir / "qualification.json",
                {
                    "outcome": "PASS",
                    "account_fingerprint": FINGERPRINT,
                    "started_at_utc": "2026-09-16T09:00:00Z",
                    "ended_at_utc": "2026-09-16T09:05:00Z",
                    "elapsed_seconds": 300.0,
                    "price_count": 100,
                    "heartbeat_count": 6,
                    "max_liveness_gap_seconds": 10.0,
                    "max_bridge_liveness_gap_seconds": 10.0,
                    "max_market_liveness_gap_seconds": 10.0,
                    "bridge_session_id": QUALIFICATION_SESSION,
                    "server": SERVER,
                    "boundary_audit": mt5_boundary_audit(),
                    "rejection_codes": [],
                },
            )

            self.assertEqual(review_campaign(campaign_dir), Phase8ReviewOutcome.NEED_MORE_DATA)
            derived = json.loads((campaign_dir / "review-evidence.json").read_text(encoding="utf-8"))
            self.assertTrue(derived["qualification_pass"])
            self.assertFalse(derived["campaign_minimums_met"])
            self.assertEqual(derived["denominator_date_count"], 0)
            self.assertEqual(derived["scenario_metrics"]["0.2"]["trade_count"], 0)
            self.assertEqual(derived["historical_entry_spread"], {"median_pips": 0.3, "p95_pips": 0.5})
            self.assertEqual(derived["historical_exit_spread"], {"median_pips": 0.4, "p95_pips": 0.6})


if __name__ == "__main__":
    unittest.main()
