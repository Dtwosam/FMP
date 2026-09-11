from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .dukascopy import DukascopySource
from .types import RawChunkKey

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_MANIFEST_FIELDS = {
    "manifest_version",
    "retrieval_method",
    "source",
    "source_url",
    "pair",
    "side",
    "date_utc",
    "granularity",
    "source_format",
    "record_size_bytes",
    "month_indexing",
    "status",
    "http_status",
    "sha256",
    "compressed_size_bytes",
    "records",
    "retrieved_at_utc",
}


@dataclass(frozen=True, slots=True)
class ValidatedManifest:
    status: str
    sha256: str | None
    compressed_size_bytes: int | None
    records: int | None
    http_status: int


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"manifest must be an object: {path}")
    return value


def _valid_utc_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() == timedelta(0)


def validate_manifest_for_key(
    key: RawChunkKey,
    manifest: object,
) -> ValidatedManifest | None:
    """Validate the complete frozen Phase 1 manifest contract for one key."""

    if not isinstance(manifest, dict) or set(manifest) != _REQUIRED_MANIFEST_FIELDS:
        return None

    manifest_version = manifest.get("manifest_version")
    if (
        not isinstance(manifest_version, int)
        or isinstance(manifest_version, bool)
        or manifest_version != 1
    ):
        return None

    fixed = {
        "retrieval_method": "dukascopy-public-daily-m1-bi5-v1",
        "source": "dukascopy",
        "source_url": DukascopySource().url_for(key),
        "pair": key.pair,
        "side": key.side,
        "date_utc": key.day.isoformat(),
        "granularity": "1m",
        "source_format": "bi5-lzma-daily-candles",
        "record_size_bytes": 24,
        "month_indexing": "zero_based_in_source_url",
    }
    if any(manifest.get(field) != expected for field, expected in fixed.items()):
        return None
    if not _valid_utc_timestamp(manifest.get("retrieved_at_utc")):
        return None

    status = manifest.get("status")
    http_status = manifest.get("http_status")
    sha256 = manifest.get("sha256")
    compressed_size = manifest.get("compressed_size_bytes")
    records = manifest.get("records")

    if status == "complete":
        if (
            not isinstance(http_status, int)
            or isinstance(http_status, bool)
            or not 200 <= http_status < 300
            or not isinstance(sha256, str)
            or not _SHA256_RE.fullmatch(sha256)
            or not isinstance(compressed_size, int)
            or isinstance(compressed_size, bool)
            or compressed_size <= 0
            or not isinstance(records, int)
            or isinstance(records, bool)
            or not 1 <= records <= 1440
        ):
            return None
        return ValidatedManifest(
            status="complete",
            sha256=sha256,
            compressed_size_bytes=compressed_size,
            records=records,
            http_status=http_status,
        )

    if status == "not_found":
        if (
            http_status != 404
            or isinstance(http_status, bool)
            or sha256 is not None
            or compressed_size is not None
            or records is not None
        ):
            return None
        return ValidatedManifest(
            status="not_found",
            sha256=None,
            compressed_size_bytes=None,
            records=None,
            http_status=404,
        )

    return None


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.part-", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
