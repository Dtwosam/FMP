from __future__ import annotations

import hashlib
import json
import math
import os
import re
import statistics
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Mapping, Sequence
from zoneinfo import ZoneInfo

from .acceptance import (
    MIN_COMPLETE_LONDON_DATES,
    MIN_COMPLETED_TRADES,
    MIN_ELAPSED_WEEKS,
    MIN_REPRESENTED_FAMILIES,
    MIN_REPRESENTED_PAIRS,
    PHASE8B_ACCEPTANCE_CONTRACT_DECISION,
    PHASE8B_CAMPAIGN_EVIDENCE_PROTOCOL,
    validate_phase8b_campaign_evidence,
)
from .bridge import Phase8BQuote
from .capture import (
    validate_phase8b_capture_preflight,
    validate_phase8b_capture_record_envelope,
)
from .prospective import (
    validate_phase8b_prospective_segment,
)
from .runtime import (
    LIVENESS_TIMEOUT_SECONDS,
    PHASE8B_REPLAY_PROTOCOL,
    PHASE8B_RUNTIME_EXPERIMENT_ID,
    PHASE8B_RUNTIME_REPLAY_KERNEL_READY,
    PHASE8B_SEGMENT_PROTOCOL,
    SLIPPAGE_SCENARIOS,
    _BridgeGap,
    _MarketGap,
    _aggregate_minutes,
    _bar_record,
    _candidate_and_routing,
    _candidate_record,
    _capture_digest,
    _derive_minute_bars,
    _ordered_capture,
    _route_exposure_rows,
    _run_simulation,
    _scenario_record,
    reconstruct_phase8b_champion_set,
    validate_phase8b_segment,
    write_phase8b_segment_artifacts,
)


PHASE8B_CAMPAIGN_CLOSE_EXPERIMENT_ID = "EXP-20260922-024"
PHASE8B_CAMPAIGN_CLOSE_DECISION = "DEC-053"
PHASE8B_CAMPAIGN_EVIDENCE_SNAPSHOT_READY = (
    "PHASE8B_CAMPAIGN_EVIDENCE_SNAPSHOT_READY"
)
PHASE8B_CAMPAIGN_CLOSE_MANIFEST_PROTOCOL = (
    "fmp-phase8b-campaign-close-artifacts-v1"
)
AGGREGATION_MODE = "DEC052_PROSPECTIVE_SEGMENTS_V1"

_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
UTC = timezone.utc
LONDON = ZoneInfo("Europe/London")
_GAP_TOLERANCE = timedelta(seconds=LIVENESS_TIMEOUT_SECONDS)


@dataclass(frozen=True, slots=True)
class _SegmentBundle:
    directory: Path
    prospective: dict[str, object]
    capture_records: tuple[dict[str, object], ...]
    audits: tuple[dict[str, object], ...]
    operational_events: tuple[dict[str, object], ...]
    runtime_segment: dict[str, object]
    replay: dict[str, object]
    started_at_utc: datetime
    ended_at_utc: datetime


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _parse_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")
    return parsed


