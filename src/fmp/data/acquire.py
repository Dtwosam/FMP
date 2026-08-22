from __future__ import annotations

import hashlib
import lzma
import os
import struct
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path

from .dukascopy import DukascopySource, HttpResponse, HttpTransport, UrllibTransport
from .manifest import atomic_write_json, load_manifest
from .types import RawChunkKey

_RECORD_SIZE = 24
_MANIFEST_VERSION = 1
_RETRIEVAL_METHOD = "dukascopy-public-daily-m1-bi5-v1"


class AcquisitionError(RuntimeError):
    pass


class AcquisitionStatus(StrEnum):
    COMPLETE = "complete"
    ALREADY_VERIFIED = "already_verified"
    NOT_FOUND = "not_found"


@dataclass(frozen=True, slots=True)
class AcquisitionResult:
    key: RawChunkKey
    status: AcquisitionStatus
    sha256: str | None
    records: int | None
    compressed_size: int | None
    http_status: int | None


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_daily_m1_bi5(body: bytes) -> int:
    if not body:
        raise AcquisitionError("source response was empty")
    try:
        raw = lzma.decompress(body)
    except lzma.LZMAError as exc:
        raise AcquisitionError("source response is not valid LZMA-compressed bi5") from exc
    if not raw or len(raw) % _RECORD_SIZE != 0:
        raise AcquisitionError(
            f"decompressed candle payload length {len(raw)} is not a non-zero multiple of {_RECORD_SIZE}"
        )
    records = len(raw) // _RECORD_SIZE
    if records > 1440:
        raise AcquisitionError(f"daily 1-minute chunk has impossible record count: {records}")
    previous_offset = -1
    for offset in range(0, len(raw), _RECORD_SIZE):
        seconds = struct.unpack_from(">I", raw, offset)[0]
        if seconds >= 86400:
            raise AcquisitionError(f"candle second offset outside UTC day: {seconds}")
        if seconds <= previous_offset:
            raise AcquisitionError("candle second offsets are not strictly increasing")
        previous_offset = seconds
    return records


def _atomic_write_bytes(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.part-", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def _existing_verified_result(
    key: RawChunkKey,
    raw_path: Path,
    manifest_path: Path,
    *,
    recheck_not_found: bool = False,
) -> AcquisitionResult | None:
    if not raw_path.exists() and not manifest_path.exists():
        return None
    if manifest_path.exists():
        manifest = load_manifest(manifest_path)
        status = manifest.get("status")
        if status == AcquisitionStatus.NOT_FOUND.value and not raw_path.exists():
            if recheck_not_found:
                return None
            return AcquisitionResult(key, AcquisitionStatus.NOT_FOUND, None, None, None, 404)
        if status == AcquisitionStatus.COMPLETE.value and raw_path.exists():
            expected = manifest.get("sha256")
            actual = _sha256_file(raw_path)
            if expected == actual:
                return AcquisitionResult(
                    key=key,
                    status=AcquisitionStatus.ALREADY_VERIFIED,
                    sha256=actual,
                    records=int(manifest["records"]),
                    compressed_size=raw_path.stat().st_size,
                    http_status=int(manifest.get("http_status", 200)),
                )
            raise AcquisitionError(f"existing raw chunk checksum mismatch: {raw_path}")
    raise AcquisitionError(
        f"raw/manifest state is incomplete or inconsistent; refusing overwrite: {raw_path} / {manifest_path}"
    )


def _manifest_payload(
    key: RawChunkKey,
    source_url: str,
    *,
    status: str,
    http_status: int,
    sha256: str | None = None,
    compressed_size: int | None = None,
    records: int | None = None,
) -> dict[str, object]:
    return {
        "manifest_version": _MANIFEST_VERSION,
        "retrieval_method": _RETRIEVAL_METHOD,
        "source": "dukascopy",
        "source_url": source_url,
        "pair": key.pair,
        "side": key.side,
        "date_utc": key.day.isoformat(),
        "granularity": "1m",
        "source_format": "bi5-lzma-daily-candles",
        "record_size_bytes": _RECORD_SIZE,
        "month_indexing": "zero_based_in_source_url",
        "status": status,
        "http_status": http_status,
        "sha256": sha256,
        "compressed_size_bytes": compressed_size,
        "records": records,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def acquire_chunk(
    key: RawChunkKey,
    root: Path,
    *,
    source: DukascopySource | None = None,
    transport: HttpTransport | None = None,
    timeout_seconds: float = 30.0,
    max_attempts: int = 3,
    backoff_seconds: float = 0.5,
    recheck_not_found: bool = False,
) -> AcquisitionResult:
    source = source or DukascopySource()
    transport = transport or UrllibTransport()
    raw_path = root / "raw" / key.relative_raw_path
    manifest_path = root / "manifests" / key.relative_manifest_path

    existing = _existing_verified_result(
        key, raw_path, manifest_path, recheck_not_found=recheck_not_found
    )
    if existing is not None:
        return existing

    url = source.url_for(key)
    response: HttpResponse | None = None
    last_error: Exception | None = None
    attempts = max(1, int(max_attempts))
    for attempt in range(1, attempts + 1):
        try:
            response = transport.get(url, timeout_seconds)
            if response.status == 404:
                atomic_write_json(
                    manifest_path,
                    _manifest_payload(key, url, status="not_found", http_status=404),
                )
                return AcquisitionResult(key, AcquisitionStatus.NOT_FOUND, None, None, None, 404)
            if 200 <= response.status < 300:
                break
            if 400 <= response.status < 500:
                raise AcquisitionError(f"non-retryable HTTP status {response.status} for {url}")
            last_error = AcquisitionError(f"retryable HTTP status {response.status} for {url}")
        except (ConnectionError, TimeoutError, OSError) as exc:
            last_error = exc
        if attempt < attempts:
            time.sleep(backoff_seconds * (2 ** (attempt - 1)))
    else:
        raise AcquisitionError(f"failed to acquire {url} after {attempts} attempts") from last_error

    if response is None or not (200 <= response.status < 300):
        raise AcquisitionError(f"failed to acquire {url}") from last_error

    records = inspect_daily_m1_bi5(response.body)
    digest = _sha256_bytes(response.body)
    _atomic_write_bytes(raw_path, response.body)
    atomic_write_json(
        manifest_path,
        _manifest_payload(
            key,
            url,
            status="complete",
            http_status=response.status,
            sha256=digest,
            compressed_size=len(response.body),
            records=records,
        ),
    )
    return AcquisitionResult(
        key=key,
        status=AcquisitionStatus.COMPLETE,
        sha256=digest,
        records=records,
        compressed_size=len(response.body),
        http_status=response.status,
    )
