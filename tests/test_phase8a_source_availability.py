from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from fmp.market_learning.source_availability import (
    SOURCE_AVAILABILITY_VERSION,
    compile_source_availability,
)
from fmp.market_learning.source_preflight import (
    PHASE2_SOURCE_HEAD_SHA,
    PHASE2_SOURCE_RUN_ID,
    SOURCE_ARTIFACTS,
)
from fmp.market_learning.source_preservation import (
    PRESERVATION_TAG,
    PRESERVATION_TITLE,
    build_preservation_manifest,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 23, 12, 0, tzinfo=UTC)
COMMIT = "a" * 40


def _action_metadata(spec, *, expired: bool = False) -> dict[str, object]:
    return {
        "id": spec.artifact_id,
        "name": spec.artifact_name,
        "size_in_bytes": spec.size_in_bytes,
        "expired": expired,
        "created_at": "2026-09-13T21:35:10Z",
        "expires_at": "2026-12-12T20:57:47Z",
        "digest": f"sha256:{spec.zip_sha256}",
        "workflow_run": {
            "id": PHASE2_SOURCE_RUN_ID,
            "head_branch": "main",
            "head_sha": PHASE2_SOURCE_HEAD_SHA,
        },
    }


def _published_release(manifest: dict[str, object]) -> dict[str, object]:
    assets = []
    for index, row in enumerate(manifest["assets"], start=200):
        assets.append(
            {
                "id": index,
                "name": row["release_asset_name"],
                "state": "uploaded",
                "size": row["size_in_bytes"],
                "digest": f"sha256:{row['zip_sha256']}",
            }
        )
    assets.append(
        {
            "id": 203,
            "name": "phase2-preservation-manifest.json",
            "state": "uploaded",
            "size": 1000,
            "digest": "sha256:" + "f" * 64,
        }
    )
    return {
        "tag_name": PRESERVATION_TAG,
        "name": PRESERVATION_TITLE,
        "draft": False,
        "prerelease": False,
        "assets": assets,
    }


class Phase2SourceAvailabilityTests(unittest.TestCase):
    def test_actions_are_preferred_when_all_originals_are_healthy(self) -> None:
        metadata = {spec.symbol: _action_metadata(spec) for spec in SOURCE_ARTIFACTS}
        manifest = build_preservation_manifest(code_commit=COMMIT)
        release = _published_release(manifest)
        report = compile_source_availability(
            metadata_by_symbol=metadata,
            now_utc=NOW,
            minimum_remaining=timedelta(hours=12),
            release=release,
            preservation_manifest=manifest,
        )
        self.assertEqual(report["availability_version"], SOURCE_AVAILABILITY_VERSION)
        self.assertEqual(report["source_mode"], "actions")
        self.assertTrue(report["original_actions_ready"])
        self.assertFalse(report["preservation_release_verified"])
        self.assertEqual(len(report["artifacts"]), 3)

    def test_one_failed_original_switches_entire_run_to_release(self) -> None:
        metadata = {spec.symbol: _action_metadata(spec) for spec in SOURCE_ARTIFACTS}
        metadata["EURUSD"]["expired"] = True
        manifest = build_preservation_manifest(code_commit=COMMIT)
        report = compile_source_availability(
            metadata_by_symbol=metadata,
            now_utc=NOW,
            release=_published_release(manifest),
            preservation_manifest=manifest,
        )
        self.assertEqual(report["source_mode"], "release")
        self.assertFalse(report["original_actions_ready"])
        self.assertTrue(report["preservation_release_verified"])
        self.assertEqual(
            [row["symbol"] for row in report["artifacts"]],
            ["EURUSD", "GBPUSD", "USDJPY"],
        )
        self.assertEqual(
            [row["asset_id"] for row in report["artifacts"]],
            [200, 201, 202],
        )
        self.assertFalse(report["new_acquisition_performed"])
        self.assertFalse(report["source_bytes_changed"])
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["live_order_authorized"])

    def test_release_is_required_if_original_bundle_is_not_fully_ready(self) -> None:
        metadata = {spec.symbol: _action_metadata(spec) for spec in SOURCE_ARTIFACTS}
        metadata["USDJPY"]["expired"] = True
        with self.assertRaisesRegex(ValueError, "no validated preservation release"):
            compile_source_availability(
                metadata_by_symbol=metadata,
                now_utc=NOW,
            )

    def test_tampered_release_cannot_rescue_expired_originals(self) -> None:
        metadata = {spec.symbol: _action_metadata(spec, expired=True) for spec in SOURCE_ARTIFACTS}
        manifest = build_preservation_manifest(code_commit=COMMIT)
        release = _published_release(manifest)
        release["assets"][0]["size"] = 1
        with self.assertRaisesRegex(ValueError, "size mismatch"):
            compile_source_availability(
                metadata_by_symbol=metadata,
                now_utc=NOW,
                release=release,
                preservation_manifest=manifest,
            )

    def test_tampered_manifest_cannot_rescue_expired_originals(self) -> None:
        metadata = {spec.symbol: _action_metadata(spec, expired=True) for spec in SOURCE_ARTIFACTS}
        manifest = build_preservation_manifest(code_commit=COMMIT)
        manifest["assets"][2]["processed_manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "USDJPY identity mismatch"):
            compile_source_availability(
                metadata_by_symbol=metadata,
                now_utc=NOW,
                release=_published_release(build_preservation_manifest(code_commit=COMMIT)),
                preservation_manifest=manifest,
            )


if __name__ == "__main__":
    unittest.main()
