from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from fmp.data.phase2.artifacts import PHASE1_FROZEN_PLAN_SHA256, PHASE1_SOURCE_CHECKPOINT
from fmp.features.contracts import PROCESSED_SCHEMA_VERSION, SUPPORTED_SYMBOLS, SUPPORTED_TIMEFRAMES
from fmp.features.schema import FEATURE_COLUMNS, FEATURE_VALUE_COLUMNS

from .contracts import (
    EVIDENCE_LABEL,
    EXPERIMENT_ID,
    MARKET_FEATURE_SET_VERSION,
    MARKET_HISTORY_END_EXCLUSIVE,
    MARKET_HISTORY_START,
)


EXPECTED_SOURCE_MANIFEST_SHA256 = {
    "EURUSD": "fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a",
    "GBPUSD": "a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94",
    "USDJPY": "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
}
EXPECTED_CELLS = tuple(
    sorted(
        (symbol, timeframe)
        for symbol in SUPPORTED_SYMBOLS
        for timeframe in SUPPORTED_TIMEFRAMES
    )
)


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _expected_months() -> tuple[str, ...]:
    out: list[str] = []
    year = MARKET_HISTORY_START.year
    month = MARKET_HISTORY_START.month
    while (year, month) <= (2026, 8):
        out.append(f"{year:04d}-{month:02d}")
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return tuple(out)


def _parse_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO UTC string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be valid ISO UTC") from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(f"{field} must use UTC")
    return parsed


def _load_manifest(path: Path) -> tuple[Mapping[str, object], str]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid EXP-044 feature manifest: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"EXP-044 feature manifest root must be an object: {path}")
    return value, _sha256_bytes(raw)


