from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fmp.shadow.campaign import (
    FULL_MARKET_CLOSURE_REASON,
    CampaignEvidenceSummary,
    ProviderClosure,
    denominator_london_dates,
    minimum_review_evidence_met,
    register_campaign,
)
from fmp.shadow.cli import build_parser, main


UTC = timezone.utc
CODE_COMMIT = "c" * 40
REFERENCE_SHA = "d" * 64


def _reference_record() -> dict[str, object]:
    return {
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
            "2025-Q1",
            "2025-Q2",
            "2025-Q3",
            "2025-Q4",
            "2026-Q1",
            "2026-Q2",
            "2026-partial-Q3",
        ],
        "trade_count": 100,
        "entry_spread_pips": {"count": 100, "median": 0.8, "p95": 1.4, "p95_method": "nearest_rank"},
        "exit_spread_pips": {"count": 100, "median": 0.9, "p95": 1.5, "p95_method": "nearest_rank"},
        "trades": [],
    }


def _write_reference(root: Path) -> str:
    record = _reference_record()
    payload = (
        json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    (root / "reference.json").write_bytes(payload)
    (root / "reference.sha256").write_text(digest + "\n", encoding="utf-8")
    return digest


class Phase8CampaignTests(unittest.TestCase):
    def test_registration_verifies_reference_and_freezes_all_protocol_thresholds(self) -> None:
        with TemporaryDirectory() as ref_tmp, TemporaryDirectory() as campaign_tmp:
            reference_dir = Path(ref_tmp)
            campaign_dir = Path(campaign_tmp)
            digest = _write_reference(reference_dir)
            started = datetime(2026, 9, 16, 10, 30, tzinfo=UTC)

            record = register_campaign(
                reference_dir=reference_dir,
                campaign_dir=campaign_dir,
                code_commit=CODE_COMMIT,
                campaign_start_utc=started,
            )

            self.assertEqual(record["registration_version"], 2)
            self.assertEqual(record["campaign_start_utc"], "2026-09-16T10:30:00Z")
            self.assertEqual(record["first_london_date"], "2026-09-16")
            self.assertEqual(record["code_commit"], CODE_COMMIT)
            self.assertEqual(record["reference_sha256"], digest)
            self.assertEqual(record["phase8_experiment"], "EXP-20260922-011")
            self.assertEqual(record["provider"], "FP_MARKETS_MT5_DEMO")
            self.assertEqual(record["connector_protocol"], "fmp-mt5-demo-file-bridge-v1")
            self.assertEqual(record["transport"], "MT5_FILE_COMMON_JSONL")
            self.assertEqual(record["bridge_file"], "FMP/phase8-usdjpy-feed.jsonl")
            self.assertEqual(record["allowed_servers"], ["FPMarketsSC-Demo", "FPMarketsSC-Demo2"])
            self.assertEqual(record["provider_instrument"], "USDJPY")
            self.assertNotIn("host", record)
            self.assertNotIn("path_template", record)
            self.assertNotIn("instrument", record)
            self.assertEqual(record["strategy"]["id"], "session_breakout")
            self.assertEqual(record["slippage_scenarios"], [0.2, 0.5, 1.0])
            self.assertEqual(record["gating_slippage_scenarios"], [0.2, 0.5])
            self.assertEqual(record["starting_equity_usd"], 100_000.0)
            thresholds = record["acceptance_thresholds"]
            self.assertEqual(thresholds["minimum_completed_scorable_trades_0p2"], 40)
            self.assertEqual(thresholds["minimum_elapsed_calendar_weeks"], 8)
            self.assertEqual(thresholds["minimum_fully_observed_london_dates"], 30)
            self.assertEqual(thresholds["minimum_valid_date_coverage_fraction"], 0.90)
            self.assertEqual(thresholds["maximum_processing_latency_p99_ms"], 250.0)
            self.assertEqual(thresholds["maximum_quote_delay_seconds"], 5.0)
            self.assertEqual(thresholds["maximum_spread_parity_delta_pips"], 0.5)
            self.assertEqual(thresholds["maximum_drawdown_fraction"], 0.05)
            self.assertTrue((campaign_dir / "registration.json").is_file())

    def test_registration_is_exactly_once_and_tampered_reference_fails_closed(self) -> None:
        with TemporaryDirectory() as ref_tmp, TemporaryDirectory() as campaign_tmp:
            reference_dir = Path(ref_tmp)
            campaign_dir = Path(campaign_tmp)
            _write_reference(reference_dir)
            started = datetime(2026, 9, 16, 10, 30, tzinfo=UTC)
            register_campaign(
                reference_dir=reference_dir,
                campaign_dir=campaign_dir,
                code_commit=CODE_COMMIT,
                campaign_start_utc=started,
            )
            with self.assertRaisesRegex(FileExistsError, "registration"):
                register_campaign(
                    reference_dir=reference_dir,
                    campaign_dir=campaign_dir,
                    code_commit=CODE_COMMIT,
                    campaign_start_utc=started + timedelta(days=1),
                )

        with TemporaryDirectory() as ref_tmp, TemporaryDirectory() as campaign_tmp:
            reference_dir = Path(ref_tmp)
            _write_reference(reference_dir)
            (reference_dir / "reference.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "digest"):
                register_campaign(
                    reference_dir=reference_dir,
                    campaign_dir=Path(campaign_tmp),
                    code_commit=CODE_COMMIT,
                    campaign_start_utc=datetime(2026, 9, 16, 10, 30, tzinfo=UTC),
                )

    def test_weekday_denominator_allows_only_predeclared_documented_full_market_closures(self) -> None:
        start = date(2026, 9, 14)
        cutoff = datetime(2026, 9, 21, 23, 0, tzinfo=UTC)
        closure = ProviderClosure(
            london_date=date(2026, 9, 17),
            reason=FULL_MARKET_CLOSURE_REASON,
            documentation="provider holiday notice",
            recorded_at_utc=datetime(2026, 9, 16, 12, 0, tzinfo=UTC),
        )
        dates = denominator_london_dates(
            first_london_date=start,
            review_cutoff_utc=cutoff,
            provider_closures=(closure,),
        )
        self.assertEqual(
            dates,
            (
                date(2026, 9, 14),
                date(2026, 9, 15),
                date(2026, 9, 16),
                date(2026, 9, 18),
                date(2026, 9, 21),
            ),
        )

        late = ProviderClosure(
            london_date=date(2026, 9, 18),
            reason=FULL_MARKET_CLOSURE_REASON,
            documentation="late provider notice",
            recorded_at_utc=datetime(2026, 9, 18, 8, 0, tzinfo=UTC),
        )
        with self.assertRaisesRegex(ValueError, "before the London date begins"):
            denominator_london_dates(
                first_london_date=start,
                review_cutoff_utc=cutoff,
                provider_closures=(late,),
            )

        with self.assertRaisesRegex(ValueError, "full-market closure"):
            ProviderClosure(
                london_date=date(2026, 9, 18),
                reason="OUTAGE",
                documentation="operator outage",
                recorded_at_utc=datetime(2026, 9, 17, 12, 0, tzinfo=UTC),
            )

    def test_review_minimums_require_all_five_frozen_conditions(self) -> None:
        base = CampaignEvidenceSummary(
            completed_scorable_trades_0p2=40,
            first_observation_utc=datetime(2026, 7, 1, tzinfo=UTC),
            last_observation_utc=datetime(2026, 8, 26, tzinfo=UTC),
            fully_observed_london_dates=30,
            all_scored_trades_have_complete_path=True,
            all_three_scenarios_share_candidate_sequence=True,
        )
        self.assertTrue(minimum_review_evidence_met(base))

        failures = (
            {"completed_scorable_trades_0p2": 39},
            {"last_observation_utc": datetime(2026, 8, 25, 23, 59, tzinfo=UTC)},
            {"fully_observed_london_dates": 29},
            {"all_scored_trades_have_complete_path": False},
            {"all_three_scenarios_share_candidate_sequence": False},
        )
        values = base.__dict__ if hasattr(base, "__dict__") else {
            "completed_scorable_trades_0p2": base.completed_scorable_trades_0p2,
            "first_observation_utc": base.first_observation_utc,
            "last_observation_utc": base.last_observation_utc,
            "fully_observed_london_dates": base.fully_observed_london_dates,
            "all_scored_trades_have_complete_path": base.all_scored_trades_have_complete_path,
            "all_three_scenarios_share_candidate_sequence": base.all_three_scenarios_share_candidate_sequence,
        }
        for override in failures:
            record = dict(values)
            record.update(override)
            self.assertFalse(minimum_review_evidence_met(CampaignEvidenceSummary(**record)))

    def test_register_cli_is_source_free_and_has_no_threshold_overrides(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "register",
                "--reference",
                "reference",
                "--campaign-dir",
                "campaign",
            ]
        )
        self.assertEqual(args.command, "register")
        for forbidden in (
            "minimum_trades",
            "weeks",
            "minimum_dates",
            "coverage",
            "spread_tolerance",
            "slippage",
            "host",
            "instrument",
        ):
            self.assertFalse(hasattr(args, forbidden))

        calls: list[dict[str, object]] = []
        started = datetime(2026, 9, 16, 10, 30, tzinfo=UTC)
        rc = main(
            [
                "register",
                "--reference",
                "reference",
                "--campaign-dir",
                "campaign",
            ],
            environ={},
            register_command=lambda **kwargs: calls.append(kwargs) or {},
            code_commit_resolver=lambda: CODE_COMMIT,
            utc_now=lambda: started,
        )
        self.assertEqual(rc, 0)
        self.assertEqual(calls[0]["reference_dir"], Path("reference"))
        self.assertEqual(calls[0]["campaign_dir"], Path("campaign"))
        self.assertEqual(calls[0]["code_commit"], CODE_COMMIT)
        self.assertEqual(calls[0]["campaign_start_utc"], started)


if __name__ == "__main__":
    unittest.main()
