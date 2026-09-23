from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping

from .source_preflight import (
    PHASE2_SOURCE_HEAD_SHA,
    PHASE2_SOURCE_RUN_ID,
    SOURCE_ARTIFACTS,
    compile_source_preflight,
)
from .source_preservation import (
    PRESERVATION_TAG,
    validate_preservation_manifest,
    validate_published_release_metadata,
)


SOURCE_AVAILABILITY_VERSION = "fmp-phase2-source-availability-v1"


def compile_source_availability(
    *,
    metadata_by_symbol: Mapping[str, Mapping[str, object]],
    now_utc: datetime,
    minimum_remaining: timedelta = timedelta(hours=12),
    release: Mapping[str, object] | None = None,
    preservation_manifest: Mapping[str, object] | None = None,
) -> dict[str, object]:
    try:
        actions = compile_source_preflight(
            metadata_by_symbol=metadata_by_symbol,
            now_utc=now_utc,
            minimum_remaining=minimum_remaining,
        )
    except ValueError as actions_error:
        if release is None or preservation_manifest is None:
            raise ValueError(
                "original Phase 2 Actions artifacts are unavailable and no "
                "validated preservation release was supplied"
            ) from actions_error
        manifest_result = validate_preservation_manifest(preservation_manifest)
        release_result = validate_published_release_metadata(
            release=release,
            manifest=preservation_manifest,
        )
        return {
            "availability_version": SOURCE_AVAILABILITY_VERSION,
            "experiment_id": "EXP-20260923-044",
            "historical_source": "Dukascopy",
            "phase2_source_run_id": PHASE2_SOURCE_RUN_ID,
            "phase2_source_head_sha": PHASE2_SOURCE_HEAD_SHA,
            "checked_at_utc": now_utc.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "minimum_remaining_seconds": int(minimum_remaining.total_seconds()),
            "source_mode": "release",
            "source_ready": True,
            "original_actions_ready": False,
            "preservation_release_verified": True,
            "preservation_tag": PRESERVATION_TAG,
            "preservation_code_commit": manifest_result["preservation_code_commit"],
            "new_acquisition_performed": False,
            "source_bytes_changed": False,
            "model_fit_authorized": False,
            "promotion_authorized": False,
            "shadow_authorized": False,
            "demo_order_authorized": False,
            "broker_mutation_authorized": False,
            "live_order_authorized": False,
            "real_money_authorized": False,
            "artifacts": release_result["assets"],
        }

    return {
        "availability_version": SOURCE_AVAILABILITY_VERSION,
        "experiment_id": "EXP-20260923-044",
        "historical_source": "Dukascopy",
        "phase2_source_run_id": PHASE2_SOURCE_RUN_ID,
        "phase2_source_head_sha": PHASE2_SOURCE_HEAD_SHA,
        "checked_at_utc": actions["checked_at_utc"],
        "minimum_remaining_seconds": actions["minimum_remaining_seconds"],
        "source_mode": "actions",
        "source_ready": True,
        "original_actions_ready": True,
        "preservation_release_verified": False,
        "preservation_tag": PRESERVATION_TAG,
        "new_acquisition_performed": False,
        "source_bytes_changed": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "earliest_expires_at": actions["earliest_expires_at"],
        "artifacts": actions["artifacts"],
    }


def load_optional_json(path: Path | None) -> Mapping[str, object] | None:
    if path is None:
        return None
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read source availability JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"source availability JSON must be an object: {path}")
    return value


def write_source_availability(
    *,
    report: Mapping[str, object],
    path: Path,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(dict(report), sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "SOURCE_AVAILABILITY_VERSION",
    "compile_source_availability",
    "load_optional_json",
    "write_source_availability",
]
