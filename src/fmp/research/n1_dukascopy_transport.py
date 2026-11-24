"""Retrieve the DEC-639 daily-file envelope and keep only DEC-638 minutes.

The public Dukascopy object is one UTC day. This module hashes those
compressed bytes, extracts the approved minutes, and deletes the payload.
It does not call ``acquire_chunk`` and it does not write the historical
raw store. A real download waits until publication is verified and the
observation window has completed.
"""

from __future__ import annotations

import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

from fmp.contracts import QuoteBar
from fmp.data.dukascopy import DukascopySource, HttpTransport, UrllibTransport
from fmp.data.phase2.bi5 import Phase2DecodeError, decode_bi5_day
from fmp.data.types import RawChunkKey
from fmp.research.n1_news_shock import (
    N1Release,
    new_york_clock_utc,
    required_n1_observation_keys,
)
from fmp.research.n1_prospective_pilot import (
    COLLECTION_LIMITATION_CLASS,
    EVIDENCE_CLASS,
    TRANSPORT_EFFECTIVE_UTC,
    DuplicatePilotObservation,
    SourceFileRecord,
    TransportProvenance,
    _TRANSPORT_SEAL,
    _qualifies,
    _quote_input_sha256,
    _refuse_protected_evidence_directory,
    _require_approved_release,
    append_transported_pilot_evidence,
    assert_frozen_signal_blob,
    prospective_observation_stored,
)

_PAIRS = ("EURUSD", "GBPUSD", "USDJPY")
_SIDES = ("BID", "ASK")
_FILE_COUNT = len(_PAIRS) * len(_SIDES)


def observe_n1_transport_window(
    release: N1Release,
    *,
    transport_directory: Path,
    evidence_directory: Path,
    bls_status_verified_at_utc: datetime,
    now_utc: datetime,
    transport: HttpTransport | None = None,
    source: DukascopySource | None = None,
    timeout_seconds: float = 30.0,
):
    """Record one approved event. Download only after the window is complete."""

    assert_frozen_signal_blob()
    if not isinstance(release, N1Release):
        raise TypeError("release must be an N1Release")
    _refuse_protected_evidence_directory(transport_directory)
    _refuse_protected_evidence_directory(evidence_directory)
    _require_approved_release(release)
    now = _require_utc(now_utc, "now_utc")
    verified = _require_utc(bls_status_verified_at_utc, "bls_status_verified_at_utc")
    _require_retrieval_clock(release.new_york_date, now)
    _require_verification_clock(release.new_york_date, verified, now)
    if prospective_observation_stored(evidence_directory, release.release_id):
        raise DuplicatePilotObservation(
            "an observation for this release and slippage is already stored"
        )
    if _qualifies(release):
        source_files, bars, limitation, evidence_class = _acquire_daily_files(
            release,
            transport_directory,
            transport=transport,
            source=source or DukascopySource(),
            timeout_seconds=timeout_seconds,
        )
    else:
        source_files = ()
        bars = ()
        limitation = "publication_not_at_0830"
        evidence_class = COLLECTION_LIMITATION_CLASS
    provenance = TransportProvenance(
        seal=_TRANSPORT_SEAL,
        source_files=source_files,
        quote_input_sha256=_quote_input_sha256(bars),
        bls_status_verified_at_utc=verified.astimezone(timezone.utc).isoformat(),
        data_retrieved_at_utc=now.astimezone(timezone.utc).isoformat(),
        collection_limitation=limitation,
        evidence_class=evidence_class,
    )
    return append_transported_pilot_evidence(evidence_directory, release, bars, provenance)


def _acquire_daily_files(
    release: N1Release,
    transport_directory: Path,
    *,
    transport: HttpTransport | None,
    source: DukascopySource,
    timeout_seconds: float,
) -> tuple[tuple[SourceFileRecord, ...], tuple[QuoteBar, ...], str | None, str]:
    client = transport if transport is not None else UrllibTransport()
    work = transport_directory / f".n1-{release.release_id}"
    _refuse_protected_evidence_directory(work)
    if work.exists():
        raise ValueError("transport work directory already exists")
    transport_directory.mkdir(parents=True, exist_ok=True)
    work.mkdir()
    files: list[SourceFileRecord] = []
    kept: dict[tuple[datetime, str], dict[str, tuple[float, float, float, float]]] = {}
    approved = set(required_n1_observation_keys(release.new_york_date))
    try:
        for pair in _PAIRS:
            for side in _SIDES:
                key = RawChunkKey(pair, side, release.new_york_date)
                url = source.url_for(key)
                record, body = _fetch_compressed(client, url, key, timeout_seconds)
                if body is not None:
                    path = work / f"{pair}_{side}_candles_min_1.bi5"
                    path.write_bytes(body)
                    stored = path.read_bytes()
                    digest = hashlib.sha256(stored).hexdigest()
                    if digest != hashlib.sha256(body).hexdigest():
                        record = _recorded(
                            key,
                            url,
                            sha256=digest,
                            size=len(stored),
                            http_status=record.http_status,
                            status="hash_mismatch",
                        )
                    else:
                        try:
                            _keep_approved_minutes(key, stored, approved, kept)
                        except Phase2DecodeError:
                            record = _recorded(
                                key,
                                url,
                                sha256=digest,
                                size=len(stored),
                                http_status=record.http_status,
                                status="decode_error",
                            )
                        else:
                            record = _recorded(
                                key,
                                url,
                                sha256=digest,
                                size=len(stored),
                                http_status=record.http_status,
                                status="hashed",
                            )
                files.append(record)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if len(files) != _FILE_COUNT:
        raise RuntimeError("the daily transport requested a file outside the twelve-file cap")
    bars = _bars_from_sides(kept)
    return tuple(files), tuple(bars), *_classification(tuple(files), tuple(bars), approved)


