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


def validate_preservation_manifest(
    manifest: Mapping[str, object],
) -> dict[str, object]:
    if manifest.get("preservation_version") != PRESERVATION_VERSION:
        raise ValueError("preservation manifest version mismatch")
    if manifest.get("experiment_id") != "EXP-20260923-044":
        raise ValueError("preservation manifest experiment identity mismatch")
    if manifest.get("historical_source") != "Dukascopy":
        raise ValueError("preservation manifest historical source mismatch")
    if manifest.get("phase2_source_run_id") != PHASE2_SOURCE_RUN_ID:
        raise ValueError("preservation manifest Phase 2 run mismatch")
    if manifest.get("phase2_source_head_sha") != PHASE2_SOURCE_HEAD_SHA:
        raise ValueError("preservation manifest Phase 2 commit mismatch")
    if manifest.get("preservation_tag") != PRESERVATION_TAG:
        raise ValueError("preservation manifest tag mismatch")
    if manifest.get("preservation_title") != PRESERVATION_TITLE:
        raise ValueError("preservation manifest title mismatch")
    code_commit = manifest.get("preservation_code_commit")
    if not isinstance(code_commit, str) or _SHA40.fullmatch(code_commit) is None:
        raise ValueError("preservation manifest code commit is invalid")
    if manifest.get("reuse_existing_accepted_history") is not True:
        raise ValueError("preservation manifest must reuse accepted history")
    if manifest.get("new_acquisition_performed") is not False:
        raise ValueError("preservation manifest cannot claim new acquisition")
    if manifest.get("source_bytes_changed") is not False:
        raise ValueError("preservation manifest cannot change source bytes")
    for flag in (
        "model_fit_authorized",
        "promotion_authorized",
        "shadow_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
    ):
        if manifest.get(flag) is not False:
            raise ValueError(f"preservation manifest {flag} must remain false")

    raw_assets = manifest.get("assets")
    if not isinstance(raw_assets, list) or len(raw_assets) != len(SOURCE_ARTIFACTS):
        raise ValueError("preservation manifest assets are incomplete")
    by_symbol: dict[str, Mapping[str, object]] = {}
    for raw in raw_assets:
        if not isinstance(raw, Mapping):
            raise ValueError("preservation manifest asset row is malformed")
        symbol = raw.get("symbol")
        if not isinstance(symbol, str) or symbol in by_symbol:
            raise ValueError("preservation manifest asset symbol is invalid")
        by_symbol[symbol] = raw

    verified: list[dict[str, object]] = []
    for spec in SOURCE_ARTIFACTS:
        raw = by_symbol.get(spec.symbol)
        if raw is None:
            raise ValueError(f"preservation manifest missing {spec.symbol}")
        expected = {
            "symbol": spec.symbol,
            "original_actions_artifact_id": spec.artifact_id,
            "original_actions_artifact_name": spec.artifact_name,
            "release_asset_name": release_asset_name(spec.symbol),
            "zip_sha256": spec.zip_sha256,
            "size_in_bytes": spec.size_in_bytes,
            "processed_manifest_sha256": spec.processed_manifest_sha256,
        }
        if dict(raw) != expected:
            raise ValueError(f"preservation manifest {spec.symbol} identity mismatch")
        verified.append(expected)

    if set(by_symbol) != {spec.symbol for spec in SOURCE_ARTIFACTS}:
        raise ValueError("preservation manifest contains unexpected symbols")
    return {
        "preservation_manifest_verified": True,
        "preservation_code_commit": code_commit.lower(),
        "assets": verified,
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


def _release_assets_by_name(
    release: Mapping[str, object],
) -> dict[str, Mapping[str, object]]:
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
    return by_name


def validate_published_release_metadata(
    *,
    release: Mapping[str, object],
    manifest: Mapping[str, object],
) -> dict[str, object]:
    validate_preservation_manifest(manifest)
    if release.get("tag_name") != PRESERVATION_TAG:
        raise ValueError("published preservation release tag mismatch")
    if release.get("name") != PRESERVATION_TITLE:
        raise ValueError("published preservation release title mismatch")
    if release.get("draft") is not False:
        raise ValueError("published preservation release must not be draft")
    if release.get("prerelease") is not False:
        raise ValueError("published preservation release must not be prerelease")

    by_name = _release_assets_by_name(release)
    expected_names = {
        release_asset_name(spec.symbol) for spec in SOURCE_ARTIFACTS
    } | {"phase2-preservation-manifest.json"}
    if set(by_name) != expected_names:
        raise ValueError("published preservation release asset set mismatch")

    verified: list[dict[str, object]] = []
    for spec in SOURCE_ARTIFACTS:
        name = release_asset_name(spec.symbol)
        actual = by_name[name]
        asset_id = actual.get("id")
        if not isinstance(asset_id, int) or isinstance(asset_id, bool) or asset_id <= 0:
            raise ValueError(f"published preservation release asset id is invalid: {name}")
        if actual.get("state") != "uploaded":
            raise ValueError(f"published preservation release asset is not uploaded: {name}")
        if actual.get("size") != spec.size_in_bytes:
            raise ValueError(f"published preservation release asset size mismatch: {name}")
        if actual.get("digest") != f"sha256:{spec.zip_sha256}":
            raise ValueError(f"published preservation release asset digest mismatch: {name}")
        verified.append(
            {
                "symbol": spec.symbol,
                "asset_id": asset_id,
                "name": name,
                "size_in_bytes": spec.size_in_bytes,
                "zip_sha256": spec.zip_sha256,
                "processed_manifest_sha256": spec.processed_manifest_sha256,
            }
        )

    manifest_asset = by_name["phase2-preservation-manifest.json"]
    manifest_asset_id = manifest_asset.get("id")
    if (
        not isinstance(manifest_asset_id, int)
        or isinstance(manifest_asset_id, bool)
        or manifest_asset_id <= 0
    ):
        raise ValueError("published preservation manifest asset id is invalid")
    if manifest_asset.get("state") != "uploaded":
        raise ValueError("published preservation manifest asset is not uploaded")

    return {
        "preservation_tag": PRESERVATION_TAG,
        "published_release_verified": True,
        "manifest_asset_id": manifest_asset_id,
        "verified_zip_asset_count": len(verified),
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "trading_authorized": False,
        "assets": verified,
    }


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
    "validate_preservation_manifest",
    "validate_published_release_metadata",
    "validate_release_metadata",
    "write_preservation_manifest",
]
