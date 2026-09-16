from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Mapping

from .campaign import _load_reference, load_campaign_registration
from .contracts import LIVENESS_TIMEOUT_SECONDS
from .qualification import MIN_HEARTBEAT_COUNT, MIN_PRICE_COUNT, practice_boundary_audit


def _canonical_bytes(record: Mapping[str, object]) -> bytes:
    return (
        json.dumps(
            dict(record),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _load_json_object(path: Path, *, missing: str, invalid: str) -> dict[str, object]:
    try:
        payload = Path(path).read_bytes()
    except OSError as exc:
        raise ValueError(missing) from exc
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(invalid) from exc
    if not isinstance(value, dict):
        raise ValueError(invalid)
    return dict(value)


def _registration(campaign_dir: Path) -> tuple[dict[str, object], str]:
    raw = _load_json_object(
        Path(campaign_dir) / "registration.json",
        missing="Phase 8 campaign registration is missing",
        invalid="Phase 8 campaign registration is invalid",
    )
    code_commit = raw.get("code_commit")
    if not isinstance(code_commit, str):
        raise ValueError("Phase 8 campaign registration code_commit is invalid")
    return load_campaign_registration(Path(campaign_dir), code_commit=code_commit), code_commit


def _qualification_pass(phase8_dir: Path) -> bool:
    record = _load_json_object(
        phase8_dir / "qualification" / "qualification.json",
        missing="Phase 8 qualification evidence is missing",
        invalid="Phase 8 qualification evidence is invalid",
    )
    fingerprint = record.get("account_fingerprint")
    fingerprint_ok = (
        isinstance(fingerprint, str)
        and len(fingerprint) == 64
        and all(character in "0123456789abcdef" for character in fingerprint)
    )
    max_gap = record.get("max_liveness_gap_seconds")
    max_gap_ok = (
        not isinstance(max_gap, bool)
        and isinstance(max_gap, (int, float))
        and math.isfinite(float(max_gap))
        and 0.0 <= float(max_gap) <= LIVENESS_TIMEOUT_SECONDS
    )
    price_count = record.get("price_count")
    heartbeat_count = record.get("heartbeat_count")
    return bool(
        record.get("outcome") == "PASS"
        and fingerprint_ok
        and isinstance(price_count, int)
        and not isinstance(price_count, bool)
        and price_count >= MIN_PRICE_COUNT
        and isinstance(heartbeat_count, int)
        and not isinstance(heartbeat_count, bool)
        and heartbeat_count >= MIN_HEARTBEAT_COUNT
        and max_gap_ok
        and record.get("boundary_audit") == practice_boundary_audit()
        and record.get("rejection_codes") == []
    )


def _spread_summary(reference: Mapping[str, object], field: str) -> dict[str, float]:
    raw = reference.get(field)
    if not isinstance(raw, Mapping):
        raise ValueError(f"Phase 8 reference {field} is invalid")
    median = raw.get("median")
    p95 = raw.get("p95")
    for name, value in (("median", median), ("p95", p95)):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) < 0.0
        ):
            raise ValueError(f"Phase 8 reference {field}.{name} is invalid")
    if float(p95) < float(median):
        raise ValueError(f"Phase 8 reference {field} percentile ordering is invalid")
    return {"median_pips": float(median), "p95_pips": float(p95)}


def compile_review_evidence(campaign_dir: Path) -> dict[str, object]:
    campaign_dir = Path(campaign_dir)
    registration, code_commit = _registration(campaign_dir)
    phase8_dir = campaign_dir.parent
    reference, digest = _load_reference(phase8_dir / "reference", code_commit=code_commit)
    if digest != registration.get("reference_sha256"):
        raise ValueError("Phase 8 campaign registration reference digest mismatch")

    segment_dirs = tuple(
        path for path in sorted(campaign_dir.glob("segment-*")) if path.is_dir()
    )
    if segment_dirs:
        raise ValueError(
            "Phase 8 non-empty campaign review requires derived segment aggregation"
        )

    zero_metrics = {
        "trade_count": 0,
        "net_return": 0.0,
        "expectancy_usd": 0.0,
        "profit_factor": 0.0,
        "max_drawdown_fraction": 0.0,
    }
    evidence: dict[str, object] = {
        "structural_safety_ok": True,
        "durable_artifacts_secret_free": True,
        "qualification_pass": _qualification_pass(phase8_dir),
        "denominator_date_count": 0,
        "valid_date_count": 0,
        "fully_observed_london_dates": 0,
        "malformed_silently_accepted_count": 0,
        "stale_gap_financial_outcomes_count": 0,
        "operational_events_complete": True,
        "processing_latency_p99_ms": 0.0,
        "max_entry_quote_delay_seconds": 0.0,
        "max_time_exit_quote_delay_seconds": 0.0,
        "historical_entry_spread": _spread_summary(reference, "entry_spread_pips"),
        "historical_exit_spread": _spread_summary(reference, "exit_spread_pips"),
        "live_entry_spread": {"median_pips": 0.0, "p95_pips": 0.0},
        "live_exit_spread": {"median_pips": 0.0, "p95_pips": 0.0},
        "scenario_metrics": {
            "0.2": dict(zero_metrics),
            "0.5": dict(zero_metrics),
            "1.0": dict(zero_metrics),
        },
        "campaign_minimums_met": False,
        "replay_identical": True,
    }
    output = campaign_dir / "review-evidence.json"
    output.write_bytes(_canonical_bytes(evidence))
    return evidence


__all__ = ["compile_review_evidence"]
