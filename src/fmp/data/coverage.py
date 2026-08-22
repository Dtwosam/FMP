from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable

from .manifest import load_manifest
from .types import RawChunkKey


def build_coverage_report(root: Path) -> dict[str, Any]:
    manifests_root = root / "manifests" / "dukascopy" / "v1"
    totals = {"manifests": 0, "complete": 0, "not_found": 0, "other": 0}
    pairs: dict[str, dict[str, int]] = defaultdict(
        lambda: {"manifests": 0, "complete": 0, "not_found": 0, "other": 0}
    )
    first_date: dict[str, str] = {}
    last_date: dict[str, str] = {}

    if manifests_root.exists():
        for path in sorted(manifests_root.rglob("*.json")):
            manifest = load_manifest(path)
            pair = str(manifest.get("pair", "UNKNOWN"))
            status = str(manifest.get("status", "other"))
            bucket = status if status in {"complete", "not_found"} else "other"
            totals["manifests"] += 1
            totals[bucket] += 1
            pairs[pair]["manifests"] += 1
            pairs[pair][bucket] += 1
            day = str(manifest.get("date_utc", ""))
            if day:
                first_date[pair] = min(first_date.get(pair, day), day)
                last_date[pair] = max(last_date.get(pair, day), day)

    pair_payload: dict[str, dict[str, Any]] = {}
    for pair in sorted(pairs):
        payload: dict[str, Any] = dict(pairs[pair])
        payload["first_date"] = first_date.get(pair)
        payload["last_date"] = last_date.get(pair)
        pair_payload[pair] = payload

    return {
        "report_version": 1,
        "source": "dukascopy",
        "granularity": "1m",
        "totals": totals,
        "pairs": pair_payload,
        "note": "Coverage reports acquisition outcomes only; Phase 2 determines data cleanliness.",
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _iter_days(start: date, end_exclusive: date) -> Iterable[date]:
    current = start
    while current < end_exclusive:
        yield current
        current += timedelta(days=1)


def verify_snapshot(
    root: Path,
    pairs: Iterable[str],
    start: date,
    end_exclusive: date,
    *,
    issue_sample_limit: int = 20,
) -> dict[str, Any]:
    """Verify acquisition completeness/provenance, not market-data quality.

    Every planned pair/date/side must have a manifest. A complete manifest must
    have a raw file whose SHA-256 matches. A not_found manifest must have no raw
    file. Phase 2 remains responsible for deciding whether any source gap is
    expected or suspicious.
    """
    if end_exclusive <= start:
        raise ValueError("end must be after start")

    counts = {
        "planned_chunks": 0,
        "complete": 0,
        "not_found": 0,
        "missing_manifest": 0,
        "missing_raw": 0,
        "checksum_mismatch": 0,
        "unexpected_raw": 0,
        "invalid_manifest": 0,
    }
    issue_samples: list[dict[str, str]] = []

    def add_issue(kind: str, key: RawChunkKey, detail: str) -> None:
        counts[kind] += 1
        if len(issue_samples) < issue_sample_limit:
            issue_samples.append(
                {
                    "kind": kind,
                    "pair": key.pair,
                    "side": key.side,
                    "date_utc": key.day.isoformat(),
                    "detail": detail,
                }
            )

    for pair in pairs:
        for day in _iter_days(start, end_exclusive):
            for side in ("BID", "ASK"):
                key = RawChunkKey(pair, side, day)  # type: ignore[arg-type]
                counts["planned_chunks"] += 1
                raw_path = root / "raw" / key.relative_raw_path
                manifest_path = root / "manifests" / key.relative_manifest_path
                if not manifest_path.is_file():
                    add_issue("missing_manifest", key, str(manifest_path))
                    continue
                try:
                    manifest = load_manifest(manifest_path)
                except (OSError, ValueError) as exc:
                    add_issue("invalid_manifest", key, str(exc))
                    continue

                expected_identity = (
                    manifest.get("pair") == key.pair
                    and manifest.get("side") == key.side
                    and manifest.get("date_utc") == key.day.isoformat()
                    and manifest.get("granularity") == "1m"
                    and manifest.get("source") == "dukascopy"
                )
                if not expected_identity:
                    add_issue("invalid_manifest", key, "manifest identity/provenance mismatch")
                    continue

                status = manifest.get("status")
                if status == "complete":
                    if not raw_path.is_file():
                        add_issue("missing_raw", key, str(raw_path))
                        continue
                    expected_digest = manifest.get("sha256")
                    actual_digest = _sha256_file(raw_path)
                    if not expected_digest or actual_digest != expected_digest:
                        add_issue("checksum_mismatch", key, str(raw_path))
                        continue
                    counts["complete"] += 1
                elif status == "not_found":
                    if raw_path.exists():
                        add_issue("unexpected_raw", key, str(raw_path))
                        continue
                    counts["not_found"] += 1
                else:
                    add_issue("invalid_manifest", key, f"unsupported status: {status!r}")

    issue_total = sum(
        counts[name]
        for name in (
            "missing_manifest",
            "missing_raw",
            "checksum_mismatch",
            "unexpected_raw",
            "invalid_manifest",
        )
    )
    return {
        "report_version": 1,
        "source": "dukascopy",
        "granularity": "1m",
        "start_date": start.isoformat(),
        "end_date_exclusive": end_exclusive.isoformat(),
        **counts,
        "issues": issue_total,
        "issue_samples": issue_samples,
        "ready": issue_total == 0
        and counts["complete"] + counts["not_found"] == counts["planned_chunks"],
        "note": "ready means acquisition/provenance complete only; Phase 2 still determines data cleanliness.",
    }
