from __future__ import annotations

import unittest

from fmp.market_learning.source_preservation import (
    PRESERVATION_TAG,
    PRESERVATION_TITLE,
    PRESERVATION_VERSION,
    build_preservation_manifest,
    release_asset_name,
    validate_preservation_manifest,
    validate_published_release_metadata,
    validate_release_metadata,
)


COMMIT = "a" * 40


def _release(manifest: dict[str, object]) -> dict[str, object]:
    assets = []
    for row in manifest["assets"]:
        assets.append(
            {
                "name": row["release_asset_name"],
                "state": "uploaded",
                "size": row["size_in_bytes"],
                "digest": f"sha256:{row['zip_sha256']}",
            }
        )
    assets.append(
        {
            "name": "phase2-preservation-manifest.json",
            "state": "uploaded",
            "size": 1234,
            "digest": "sha256:" + "f" * 64,
        }
    )
    return {
        "tag_name": PRESERVATION_TAG,
        "name": PRESERVATION_TITLE,
        "draft": True,
        "prerelease": False,
        "assets": assets,
    }


class Phase2SourcePreservationTests(unittest.TestCase):
    def test_manifest_freezes_exact_three_existing_artifacts(self) -> None:
        manifest = build_preservation_manifest(code_commit=COMMIT)
        self.assertEqual(manifest["preservation_version"], PRESERVATION_VERSION)
        self.assertEqual(manifest["preservation_tag"], PRESERVATION_TAG)
        self.assertEqual(manifest["phase2_source_run_id"], 34782357048)
        self.assertEqual(
            manifest["phase2_source_head_sha"],
            "158c1c121655867b7fb2886fe755585dfcd682ec",
        )
        self.assertTrue(manifest["reuse_existing_accepted_history"])
        self.assertFalse(manifest["new_acquisition_performed"])
        self.assertFalse(manifest["source_bytes_changed"])
        self.assertEqual(len(manifest["assets"]), 3)
        self.assertEqual(
            [row["symbol"] for row in manifest["assets"]],
            ["EURUSD", "GBPUSD", "USDJPY"],
        )
        self.assertEqual(
            [row["release_asset_name"] for row in manifest["assets"]],
            [
                release_asset_name("EURUSD"),
                release_asset_name("GBPUSD"),
                release_asset_name("USDJPY"),
            ],
        )
        for flag in (
            "model_fit_authorized",
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
        ):
            self.assertFalse(manifest[flag])

    def test_preservation_manifest_validator_rejects_identity_drift(self) -> None:
        manifest = build_preservation_manifest(code_commit=COMMIT)
        result = validate_preservation_manifest(manifest)
        self.assertTrue(result["preservation_manifest_verified"])
        self.assertEqual(result["preservation_code_commit"], COMMIT)

        tampered = dict(manifest)
        tampered["assets"] = [dict(row) for row in manifest["assets"]]
        tampered["assets"][0]["zip_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "EURUSD identity mismatch"):
            validate_preservation_manifest(tampered)

    def test_published_release_verification_returns_exact_download_ids(self) -> None:
        manifest = build_preservation_manifest(code_commit=COMMIT)
        release = _release(manifest)
        release["draft"] = False
        for index, asset in enumerate(release["assets"], start=100):
            asset["id"] = index
        result = validate_published_release_metadata(
            release=release,
            manifest=manifest,
        )
        self.assertTrue(result["published_release_verified"])
        self.assertEqual(result["verified_zip_asset_count"], 3)
        self.assertEqual(
            [row["symbol"] for row in result["assets"]],
            ["EURUSD", "GBPUSD", "USDJPY"],
        )
        self.assertEqual(
            [row["asset_id"] for row in result["assets"]],
            [100, 101, 102],
        )
        self.assertEqual(result["manifest_asset_id"], 103)

    def test_published_release_rejects_tampered_or_draft_assets(self) -> None:
        manifest = build_preservation_manifest(code_commit=COMMIT)
        release = _release(manifest)
        for index, asset in enumerate(release["assets"], start=100):
            asset["id"] = index
        with self.assertRaisesRegex(ValueError, "must not be draft"):
            validate_published_release_metadata(
                release=release,
                manifest=manifest,
            )

        release["draft"] = False
        release["assets"][1]["digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            validate_published_release_metadata(
                release=release,
                manifest=manifest,
            )

    def test_release_verification_accepts_exact_uploaded_assets(self) -> None:
        manifest = build_preservation_manifest(code_commit=COMMIT)
        result = validate_release_metadata(
            release=_release(manifest),
            manifest=manifest,
        )
        self.assertTrue(result["release_assets_verified"])
        self.assertEqual(result["verified_zip_asset_count"], 3)
        self.assertFalse(result["model_fit_authorized"])
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["trading_authorized"])

    def test_release_verification_rejects_wrong_digest(self) -> None:
        manifest = build_preservation_manifest(code_commit=COMMIT)
        release = _release(manifest)
        release["assets"][0]["digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            validate_release_metadata(release=release, manifest=manifest)

    def test_release_verification_rejects_missing_or_extra_assets(self) -> None:
        manifest = build_preservation_manifest(code_commit=COMMIT)
        release = _release(manifest)
        release["assets"].pop()
        with self.assertRaisesRegex(ValueError, "asset set mismatch"):
            validate_release_metadata(release=release, manifest=manifest)

    def test_release_must_be_draft_during_verification(self) -> None:
        manifest = build_preservation_manifest(code_commit=COMMIT)
        release = _release(manifest)
        release["draft"] = False
        with self.assertRaisesRegex(ValueError, "remain draft"):
            validate_release_metadata(release=release, manifest=manifest)

    def test_invalid_preservation_commit_fails_closed(self) -> None:
        for value in ("deadbeef", "g" * 40):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "40-character Git SHA"):
                    build_preservation_manifest(code_commit=value)


if __name__ == "__main__":
    unittest.main()
