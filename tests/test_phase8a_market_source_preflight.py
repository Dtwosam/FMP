from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from fmp.market_learning.source_preflight import (
    PHASE2_SOURCE_HEAD_SHA,
    PHASE2_SOURCE_RUN_ID,
    SOURCE_ARTIFACTS,
    compile_source_preflight,
    validate_source_artifact_metadata,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 23, 10, 0, tzinfo=UTC)


def _metadata(spec, *, expires_at: str = "2026-12-12T20:57:47Z") -> dict[str, object]:
    return {
        "id": spec.artifact_id,
        "name": spec.artifact_name,
        "size_in_bytes": spec.size_in_bytes,
        "expired": False,
        "created_at": "2026-09-13T21:35:10Z",
        "expires_at": expires_at,
        "digest": f"sha256:{spec.zip_sha256}",
        "workflow_run": {
            "id": PHASE2_SOURCE_RUN_ID,
            "head_branch": "main",
            "head_sha": PHASE2_SOURCE_HEAD_SHA,
        },
    }


class MarketSourcePreflightTests(unittest.TestCase):
    def test_complete_source_preflight_is_ready_and_authorizes_nothing(self) -> None:
        metadata = {spec.symbol: _metadata(spec) for spec in SOURCE_ARTIFACTS}
        report = compile_source_preflight(
            metadata_by_symbol=metadata,
            now_utc=NOW,
            minimum_remaining=timedelta(hours=12),
        )
        self.assertTrue(report["source_ready"])
        self.assertFalse(report["new_acquisition_performed"])
        self.assertEqual(report["historical_source"], "Dukascopy")
        self.assertEqual(report["phase2_source_run_id"], PHASE2_SOURCE_RUN_ID)
        self.assertEqual(report["phase2_source_head_sha"], PHASE2_SOURCE_HEAD_SHA)
        self.assertEqual(len(report["artifacts"]), 3)
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["demo_order_authorized"])
        self.assertFalse(report["broker_mutation_authorized"])
        self.assertFalse(report["live_order_authorized"])
        self.assertFalse(report["real_money_authorized"])

    def test_wrong_digest_fails_closed(self) -> None:
        spec = SOURCE_ARTIFACTS[0]
        metadata = _metadata(spec)
        metadata["digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            validate_source_artifact_metadata(
                metadata=metadata,
                spec=spec,
                now_utc=NOW,
                minimum_remaining=timedelta(hours=12),
            )

    def test_expired_artifact_fails_closed(self) -> None:
        spec = SOURCE_ARTIFACTS[0]
        metadata = _metadata(spec)
        metadata["expired"] = True
        with self.assertRaisesRegex(ValueError, "expired"):
            validate_source_artifact_metadata(
                metadata=metadata,
                spec=spec,
                now_utc=NOW,
                minimum_remaining=timedelta(hours=12),
            )

    def test_wrong_source_run_or_commit_fails_closed(self) -> None:
        spec = SOURCE_ARTIFACTS[0]
        metadata = _metadata(spec)
        metadata["workflow_run"]["id"] = PHASE2_SOURCE_RUN_ID + 1
        with self.assertRaisesRegex(ValueError, "source run id"):
            validate_source_artifact_metadata(
                metadata=metadata,
                spec=spec,
                now_utc=NOW,
                minimum_remaining=timedelta(hours=12),
            )

        metadata = _metadata(spec)
        metadata["workflow_run"]["head_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "source commit"):
            validate_source_artifact_metadata(
                metadata=metadata,
                spec=spec,
                now_utc=NOW,
                minimum_remaining=timedelta(hours=12),
            )

    def test_insufficient_remaining_lifetime_fails_closed(self) -> None:
        spec = SOURCE_ARTIFACTS[0]
        metadata = _metadata(spec, expires_at="2026-09-23T20:00:00Z")
        with self.assertRaisesRegex(ValueError, "enough remaining lifetime"):
            validate_source_artifact_metadata(
                metadata=metadata,
                spec=spec,
                now_utc=NOW,
                minimum_remaining=timedelta(hours=12),
            )

    def test_exact_three_symbols_are_required(self) -> None:
        metadata = {spec.symbol: _metadata(spec) for spec in SOURCE_ARTIFACTS}
        metadata.pop("USDJPY")
        with self.assertRaisesRegex(ValueError, "exact EURUSD/GBPUSD/USDJPY"):
            compile_source_preflight(
                metadata_by_symbol=metadata,
                now_utc=NOW,
            )


if __name__ == "__main__":
    unittest.main()