def _validate_artifact_file(
    *,
    manifest_root: Path,
    raw_artifact: object,
    expected_prefix: str,
) -> tuple[str, int]:
    if not isinstance(raw_artifact, Mapping):
        raise ValueError("feature artifact row must be an object")
    relative = raw_artifact.get("path")
    expected_sha = raw_artifact.get("sha256")
    expected_size = raw_artifact.get("size_bytes")
    row_count = raw_artifact.get("row_count")
    if not isinstance(relative, str) or not relative.startswith(expected_prefix):
        raise ValueError("feature artifact path does not match cell identity")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        raise ValueError("feature artifact sha256 is invalid")
    if not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size <= 0:
        raise ValueError("feature artifact size is invalid")
    if not isinstance(row_count, int) or isinstance(row_count, bool) or row_count <= 0:
        raise ValueError("feature artifact row count is invalid")

    root = manifest_root.resolve()
    candidate = (manifest_root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("feature artifact path escapes evidence root") from exc
    if not candidate.is_file():
        raise ValueError(f"feature artifact file is missing: {relative}")
    if candidate.stat().st_size != expected_size:
        raise ValueError(f"feature artifact size mismatch: {relative}")
    if _sha256_file(candidate) != expected_sha:
        raise ValueError(f"feature artifact checksum mismatch: {relative}")
    return relative, row_count


def compile_feature_evidence(
    *,
    root: Path,
    expected_code_commit: str,
) -> dict[str, object]:
    if not expected_code_commit.strip():
        raise ValueError("expected_code_commit must be non-empty")
    root = Path(root)
    manifest_paths = sorted(root.rglob("manifest.json"))
    if len(manifest_paths) != len(EXPECTED_CELLS):
        raise ValueError(
            f"EXP-044 feature evidence requires exactly {len(EXPECTED_CELLS)} manifests"
        )

    expected_months = _expected_months()
    seen: set[tuple[str, str]] = set()
    cells: list[dict[str, object]] = []
    accepted_end = datetime(
        MARKET_HISTORY_END_EXCLUSIVE.year,
        MARKET_HISTORY_END_EXCLUSIVE.month,
        MARKET_HISTORY_END_EXCLUSIVE.day,
        tzinfo=timezone.utc,
    )
    accepted_start = datetime(
        MARKET_HISTORY_START.year,
        MARKET_HISTORY_START.month,
        MARKET_HISTORY_START.day,
        tzinfo=timezone.utc,
    )

    for path in manifest_paths:
        manifest, manifest_sha = _load_manifest(path)
        if manifest.get("experiment_id") != EXPERIMENT_ID:
            raise ValueError("EXP-044 feature manifest experiment identity mismatch")
        if manifest.get("feature_set_version") != MARKET_FEATURE_SET_VERSION:
            raise ValueError("EXP-044 feature-set identity mismatch")
        if manifest.get("base_feature_definition_version") != "fmp-feature-v1":
            raise ValueError("EXP-044 base feature definition identity mismatch")
        if manifest.get("evidence_label") != EVIDENCE_LABEL:
            raise ValueError("EXP-044 evidence label mismatch")
        if manifest.get("untouched_oos") is not False:
            raise ValueError("EXP-044 historical evidence cannot claim untouched OOS")
        if manifest.get("model_training_authorized") is not False:
            raise ValueError("EXP-044 feature materialization cannot authorize model fitting")
        if manifest.get("promotion_authorized") is not False:
            raise ValueError("EXP-044 feature materialization cannot authorize promotion")
        if manifest.get("code_commit") != expected_code_commit:
            raise ValueError("EXP-044 feature manifest code commit mismatch")

        symbol = manifest.get("symbol")
        timeframe = manifest.get("timeframe")
        cell = (symbol, timeframe)
        if cell not in EXPECTED_CELLS:
            raise ValueError(f"unexpected EXP-044 feature cell: {cell!r}")
        if cell in seen:
            raise ValueError(f"duplicate EXP-044 feature cell: {cell!r}")
        seen.add(cell)

        expected_source_sha = EXPECTED_SOURCE_MANIFEST_SHA256[str(symbol)]
        if manifest.get("processed_manifest_sha256") != expected_source_sha:
            raise ValueError(f"{symbol} processed manifest identity mismatch")

        source = manifest.get("historical_source")
        expected_source = {
            "provider": "Dukascopy",
            "reuse_existing_accepted_history": True,
            "new_acquisition_performed": False,
            "phase1_checkpoint": PHASE1_SOURCE_CHECKPOINT,
            "phase1_frozen_plan_sha256": PHASE1_FROZEN_PLAN_SHA256,
            "phase2_schema_version": PROCESSED_SCHEMA_VERSION,
        }
        if source != expected_source:
            raise ValueError(f"{symbol} historical source provenance mismatch")

        generation = manifest.get("generation_parameters")
        if generation != {
            "requested_start": "2015-01-01",
            "requested_end_exclusive": "2026-08-21",
        }:
            raise ValueError("EXP-044 generation range mismatch")
        opened_months = manifest.get("opened_source_months")
        if tuple(opened_months) != expected_months if isinstance(opened_months, list) else True:
            raise ValueError("EXP-044 opened source months are incomplete or out of order")

        if tuple(manifest.get("feature_columns", ())) != FEATURE_VALUE_COLUMNS:
            raise ValueError("EXP-044 feature columns do not match frozen definitions")
        if tuple(manifest.get("schema_columns", ())) != FEATURE_COLUMNS:
            raise ValueError("EXP-044 schema columns do not match frozen definitions")

        row_count = manifest.get("row_count")
        unique_count = manifest.get("unique_key_count")
        if (
            not isinstance(row_count, int)
            or isinstance(row_count, bool)
            or row_count <= 0
            or unique_count != row_count
        ):
            raise ValueError("EXP-044 feature row/unique counts are invalid")

        output_start = _parse_utc(manifest.get("output_start_utc"), field="output_start_utc")
        output_end = _parse_utc(manifest.get("output_end_utc"), field="output_end_utc")
        if output_start < accepted_start or output_end > accepted_end or output_start >= output_end:
            raise ValueError("EXP-044 feature output coverage is outside accepted history")

        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, list) or len(artifacts) != len(expected_months):
            raise ValueError("EXP-044 feature artifact month count mismatch")
        expected_prefix = (
            f"data/features/{MARKET_FEATURE_SET_VERSION}/{symbol}/{timeframe}/"
        )
        artifact_paths: list[str] = []
        artifact_rows = 0
        for artifact in artifacts:
            relative, rows = _validate_artifact_file(
                manifest_root=path.parent,
                raw_artifact=artifact,
                expected_prefix=expected_prefix,
            )
            artifact_paths.append(relative)
            artifact_rows += rows
        if artifact_paths != sorted(artifact_paths) or len(set(artifact_paths)) != len(artifact_paths):
            raise ValueError("EXP-044 feature artifacts must be sorted and unique")
        if artifact_rows != row_count:
            raise ValueError("EXP-044 artifact row counts do not sum to manifest row count")

        cells.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "manifest_sha256": manifest_sha,
                "processed_manifest_sha256": expected_source_sha,
                "row_count": row_count,
                "artifact_count": len(artifacts),
                "output_start_utc": manifest["output_start_utc"],
                "output_end_utc": manifest["output_end_utc"],
            }
        )

    if tuple(sorted(seen)) != EXPECTED_CELLS:
        raise ValueError("EXP-044 feature evidence does not contain the exact nine cells")

    cells.sort(key=lambda item: (str(item["symbol"]), str(item["timeframe"])))
    evidence: dict[str, object] = {
        "evidence_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "code_commit": expected_code_commit,
        "historical_source": {
            "provider": "Dukascopy",
            "reuse_existing_accepted_history": True,
            "new_acquisition_performed": False,
            "phase1_checkpoint": PHASE1_SOURCE_CHECKPOINT,
            "phase1_frozen_plan_sha256": PHASE1_FROZEN_PLAN_SHA256,
            "phase2_schema_version": PROCESSED_SCHEMA_VERSION,
            "processed_manifest_sha256_by_symbol": dict(
                sorted(EXPECTED_SOURCE_MANIFEST_SHA256.items())
            ),
        },
        "expected_cell_count": len(EXPECTED_CELLS),
        "verified_cell_count": len(cells),
        "feature_evidence_complete": True,
        "model_fit_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "cells": cells,
    }
    evidence["evidence_fingerprint"] = _sha256_bytes(_canonical_json(evidence))
    return evidence


def write_feature_evidence(*, evidence: Mapping[str, object], path: Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(dict(evidence), sort_keys=True, indent=2, allow_nan=False) + "\n"
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing EXP-044 feature evidence: {destination}")
    destination.write_text(payload, encoding="utf-8")


__all__ = [
    "EXPECTED_CELLS",
    "EXPECTED_SOURCE_MANIFEST_SHA256",
    "compile_feature_evidence",
    "write_feature_evidence",
]
