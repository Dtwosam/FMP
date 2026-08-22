from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .manifest import load_manifest


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