def _fetch_compressed(transport: HttpTransport, url: str, key: RawChunkKey, timeout_seconds: float):
    try:
        response = transport.get(url, timeout_seconds)
    except (ConnectionError, TimeoutError, OSError):
        return _recorded(key, url, sha256=None, size=None, http_status=None, status="unavailable"), None
    if response.status == 404:
        return (
            _recorded(key, url, sha256=None, size=None, http_status=404, status="not_found"),
            None,
        )
    if not 200 <= response.status < 300:
        return (
            _recorded(
                key,
                url,
                sha256=None,
                size=None,
                http_status=response.status,
                status="unavailable",
            ),
            None,
        )
    return (
        _recorded(key, url, sha256=None, size=None, http_status=response.status, status="pending"),
        response.body,
    )


def _keep_approved_minutes(
    key: RawChunkKey,
    body: bytes,
    approved: set[tuple[datetime, str]],
    kept: dict[tuple[datetime, str], dict[str, tuple[float, float, float, float]]],
) -> None:
    frame = decode_bi5_day(key, body)
    try:
        for row in frame.iter_rows(named=True):
            stamp = _utc_timestamp(row["timestamp_utc"])
            identity = (stamp, row["symbol"])
            if identity not in approved:
                continue
            slot = kept.setdefault(identity, {})
            if row["side"] in slot:
                raise ValueError("duplicate side in source file")
            slot[row["side"]] = (row["open"], row["high"], row["low"], row["close"])
    finally:
        del frame


def _bars_from_sides(
    kept: dict[tuple[datetime, str], dict[str, tuple[float, float, float, float]]],
) -> list[QuoteBar]:
    bars: list[QuoteBar] = []
    for (stamp, symbol), sides in sorted(kept.items()):
        if "BID" not in sides or "ASK" not in sides:
            continue
        bid_open, bid_high, bid_low, bid_close = sides["BID"]
        ask_open, ask_high, ask_low, ask_close = sides["ASK"]
        try:
            bars.append(
                QuoteBar(
                    timestamp_utc=stamp,
                    symbol=symbol,
                    bid_open=bid_open,
                    bid_high=bid_high,
                    bid_low=bid_low,
                    bid_close=bid_close,
                    ask_open=ask_open,
                    ask_high=ask_high,
                    ask_low=ask_low,
                    ask_close=ask_close,
                )
            )
        except ValueError:
            continue
    return bars


def _classification(
    files: tuple[SourceFileRecord, ...],
    bars: tuple[QuoteBar, ...],
    approved: set[tuple[datetime, str]],
) -> tuple[str | None, str]:
    statuses = {item.status for item in files}
    if "not_found" in statuses or "unavailable" in statuses:
        limitation: str | None = "source_not_available"
    elif "decode_error" in statuses or "hash_mismatch" in statuses:
        limitation = "source_undecodable"
    else:
        present = {(bar.timestamp_utc, bar.symbol) for bar in bars}
        limitation = None if present == approved else "incomplete_minutes"
    hashed = any(item.status == "hashed" and item.sha256 for item in files)
    if bars and hashed:
        return limitation, EVIDENCE_CLASS
    return limitation or "source_not_available", COLLECTION_LIMITATION_CLASS


def _recorded(
    key: RawChunkKey,
    url: str,
    *,
    sha256: str | None,
    size: int | None,
    http_status: int | None,
    status: str,
) -> SourceFileRecord:
    return SourceFileRecord(
        pair=key.pair,
        side=key.side,
        url=url,
        sha256=sha256,
        compressed_size_bytes=size,
        http_status=http_status,
        status=status,
    )


def _utc_timestamp(value: object) -> datetime:
    if not isinstance(value, datetime):
        raise Phase2DecodeError("decoded timestamp is not a datetime")
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)
    return value.astimezone(timezone.utc)


def _require_utc(value: datetime, field: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must use UTC")
    if value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field} must use UTC")
    return value.astimezone(timezone.utc)


def _require_retrieval_clock(day, now: datetime) -> None:
    effective = datetime.fromisoformat(TRANSPORT_EFFECTIVE_UTC).astimezone(timezone.utc)
    if now <= effective:
        raise ValueError("retrieval is not strictly after the transport decision")
    if now < new_york_clock_utc(day, 9, 31):
        raise ValueError("the observation window is not complete")


def _require_verification_clock(day, verified: datetime, now: datetime) -> None:
    effective = datetime.fromisoformat(TRANSPORT_EFFECTIVE_UTC).astimezone(timezone.utc)
    if verified <= effective:
        raise ValueError("bls_status_verified_at_utc is not strictly after the transport decision")
    if verified < new_york_clock_utc(day, 8, 30):
        raise ValueError("BLS verification is before the scheduled publication minute")
    if verified > now:
        raise ValueError("BLS verification is after the retrieval clock")
