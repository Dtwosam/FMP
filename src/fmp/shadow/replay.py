from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Mapping

from .evidence import EvidenceWriter, finalize_existing_segment
from .mt5_bridge import BridgeStartRecord, parse_bridge_line
from .runner import ShadowRunner


REPLAY_PROTOCOL = "fmp-phase8-shadow-replay-v1"
_DERIVED_FILES = (
    "normalized.jsonl",
    "bars.jsonl",
    "decisions.jsonl",
    "scenarios.jsonl",
)
_SEMANTIC_FILES = (
    "bars.jsonl",
    "decisions.jsonl",
    "scenarios.jsonl",
)


class ReplayMismatchError(RuntimeError):
    pass


def _parse_utc(value: object, *, field_name: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a UTC timestamp string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"{field_name} must be a valid UTC timestamp") from None
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} must use UTC")
    return parsed


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        raise FileNotFoundError(f"Phase 8 replay input missing: {path.name}")
    records: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            raise ValueError(f"{path.name} line {line_number} is not valid JSON") from None
        if not isinstance(record, dict):
            raise ValueError(f"{path.name} line {line_number} must be a JSON object")
        records.append(record)
    return records


def _segment_identity(
    operational_records: list[dict[str, object]],
) -> tuple[datetime, datetime, str, str, bool, str]:
    starts = [record for record in operational_records if record.get("event") == "segment_start"]
    disconnects = [record for record in operational_records if record.get("event") == "disconnect"]
    if len(starts) != 1:
        raise ValueError("Phase 8 replay requires exactly one segment_start record")
    if len(disconnects) != 1:
        raise ValueError("Phase 8 replay requires exactly one disconnect record")
    start = starts[0]
    disconnect = disconnects[0]
    code_commit = start.get("code_commit")
    fingerprint = start.get("account_fingerprint_sha256")
    reason = disconnect.get("reason")
    if not isinstance(code_commit, str):
        raise ValueError("segment_start code_commit is missing")
    if not isinstance(fingerprint, str):
        raise ValueError("segment_start account fingerprint is missing")
    if not isinstance(reason, str) or not reason:
        raise ValueError("disconnect reason is missing")
    return (
        _parse_utc(start.get("timestamp_utc"), field_name="segment_start timestamp"),
        _parse_utc(disconnect.get("timestamp_utc"), field_name="disconnect timestamp"),
        code_commit,
        fingerprint,
        any(record.get("event") == "restart" for record in operational_records),
        reason,
    )


def _parse_stored_bridge_record(provider_object: Mapping[str, object], *, index: int):  # type: ignore[no-untyped-def]
    try:
        payload = (
            json.dumps(
                dict(provider_object),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError):
        raise ValueError(f"raw.jsonl record {index} provider_object is not canonical JSON") from None
    try:
        return parse_bridge_line(payload)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"raw.jsonl record {index} is not valid MT5 bridge evidence") from exc


def _bridge_identity(
    raw_records: list[dict[str, object]],
    *,
    operational_account_fingerprint: str,
) -> tuple[str, str, str]:
    if not raw_records:
        raise ValueError("Phase 8 replay requires MT5 bridge raw evidence")
    provider_object = raw_records[0].get("provider_object")
    if not isinstance(provider_object, Mapping):
        raise ValueError("raw.jsonl record 0 provider_object must be an object")
    first = _parse_stored_bridge_record(provider_object, index=0)
    if not isinstance(first, BridgeStartRecord):
        raise ValueError("Phase 8 replay raw evidence must begin with BRIDGE_START")
    if first.account_fingerprint != operational_account_fingerprint:
        raise ValueError("Phase 8 replay account fingerprint identity mismatch")
    return first.bridge_session_id, first.server, first.account_fingerprint


