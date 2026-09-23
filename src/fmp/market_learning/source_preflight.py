from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping


PHASE2_SOURCE_RUN_ID = 34782357048
PHASE2_SOURCE_HEAD_SHA = "158c1c121655867b7fb2886fe755585dfcd682ec"


@dataclass(frozen=True, slots=True)
class SourceArtifactSpec:
    symbol: str
    artifact_id: int
    artifact_name: str
    zip_sha256: str
    size_in_bytes: int
    processed_manifest_sha256: str


SOURCE_ARTIFACTS = (
    SourceArtifactSpec(
        symbol="EURUSD",
        artifact_id=10325737935,
        artifact_name="phase2-full-history-EURUSD",
        zip_sha256="db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3",
        size_in_bytes=182037581,
        processed_manifest_sha256="fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a",
    ),
    SourceArtifactSpec(
        symbol="GBPUSD",
        artifact_id=10326096831,
        artifact_name="phase2-full-history-GBPUSD",
        zip_sha256="fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2",
        size_in_bytes=190706384,
        processed_manifest_sha256="a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94",
    ),
    SourceArtifactSpec(
        symbol="USDJPY",
        artifact_id=10327600628,
        artifact_name="phase2-full-history-USDJPY",
        zip_sha256="6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72",
        size_in_bytes=160033414,
        processed_manifest_sha256="e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
    ),
)


def _parse_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty ISO UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be valid ISO UTC") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)


def validate_source_artifact_metadata(
    *,
    metadata: Mapping[str, object],
    spec: SourceArtifactSpec,
    now_utc: datetime,
    minimum_remaining: timedelta,
) -> dict[str, object]:
    if now_utc.tzinfo is None or now_utc.utcoffset() != timedelta(0):
        raise ValueError("source-preflight now_utc must use UTC")
    if minimum_remaining < timedelta(0):
        raise ValueError("minimum_remaining must be non-negative")

    if metadata.get("id") != spec.artifact_id:
        raise ValueError(f"{spec.symbol} Phase 2 artifact id mismatch")
    if metadata.get("name") != spec.artifact_name:
        raise ValueError(f"{spec.symbol} Phase 2 artifact name mismatch")
    if metadata.get("expired") is not False:
        raise ValueError(f"{spec.symbol} Phase 2 artifact is expired")
    if metadata.get("digest") != f"sha256:{spec.zip_sha256}":
        raise ValueError(f"{spec.symbol} Phase 2 artifact digest mismatch")
    if metadata.get("size_in_bytes") != spec.size_in_bytes:
        raise ValueError(f"{spec.symbol} Phase 2 artifact size mismatch")

    workflow_run = metadata.get("workflow_run")
    if not isinstance(workflow_run, Mapping):
        raise ValueError(f"{spec.symbol} Phase 2 artifact workflow_run is invalid")
    if workflow_run.get("id") != PHASE2_SOURCE_RUN_ID:
        raise ValueError(f"{spec.symbol} Phase 2 source run id mismatch")
    if workflow_run.get("head_branch") != "main":
        raise ValueError(f"{spec.symbol} Phase 2 source branch mismatch")
    if workflow_run.get("head_sha") != PHASE2_SOURCE_HEAD_SHA:
        raise ValueError(f"{spec.symbol} Phase 2 source commit mismatch")

    created_at = _parse_utc(metadata.get("created_at"), field="created_at")
    expires_at = _parse_utc(metadata.get("expires_at"), field="expires_at")
    if expires_at <= created_at:
        raise ValueError(f"{spec.symbol} Phase 2 artifact expiry precedes creation")
    remaining = expires_at - now_utc
    if remaining < minimum_remaining:
        raise ValueError(
            f"{spec.symbol} Phase 2 artifact does not have enough remaining lifetime"
        )

    return {
        "symbol": spec.symbol,
        "artifact_id": spec.artifact_id,
        "artifact_name": spec.artifact_name,
        "zip_sha256": spec.zip_sha256,
        "size_in_bytes": spec.size_in_bytes,
        "processed_manifest_sha256": spec.processed_manifest_sha256,
        "source_run_id": PHASE2_SOURCE_RUN_ID,
        "source_head_sha": PHASE2_SOURCE_HEAD_SHA,
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
        "remaining_seconds": int(remaining.total_seconds()),
    }


def compile_source_preflight(
    *,
    metadata_by_symbol: Mapping[str, Mapping[str, object]],
    now_utc: datetime,
    minimum_remaining: timedelta = timedelta(hours=12),
) -> dict[str, object]:
    expected_symbols = tuple(spec.symbol for spec in SOURCE_ARTIFACTS)
    if tuple(sorted(metadata_by_symbol)) != tuple(sorted(expected_symbols)):
        raise ValueError("source preflight requires exact EURUSD/GBPUSD/USDJPY metadata")

    artifacts = [
        validate_source_artifact_metadata(
            metadata=metadata_by_symbol[spec.symbol],
            spec=spec,
            now_utc=now_utc,
            minimum_remaining=minimum_remaining,
        )
        for spec in SOURCE_ARTIFACTS
    ]
    earliest_expiry = min(str(item["expires_at"]) for item in artifacts)
    report: dict[str, object] = {
        "preflight_version": 1,
        "experiment_id": "EXP-20260923-044",
        "historical_source": "Dukascopy",
        "phase2_source_run_id": PHASE2_SOURCE_RUN_ID,
        "phase2_source_head_sha": PHASE2_SOURCE_HEAD_SHA,
        "checked_at_utc": now_utc.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "minimum_remaining_seconds": int(minimum_remaining.total_seconds()),
        "earliest_expires_at": earliest_expiry,
        "source_ready": True,
        "new_acquisition_performed": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "artifacts": artifacts,
    }
    return report


def load_metadata_directory(root: Path) -> dict[str, Mapping[str, object]]:
    directory = Path(root)
    out: dict[str, Mapping[str, object]] = {}
    for spec in SOURCE_ARTIFACTS:
        path = directory / f"{spec.symbol}.json"
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read source metadata: {path}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"source metadata root must be an object: {path}")
        out[spec.symbol] = value
    return out


def write_source_preflight(*, report: Mapping[str, object], path: Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(dict(report), sort_keys=True, indent=2, allow_nan=False) + "\n"
    destination.write_text(payload, encoding="utf-8")


__all__ = [
    "PHASE2_SOURCE_HEAD_SHA",
    "PHASE2_SOURCE_RUN_ID",
    "SOURCE_ARTIFACTS",
    "SourceArtifactSpec",
    "compile_source_preflight",
    "load_metadata_directory",
    "validate_source_artifact_metadata",
    "write_source_preflight",
]
