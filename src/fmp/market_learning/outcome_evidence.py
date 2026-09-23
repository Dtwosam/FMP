from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from .contracts import (
    EVIDENCE_LABEL,
    EXPERIMENT_ID,
    HORIZONS_MINUTES,
    MARKET_FEATURE_SET_VERSION,
    MARKET_HISTORY_END_EXCLUSIVE,
    SLIPPAGE_PIPS,
)
from .evidence import EXPECTED_CELLS, EXPECTED_SOURCE_MANIFEST_SHA256
from .outcomes import MARKET_OUTCOME_SET_VERSION, OUTCOME_COLUMNS


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


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


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
        raise ValueError(f"invalid EXP-044 outcome manifest: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"EXP-044 outcome manifest root must be an object: {path}")
    return value, _sha256_bytes(raw)


def _validate_artifact(
    *,
    manifest_root: Path,
    raw_artifact: object,
    expected_prefix: str,
) -> tuple[str, int]:
    if not isinstance(raw_artifact, Mapping):
        raise ValueError("outcome artifact row must be an object")
    relative = raw_artifact.get("path")
    expected_sha = raw_artifact.get("sha256")
    expected_size = raw_artifact.get("size_bytes")
    row_count = raw_artifact.get("row_count")
    if not isinstance(relative, str) or not relative.startswith(expected_prefix):
        raise ValueError("outcome artifact path does not match cell identity")
    _validate_sha256(expected_sha, field="outcome artifact sha256")
    if (
        not isinstance(expected_size, int)
        or isinstance(expected_size, bool)
        or expected_size <= 0
    ):
        raise ValueError("outcome artifact size is invalid")
    if (
        not isinstance(row_count, int)
        or isinstance(row_count, bool)
        or row_count <= 0
    ):
        raise ValueError("outcome artifact row count is invalid")

    root = manifest_root.resolve()
    candidate = (manifest_root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("outcome artifact path escapes evidence root") from exc
    if not candidate.is_file():
        raise ValueError(f"outcome artifact file is missing: {relative}")
    if candidate.stat().st_size != expected_size:
        raise ValueError(f"outcome artifact size mismatch: {relative}")
    if _sha256_file(candidate) != expected_sha:
        raise ValueError(f"outcome artifact checksum mismatch: {relative}")
    return relative, row_count


def compile_outcome_evidence(
    *,
    root: Path,
    expected_code_commit: str,
    expected_feature_evidence_fingerprint: str,
) -> dict[str, object]:
    _validate_commit(expected_code_commit, field="expected_code_commit")
    _validate_sha256(
        expected_feature_evidence_fingerprint,
        field="expected_feature_evidence_fingerprint",
    )

    manifest_paths = sorted(Path(root).rglob("manifest.json"))
    if len(manifest_paths) != len(EXPECTED_CELLS):
        raise ValueError(
            f"EXP-044 outcome evidence requires exactly {len(EXPECTED_CELLS)} manifests"
        )

    seen: list[tuple[str, str]] = []
    cells: list[dict[str, object]] = []
    accepted_end = datetime(
        MARKET_HISTORY_END_EXCLUSIVE.year,
        MARKET_HISTORY_END_EXCLUSIVE.month,
        MARKET_HISTORY_END_EXCLUSIVE.day,
        tzinfo=timezone.utc,
    )

    for path in manifest_paths:
        manifest, manifest_sha = _load_manifest(path)
        if manifest.get("experiment_id") != EXPERIMENT_ID:
            raise ValueError("EXP-044 outcome experiment identity mismatch")
        if manifest.get("outcome_set_version") != MARKET_OUTCOME_SET_VERSION:
            raise ValueError("EXP-044 outcome-set identity mismatch")
        if manifest.get("feature_set_version") != MARKET_FEATURE_SET_VERSION:
            raise ValueError("EXP-044 outcome feature-set identity mismatch")
        if manifest.get("evidence_label") != EVIDENCE_LABEL:
            raise ValueError("EXP-044 outcome evidence label mismatch")
        if manifest.get("untouched_oos") is not False:
            raise ValueError("EXP-044 outcome history cannot claim untouched OOS")
        if manifest.get("model_fit_authorized") is not False:
            raise ValueError("EXP-044 outcomes cannot authorize model fitting")
        if manifest.get("promotion_authorized") is not False:
            raise ValueError("EXP-044 outcomes cannot authorize promotion")
        if manifest.get("code_commit") != expected_code_commit:
            raise ValueError("EXP-044 outcome code commit mismatch")
        if (
            manifest.get("feature_evidence_fingerprint")
            != expected_feature_evidence_fingerprint
        ):
            raise ValueError("EXP-044 outcome feature evidence fingerprint mismatch")

        symbol = manifest.get("symbol")
        timeframe = manifest.get("timeframe")
        identity = (symbol, timeframe)
        if identity not in EXPECTED_CELLS:
            raise ValueError(f"unexpected EXP-044 outcome cell: {identity!r}")
        if identity in seen:
            raise ValueError(f"duplicate EXP-044 outcome cell: {identity!r}")
        seen.append(identity)

        if (
            manifest.get("processed_manifest_sha256")
            != EXPECTED_SOURCE_MANIFEST_SHA256[str(symbol)]
        ):
            raise ValueError("EXP-044 outcome Phase 2 source identity mismatch")
        _validate_sha256(
            manifest.get("feature_manifest_sha256"),
            field="feature_manifest_sha256",
        )
        if manifest.get("horizons_minutes") != list(HORIZONS_MINUTES):
            raise ValueError("EXP-044 outcome horizon contract mismatch")
        if manifest.get("slippage_pips_per_fill") != list(SLIPPAGE_PIPS):
            raise ValueError("EXP-044 outcome slippage contract mismatch")
        if manifest.get("schema_columns") != list(OUTCOME_COLUMNS):
            raise ValueError("EXP-044 outcome schema columns mismatch")
        _validate_sha256(manifest.get("schema_sha256"), field="outcome schema sha256")

        source_rows = manifest.get("source_feature_rows")
        labeled_rows = manifest.get("labeled_rows")
        if (
            not isinstance(source_rows, int)
            or isinstance(source_rows, bool)
            or source_rows <= 0
        ):
            raise ValueError("EXP-044 outcome source feature row count is invalid")
        if (
            not isinstance(labeled_rows, int)
            or isinstance(labeled_rows, bool)
            or labeled_rows <= 0
        ):
            raise ValueError("EXP-044 outcome labeled row count is invalid")

        labeled_by = manifest.get("labeled_rows_by_horizon")
        missing_entry = manifest.get("missing_entry_rows_by_horizon")
        missing_exit = manifest.get("missing_exit_rows_by_horizon")
        if not all(isinstance(value, Mapping) for value in (labeled_by, missing_entry, missing_exit)):
            raise ValueError("EXP-044 outcome row-accounting maps are invalid")
        labeled_sum = 0
        for horizon in HORIZONS_MINUTES:
            key = str(horizon)
            values = (
                labeled_by.get(key),
                missing_entry.get(key),
                missing_exit.get(key),
            )
            if any(
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
                for value in values
            ):
                raise ValueError("EXP-044 outcome horizon row accounting is invalid")
            if sum(values) != source_rows:
                raise ValueError("EXP-044 outcome horizon rows do not reconcile")
            labeled_sum += int(values[0])
        if labeled_sum != labeled_rows:
            raise ValueError("EXP-044 outcome labeled rows do not reconcile")

        output_start = _parse_utc(manifest.get("output_start_utc"), field="output_start_utc")
        output_end = _parse_utc(manifest.get("output_end_utc"), field="output_end_utc")
        if output_start >= output_end or output_end >= accepted_end:
            raise ValueError("EXP-044 outcome coverage exceeds accepted history")

        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise ValueError("EXP-044 outcome artifacts must be a non-empty list")
        prefix = (
            f"data/market-outcomes/{MARKET_OUTCOME_SET_VERSION}/"
            f"{symbol}/{timeframe}/"
        )
        artifact_paths: list[str] = []
        artifact_rows = 0
        for artifact in artifacts:
            relative, rows = _validate_artifact(
                manifest_root=path.parent,
                raw_artifact=artifact,
                expected_prefix=prefix,
            )
            artifact_paths.append(relative)
            artifact_rows += rows
        if artifact_paths != sorted(artifact_paths):
            raise ValueError("EXP-044 outcome artifacts must be sorted")
        if len(set(artifact_paths)) != len(artifact_paths):
            raise ValueError("EXP-044 outcome artifact paths must be unique")
        if artifact_rows != labeled_rows:
            raise ValueError("EXP-044 outcome artifact rows do not sum to labeled rows")

        cells.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "manifest_sha256": manifest_sha,
                "feature_manifest_sha256": manifest["feature_manifest_sha256"],
                "processed_manifest_sha256": manifest["processed_manifest_sha256"],
                "source_feature_rows": source_rows,
                "labeled_rows": labeled_rows,
                "artifact_count": len(artifacts),
                "output_start_utc": manifest["output_start_utc"],
                "output_end_utc": manifest["output_end_utc"],
            }
        )

    cells.sort(key=lambda item: (str(item["symbol"]), str(item["timeframe"])))
    if tuple((cell["symbol"], cell["timeframe"]) for cell in cells) != EXPECTED_CELLS:
        raise ValueError("EXP-044 outcome evidence does not contain the exact nine cells")

    evidence: dict[str, object] = {
        "evidence_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "code_commit": expected_code_commit,
        "feature_evidence_fingerprint": expected_feature_evidence_fingerprint,
        "expected_cell_count": len(EXPECTED_CELLS),
        "verified_cell_count": len(cells),
        "outcome_evidence_complete": True,
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


def write_outcome_evidence(*, evidence: Mapping[str, object], path: Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(dict(evidence), sort_keys=True, indent=2, allow_nan=False) + "\n"
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing EXP-044 outcome evidence: {destination}")
    destination.write_text(payload, encoding="utf-8")


__all__ = ["compile_outcome_evidence", "write_outcome_evidence"]
