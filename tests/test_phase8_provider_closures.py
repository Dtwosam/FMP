from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import fmp.shadow.campaign as campaign_module
from fmp.shadow.cli import build_parser


UTC = timezone.utc
CODE_COMMIT = "c" * 40
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


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _registered_campaign(root: Path) -> Path:
    reference = root / "reference"
    campaign = root / "campaign"
    payload = _canonical(REFERENCE)
    digest = hashlib.sha256(payload).hexdigest()
    reference.mkdir(parents=True)
    (reference / "reference.json").write_bytes(payload)
    (reference / "reference.sha256").write_text(digest + "\n", encoding="ascii")
    campaign_module.register_campaign(
        reference_dir=reference,
        campaign_dir=campaign,
        code_commit=CODE_COMMIT,
        campaign_start_utc=datetime(2026, 9, 16, 0, 0, tzinfo=UTC),
    )
    return campaign


class Phase8ProviderClosurePersistenceTests(unittest.TestCase):
    def test_provider_closure_is_append_only_canonical_and_loads_for_denominator(self) -> None:
        self.assertTrue(hasattr(campaign_module, "record_provider_closure"))
        self.assertTrue(hasattr(campaign_module, "load_provider_closures"))
        with TemporaryDirectory() as tmp:
            campaign = _registered_campaign(Path(tmp))
            closure = campaign_module.record_provider_closure(
                campaign_dir=campaign,
                code_commit=CODE_COMMIT,
                london_date=date(2026, 9, 18),
                documentation="OANDA published full-market closure notice",
                recorded_at_utc=datetime(2026, 9, 17, 20, 0, tzinfo=UTC),
            )
            self.assertEqual(closure.reason, campaign_module.FULL_MARKET_CLOSURE_REASON)
            path = campaign / "provider-closures.jsonl"
            self.assertEqual(path.read_bytes(), _canonical({
                "code_commit": CODE_COMMIT,
                "documentation": "OANDA published full-market closure notice",
                "london_date": "2026-09-18",
                "protocol": "fmp-phase8-provider-closure-v1",
                "reason": campaign_module.FULL_MARKET_CLOSURE_REASON,
                "recorded_at_utc": "2026-09-17T20:00:00Z",
            }))
            loaded = campaign_module.load_provider_closures(campaign, code_commit=CODE_COMMIT)
            self.assertEqual(loaded, (closure,))
            denominator = campaign_module.denominator_london_dates(
                first_london_date=date(2026, 9, 16),
                review_cutoff_utc=datetime(2026, 9, 19, 0, 0, tzinfo=UTC),
                provider_closures=loaded,
            )
            self.assertEqual(denominator, (date(2026, 9, 16), date(2026, 9, 17)))

    def test_duplicate_backdated_weekend_and_tampered_records_fail_closed(self) -> None:
        self.assertTrue(hasattr(campaign_module, "record_provider_closure"))
        with TemporaryDirectory() as tmp:
            campaign = _registered_campaign(Path(tmp))
            kwargs = dict(
                campaign_dir=campaign,
                code_commit=CODE_COMMIT,
                london_date=date(2026, 9, 18),
                documentation="provider notice",
                recorded_at_utc=datetime(2026, 9, 17, 20, 0, tzinfo=UTC),
            )
            campaign_module.record_provider_closure(**kwargs)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                campaign_module.record_provider_closure(**kwargs)
            with self.assertRaisesRegex(ValueError, "before"):
                campaign_module.record_provider_closure(
                    campaign_dir=campaign,
                    code_commit=CODE_COMMIT,
                    london_date=date(2026, 9, 21),
                    documentation="provider notice",
                    recorded_at_utc=datetime(2026, 9, 21, 0, 1, tzinfo=UTC),
                )
            with self.assertRaisesRegex(ValueError, "weekday"):
                campaign_module.record_provider_closure(
                    campaign_dir=campaign,
                    code_commit=CODE_COMMIT,
                    london_date=date(2026, 9, 19),
                    documentation="provider notice",
                    recorded_at_utc=datetime(2026, 9, 18, 20, 0, tzinfo=UTC),
                )
            with (campaign / "provider-closures.jsonl").open("ab") as handle:
                handle.write(b"{}\n")
            with self.assertRaises(ValueError):
                campaign_module.load_provider_closures(campaign, code_commit=CODE_COMMIT)

    def test_cli_exposes_only_explicit_source_free_closure_recording_inputs(self) -> None:
        parser = build_parser()
        args = parser.parse_args([
            "record-closure",
            "--campaign-dir",
            "campaign",
            "--london-date",
            "2026-09-18",
            "--documentation",
            "provider notice",
        ])
        self.assertEqual(args.command, "record-closure")
        self.assertEqual(args.london_date, date(2026, 9, 18))
        self.assertEqual(args.documentation, "provider notice")
        for forbidden in ("recorded_at", "reason", "host", "instrument", "threshold"):
            self.assertFalse(hasattr(args, forbidden))


if __name__ == "__main__":
    unittest.main()