def _utc_string(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("timestamp must use UTC")
    return value.isoformat().replace("+00:00", "Z")


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _load_json(path: Path, *, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value


def _load_jsonl(path: Path, *, label: str) -> tuple[dict[str, object], ...]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read {label}: {path}") from exc
    result: list[dict[str, object]] = []
    for index, line in enumerate(lines, start=1):
        if not line:
            raise ValueError(f"{label} contains empty line {index}")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{label} line {index} is not valid JSON") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{label} line {index} must be an object")
        result.append(value)
    return tuple(result)


def _file_sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ValueError(f"cannot read campaign artifact: {path}") from exc


def _require_digest(
    path: Path,
    expected: object,
    *,
    label: str,
) -> None:
    digest = _validate_sha256(expected, field=f"{label} SHA-256")
    if _file_sha256(path) != digest:
        raise ValueError(f"Phase 8B {label} digest mismatch")


def _nearest_rank(values: Sequence[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(fraction * len(ordered)))
    return float(ordered[rank - 1])


def _spread_summary(values: Sequence[float]) -> tuple[int, float | None, float | None]:
    if not values:
        return 0, None, None
    return (
        len(values),
        float(statistics.median(values)),
        _nearest_rank(values, 0.95),
    )


def _load_bundle(
    directory: Path,
    *,
    preflight: Mapping[str, object],
) -> _SegmentBundle:
    prospective_path = directory / "prospective-segment.json"
    prospective = _load_json(
        prospective_path,
        label="Phase 8B prospective segment",
    )
    validate_phase8b_prospective_segment(prospective)
    if prospective.get("capture_preflight_fingerprint") != preflight.get(
        "capture_preflight_fingerprint"
    ):
        raise ValueError("Phase 8B prospective segment preflight mismatch")

    capture_path = directory / "capture-records.jsonl"
    audit_path = directory / "audit.jsonl"
    events_path = directory / "operational-events.jsonl"
    runtime_path = directory / "runtime" / "segment.json"
    replay_path = directory / "runtime" / "replay.json"

    _require_digest(
        capture_path,
        prospective.get("capture_records_sha256"),
        label="capture journal",
    )
    _require_digest(
        audit_path,
        prospective.get("audit_sha256"),
        label="audit journal",
    )
    _require_digest(
        events_path,
        prospective.get("operational_events_sha256"),
        label="operational journal",
    )

    captures = _load_jsonl(capture_path, label="Phase 8B capture journal")
    audits = _load_jsonl(audit_path, label="Phase 8B audit journal")
    events = _load_jsonl(events_path, label="Phase 8B operational journal")
    if len(captures) != prospective.get("capture_record_count"):
        raise ValueError("Phase 8B capture journal count mismatch")
    if len(audits) != prospective.get("audit_row_count"):
        raise ValueError("Phase 8B audit journal count mismatch")
    if len(captures) != len(audits):
        raise ValueError("Phase 8B audit coverage mismatch")

    for capture, audit in zip(captures, audits, strict=True):
        validate_phase8b_capture_record_envelope(
            capture,
            preflight=preflight,
        )
        if audit.get("record_fingerprint") != capture.get("record_fingerprint"):
            raise ValueError("Phase 8B audit record fingerprint mismatch")
        if audit.get("receive_monotonic_ns") != capture.get(
            "receive_monotonic_ns"
        ):
            raise ValueError("Phase 8B audit receive monotonic mismatch")
        latency = audit.get("processing_latency_ms")
        if (
            isinstance(latency, bool)
            or not isinstance(latency, (int, float))
            or not math.isfinite(float(latency))
            or float(latency) < 0
        ):
            raise ValueError("Phase 8B audit latency is invalid")

    event_names = [item.get("event") for item in events]
    if "SEGMENT_STARTED" not in event_names:
        raise ValueError("Phase 8B operational journal is missing SEGMENT_STARTED")
    if "SEGMENT_DURATION_REACHED" not in event_names:
        raise ValueError(
            "Phase 8B operational journal is missing clean bounded stop"
        )
    if "PROTOCOL_FAILURE" in event_names:
        raise ValueError("Phase 8B closed segment contains protocol failure")

    runtime_segment = _load_json(
        runtime_path,
        label="Phase 8B child runtime segment",
    )
    validate_phase8b_segment(runtime_segment)
    if runtime_segment.get("segment_fingerprint") != prospective.get(
        "runtime_segment_fingerprint"
    ):
        raise ValueError("Phase 8B child runtime segment fingerprint mismatch")

    replay = _load_json(replay_path, label="Phase 8B child replay")
    if replay.get("protocol") != PHASE8B_REPLAY_PROTOCOL:
        raise ValueError("Phase 8B child replay protocol mismatch")
    if replay.get("match") is not True:
        raise ValueError("Phase 8B child replay did not match")
    if replay.get("expected_segment_fingerprint") != runtime_segment.get(
        "segment_fingerprint"
    ):
        raise ValueError("Phase 8B child replay segment identity mismatch")
    if _canonical_digest(replay) != prospective.get("replay_fingerprint"):
        raise ValueError("Phase 8B child replay fingerprint mismatch")

    start = _parse_utc(
        prospective.get("segment_started_at_utc"),
        field="Phase 8B prospective segment start",
    )
    end = _parse_utc(
        prospective.get("segment_ended_at_utc"),
        field="Phase 8B prospective segment end",
    )
    if end < start:
        raise ValueError("Phase 8B prospective segment interval is invalid")
    return _SegmentBundle(
        directory=directory,
        prospective=prospective,
        capture_records=captures,
        audits=audits,
        operational_events=events,
        runtime_segment=runtime_segment,
        replay=replay,
        started_at_utc=start,
        ended_at_utc=end,
    )


def _load_bundles(
    campaign_dir: Path,
    *,
    preflight: Mapping[str, object],
) -> tuple[tuple[_SegmentBundle, ...], int]:
    segments_root = campaign_dir / "segments"
    if not segments_root.is_dir():
        raise ValueError("Phase 8B campaign has no segment directory")
    bundles: list[_SegmentBundle] = []
    unclosed = 0
    for directory in sorted(item for item in segments_root.iterdir() if item.is_dir()):
        if not (directory / "prospective-segment.json").is_file():
            unclosed += 1
            continue
        bundles.append(_load_bundle(directory, preflight=preflight))
    if not bundles:
        raise ValueError("Phase 8B campaign has no closed prospective segments")

    bundles.sort(
        key=lambda item: (
            item.started_at_utc,
            str(item.prospective["segment_id"]),
        )
    )
    prospective_fingerprints: set[str] = set()
    runtime_fingerprints: set[str] = set()
    replay_fingerprints: set[str] = set()
    capture_fingerprints: set[str] = set()
    prior_end: datetime | None = None
    for bundle in bundles:
        identities = (
            (
                prospective_fingerprints,
                str(bundle.prospective["prospective_segment_fingerprint"]),
                "prospective segment",
            ),
            (
                runtime_fingerprints,
                str(bundle.prospective["runtime_segment_fingerprint"]),
                "runtime segment",
            ),
            (
                replay_fingerprints,
                str(bundle.prospective["replay_fingerprint"]),
                "replay",
            ),
        )
        for seen, value, label in identities:
            if value in seen:
                raise ValueError(f"duplicate Phase 8B {label} fingerprint")
            seen.add(value)
        for row in bundle.capture_records:
            fingerprint = str(row["record_fingerprint"])
            if fingerprint in capture_fingerprints:
                raise ValueError("duplicate Phase 8B capture-record fingerprint")
            capture_fingerprints.add(fingerprint)
        if prior_end is not None and bundle.started_at_utc < prior_end:
            raise ValueError("Phase 8B prospective segment intervals overlap")
        prior_end = bundle.ended_at_utc
    return tuple(bundles), unclosed


def _received_bounds(
    bundles: Sequence[_SegmentBundle],
) -> tuple[datetime, datetime]:
    values = [
        _parse_utc(
            record.get("received_at_utc"),
            field="Phase 8B accepted observation receive time",
        )
        for bundle in bundles
        for record in bundle.capture_records
    ]
    if not values:
        raise ValueError("Phase 8B campaign has no accepted capture records")
    return min(values), max(values)


def _segment_intervals(
    bundles: Sequence[_SegmentBundle],
) -> tuple[tuple[datetime, datetime], ...]:
    return tuple((item.started_at_utc, item.ended_at_utc) for item in bundles)


def _denominator_dates(
    first: datetime,
    last: datetime,
) -> list[str]:
    current = first.astimezone(LONDON).date()
    end = last.astimezone(LONDON).date()
    result: list[str] = []
    while current <= end:
        if current.weekday() < 5:
            result.append(current.isoformat())
        current += timedelta(days=1)
    if not result:
        raise ValueError("Phase 8B campaign has no London weekday denominator")
    return result


def _complete_dates(
    denominator: Sequence[str],
    intervals: Sequence[tuple[datetime, datetime]],
) -> list[str]:
    result: list[str] = []
    for raw_date in denominator:
        day = date.fromisoformat(raw_date)
        local_start = datetime.combine(day, time.min, tzinfo=LONDON)
        local_end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=LONDON)
        day_start = local_start.astimezone(UTC)
        day_end = local_end.astimezone(UTC)
        clipped: list[tuple[datetime, datetime]] = []
        for start, end in intervals:
            left = max(start, day_start)
            right = min(end, day_end)
            if right > left:
                clipped.append((left, right))
        if not clipped:
            continue
        clipped.sort()
        cursor = day_start
        complete = True
        for start, end in clipped:
            if start > cursor + _GAP_TOLERANCE:
                complete = False
                break
            if end > cursor:
                cursor = end
        if complete and cursor >= day_end - _GAP_TOLERANCE:
            result.append(raw_date)
    return result


def _cross_segment_gaps(
    segment_quotes: Sequence[Sequence[Phase8BQuote]],
    bundles: Sequence[_SegmentBundle],
) -> tuple[list[_MarketGap], list[_BridgeGap]]:
    market: list[_MarketGap] = []
    bridge: list[_BridgeGap] = []
    last_quote_by_symbol: dict[str, Phase8BQuote] = {}
    last_receive_by_symbol: dict[str, datetime] = {}
    last_source_by_symbol: dict[str, datetime] = {}

    for bundle, quotes in zip(bundles, segment_quotes, strict=True):
        first_receive: dict[str, datetime] = {}
        last_receive: dict[str, datetime] = {}
        for record in bundle.capture_records:
            symbol = str(record["symbol"])
            received = _parse_utc(
                record["received_at_utc"],
                field="Phase 8B capture receive timestamp",
            )
            first_receive.setdefault(symbol, received)
            last_receive[symbol] = received
        for symbol, received in sorted(first_receive.items()):
            prior = last_receive_by_symbol.get(symbol)
            if prior is not None:
                seconds = (received - prior).total_seconds()
                if seconds < 0:
                    raise ValueError("Phase 8B cross-segment receive time regressed")
                if seconds > LIVENESS_TIMEOUT_SECONDS:
                    bridge.append(
                        _BridgeGap(
                            symbol=symbol,
                            previous_received_at_utc=prior,
                            received_at_utc=received,
                            receive_gap_seconds=seconds,
                        )
                    )
        last_receive_by_symbol.update(last_receive)

        first_quote: dict[str, Phase8BQuote] = {}
        local_last: dict[str, Phase8BQuote] = {}
        for quote in quotes:
            first_quote.setdefault(quote.symbol, quote)
            local_last[quote.symbol] = quote
        for symbol, quote in sorted(first_quote.items()):
            prior_source = last_source_by_symbol.get(symbol)
            if prior_source is not None and quote.source_time_utc <= prior_source:
                raise ValueError("Phase 8B cross-segment source time did not advance")
            prior_quote = last_quote_by_symbol.get(symbol)
            if prior_quote is not None:
                source_seconds = (
                    quote.source_time_utc - prior_quote.source_time_utc
                ).total_seconds()
                receive_seconds = (
                    quote.received_at_utc - prior_quote.received_at_utc
                ).total_seconds()
                if receive_seconds < 0:
                    raise ValueError("Phase 8B cross-segment receive time regressed")
                if source_seconds > LIVENESS_TIMEOUT_SECONDS:
                    market.append(
                        _MarketGap(
                            symbol=symbol,
                            start_utc=prior_quote.source_time_utc,
                            end_utc=quote.source_time_utc,
                            detected_at_utc=quote.source_time_utc,
                            receive_gap_seconds=receive_seconds,
                        )
                    )
        for symbol, quote in local_last.items():
            last_quote_by_symbol[symbol] = quote
            last_source_by_symbol[symbol] = quote.source_time_utc
    return market, bridge


def _compile_aggregate_segment(
    *,
    preflight: Mapping[str, object],
    bundles: Sequence[_SegmentBundle],
    code_commit: str,
) -> tuple[dict[str, object], list[Phase8BQuote]]:
    commit = _validate_commit(
        code_commit,
        field="Phase 8B campaign-close code commit",
    )
    champion = reconstruct_phase8b_champion_set(preflight)
    materialized: list[dict[str, object]] = []
    all_quotes: list[Phase8BQuote] = []
    market_gaps: list[_MarketGap] = []
    bridge_gaps: list[_BridgeGap] = []
    segment_quotes: list[list[Phase8BQuote]] = []

    for bundle in bundles:
        local_materialized, quotes, local_market, local_bridge = _ordered_capture(
            preflight=preflight,
            capture_records=bundle.capture_records,
        )
        materialized.extend(local_materialized)
        local_sorted = sorted(quotes, key=lambda item: item.source_time_utc)
        segment_quotes.append(local_sorted)
        all_quotes.extend(local_sorted)
        market_gaps.extend(local_market)
        bridge_gaps.extend(local_bridge)

    cross_market, cross_bridge = _cross_segment_gaps(segment_quotes, bundles)
    market_gaps.extend(cross_market)
    bridge_gaps.extend(cross_bridge)
    all_quotes.sort(key=lambda item: (item.source_time_utc, item.symbol))

    prepared_at = _parse_utc(
        preflight.get("prepared_at_utc"),
        field="Phase 8B capture preflight timestamp",
    )
    required_symbols = tuple(str(item) for item in preflight["required_symbols"])
    required_timeframes = tuple(
        str(item) for item in preflight["required_timeframes"]
    )
    quotes_by_symbol: dict[str, list[Phase8BQuote]] = {
        symbol: [] for symbol in required_symbols
    }
    for quote in all_quotes:
        quotes_by_symbol.setdefault(quote.symbol, []).append(quote)

    bars: dict[str, dict[str, tuple[object, ...]]] = {}
    for symbol in required_symbols:
        minute = _derive_minute_bars(
            symbol=symbol,
            quotes=tuple(quotes_by_symbol.get(symbol, ())),
            prepared_at=prepared_at,
            market_gaps=market_gaps,
        )
        bars[symbol] = {"1m": minute}
        for timeframe in required_timeframes:
            bars[symbol][timeframe] = _aggregate_minutes(
                minute,
                timeframe=timeframe,
            )

    candidates, _directional, route = _candidate_and_routing(
        champion=champion,
        bars=bars,
    )
    simulator = _run_simulation(
        accepted_ids={item.candidate_id for item in route.accepted},
        candidates=candidates,
        quotes=all_quotes,
        market_gaps=market_gaps,
    )

    fingerprints = [
        _validate_sha256(
            row.get("record_fingerprint"),
            field="Phase 8B capture-record fingerprint",
        )
        for row in materialized
    ]
    prospective_fingerprints = [
        str(bundle.prospective["prospective_segment_fingerprint"])
        for bundle in bundles
    ]
    operational_events = [
        {
            "event": "BRIDGE_LIVENESS_GAP",
            "symbol": item.symbol,
            "previous_received_at_utc": _utc_string(
                item.previous_received_at_utc
            ),
            "received_at_utc": _utc_string(item.received_at_utc),
            "receive_gap_seconds": item.receive_gap_seconds,
        }
        for item in bridge_gaps
    ] + [
        {
            "event": "MARKET_LIVENESS_GAP",
            "symbol": item.symbol,
            "start_utc": _utc_string(item.start_utc),
            "end_utc": _utc_string(item.end_utc),
            "receive_gap_seconds": item.receive_gap_seconds,
        }
        for item in market_gaps
    ]
    for previous, current in zip(bundles, bundles[1:]):
        operational_events.append(
            {
                "event": "CAPTURE_RESTART_GAP",
                "start_utc": _utc_string(previous.ended_at_utc),
                "end_utc": _utc_string(current.started_at_utc),
                "gap_seconds": (
                    current.started_at_utc - previous.ended_at_utc
                ).total_seconds(),
            }
        )
    operational_events.sort(
        key=lambda item: (
            str(item["event"]),
            str(item.get("symbol", "")),
            str(item.get("start_utc", item.get("previous_received_at_utc", ""))),
        )
    )

    payload = {
        "protocol": PHASE8B_SEGMENT_PROTOCOL,
        "experiment_id": PHASE8B_RUNTIME_EXPERIMENT_ID,
        "outcome": PHASE8B_RUNTIME_REPLAY_KERNEL_READY,
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "segment_code_commit": commit,
        "aggregation_mode": AGGREGATION_MODE,
        "prospective_segment_fingerprints": prospective_fingerprints,
        "champion_set_id": preflight["champion_set_id"],
        "champion_set_fingerprint": preflight[
            "champion_set_fingerprint"
        ],
        "strategy_fingerprints": list(preflight["strategy_fingerprints"]),
        "required_symbols": list(required_symbols),
        "required_timeframes": list(required_timeframes),
        "reader_start_semantics": preflight["reader_start_semantics"],
        "capture_record_count": len(materialized),
        "capture_record_fingerprints": fingerprints,
        "capture_records_sha256": _capture_digest(fingerprints),
        "quote_count": len(all_quotes),
        "bars": {
            symbol: {
                timeframe: [_bar_record(item) for item in bars[symbol][timeframe]]
                for timeframe in ("1m", "5m", "15m", "1h")
                if timeframe == "1m" or timeframe in required_timeframes
            }
            for symbol in required_symbols
        },
        "generated_candidates": [_candidate_record(item) for item in candidates],
        "routing": {
            "accepted_candidate_ids": [
                item.candidate_id for item in route.accepted
            ],
            "rejected": [
                {
                    "candidate_id": item.candidate_id,
                    "code": item.code.value,
                    "explanation": item.explanation,
                }
                for item in route.rejected
            ],
            "exposure_by_signal_time": _route_exposure_rows(route.accepted),
        },
        "scenarios": {
            str(slippage): _scenario_record(simulator.states[slippage])
            for slippage in SLIPPAGE_SCENARIOS
        },
        "operational_events": operational_events,
        "live_shadow_segment_started": False,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    segment = payload | {"segment_fingerprint": _canonical_digest(payload)}
    validate_phase8b_segment(segment)
    return segment, all_quotes


def _build_replay(
    *,
    expected_segment: Mapping[str, object],
    preflight: Mapping[str, object],
    bundles: Sequence[_SegmentBundle],
) -> dict[str, object]:
    replayed, _quotes = _compile_aggregate_segment(
        preflight=preflight,
        bundles=bundles,
        code_commit=str(expected_segment["segment_code_commit"]),
    )
    expected_bytes = _canonical_bytes(expected_segment)
    replay_bytes = _canonical_bytes(replayed)
    result = {
        "protocol": PHASE8B_REPLAY_PROTOCOL,
        "experiment_id": PHASE8B_RUNTIME_EXPERIMENT_ID,
        "aggregation_mode": AGGREGATION_MODE,
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "expected_segment_fingerprint": expected_segment[
            "segment_fingerprint"
        ],
        "replay_segment_fingerprint": replayed["segment_fingerprint"],
        "expected_segment_sha256": hashlib.sha256(expected_bytes).hexdigest(),
        "replay_segment_sha256": hashlib.sha256(replay_bytes).hexdigest(),
        "match": expected_bytes == replay_bytes,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    return result


def _scenario_evidence(
    aggregate: Mapping[str, object],
) -> dict[str, object]:
    scenarios = aggregate["scenarios"]
    assert isinstance(scenarios, Mapping)
    result: dict[str, object] = {}
    for key in ("0.2", "0.5", "1.0"):
        row = scenarios[key]
        assert isinstance(row, Mapping)
        completed = row["completed_trades"]
        metrics = row["metrics"]
        assert isinstance(completed, list)
        assert isinstance(metrics, Mapping)
        result[key] = {
            "trade_count": len(completed),
            "net_return": metrics["net_return"],
            "expectancy_usd": metrics["expectancy_usd"],
            "profit_factor": metrics["profit_factor"],
            "max_drawdown_fraction": metrics["max_drawdown_fraction"],
        }
    return result


def _decision_universe(row: Mapping[str, object]) -> set[str]:
    result: set[str] = set()
    completed = row.get("completed_trades")
    if isinstance(completed, list):
        for trade in completed:
            if isinstance(trade, Mapping):
                result.add(str(trade["decision_id"]))
    for field in ("risk_rejections", "outcomes"):
        value = row.get(field)
        if isinstance(value, Mapping):
            result.update(str(item) for item in value)
    for field in ("open_decision_ids", "pending_decision_ids"):
        value = row.get(field)
        if isinstance(value, list):
            result.update(str(item) for item in value)
    return result


def _same_candidate_sequence(aggregate: Mapping[str, object]) -> bool:
    scenarios = aggregate["scenarios"]
    assert isinstance(scenarios, Mapping)
    universes = [
        _decision_universe(scenarios[key])  # type: ignore[arg-type]
        for key in ("0.2", "0.5", "1.0")
    ]
    return universes[0] == universes[1] == universes[2]


def _representation(
    aggregate: Mapping[str, object],
) -> tuple[list[str], list[str]]:
    generated = aggregate["generated_candidates"]
    scenarios = aggregate["scenarios"]
    assert isinstance(generated, list)
    assert isinstance(scenarios, Mapping)
    candidate_map: dict[str, Mapping[str, object]] = {}
    for row in generated:
        if not isinstance(row, Mapping):
            raise ValueError("Phase 8B aggregate candidate row is malformed")
        candidate_id = str(row["candidate_id"])
        if candidate_id in candidate_map:
            raise ValueError("duplicate Phase 8B aggregate candidate ID")
        candidate_map[candidate_id] = row
    baseline = scenarios["0.2"]
    assert isinstance(baseline, Mapping)
    trades = baseline["completed_trades"]
    assert isinstance(trades, list)
    families: set[str] = set()
    pairs: set[str] = set()
    for trade in trades:
        if not isinstance(trade, Mapping):
            raise ValueError("Phase 8B aggregate trade row is malformed")
        decision_id = str(trade["decision_id"])
        candidate = candidate_map.get(decision_id)
        if candidate is None:
            raise ValueError("Phase 8B completed decision has no candidate metadata")
        metadata = candidate.get("metadata")
        if not isinstance(metadata, Mapping):
            raise ValueError("Phase 8B candidate metadata is malformed")
        family = metadata.get("strategy_family")
        if not isinstance(family, str) or not family:
            raise ValueError("Phase 8B candidate strategy family is missing")
        families.add(family)
        pairs.add(str(trade["symbol"]))
    return sorted(families), sorted(pairs)


def _quote_index(
    quotes: Sequence[Phase8BQuote],
) -> dict[tuple[str, str], Phase8BQuote]:
    result: dict[tuple[str, str], Phase8BQuote] = {}
    for quote in quotes:
        key = (quote.symbol, _utc_string(quote.source_time_utc))
        if key in result:
            raise ValueError("duplicate Phase 8B quote source identity")
        result[key] = quote
    return result


def _pip_size(symbol: str) -> float:
    if symbol == "USDJPY":
        return 0.01
    if symbol in {"EURUSD", "GBPUSD"}:
        return 0.0001
    raise ValueError("unsupported Phase 8B spread symbol")


def _spread_evidence(
    aggregate: Mapping[str, object],
    quotes: Sequence[Phase8BQuote],
    required_symbols: Sequence[str],
) -> dict[str, object]:
    index = _quote_index(quotes)
    scenarios = aggregate["scenarios"]
    assert isinstance(scenarios, Mapping)
    baseline = scenarios["0.2"]
    assert isinstance(baseline, Mapping)
    trades = baseline["completed_trades"]
    assert isinstance(trades, list)
    entry: dict[str, list[float]] = {symbol: [] for symbol in required_symbols}
    exit_: dict[str, list[float]] = {symbol: [] for symbol in required_symbols}
    for trade in trades:
        if not isinstance(trade, Mapping):
            raise ValueError("Phase 8B aggregate trade row is malformed")
        symbol = str(trade["symbol"])
        for field, target in (
            ("entry_timestamp_utc", entry),
            ("exit_timestamp_utc", exit_),
        ):
            timestamp = str(trade[field])
            quote = index.get((symbol, timestamp))
            if quote is None:
                raise ValueError(
                    f"Phase 8B {symbol} completed trade lacks exact spread quote"
                )
            target[symbol].append((quote.ask - quote.bid) / _pip_size(symbol))

    result: dict[str, object] = {}
    for symbol in required_symbols:
        entry_count, entry_median, entry_p95 = _spread_summary(entry[symbol])
        exit_count, exit_median, exit_p95 = _spread_summary(exit_[symbol])
        result[symbol] = {
            "entry_sample_count": entry_count,
            "exit_sample_count": exit_count,
            "entry_median_pips": entry_median,
            "entry_p95_pips": entry_p95,
            "exit_median_pips": exit_median,
            "exit_p95_pips": exit_p95,
        }
    return result


def _timing_evidence(
    bundles: Sequence[_SegmentBundle],
    aggregate: Mapping[str, object],
) -> dict[str, object]:
    latency = [
        float(row["processing_latency_ms"])
        for bundle in bundles
        for row in bundle.audits
    ]
    p99 = _nearest_rank(latency, 0.99)
    if p99 is None:
        raise ValueError("Phase 8B campaign has no processing latency samples")
    scenarios = aggregate["scenarios"]
    assert isinstance(scenarios, Mapping)
    baseline = scenarios["0.2"]
    assert isinstance(baseline, Mapping)
    outcomes = baseline["outcomes"]
    assert isinstance(outcomes, Mapping)
    return {
        "p99_processing_latency_ms": p99,
        "entry_deadline_violation_count": sum(
            1 for value in outcomes.values()
            if value == "ENTRY_DEADLINE_MISSED"
        ),
        "scheduled_exit_deadline_violation_count": sum(
            1 for value in outcomes.values()
            if value == "EXIT_DEADLINE_MISSED"
        ),
    }


def _campaign_evidence(
    *,
    preflight: Mapping[str, object],
    bundles: Sequence[_SegmentBundle],
    unclosed_count: int,
    aggregate: Mapping[str, object],
    replay: Mapping[str, object],
    quotes: Sequence[Phase8BQuote],
) -> dict[str, object]:
    if replay.get("match") is not True:
        raise ValueError("Phase 8B aggregate replay mismatch")
    scenarios_for_terminal = aggregate.get("scenarios")
    if not isinstance(scenarios_for_terminal, Mapping):
        raise ValueError("Phase 8B aggregate scenarios are malformed")
    for key in ("0.2", "0.5", "1.0"):
        row = scenarios_for_terminal.get(key)
        if not isinstance(row, Mapping):
            raise ValueError(f"Phase 8B aggregate scenario {key} is malformed")
        open_ids = row.get("open_decision_ids")
        pending_ids = row.get("pending_decision_ids")
        if not isinstance(open_ids, list) or not isinstance(pending_ids, list):
            raise ValueError(
                f"Phase 8B aggregate scenario {key} terminal state is malformed"
            )
        if open_ids or pending_ids:
            raise ValueError(
                "Phase 8B campaign closure requires zero open and pending decisions"
            )
    first, last = _received_bounds(bundles)
    denominator = _denominator_dates(first, last)
    complete = _complete_dates(denominator, _segment_intervals(bundles))
    scenarios = _scenario_evidence(aggregate)
    baseline = aggregate["scenarios"]["0.2"]  # type: ignore[index]
    assert isinstance(baseline, Mapping)
    completed = baseline["completed_trades"]
    assert isinstance(completed, list)
    families, pairs = _representation(aggregate)
    required_symbols = sorted(str(item) for item in preflight["required_symbols"])
    stale_ids = {
        str(key)
        for key, value in baseline["outcomes"].items()  # type: ignore[union-attr]
        if value == "OUTCOME_UNKNOWN_AFTER_GAP"
    }
    completed_ids = {
        str(item["decision_id"])
        for item in completed
        if isinstance(item, Mapping)
    }
    stale_in_financial = len(stale_ids & completed_ids)
    payload = {
        "protocol": PHASE8B_CAMPAIGN_EVIDENCE_PROTOCOL,
        "contract_decision": PHASE8B_ACCEPTANCE_CONTRACT_DECISION,
        "closure_decision": PHASE8B_CAMPAIGN_CLOSE_DECISION,
        "prospective_evidence": True,
        "prospective_segment_closed": True,
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "segment_fingerprint": aggregate["segment_fingerprint"],
        "replay_fingerprint": _canonical_digest(replay),
        "replay_match": True,
        "champion_set_fingerprint": preflight[
            "champion_set_fingerprint"
        ],
        "strategy_fingerprints": sorted(
            str(item) for item in preflight["strategy_fingerprints"]
        ),
        "required_symbols": required_symbols,
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "prospective_segment_fingerprints": [
            bundle.prospective["prospective_segment_fingerprint"]
            for bundle in bundles
        ],
        "campaign_start_utc": preflight["campaign_start_utc"],
        "first_observation_utc": _utc_string(first),
        "last_observation_utc": _utc_string(last),
        "denominator_london_dates": denominator,
        "complete_london_dates": complete,
        "completed_trade_count_0_2": len(completed),
        "same_candidate_sequence_all_scenarios": _same_candidate_sequence(
            aggregate
        ),
        "structural_safety": {
            "no_order_surface": True,
            "quote_only_bridge": True,
            "zero_demo_orders": True,
            "zero_live_orders": True,
            "zero_broker_mutations": True,
            "zero_real_money_actions": True,
        },
        "integrity": {
            "malformed_silently_accepted_count": 0,
            "stale_gap_trades_in_financial_metrics_count": stale_in_financial,
            "all_operational_events_logged": True,
            "eligible_closed_segment_count": len(bundles),
            "unclosed_segment_directory_count": unclosed_count,
        },
        "timing": _timing_evidence(bundles, aggregate),
        "scenarios": scenarios,
        "representation": {
            "strategy_families_with_completed_trades": families,
            "pairs_with_completed_trades": pairs,
        },
        "live_spread_by_symbol": _spread_evidence(
            aggregate,
            quotes,
            required_symbols,
        ),
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
    }
    evidence = payload | {
        "campaign_evidence_fingerprint": _canonical_digest(payload)
    }
    validate_phase8b_campaign_evidence(evidence)
    return evidence


PHASE8B_CAMPAIGN_PROGRESS_PROTOCOL = "fmp-phase8b-campaign-progress-v1"
PHASE8B_CAMPAIGN_PROGRESS_DECISION = "DEC-071"
PHASE8B_CAMPAIGN_PROGRESS_EXPERIMENT_ID = "EXP-20260923-042"
PHASE8B_CAMPAIGN_PROGRESS_AVAILABLE = "PHASE8B_CAMPAIGN_PROGRESS_AVAILABLE"
PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS = "PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS"


def _remaining(required: float, current: float) -> float:
    return max(0.0, required - current)


def preview_phase8b_campaign_progress_directory(
    *,
    campaign_dir: Path,
    code_commit: str,
) -> dict[str, object]:
    root = Path(campaign_dir)
    preflight = _load_json(
        root / "capture-preflight.json",
        label="Phase 8B capture preflight",
    )
    validate_phase8b_capture_preflight(preflight)
    commit = _validate_commit(
        code_commit,
        field="Phase 8B campaign-progress code commit",
    )

    try:
        bundles, unclosed_count = _load_bundles(root, preflight=preflight)
    except ValueError as exc:
        if str(exc) not in {
            "Phase 8B campaign has no segment directory",
            "Phase 8B campaign has no closed prospective segments",
        }:
            raise
        return {
            "protocol": PHASE8B_CAMPAIGN_PROGRESS_PROTOCOL,
            "decision": PHASE8B_CAMPAIGN_PROGRESS_DECISION,
            "experiment_id": PHASE8B_CAMPAIGN_PROGRESS_EXPERIMENT_ID,
            "outcome": PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS,
            "campaign_progress_code_commit": commit,
            "capture_preflight_fingerprint": preflight[
                "capture_preflight_fingerprint"
            ],
            "champion_set_fingerprint": preflight[
                "champion_set_fingerprint"
            ],
            "eligible_closed_segment_count": 0,
            "unclosed_segment_directory_count": 0,
            "minimum_evidence": {
                "elapsed_weeks": 0.0,
                "elapsed_weeks_required": MIN_ELAPSED_WEEKS,
                "elapsed_weeks_pass": False,
                "elapsed_weeks_remaining": float(MIN_ELAPSED_WEEKS),
                "complete_london_dates": 0,
                "complete_london_dates_required": MIN_COMPLETE_LONDON_DATES,
                "complete_london_dates_pass": False,
                "complete_london_dates_remaining": MIN_COMPLETE_LONDON_DATES,
                "completed_trade_count_0_2": 0,
                "completed_trade_count_required": MIN_COMPLETED_TRADES,
                "completed_trade_count_pass": False,
                "completed_trade_count_remaining": MIN_COMPLETED_TRADES,
                "represented_strategy_family_count": 0,
                "represented_strategy_family_count_required": MIN_REPRESENTED_FAMILIES,
                "represented_strategy_family_count_pass": False,
                "represented_strategy_family_count_remaining": MIN_REPRESENTED_FAMILIES,
                "represented_pair_count": 0,
                "represented_pair_count_required": MIN_REPRESENTED_PAIRS,
                "represented_pair_count_pass": False,
                "represented_pair_count_remaining": MIN_REPRESENTED_PAIRS,
                "all_minimums_pass": False,
            },
            "currently_closeable": False,
            "aggregate_replay_match": None,
            "acceptance_authorized": False,
            "promotion_authorized": False,
            "shadow_validation_authorized": False,
            "demo_order_authorized": False,
            "live_order_authorized": False,
            "broker_mutation_authorized": False,
            "real_money_authorized": False,
            "phase9_authorized": False,
        }

    aggregate, quotes = _compile_aggregate_segment(
        preflight=preflight,
        bundles=bundles,
        code_commit=commit,
    )
    replay = _build_replay(
        expected_segment=aggregate,
        preflight=preflight,
        bundles=bundles,
    )
    replay_match = replay.get("match") is True

    first, last = _received_bounds(bundles)
    denominator = _denominator_dates(first, last)
    complete = _complete_dates(denominator, _segment_intervals(bundles))
    elapsed_weeks = (last - first).total_seconds() / (7 * 24 * 60 * 60)

    scenarios = aggregate.get("scenarios")
    if not isinstance(scenarios, Mapping):
        raise ValueError("Phase 8B campaign-progress scenarios are malformed")
    baseline = scenarios.get("0.2")
    if not isinstance(baseline, Mapping):
        raise ValueError("Phase 8B campaign-progress baseline is malformed")
    completed = baseline.get("completed_trades")
    if not isinstance(completed, list):
        raise ValueError("Phase 8B campaign-progress completed trades malformed")
    families, pairs = _representation(aggregate)

    closeable = replay_match
    for key in ("0.2", "0.5", "1.0"):
        row = scenarios.get(key)
        if not isinstance(row, Mapping):
            raise ValueError(
                f"Phase 8B campaign-progress scenario {key} is malformed"
            )
        open_ids = row.get("open_decision_ids")
        pending_ids = row.get("pending_decision_ids")
        if not isinstance(open_ids, list) or not isinstance(pending_ids, list):
            raise ValueError(
                f"Phase 8B campaign-progress scenario {key} terminal state malformed"
            )
        if open_ids or pending_ids:
            closeable = False

    minimums = {
        "elapsed_weeks": elapsed_weeks,
        "elapsed_weeks_required": MIN_ELAPSED_WEEKS,
        "elapsed_weeks_pass": elapsed_weeks >= MIN_ELAPSED_WEEKS,
        "elapsed_weeks_remaining": _remaining(
            float(MIN_ELAPSED_WEEKS), elapsed_weeks
        ),
        "complete_london_dates": len(complete),
        "complete_london_dates_required": MIN_COMPLETE_LONDON_DATES,
        "complete_london_dates_pass": len(complete)
        >= MIN_COMPLETE_LONDON_DATES,
        "complete_london_dates_remaining": max(
            0, MIN_COMPLETE_LONDON_DATES - len(complete)
        ),
        "completed_trade_count_0_2": len(completed),
        "completed_trade_count_required": MIN_COMPLETED_TRADES,
        "completed_trade_count_pass": len(completed) >= MIN_COMPLETED_TRADES,
        "completed_trade_count_remaining": max(
            0, MIN_COMPLETED_TRADES - len(completed)
        ),
        "represented_strategy_family_count": len(families),
        "represented_strategy_family_count_required": MIN_REPRESENTED_FAMILIES,
        "represented_strategy_family_count_pass": len(families)
        >= MIN_REPRESENTED_FAMILIES,
        "represented_strategy_family_count_remaining": max(
            0, MIN_REPRESENTED_FAMILIES - len(families)
        ),
        "represented_pair_count": len(pairs),
        "represented_pair_count_required": MIN_REPRESENTED_PAIRS,
        "represented_pair_count_pass": len(pairs) >= MIN_REPRESENTED_PAIRS,
        "represented_pair_count_remaining": max(
            0, MIN_REPRESENTED_PAIRS - len(pairs)
        ),
    }
    minimums["all_minimums_pass"] = all(
        minimums[field] is True
        for field in (
            "elapsed_weeks_pass",
            "complete_london_dates_pass",
            "completed_trade_count_pass",
            "represented_strategy_family_count_pass",
            "represented_pair_count_pass",
        )
    )

    return {
        "protocol": PHASE8B_CAMPAIGN_PROGRESS_PROTOCOL,
        "decision": PHASE8B_CAMPAIGN_PROGRESS_DECISION,
        "experiment_id": PHASE8B_CAMPAIGN_PROGRESS_EXPERIMENT_ID,
        "outcome": PHASE8B_CAMPAIGN_PROGRESS_AVAILABLE,
        "campaign_progress_code_commit": commit,
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "champion_set_fingerprint": preflight["champion_set_fingerprint"],
        "eligible_closed_segment_count": len(bundles),
        "unclosed_segment_directory_count": unclosed_count,
        "first_observation_utc": _utc_string(first),
        "last_observation_utc": _utc_string(last),
        "denominator_london_date_count": len(denominator),
        "complete_london_date_count": len(complete),
        "represented_strategy_families": families,
        "represented_pairs": pairs,
        "minimum_evidence": minimums,
        "currently_closeable": closeable,
        "aggregate_replay_match": replay_match,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "shadow_validation_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }


def close_phase8b_campaign_directory(
    *,
    campaign_dir: Path,
    code_commit: str,
) -> dict[str, object]:
    root = Path(campaign_dir)
    preflight = _load_json(
        root / "capture-preflight.json",
        label="Phase 8B capture preflight",
    )
    validate_phase8b_capture_preflight(preflight)
    commit = _validate_commit(
        code_commit,
        field="Phase 8B campaign-close code commit",
    )
    bundles, unclosed_count = _load_bundles(root, preflight=preflight)
    prospective_fingerprints = [
        str(item.prospective["prospective_segment_fingerprint"])
        for item in bundles
    ]
    closure_payload = {
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "prospective_segment_fingerprints": prospective_fingerprints,
        "campaign_close_code_commit": commit,
    }
    closure_id = _canonical_digest(closure_payload)
    closure_dir = root / "closures" / closure_id
    if closure_dir.exists():
        raise FileExistsError("Phase 8B campaign closure snapshot already exists")

    aggregate, quotes = _compile_aggregate_segment(
        preflight=preflight,
        bundles=bundles,
        code_commit=commit,
    )
    replay = _build_replay(
        expected_segment=aggregate,
        preflight=preflight,
        bundles=bundles,
    )
    if replay.get("match") is not True:
        raise ValueError("Phase 8B aggregate replay mismatch")
    evidence = _campaign_evidence(
        preflight=preflight,
        bundles=bundles,
        unclosed_count=unclosed_count,
        aggregate=aggregate,
        replay=replay,
        quotes=quotes,
    )

    closure_dir.mkdir(parents=True, exist_ok=False)
    runtime_dir = closure_dir / "runtime"
    write_phase8b_segment_artifacts(
        segment=aggregate,
        replay=replay,
        out_dir=runtime_dir,
    )
    evidence_path = closure_dir / "campaign-evidence.json"
    _atomic_write(evidence_path, _stable_json_bytes(evidence))
    manifest = {
        "protocol": PHASE8B_CAMPAIGN_CLOSE_MANIFEST_PROTOCOL,
        "experiment_id": PHASE8B_CAMPAIGN_CLOSE_EXPERIMENT_ID,
        "decision": PHASE8B_CAMPAIGN_CLOSE_DECISION,
        "closure_id": closure_id,
        "outcome": PHASE8B_CAMPAIGN_EVIDENCE_SNAPSHOT_READY,
        "campaign_evidence_fingerprint": evidence[
            "campaign_evidence_fingerprint"
        ],
        "segment_fingerprint": aggregate["segment_fingerprint"],
        "replay_fingerprint": evidence["replay_fingerprint"],
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "artifacts": [
            {
                "path": "campaign-evidence.json",
                "sha256": _file_sha256(evidence_path),
            },
            {
                "path": "runtime/segment.json",
                "sha256": _file_sha256(runtime_dir / "segment.json"),
            },
            {
                "path": "runtime/replay.json",
                "sha256": _file_sha256(runtime_dir / "replay.json"),
            },
            {
                "path": "runtime/manifest.json",
                "sha256": _file_sha256(runtime_dir / "manifest.json"),
            },
        ],
    }
    _atomic_write(
        closure_dir / "manifest.json",
        _stable_json_bytes(manifest),
    )
    return {
        "outcome": PHASE8B_CAMPAIGN_EVIDENCE_SNAPSHOT_READY,
        "closure_id": closure_id,
        "campaign_evidence": evidence,
        "manifest": manifest,
    }


__all__ = [
    "AGGREGATION_MODE",
    "PHASE8B_CAMPAIGN_CLOSE_DECISION",
    "PHASE8B_CAMPAIGN_CLOSE_EXPERIMENT_ID",
    "PHASE8B_CAMPAIGN_CLOSE_MANIFEST_PROTOCOL",
    "PHASE8B_CAMPAIGN_EVIDENCE_SNAPSHOT_READY",
    "PHASE8B_CAMPAIGN_PROGRESS_AVAILABLE",
    "PHASE8B_CAMPAIGN_PROGRESS_DECISION",
    "PHASE8B_CAMPAIGN_PROGRESS_EXPERIMENT_ID",
    "PHASE8B_CAMPAIGN_PROGRESS_PROTOCOL",
    "PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS",
    "close_phase8b_campaign_directory",
    "preview_phase8b_campaign_progress_directory",
]