def _feed_raw_records(
    runner: ShadowRunner,
    raw_records: list[dict[str, object]],
) -> None:
    previous_monotonic: int | None = None
    for index, record in enumerate(raw_records):
        provider_object = record.get("provider_object")
        received = record.get("received_at_utc")
        monotonic = record.get("receive_monotonic_ns")
        if not isinstance(provider_object, Mapping):
            raise ValueError(f"raw.jsonl record {index} provider_object must be an object")
        if isinstance(monotonic, bool) or not isinstance(monotonic, int) or monotonic < 0:
            raise ValueError(f"raw.jsonl record {index} receive_monotonic_ns is invalid")
        if previous_monotonic is not None and monotonic < previous_monotonic:
            raise ValueError("raw.jsonl receive monotonic time regressed")
        previous_monotonic = monotonic
        bridge_record = _parse_stored_bridge_record(provider_object, index=index)
        runner.process_bridge_record(
            bridge_record,
            received_at_utc=_parse_utc(received, field_name="raw received_at_utc"),
            receive_monotonic_ns=monotonic,
        )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest_files(root: Path, filenames: tuple[str, ...]) -> str:
    digest = hashlib.sha256()
    for name in filenames:
        data = (root / name).read_bytes()
        digest.update(name.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def _write_replay_record(path: Path, record: Mapping[str, object]) -> None:
    data = (
        json.dumps(
            dict(record),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def replay_segment(
    segment_dir: Path,
    *,
    allow_normalized_metadata_difference: bool = False,
) -> dict[str, object]:
    segment_dir = Path(segment_dir)
    raw_records = _read_jsonl(segment_dir / "raw.jsonl")
    operational_records = _read_jsonl(segment_dir / "operational.jsonl")
    (
        run_start,
        run_end,
        code_commit,
        operational_account_fingerprint,
        restarted,
        disconnect_reason,
    ) = _segment_identity(operational_records)
    bridge_session_id, server, account_fingerprint = _bridge_identity(
        raw_records,
        operational_account_fingerprint=operational_account_fingerprint,
    )

    compare_files = _SEMANTIC_FILES if allow_normalized_metadata_difference else _DERIVED_FILES
    for name in _DERIVED_FILES:
        if not (segment_dir / name).is_file():
            raise FileNotFoundError(f"Phase 8 replay input missing: {name}")

    with TemporaryDirectory(prefix="fmp-phase8-replay-") as temporary:
        replay_root = Path(temporary)
        evidence = EvidenceWriter(
            replay_root,
            code_commit=code_commit,
            bridge_source_commit=code_commit,
            bridge_session_id=bridge_session_id,
            server=server,
            account_fingerprint_sha256=account_fingerprint,
            run_start_utc=run_start,
        )
        runner = ShadowRunner(evidence=evidence)
        runner.start(now_utc=run_start, restarted=restarted)
        _feed_raw_records(runner, raw_records)
        runner.disconnect(now_utc=run_end, reason=disconnect_reason)

        mismatched = [
            name
            for name in compare_files
            if (segment_dir / name).read_bytes() != (replay_root / name).read_bytes()
        ]
        digest = _digest_files(replay_root, compare_files)
        replay_hashes = {name: _sha256(replay_root / name) for name in _DERIVED_FILES}

    live_hashes = {name: _sha256(segment_dir / name) for name in _DERIVED_FILES}
    result: dict[str, object] = {
        "protocol": REPLAY_PROTOCOL,
        "match": not mismatched,
        "compared_files": sorted(compare_files),
        "semantic_files": list(_SEMANTIC_FILES),
        "mismatched_files": sorted(mismatched),
        "live_file_sha256": live_hashes,
        "replay_file_sha256": replay_hashes,
        "replay_result_digest": digest,
    }
    _write_replay_record(segment_dir / "replay.json", result)
    if mismatched:
        raise ReplayMismatchError(
            "Phase 8 replay mismatch: " + ", ".join(sorted(mismatched))
        )

    finalize_existing_segment(
        segment_dir,
        code_commit=code_commit,
        bridge_source_commit=code_commit,
        bridge_session_id=bridge_session_id,
        server=server,
        account_fingerprint_sha256=account_fingerprint,
        run_start_utc=run_start,
        run_end_utc=run_end,
        replay_result_digest=digest,
    )
    return result


__all__ = ["REPLAY_PROTOCOL", "ReplayMismatchError", "replay_segment"]
