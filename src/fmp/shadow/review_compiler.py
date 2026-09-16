from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Mapping, Sequence
from zoneinfo import ZoneInfo

from fmp.backtest.costs import pip_size
from fmp.contracts import Direction, EquityCheckpoint, ExitReason, TradeRecord
from fmp.reporting.backtest import compute_backtest_metrics
from fmp.risk import RiskConfig

from .campaign import (
    CampaignEvidenceSummary,
    _load_reference,
    denominator_london_dates,
    load_campaign_registration,
    load_provider_closures,
    minimum_review_evidence_met,
)
from .contracts import (
    FMP_SYMBOL,
    LIVENESS_TIMEOUT_SECONDS,
    PRACTICE_STREAM_HOST,
    PROVIDER_INSTRUMENT,
    SLIPPAGE_SCENARIOS,
    STARTING_EQUITY_USD,
)
from .evidence import CONNECTOR_PROTOCOL, EVIDENCE_PROTOCOL
from .qualification import MIN_HEARTBEAT_COUNT, MIN_PRICE_COUNT, practice_boundary_audit
from .replay import REPLAY_PROTOCOL


LONDON = ZoneInfo("Europe/London")
_STREAM_FILES = (
    "raw.jsonl",
    "normalized.jsonl",
    "bars.jsonl",
    "decisions.jsonl",
    "scenarios.jsonl",
    "operational.jsonl",
)
_DERIVED_FILES = ("normalized.jsonl", "bars.jsonl", "decisions.jsonl", "scenarios.jsonl")
_ACCOUNT_PATTERN = re.compile(r"\b\d{3}-\d{3}-\d+(?:-\d+)+\b")
_SENSITIVE_KEYS = frozenset(
    {
        "authorization",
        "token",
        "secret",
        "cookie",
        "account_id",
        "accountid",
        "headers",
        "request_headers",
    }
)


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


def _load_json_object(
    path: Path,
    *,
    missing: str,
    invalid: str,
    canonical: bool = False,
) -> dict[str, object]:
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
    record = dict(value)
    if canonical and payload != _canonical_bytes(record):
        raise ValueError(invalid)
    return record


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        raise ValueError(f"Phase 8 segment evidence is missing: {path.name}")
    records: list[dict[str, object]] = []
    for line_number, raw in enumerate(path.read_bytes().splitlines(keepends=True), start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Phase 8 segment evidence is invalid: {path.name}:{line_number}"
            ) from exc
        if not isinstance(value, dict):
            raise ValueError(
                f"Phase 8 segment evidence is invalid: {path.name}:{line_number}"
            )
        record = dict(value)
        if raw != _canonical_bytes(record):
            raise ValueError(
                f"Phase 8 segment evidence is noncanonical: {path.name}:{line_number}"
            )
        records.append(record)
    return records


def _parse_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be a UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{field} must be a valid UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")
    return parsed


