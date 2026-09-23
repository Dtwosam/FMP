from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Mapping

from .source_preflight import (
    PHASE2_SOURCE_HEAD_SHA,
    PHASE2_SOURCE_RUN_ID,
    SOURCE_ARTIFACTS,
)


PRESERVATION_VERSION = "fmp-phase2-release-preservation-v1"
PRESERVATION_TAG = "fmp-phase2-accepted-artifacts-v1"
PRESERVATION_TITLE = "FMP Phase 2 accepted artifacts v1"

_SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")


def release_asset_name(symbol: str) -> str:
    return f"phase2-full-history-{symbol}.zip"


def build_preservation_manifest(*, code_commit: str) -> dict[str, object]:
    if _SHA40.fullmatch(code_commit) is None:
        raise ValueError("preservation code_commit must be a 40-character Git SHA")

    assets: list[dict[str, object]] = []
    for spec in SOURCE_ARTIFACTS:
        assets.append(
            {
                "symbol": spec.symbol,
                "original_actions_artifact_id": spec.artifact_id,
                "original_actions_artifact_name": spec.artifact_name,
                "release_asset_name": release_asset_name(spec.symbol),
                "zip_sha256": spec.zip_sha256,
                "size_in_bytes": spec.size_in_bytes,
                "processed_manifest_sha256": spec.processed_manifest_sha256,
            }
        )

    return {
        "preservation_version": PRESERVATION_VERSION,
        "experiment_id": "EXP-20260923-044",
        "historical_source": "Dukascopy",
        "phase2_source_run_id": PHASE2_SOURCE_RUN_ID,
        "phase2_source_head_sha": PHASE2_SOURCE_HEAD_SHA,
        "preservation_tag": PRESERVATION_TAG,
        "preservation_title": PRESERVATION_TITLE,
        "preservation_code_commit": code_commit.lower(),
        "reuse_existing_accepted_history": True,
        "new_acquisition_performed": False,
        "source_bytes_changed": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "assets": assets,
    }


def write_preservation_manifest(
    *,
    manifest: Mapping[str, object],
    path: Path,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(dict(manifest), sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def validate_release_metadata(
    *,
    release: Mapping[str, object],
    manifest: Mapping[str, object],
) -> dict[str, object]:
    if release.get("tag_name") != PRESERVATION_TAG:
        raise ValueError("preservation release tag mismatch")
    if release.get("name") != PRESERVATION_TITLE:
        raise ValueError("preservation release title mismatch")
    if release.get("draft") is not True:
        raise ValueError("preservation release must remain draft during verification")
    if release.get("prerelease") is not False:
        raise ValueError("preservation release must not be a prerelease")

    expected_assets = manifest.get("assets")
    if not isinstance(expected_assets, list) or len(expected_assets) != 3:
        raise ValueError("preservation manifest assets are incomplete")

    raw_assets = release.get("assets")
    if not isinstance(raw_assets, list):
        raise ValueError("preservation release assets are malformed")
    by_name: dict[str, Mapping[str, object]] = {}
    for raw in raw_assets:
        if not isinstance(raw, Mapping):
            raise ValueError("preservation release asset row is malformed")
        name = raw.get("name")
        if not isinstance(name, str):
            raise ValueError("preservation release asset name is invalid")
        if name in by_name:
            raise ValueError("duplicate preservation release asset name")
        by_name[name] = raw

    expected_names = {
        str(item["release_asset_name"])
        for item in expected_assets
        if isinstance(item, Mapping)
    }
    expected_names.add("phase2-preservation-manifest.json")
    if set(by_name) != expected_names:
        raise ValueError("preservation release asset set mismatch")

    verified: list[dict[str, object]] = []
    for expected in expected_assets:
        if not isinstance(expected, Mapping):
            raise ValueError("preservation manifest asset row is malformed")
        name = expected.get("release_asset_name")
        if not isinstance(name, str):
            raise ValueError("preservation manifest release asset name is invalid")
        actual = by_name[name]
        if actual.get("state") != "uploaded":
            raise ValueError(f"preservation release asset is not uploaded: {name}")
        if actual.get("size") != expected.get("size_in_bytes"):
            raise ValueError(f"preservation release asset size mismatch: {name}")
        if actual.get("digest") != f"sha256:{expected.get('zip_sha256')}":
            raise ValueError(f"preservation release asset digest mismatch: {name}")
        verified.append(
            {
                "name": name,
                "size": actual.get("size"),
                "digest": actual.get("digest"),
            }
        )

    manifest_asset = by_name["phase2-preservation-manifest.json"]
    if manifest_asset.get("state") != "uploaded":
        raise ValueError("preservation manifest release asset is not uploaded")

    return {
        "preservation_tag": PRESERVATION_TAG,
        "verified_zip_asset_count": len(verified),
        "release_assets_verified": True,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "trading_authorized": False,
        "assets": verified,
    }


__all__ = [
    "PRESERVATION_TAG",
    "PRESERVATION_TITLE",
    "PRESERVATION_VERSION",
    "build_preservation_manifest",
    "release_asset_name",
    "validate_release_metadata",
    "write_preservation_manifest",
]