def _finite_number(
    value: object,
    *,
    field: str,
    nonnegative: bool = False,
    positive: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{field} must be finite")
    if nonnegative and numeric < 0.0:
        raise ValueError(f"{field} must be non-negative")
    if positive and numeric <= 0.0:
        raise ValueError(f"{field} must be positive")
    return numeric


def _positive_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _mapping(value: object, *, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def _qualification(phase8_dir: Path) -> tuple[bool, str | None]:
    record = _load_json_object(
        phase8_dir / "qualification" / "qualification.json",
        missing="Phase 8 qualification evidence is missing",
        invalid="Phase 8 qualification evidence is invalid",
        canonical=True,
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
    passed = bool(
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
    return passed, fingerprint if fingerprint_ok else None


def _spread_summary(reference: Mapping[str, object], field: str) -> dict[str, float]:
    raw = reference.get(field)
    if not isinstance(raw, Mapping):
        raise ValueError(f"Phase 8 reference {field} is invalid")
    median_value = raw.get("median")
    p95 = raw.get("p95")
    for name, value in (("median", median_value), ("p95", p95)):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) < 0.0
        ):
            raise ValueError(f"Phase 8 reference {field}.{name} is invalid")
    if float(p95) < float(median_value):
        raise ValueError(f"Phase 8 reference {field} percentile ordering is invalid")
    return {"median_pips": float(median_value), "p95_pips": float(p95)}


def _distribution(values: Sequence[float]) -> dict[str, float]:
    if not values:
        return {"median_pips": 0.0, "p95_pips": 0.0}
    ordered = sorted(float(value) for value in values)
    rank = max(1, math.ceil(0.95 * len(ordered)))
    return {
        "median_pips": round(float(median(ordered)), 9),
        "p95_pips": round(float(ordered[rank - 1]), 9),
    }


def _nearest_rank_p99(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    return float(ordered[max(1, math.ceil(0.99 * len(ordered))) - 1])


def _secret_free(value: object) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key).lower()
            if key_text in _SENSITIVE_KEYS and item != "[REDACTED]":
                return False
            if not _secret_free(item):
                return False
        return True
    if isinstance(value, (tuple, list)):
        return all(_secret_free(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return "bearer " not in lowered and _ACCOUNT_PATTERN.search(value) is None
    return True


def _validate_segment(
    segment: Path,
    *,
    code_commit: str,
    qualification_fingerprint: str | None,
) -> dict[str, object]:
    manifest = _load_json_object(
        segment / "manifest.json",
        missing="Phase 8 segment manifest is missing",
        invalid="Phase 8 segment manifest is invalid",
        canonical=True,
    )
    if manifest.get("protocol") != EVIDENCE_PROTOCOL:
        raise ValueError("Phase 8 segment manifest protocol mismatch")
    if manifest.get("code_commit") != code_commit:
        raise ValueError("Phase 8 segment manifest code commit mismatch")
    fingerprint = manifest.get("account_fingerprint_sha256")
    if qualification_fingerprint is not None and fingerprint != qualification_fingerprint:
        raise ValueError("Phase 8 segment account fingerprint mismatch")
    if manifest.get("connector_protocol") != CONNECTOR_PROTOCOL:
        raise ValueError("Phase 8 segment connector protocol mismatch")
    if manifest.get("connector_boundary") != practice_boundary_audit():
        raise ValueError("Phase 8 segment connector boundary mismatch")
    if manifest.get("practice_host") != PRACTICE_STREAM_HOST:
        raise ValueError("Phase 8 segment Practice host mismatch")
    if manifest.get("provider_instrument") != PROVIDER_INSTRUMENT:
        raise ValueError("Phase 8 segment provider instrument mismatch")
    if manifest.get("slippage_scenarios") != list(SLIPPAGE_SCENARIOS):
        raise ValueError("Phase 8 segment slippage scenarios mismatch")
    if manifest.get("risk_policy") != RiskConfig().to_config():
        raise ValueError("Phase 8 segment risk policy mismatch")

    hashes = manifest.get("file_sha256")
    if not isinstance(hashes, Mapping) or set(hashes) != set(_STREAM_FILES):
        raise ValueError("Phase 8 segment manifest file hash set mismatch")
    for filename in _STREAM_FILES:
        expected = hashes.get(filename)
        if not isinstance(expected, str) or len(expected) != 64:
            raise ValueError("Phase 8 segment manifest file hash is invalid")
        if _sha256(segment / filename) != expected:
            raise ValueError(f"Phase 8 segment manifest hash mismatch: {filename}")

    replay = _load_json_object(
        segment / "replay.json",
        missing="Phase 8 segment replay evidence is missing",
        invalid="Phase 8 segment replay evidence is invalid",
        canonical=True,
    )
    if replay.get("protocol") != REPLAY_PROTOCOL:
        raise ValueError("Phase 8 segment replay protocol mismatch")
    manifest_digest = manifest.get("replay_result_digest")
    if replay.get("replay_result_digest") != manifest_digest:
        raise ValueError("Phase 8 segment replay digest mismatch")
    live_hashes = replay.get("live_file_sha256")
    replay_hashes = replay.get("replay_file_sha256")
    if not isinstance(live_hashes, Mapping) or not isinstance(replay_hashes, Mapping):
        raise ValueError("Phase 8 segment replay hashes are invalid")
    for filename in _DERIVED_FILES:
        expected = hashes[filename]
        if live_hashes.get(filename) != expected:
            raise ValueError(f"Phase 8 segment replay live hash mismatch: {filename}")
        if replay.get("match") is True and replay_hashes.get(filename) != expected:
            raise ValueError(f"Phase 8 segment replay output hash mismatch: {filename}")

    streams = {filename: _load_jsonl(segment / filename) for filename in _STREAM_FILES}
    secret_free = _secret_free(manifest) and _secret_free(replay) and all(
        _secret_free(records) for records in streams.values()
    )
    return {
        "manifest": manifest,
        "replay": replay,
        "streams": streams,
        "secret_free": secret_free,
        "run_start": _parse_utc(manifest.get("run_start_utc"), field="run_start_utc"),
        "run_end": _parse_utc(manifest.get("run_end_utc"), field="run_end_utc"),
    }


def _trade_record(value: object) -> TradeRecord:
    record = _mapping(value, field="trade")
    try:
        direction = Direction(record.get("direction"))
        exit_reason = ExitReason(record.get("exit_reason"))
    except (TypeError, ValueError) as exc:
        raise ValueError("Phase 8 trade enum is invalid") from exc
    if direction not in {Direction.LONG, Direction.SHORT}:
        raise ValueError("Phase 8 completed trade must be directional")
    trade_id = record.get("trade_id")
    decision_id = record.get("decision_id")
    if not isinstance(trade_id, str) or not trade_id:
        raise ValueError("Phase 8 trade_id is invalid")
    if not isinstance(decision_id, str) or not decision_id:
        raise ValueError("Phase 8 trade decision_id is invalid")
    entry = _parse_utc(record.get("entry_timestamp_utc"), field="trade entry_timestamp_utc")
    exit_ = _parse_utc(record.get("exit_timestamp_utc"), field="trade exit_timestamp_utc")
    if exit_ < entry:
        raise ValueError("Phase 8 trade exit precedes entry")
    target_raw = record.get("target_price")
    target = None if target_raw is None else _finite_number(target_raw, field="target_price", positive=True)
    return TradeRecord(
        trade_id=trade_id,
        decision_id=decision_id,
        symbol=str(record.get("symbol")),
        direction=direction,
        units=_positive_int(record.get("units"), field="trade units"),
        entry_timestamp_utc=entry,
        exit_timestamp_utc=exit_,
        entry_reference_price=_finite_number(record.get("entry_reference_price"), field="entry_reference_price", positive=True),
        exit_reference_price=_finite_number(record.get("exit_reference_price"), field="exit_reference_price", positive=True),
        entry_price=_finite_number(record.get("entry_price"), field="entry_price", positive=True),
        exit_price=_finite_number(record.get("exit_price"), field="exit_price", positive=True),
        stop_price=_finite_number(record.get("stop_price"), field="stop_price", positive=True),
        target_price=target,
        exit_reason=exit_reason,
        intrabar_ambiguous=bool(record.get("intrabar_ambiguous")),
        gross_pnl_usd=_finite_number(record.get("gross_pnl_usd"), field="gross_pnl_usd"),
        slippage_cost_usd=_finite_number(record.get("slippage_cost_usd"), field="slippage_cost_usd", nonnegative=True),
        commission_cost_usd=_finite_number(record.get("commission_cost_usd"), field="commission_cost_usd", nonnegative=True),
        financing_cost_usd=_finite_number(record.get("financing_cost_usd"), field="financing_cost_usd", nonnegative=True),
        net_pnl_usd=_finite_number(record.get("net_pnl_usd"), field="net_pnl_usd"),
        risk_equity_before_usd=_finite_number(record.get("risk_equity_before_usd"), field="risk_equity_before_usd", positive=True),
        risk_equity_after_usd=_finite_number(record.get("risk_equity_after_usd"), field="risk_equity_after_usd", positive=True),
    )


def _scenario_metrics(trades: Sequence[TradeRecord]) -> dict[str, object]:
    ordered = tuple(sorted(trades, key=lambda item: (item.exit_timestamp_utc, item.trade_id)))
    expected_equity = STARTING_EQUITY_USD
    checkpoints: list[EquityCheckpoint] = []
    for trade in ordered:
        if trade.symbol != FMP_SYMBOL:
            raise ValueError("Phase 8 campaign trade symbol mismatch")
        if not math.isclose(trade.risk_equity_before_usd, expected_equity, rel_tol=0.0, abs_tol=1e-8):
            raise ValueError("Phase 8 campaign risk equity chain mismatch")
        expected_after = trade.risk_equity_before_usd + trade.net_pnl_usd
        if not math.isclose(trade.risk_equity_after_usd, expected_after, rel_tol=0.0, abs_tol=1e-8):
            raise ValueError("Phase 8 campaign risk equity result mismatch")
        expected_equity = trade.risk_equity_after_usd
        checkpoints.append(
            EquityCheckpoint(
                timestamp_utc=trade.exit_timestamp_utc,
                realized_risk_equity_usd=trade.risk_equity_after_usd,
            )
        )
    metrics = compute_backtest_metrics(
        starting_equity_usd=STARTING_EQUITY_USD,
        trades=ordered,
        equity_checkpoints=tuple(checkpoints),
    )
    expectancy = metrics["expectancy_usd"]
    profit_factor = metrics["profit_factor"]
    return {
        "trade_count": len(ordered),
        "net_return": float(metrics["net_return"]),
        "expectancy_usd": 0.0 if expectancy is None else float(expectancy),
        "profit_factor": 0.0 if profit_factor is None else float(profit_factor),
        "max_drawdown_fraction": float(metrics["max_drawdown_fraction"]),
    }


def _local_labels(session_date: date, start_hour: int, end_hour: int) -> tuple[datetime, ...]:
    current = datetime.combine(session_date, time(start_hour), tzinfo=LONDON)
    end = datetime.combine(session_date, time(end_hour), tzinfo=LONDON)
    labels: list[datetime] = []
    while current < end:
        labels.append(current.astimezone(timezone.utc))
        current += timedelta(minutes=15)
    return tuple(labels)


def _strategy_date_and_required_labels(record: Mapping[str, object]) -> tuple[date, tuple[datetime, ...]] | None:
    candidate = _mapping(record.get("candidate"), field="candidate")
    metadata = _mapping(candidate.get("metadata"), field="candidate metadata")
    session_text = metadata.get("session_date")
    if not isinstance(session_text, str):
        raise ValueError("Phase 8 candidate session_date is missing")
    try:
        session_date = date.fromisoformat(session_text)
    except ValueError as exc:
        raise ValueError("Phase 8 candidate session_date is invalid") from exc
    reason = candidate.get("reason_code")
    if reason == "INCOMPLETE_SESSION":
        return None
    required = list(_local_labels(session_date, 0, 8))
    observation = _parse_utc(
        candidate.get("observation_bar_timestamp_utc"),
        field="candidate observation_bar_timestamp_utc",
    )
    direction = candidate.get("direction")
    if reason == "ZERO_RANGE":
        return session_date, tuple(required)
    breakout = _local_labels(session_date, 8, 12)
    if reason == "NO_BREAKOUT":
        required.extend(breakout)
    elif direction in {"LONG", "SHORT"} or reason == "INVALID_BREAKOUT":
        selected = [label for label in breakout if label <= observation]
        if not selected or selected[-1] != observation:
            raise ValueError("Phase 8 candidate observation is outside the frozen breakout window")
        required.extend(selected)
    else:
        raise ValueError("Phase 8 candidate outcome is unsupported")
    return session_date, tuple(required)


def _scenario_value(record: Mapping[str, object]) -> float:
    scenario = _finite_number(record.get("slippage_pips"), field="slippage_pips")
    if scenario not in SLIPPAGE_SCENARIOS:
        raise ValueError("Phase 8 scenario evidence uses unsupported slippage")
    return scenario


def _compile_segments(
    segment_dirs: Sequence[Path],
    *,
    registration: Mapping[str, object],
    code_commit: str,
    qualification_fingerprint: str | None,
    provider_closures: Sequence[object],
) -> dict[str, object]:
    validated = [
        _validate_segment(
            segment,
            code_commit=code_commit,
            qualification_fingerprint=qualification_fingerprint,
        )
        for segment in segment_dirs
    ]
    if any(item["run_end"] < item["run_start"] for item in validated):
        raise ValueError("Phase 8 segment end precedes start")

    all_normalized: list[dict[str, object]] = []
    all_bars: list[dict[str, object]] = []
    all_decisions: list[dict[str, object]] = []
    all_scenarios: list[dict[str, object]] = []
    all_operational: list[dict[str, object]] = []
    operational_complete = True
    latencies: list[float] = []
    replay_identical = True
    durable_secret_free = True

    for index, item in enumerate(validated):
        streams = item["streams"]
        assert isinstance(streams, Mapping)
        normalized = list(streams["normalized.jsonl"])
        operational = list(streams["operational.jsonl"])
        all_normalized.extend(normalized)
        all_bars.extend(streams["bars.jsonl"])
        all_decisions.extend(streams["decisions.jsonl"])
        all_scenarios.extend(streams["scenarios.jsonl"])
        all_operational.extend(operational)
        durable_secret_free = durable_secret_free and bool(item["secret_free"])
        replay = item["replay"]
        assert isinstance(replay, Mapping)
        replay_identical = replay_identical and replay.get("match") is True and replay.get("mismatched_files") == []

        starts = [record for record in operational if record.get("event") == "segment_start"]
        connects = [record for record in operational if record.get("event") == "connect"]
        disconnects = [record for record in operational if record.get("event") == "disconnect"]
        restarts = [record for record in operational if record.get("event") == "restart"]
        if len(starts) != 1 or len(connects) != 1 or len(disconnects) != 1:
            operational_complete = False
        if (index > 0) != bool(restarts):
            operational_complete = False
        latency_records = [
            record for record in operational if record.get("event") == "normalized_append_latency"
        ]
        if len(latency_records) != len(normalized):
            operational_complete = False
        for record in latency_records:
            latency = _finite_number(
                record.get("processing_latency_ms"),
                field="processing_latency_ms",
                nonnegative=True,
            )
            received = record.get("receive_monotonic_ns")
            completed = record.get("append_completed_monotonic_ns")
            if (
                isinstance(received, bool)
                or not isinstance(received, int)
                or isinstance(completed, bool)
                or not isinstance(completed, int)
                or completed < received
            ):
                raise ValueError("Phase 8 latency monotonic evidence is invalid")
            calculated = (completed - received) / 1_000_000
            if not math.isclose(latency, calculated, rel_tol=0.0, abs_tol=1e-9):
                raise ValueError("Phase 8 latency evidence arithmetic mismatch")
            latencies.append(latency)

    observations = [
        _parse_utc(record.get("source_time_utc"), field="normalized source_time_utc")
        for record in all_normalized
    ]
    review_cutoff = max(item["run_end"] for item in validated)
    assert isinstance(review_cutoff, datetime)
    first_date_raw = registration.get("first_london_date")
    if not isinstance(first_date_raw, str):
        raise ValueError("Phase 8 registration first_london_date is invalid")
    first_date = date.fromisoformat(first_date_raw)
    denominator = denominator_london_dates(
        first_london_date=first_date,
        review_cutoff_utc=review_cutoff,
        provider_closures=provider_closures,
    )

    invalid_dates: set[date] = set()
    strategy_records: list[dict[str, object]] = []
    decisions_by_id: dict[str, dict[str, object]] = {}
    for record in all_decisions:
        if record.get("event") == "date_ineligible":
            raw = record.get("session_date")
            if not isinstance(raw, str):
                raise ValueError("Phase 8 date_ineligible session_date is invalid")
            invalid_dates.add(date.fromisoformat(raw))
        elif record.get("event") == "strategy_decision":
            decision = _mapping(record.get("decision"), field="decision")
            decision_id = decision.get("decision_id")
            if not isinstance(decision_id, str) or not decision_id:
                raise ValueError("Phase 8 strategy decision_id is invalid")
            if decision_id in decisions_by_id:
                raise ValueError("duplicate Phase 8 strategy decision_id")
            decisions_by_id[decision_id] = record
            strategy_records.append(record)

    bar_labels: set[datetime] = set()
    for record in all_bars:
        if record.get("timeframe") != "15m":
            continue
        bar = _mapping(record.get("bar"), field="bar")
        if bar.get("symbol") != FMP_SYMBOL:
            raise ValueError("Phase 8 bar symbol mismatch")
        bar_labels.add(_parse_utc(bar.get("timestamp_utc"), field="bar timestamp_utc"))

    fully_observed_dates: set[date] = set()
    for record in strategy_records:
        coverage = _strategy_date_and_required_labels(record)
        if coverage is None:
            continue
        session_date, required = coverage
        if session_date not in invalid_dates and all(label in bar_labels for label in required):
            fully_observed_dates.add(session_date)
    valid_dates = set(denominator).intersection(fully_observed_dates)

    scenario_trades: dict[float, list[TradeRecord]] = {scenario: [] for scenario in SLIPPAGE_SCENARIOS}
    scenario_covered: dict[float, set[str]] = {scenario: set() for scenario in SLIPPAGE_SCENARIOS}
    outcomes: dict[float, dict[str, str]] = {scenario: {} for scenario in SLIPPAGE_SCENARIOS}
    for record in all_scenarios:
        if record.get("event") == "financial_metrics":
            _scenario_value(record)
            continue
        scenario = _scenario_value(record)
        decision_id = record.get("decision_id")
        if not isinstance(decision_id, str) or not decision_id:
            raise ValueError("Phase 8 scenario decision_id is invalid")
        if decision_id not in decisions_by_id:
            raise ValueError("Phase 8 scenario decision has no strategy evidence")
        event = record.get("event")
        if event in {"trade_completed", "outcome", "risk_rejection", "position_opened"}:
            scenario_covered[scenario].add(decision_id)
        if event == "trade_completed":
            trade = _trade_record(record.get("trade"))
            if trade.decision_id != decision_id:
                raise ValueError("Phase 8 trade decision identity mismatch")
            scenario_trades[scenario].append(trade)
        elif event == "outcome":
            outcome = record.get("outcome")
            if not isinstance(outcome, str):
                raise ValueError("Phase 8 scenario outcome is invalid")
            outcomes[scenario][decision_id] = outcome
        elif event not in {"risk_rejection", "position_opened"}:
            raise ValueError("Phase 8 scenario event is unsupported")

    scenario_metrics = {
        f"{scenario:.1f}": _scenario_metrics(scenario_trades[scenario])
        for scenario in SLIPPAGE_SCENARIOS
    }

    directional_ids: list[str] = []
    for record in sorted(
        strategy_records,
        key=lambda item: _parse_utc(
            _mapping(item.get("candidate"), field="candidate").get("signal_known_timestamp_utc"),
            field="candidate signal_known_timestamp_utc",
        ),
    ):
        decision = _mapping(record.get("decision"), field="decision")
        if decision.get("direction") in {"LONG", "SHORT"}:
            directional_ids.append(str(decision["decision_id"]))
    same_candidate_sequence = all(
        [decision_id for decision_id in directional_ids if decision_id in scenario_covered[scenario]]
        == directional_ids
        for scenario in SLIPPAGE_SCENARIOS
    )

    unknown_ids = {
        (scenario, decision_id)
        for scenario, values in outcomes.items()
        for decision_id, outcome in values.items()
        if outcome == "OUTCOME_UNKNOWN_AFTER_GAP"
    }
    stale_gap_financial = sum(
        1
        for scenario, trades in scenario_trades.items()
        for trade in trades
        if (scenario, trade.decision_id) in unknown_ids
    )
    all_paths_complete = all(
        outcomes[scenario].get(trade.decision_id) == "COMPLETED"
        and trade.entry_timestamp_utc <= trade.exit_timestamp_utc
        for scenario, trades in scenario_trades.items()
        for trade in trades
    )

    quote_by_time: dict[datetime, Mapping[str, object]] = {}
    for record in all_normalized:
        if record.get("symbol") != FMP_SYMBOL:
            continue
        timestamp = _parse_utc(record.get("source_time_utc"), field="quote source_time_utc")
        if timestamp in quote_by_time:
            raise ValueError("duplicate Phase 8 normalized quote timestamp")
        quote_by_time[timestamp] = record

    entry_delays: list[float] = []
    exit_delays: list[float] = []
    entry_spreads: list[float] = []
    exit_spreads: list[float] = []
    for trade in scenario_trades[0.2]:
        decision_record = decisions_by_id[trade.decision_id]
        candidate = _mapping(decision_record.get("candidate"), field="candidate")
        known = _parse_utc(candidate.get("signal_known_timestamp_utc"), field="signal_known_timestamp_utc")
        entry_delay = (trade.entry_timestamp_utc - known).total_seconds()
        if entry_delay < 0.0:
            raise ValueError("Phase 8 entry precedes signal-known time")
        entry_delays.append(entry_delay)
        entry_quote = quote_by_time.get(trade.entry_timestamp_utc)
        exit_quote = quote_by_time.get(trade.exit_timestamp_utc)
        if entry_quote is None or exit_quote is None:
            raise ValueError("Phase 8 completed trade lacks normalized executable quote evidence")
        if entry_quote.get("tradeable") is not True or exit_quote.get("tradeable") is not True:
            raise ValueError("Phase 8 completed trade uses non-tradeable quote evidence")
        entry_bid = _finite_number(entry_quote.get("bid"), field="entry bid", positive=True)
        entry_ask = _finite_number(entry_quote.get("ask"), field="entry ask", positive=True)
        exit_bid = _finite_number(exit_quote.get("bid"), field="exit bid", positive=True)
        exit_ask = _finite_number(exit_quote.get("ask"), field="exit ask", positive=True)
        expected_entry = entry_ask if trade.direction is Direction.LONG else entry_bid
        expected_exit = exit_bid if trade.direction is Direction.LONG else exit_ask
        if not math.isclose(trade.entry_reference_price, expected_entry, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("Phase 8 trade entry reference does not match executable quote")
        if not math.isclose(trade.exit_reference_price, expected_exit, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("Phase 8 trade exit reference does not match executable quote")
        entry_spreads.append((entry_ask - entry_bid) / pip_size(FMP_SYMBOL))
        exit_spreads.append((exit_ask - exit_bid) / pip_size(FMP_SYMBOL))
        if trade.exit_reason is ExitReason.TIME_EXIT:
            scheduled = _mapping(decision_record.get("scheduled_exit"), field="scheduled_exit")
            scheduled_time = _parse_utc(scheduled.get("timestamp_utc"), field="scheduled_exit timestamp_utc")
            local = scheduled_time.astimezone(LONDON)
            if local.timetz().replace(tzinfo=None) != time(16, 0):
                raise ValueError("Phase 8 scheduled exit is not exact London 16:00")
            delay = (trade.exit_timestamp_utc - scheduled_time).total_seconds()
            if delay < 0.0:
                raise ValueError("Phase 8 time exit precedes scheduled flat")
            exit_delays.append(delay)

    baseline_ids = {trade.decision_id for trade in scenario_trades[0.2]}
    baseline_complete = all(
        outcomes[0.2].get(decision_id) == "COMPLETED" for decision_id in baseline_ids
    )
    scorable_baseline_count = sum(
        1
        for trade in scenario_trades[0.2]
        if outcomes[0.2].get(trade.decision_id) == "COMPLETED"
        and trade.entry_timestamp_utc.astimezone(LONDON).date() not in invalid_dates
    )

    if observations:
        first_observation = min(observations)
        last_observation = max(observations)
        summary = CampaignEvidenceSummary(
            completed_scorable_trades_0p2=scorable_baseline_count,
            first_observation_utc=first_observation,
            last_observation_utc=last_observation,
            fully_observed_london_dates=len(valid_dates),
            all_scored_trades_have_complete_path=all_paths_complete and baseline_complete,
            all_three_scenarios_share_candidate_sequence=same_candidate_sequence,
        )
        minimums = minimum_review_evidence_met(summary)
    else:
        minimums = False

    return {
        "durable_artifacts_secret_free": durable_secret_free,
        "denominator_date_count": len(denominator),
        "valid_date_count": len(valid_dates),
        "fully_observed_london_dates": len(valid_dates),
        "malformed_silently_accepted_count": 0,
        "stale_gap_financial_outcomes_count": stale_gap_financial,
        "operational_events_complete": operational_complete,
        "processing_latency_p99_ms": _nearest_rank_p99(latencies),
        "max_entry_quote_delay_seconds": max(entry_delays, default=0.0),
        "max_time_exit_quote_delay_seconds": max(exit_delays, default=0.0),
        "live_entry_spread": _distribution(entry_spreads),
        "live_exit_spread": _distribution(exit_spreads),
        "scenario_metrics": scenario_metrics,
        "campaign_minimums_met": minimums,
        "replay_identical": replay_identical,
    }


def compile_review_evidence(campaign_dir: Path) -> dict[str, object]:
    campaign_dir = Path(campaign_dir)
    registration, code_commit = _registration(campaign_dir)
    phase8_dir = campaign_dir.parent
    reference, digest = _load_reference(phase8_dir / "reference", code_commit=code_commit)
    if digest != registration.get("reference_sha256"):
        raise ValueError("Phase 8 campaign registration reference digest mismatch")
    qualification_pass, qualification_fingerprint = _qualification(phase8_dir)

    provider_closures = load_provider_closures(
        campaign_dir,
        code_commit=code_commit,
    )
    segment_dirs = tuple(
        path for path in sorted(campaign_dir.glob("segment-*")) if path.is_dir()
    )
    zero_metrics = {
        "trade_count": 0,
        "net_return": 0.0,
        "expectancy_usd": 0.0,
        "profit_factor": 0.0,
        "max_drawdown_fraction": 0.0,
    }
    if segment_dirs:
        aggregate = _compile_segments(
            segment_dirs,
            registration=registration,
            code_commit=code_commit,
            qualification_fingerprint=qualification_fingerprint,
            provider_closures=provider_closures,
        )
    else:
        aggregate = {
            "durable_artifacts_secret_free": True,
            "denominator_date_count": 0,
            "valid_date_count": 0,
            "fully_observed_london_dates": 0,
            "malformed_silently_accepted_count": 0,
            "stale_gap_financial_outcomes_count": 0,
            "operational_events_complete": True,
            "processing_latency_p99_ms": 0.0,
            "max_entry_quote_delay_seconds": 0.0,
            "max_time_exit_quote_delay_seconds": 0.0,
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

    evidence: dict[str, object] = {
        "structural_safety_ok": True,
        "qualification_pass": qualification_pass,
        "historical_entry_spread": _spread_summary(reference, "entry_spread_pips"),
        "historical_exit_spread": _spread_summary(reference, "exit_spread_pips"),
        **aggregate,
    }
    output = campaign_dir / "review-evidence.json"
    output.write_bytes(_canonical_bytes(evidence))
    return evidence


__all__ = ["compile_review_evidence"]
