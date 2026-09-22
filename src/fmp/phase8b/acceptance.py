from __future__ import annotations

import hashlib
import json
import math
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping, Sequence


PHASE8B_ACCEPTANCE_EXPERIMENT_ID = "EXP-20260922-022"
PHASE8B_ACCEPTANCE_PROTOCOL = "fmp-phase8b-acceptance-v1"
PHASE8B_ACCEPTANCE_ARTIFACT_PROTOCOL = "fmp-phase8b-acceptance-artifacts-v1"
PHASE8B_CAMPAIGN_EVIDENCE_PROTOCOL = "fmp-phase8b-campaign-evidence-v1"
PHASE8B_SPREAD_REFERENCE_PROTOCOL = "fmp-phase8b-spread-reference-v1"
PHASE8B_ACCEPTANCE_CONTRACT_DECISION = "DEC-051"

PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN = (
    "PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN"
)
PHASE8B_NEED_MORE_DATA = "PHASE8B_NEED_MORE_DATA"
PHASE8B_REJECT_OPERATIONAL_MISMATCH = (
    "PHASE8B_REJECT_OPERATIONAL_MISMATCH"
)
PHASE8B_REJECT_MARKET_MISMATCH = "PHASE8B_REJECT_MARKET_MISMATCH"
PHASE8B_REJECT_FINANCIAL_MISMATCH = (
    "PHASE8B_REJECT_FINANCIAL_MISMATCH"
)
PHASE8B_REJECT_SAFETY_FAILURE = "PHASE8B_REJECT_SAFETY_FAILURE"

SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)
MIN_COMPLETED_TRADES = 40
MIN_ELAPSED_WEEKS = 8
MIN_COMPLETE_LONDON_DATES = 30
MIN_REPRESENTED_FAMILIES = 2
MIN_REPRESENTED_PAIRS = 2
MIN_COVERAGE_FRACTION = 0.90
MAX_P99_PROCESSING_LATENCY_MS = 250.0
SPREAD_TOLERANCE_PIPS = 0.5
MAX_DRAWDOWN_FRACTION = 0.05

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
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


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


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


def _require_bool(value: object, *, field: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field} must be boolean")
    return value


def _nonnegative_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _finite_number(
    value: object,
    *,
    field: str,
    nonnegative: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    if nonnegative and result < 0:
        raise ValueError(f"{field} must be non-negative")
    return result


def _optional_finite_number(
    value: object,
    *,
    field: str,
    nonnegative: bool = False,
) -> float | None:
    if value is None:
        return None
    return _finite_number(value, field=field, nonnegative=nonnegative)


def _string_list(
    value: object,
    *,
    field: str,
    nonempty: bool = False,
    sorted_required: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    result = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError(f"{field} contains invalid string")
        result.append(item)
    if nonempty and not result:
        raise ValueError(f"{field} must be non-empty")
    if len(set(result)) != len(result):
        raise ValueError(f"{field} contains duplicates")
    if sorted_required and result != sorted(result):
        raise ValueError(f"{field} must be sorted")
    return result


def _validate_dates(value: object, *, field: str) -> list[str]:
    dates = _string_list(
        value,
        field=field,
        sorted_required=True,
    )
    for item in dates:
        if not _DATE_RE.fullmatch(item):
            raise ValueError(f"{field} contains invalid date")
        try:
            datetime.fromisoformat(item)
        except ValueError as exc:
            raise ValueError(f"{field} contains invalid date") from exc
    return dates


def _validate_slippage(value: object, *, field: str) -> None:
    if value != list(SLIPPAGE_SCENARIOS):
        raise ValueError(f"{field} must be exactly [0.2, 0.5, 1.0]")


def _validate_fingerprint(
    value: Mapping[str, object],
    *,
    field: str,
) -> None:
    fingerprint = _validate_sha256(value.get(field), field=field)
    payload = dict(value)
    payload.pop(field, None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError(f"{field} mismatch")


def _validate_spread_row(
    row: object,
    *,
    field: str,
    require_samples: bool,
) -> dict[str, object]:
    if not isinstance(row, Mapping):
        raise ValueError(f"{field} must be an object")
    entry_count = _nonnegative_int(
        row.get("entry_sample_count"),
        field=f"{field}.entry_sample_count",
    )
    exit_count = _nonnegative_int(
        row.get("exit_sample_count"),
        field=f"{field}.exit_sample_count",
    )
    if require_samples and (entry_count == 0 or exit_count == 0):
        raise ValueError(f"{field} requires entry and exit samples")

    result: dict[str, object] = {
        "entry_sample_count": entry_count,
        "exit_sample_count": exit_count,
    }
    for prefix, count in (("entry", entry_count), ("exit", exit_count)):
        median = _optional_finite_number(
            row.get(f"{prefix}_median_pips"),
            field=f"{field}.{prefix}_median_pips",
            nonnegative=True,
        )
        p95 = _optional_finite_number(
            row.get(f"{prefix}_p95_pips"),
            field=f"{field}.{prefix}_p95_pips",
            nonnegative=True,
        )
        if count == 0:
            if median is not None or p95 is not None:
                raise ValueError(
                    f"{field} zero-sample {prefix} spread must be null"
                )
        else:
            if median is None or p95 is None:
                raise ValueError(
                    f"{field} sampled {prefix} spread is incomplete"
                )
            if p95 < median:
                raise ValueError(
                    f"{field} {prefix} p95 spread is below median"
                )
        result[f"{prefix}_median_pips"] = median
        result[f"{prefix}_p95_pips"] = p95
    return result


def validate_phase8b_spread_reference(
    reference: Mapping[str, object],
) -> None:
    if reference.get("protocol") != PHASE8B_SPREAD_REFERENCE_PROTOCOL:
        raise ValueError("Phase 8B spread-reference protocol mismatch")
    if (
        reference.get("contract_decision")
        != PHASE8B_ACCEPTANCE_CONTRACT_DECISION
    ):
        raise ValueError("Phase 8B spread-reference contract mismatch")
    _validate_fingerprint(
        reference,
        field="spread_reference_fingerprint",
    )
    for field in (
        "capture_preflight_fingerprint",
        "champion_set_fingerprint",
    ):
        _validate_sha256(
            reference.get(field),
            field=f"Phase 8B spread-reference {field}",
        )
    symbols = _string_list(
        reference.get("required_symbols"),
        field="Phase 8B spread-reference required_symbols",
        nonempty=True,
        sorted_required=True,
    )
    _validate_slippage(
        reference.get("slippage_scenarios"),
        field="Phase 8B spread-reference slippage_scenarios",
    )
    if reference.get("source_label") != "RETROSPECTIVE_ALREADY_SEEN":
        raise ValueError("Phase 8B spread-reference source label mismatch")
    per_symbol = reference.get("per_symbol")
    if not isinstance(per_symbol, Mapping) or set(per_symbol) != set(symbols):
        raise ValueError("Phase 8B spread-reference symbol coverage mismatch")
    for symbol in symbols:
        _validate_spread_row(
            per_symbol[symbol],
            field=f"Phase 8B spread-reference {symbol}",
            require_samples=True,
        )


def _validate_scenario_row(
    row: object,
    *,
    field: str,
) -> dict[str, object]:
    if not isinstance(row, Mapping):
        raise ValueError(f"{field} must be an object")
    return {
        "trade_count": _nonnegative_int(
            row.get("trade_count"),
            field=f"{field}.trade_count",
        ),
        "net_return": _finite_number(
            row.get("net_return"),
            field=f"{field}.net_return",
        ),
        "expectancy_usd": _optional_finite_number(
            row.get("expectancy_usd"),
            field=f"{field}.expectancy_usd",
        ),
        "profit_factor": _optional_finite_number(
            row.get("profit_factor"),
            field=f"{field}.profit_factor",
            nonnegative=True,
        ),
        "max_drawdown_fraction": _finite_number(
            row.get("max_drawdown_fraction"),
            field=f"{field}.max_drawdown_fraction",
            nonnegative=True,
        ),
    }


def validate_phase8b_campaign_evidence(
    evidence: Mapping[str, object],
) -> None:
    if evidence.get("protocol") != PHASE8B_CAMPAIGN_EVIDENCE_PROTOCOL:
        raise ValueError("Phase 8B campaign-evidence protocol mismatch")
    if (
        evidence.get("contract_decision")
        != PHASE8B_ACCEPTANCE_CONTRACT_DECISION
    ):
        raise ValueError("Phase 8B campaign-evidence contract mismatch")
    if evidence.get("prospective_evidence") is not True:
        raise ValueError("Phase 8B campaign evidence must be prospective")
    if evidence.get("prospective_segment_closed") is not True:
        raise ValueError("Phase 8B campaign evidence must be closed")

    # Authenticate the exact evidence bytes/structure before evaluating any
    # derived cross-field consistency so mutations fail at the immutable
    # boundary rather than surfacing as a secondary accounting error.
    _validate_fingerprint(
        evidence,
        field="campaign_evidence_fingerprint",
    )

    for field in (
        "capture_preflight_fingerprint",
        "segment_fingerprint",
        "replay_fingerprint",
        "champion_set_fingerprint",
    ):
        _validate_sha256(
            evidence.get(field),
            field=f"Phase 8B campaign-evidence {field}",
        )

    strategies = _string_list(
        evidence.get("strategy_fingerprints"),
        field="Phase 8B campaign-evidence strategy_fingerprints",
        nonempty=True,
        sorted_required=True,
    )
    for item in strategies:
        _validate_sha256(
            item,
            field="Phase 8B campaign-evidence strategy fingerprint",
        )
    symbols = _string_list(
        evidence.get("required_symbols"),
        field="Phase 8B campaign-evidence required_symbols",
        nonempty=True,
        sorted_required=True,
    )
    _validate_slippage(
        evidence.get("slippage_scenarios"),
        field="Phase 8B campaign-evidence slippage_scenarios",
    )

    campaign_start = _parse_utc(
        evidence.get("campaign_start_utc"),
        field="Phase 8B campaign start",
    )
    first = _parse_utc(
        evidence.get("first_observation_utc"),
        field="Phase 8B first observation",
    )
    last = _parse_utc(
        evidence.get("last_observation_utc"),
        field="Phase 8B last observation",
    )
    if first < campaign_start:
        raise ValueError("Phase 8B first observation precedes campaign start")
    if last < first:
        raise ValueError("Phase 8B last observation precedes first observation")

    denominator = _validate_dates(
        evidence.get("denominator_london_dates"),
        field="Phase 8B denominator_london_dates",
    )
    complete = _validate_dates(
        evidence.get("complete_london_dates"),
        field="Phase 8B complete_london_dates",
    )
    if not denominator:
        raise ValueError("Phase 8B denominator London dates are empty")
    if not set(complete).issubset(set(denominator)):
        raise ValueError("Phase 8B complete London dates are outside denominator")

    trades = _nonnegative_int(
        evidence.get("completed_trade_count_0_2"),
        field="Phase 8B completed_trade_count_0_2",
    )
    _require_bool(
        evidence.get("same_candidate_sequence_all_scenarios"),
        field="Phase 8B same_candidate_sequence_all_scenarios",
    )
    _require_bool(
        evidence.get("replay_match"),
        field="Phase 8B replay_match",
    )

    safety = evidence.get("structural_safety")
    if not isinstance(safety, Mapping):
        raise ValueError("Phase 8B structural_safety is malformed")
    expected_safety = {
        "no_order_surface",
        "quote_only_bridge",
        "zero_demo_orders",
        "zero_live_orders",
        "zero_broker_mutations",
        "zero_real_money_actions",
    }
    if set(safety) != expected_safety:
        raise ValueError("Phase 8B structural_safety fields mismatch")
    for field in sorted(expected_safety):
        _require_bool(
            safety.get(field),
            field=f"Phase 8B structural_safety.{field}",
        )

    integrity = evidence.get("integrity")
    if not isinstance(integrity, Mapping):
        raise ValueError("Phase 8B integrity evidence is malformed")
    _nonnegative_int(
        integrity.get("malformed_silently_accepted_count"),
        field="Phase 8B malformed_silently_accepted_count",
    )
    _nonnegative_int(
        integrity.get("stale_gap_trades_in_financial_metrics_count"),
        field="Phase 8B stale_gap_trades_in_financial_metrics_count",
    )
    _require_bool(
        integrity.get("all_operational_events_logged"),
        field="Phase 8B all_operational_events_logged",
    )

    timing = evidence.get("timing")
    if not isinstance(timing, Mapping):
        raise ValueError("Phase 8B timing evidence is malformed")
    _finite_number(
        timing.get("p99_processing_latency_ms"),
        field="Phase 8B p99_processing_latency_ms",
        nonnegative=True,
    )
    _nonnegative_int(
        timing.get("entry_deadline_violation_count"),
        field="Phase 8B entry_deadline_violation_count",
    )
    _nonnegative_int(
        timing.get("scheduled_exit_deadline_violation_count"),
        field="Phase 8B scheduled_exit_deadline_violation_count",
    )

    scenarios = evidence.get("scenarios")
    if not isinstance(scenarios, Mapping) or set(scenarios) != {
        "0.2",
        "0.5",
        "1.0",
    }:
        raise ValueError("Phase 8B scenario evidence coverage mismatch")
    scenario_rows = {
        key: _validate_scenario_row(
            scenarios[key],
            field=f"Phase 8B scenario {key}",
        )
        for key in ("0.2", "0.5", "1.0")
    }
    if scenario_rows["0.2"]["trade_count"] != trades:
        raise ValueError("Phase 8B 0.2-pip trade count mismatch")

    representation = evidence.get("representation")
    if not isinstance(representation, Mapping):
        raise ValueError("Phase 8B representation evidence is malformed")
    _string_list(
        representation.get("strategy_families_with_completed_trades"),
        field="Phase 8B represented strategy families",
        sorted_required=True,
    )
    pairs = _string_list(
        representation.get("pairs_with_completed_trades"),
        field="Phase 8B represented pairs",
        sorted_required=True,
    )
    if not set(pairs).issubset(set(symbols)):
        raise ValueError("Phase 8B represented pair is not required")

    spreads = evidence.get("live_spread_by_symbol")
    if not isinstance(spreads, Mapping) or set(spreads) != set(symbols):
        raise ValueError("Phase 8B live spread symbol coverage mismatch")
    for symbol in symbols:
        _validate_spread_row(
            spreads[symbol],
            field=f"Phase 8B live spread {symbol}",
            require_samples=False,
        )

    for field in (
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_execution_authorized",
    ):
        if evidence.get(field) is not False:
            raise ValueError(f"Phase 8B campaign evidence requires {field}=false")



def _safety_passes(evidence: Mapping[str, object]) -> bool:
    safety = evidence["structural_safety"]
    assert isinstance(safety, Mapping)
    return all(value is True for value in safety.values())


def _minimums(
    evidence: Mapping[str, object],
) -> dict[str, object]:
    first = _parse_utc(
        evidence["first_observation_utc"],
        field="Phase 8B first observation",
    )
    last = _parse_utc(
        evidence["last_observation_utc"],
        field="Phase 8B last observation",
    )
    elapsed_weeks = (last - first).total_seconds() / (7 * 24 * 60 * 60)
    complete = evidence["complete_london_dates"]
    representation = evidence["representation"]
    assert isinstance(complete, list)
    assert isinstance(representation, Mapping)
    families = representation["strategy_families_with_completed_trades"]
    pairs = representation["pairs_with_completed_trades"]
    assert isinstance(families, list)
    assert isinstance(pairs, list)
    trades = int(evidence["completed_trade_count_0_2"])
    return {
        "elapsed_weeks": elapsed_weeks,
        "elapsed_weeks_pass": elapsed_weeks >= MIN_ELAPSED_WEEKS,
        "complete_london_dates": len(complete),
        "complete_london_dates_pass": len(complete)
        >= MIN_COMPLETE_LONDON_DATES,
        "completed_trade_count_0_2": trades,
        "completed_trade_count_pass": trades >= MIN_COMPLETED_TRADES,
        "represented_strategy_family_count": len(families),
        "represented_strategy_family_count_pass": len(families)
        >= MIN_REPRESENTED_FAMILIES,
        "represented_pair_count": len(pairs),
        "represented_pair_count_pass": len(pairs)
        >= MIN_REPRESENTED_PAIRS,
    }


def _minimums_pass(result: Mapping[str, object]) -> bool:
    return all(
        result[field] is True
        for field in (
            "elapsed_weeks_pass",
            "complete_london_dates_pass",
            "completed_trade_count_pass",
            "represented_strategy_family_count_pass",
            "represented_pair_count_pass",
        )
    )


def _operational_gate(
    evidence: Mapping[str, object],
) -> dict[str, object]:
    denominator = evidence["denominator_london_dates"]
    complete = evidence["complete_london_dates"]
    assert isinstance(denominator, list)
    assert isinstance(complete, list)
    coverage = len(complete) / len(denominator)
    integrity = evidence["integrity"]
    timing = evidence["timing"]
    assert isinstance(integrity, Mapping)
    assert isinstance(timing, Mapping)
    checks = {
        "coverage_fraction": coverage,
        "coverage_pass": coverage >= MIN_COVERAGE_FRACTION,
        "malformed_silent_accept_pass": (
            integrity["malformed_silently_accepted_count"] == 0
        ),
        "stale_gap_financial_exclusion_pass": (
            integrity["stale_gap_trades_in_financial_metrics_count"] == 0
        ),
        "operational_event_logging_pass": (
            integrity["all_operational_events_logged"] is True
        ),
        "same_candidate_sequence_pass": (
            evidence["same_candidate_sequence_all_scenarios"] is True
        ),
        "replay_pass": evidence["replay_match"] is True,
        "processing_latency_pass": (
            float(timing["p99_processing_latency_ms"])
            <= MAX_P99_PROCESSING_LATENCY_MS
        ),
        "entry_deadline_pass": timing["entry_deadline_violation_count"] == 0,
        "scheduled_exit_deadline_pass": (
            timing["scheduled_exit_deadline_violation_count"] == 0
        ),
    }
    checks["pass"] = all(
        checks[field] is True
        for field in (
            "coverage_pass",
            "malformed_silent_accept_pass",
            "stale_gap_financial_exclusion_pass",
            "operational_event_logging_pass",
            "same_candidate_sequence_pass",
            "replay_pass",
            "processing_latency_pass",
            "entry_deadline_pass",
            "scheduled_exit_deadline_pass",
        )
    )
    return checks


def _spread_gate(
    evidence: Mapping[str, object],
    reference: Mapping[str, object],
) -> dict[str, object]:
    live = evidence["live_spread_by_symbol"]
    historical = reference["per_symbol"]
    representation = evidence["representation"]
    assert isinstance(live, Mapping)
    assert isinstance(historical, Mapping)
    assert isinstance(representation, Mapping)
    represented_pairs = set(
        representation["pairs_with_completed_trades"]  # type: ignore[arg-type]
    )
    rows: dict[str, dict[str, object]] = {}
    overall = True
    for symbol in evidence["required_symbols"]:  # type: ignore[assignment]
        live_row = _validate_spread_row(
            live[symbol],
            field=f"Phase 8B live spread {symbol}",
            require_samples=False,
        )
        reference_row = _validate_spread_row(
            historical[symbol],
            field=f"Phase 8B spread-reference {symbol}",
            require_samples=True,
        )
        entry_count = int(live_row["entry_sample_count"])
        exit_count = int(live_row["exit_sample_count"])
        if symbol in represented_pairs and (entry_count == 0 or exit_count == 0):
            passes = False
        elif entry_count == 0 and exit_count == 0:
            passes = True
        else:
            passes = (
                live_row["entry_median_pips"]
                <= reference_row["entry_median_pips"] + SPREAD_TOLERANCE_PIPS
                and live_row["entry_p95_pips"]
                <= reference_row["entry_p95_pips"] + SPREAD_TOLERANCE_PIPS
                and live_row["exit_median_pips"]
                <= reference_row["exit_median_pips"] + SPREAD_TOLERANCE_PIPS
                and live_row["exit_p95_pips"]
                <= reference_row["exit_p95_pips"] + SPREAD_TOLERANCE_PIPS
            )
        overall = overall and bool(passes)
        rows[str(symbol)] = {
            "pass": bool(passes),
            "entry_sample_count": entry_count,
            "exit_sample_count": exit_count,
            "entry_median_limit_pips": (
                reference_row["entry_median_pips"] + SPREAD_TOLERANCE_PIPS
            ),
            "entry_p95_limit_pips": (
                reference_row["entry_p95_pips"] + SPREAD_TOLERANCE_PIPS
            ),
            "exit_median_limit_pips": (
                reference_row["exit_median_pips"] + SPREAD_TOLERANCE_PIPS
            ),
            "exit_p95_limit_pips": (
                reference_row["exit_p95_pips"] + SPREAD_TOLERANCE_PIPS
            ),
        }
    return {"pass": overall, "per_symbol": rows}


def _financial_gate(
    evidence: Mapping[str, object],
) -> dict[str, object]:
    scenarios = evidence["scenarios"]
    assert isinstance(scenarios, Mapping)
    rows: dict[str, dict[str, object]] = {}
    overall = True
    for key in ("0.2", "0.5"):
        row = _validate_scenario_row(
            scenarios[key],
            field=f"Phase 8B scenario {key}",
        )
        expectancy = row["expectancy_usd"]
        profit_factor = row["profit_factor"]
        passes = (
            row["net_return"] > 0
            and expectancy is not None
            and expectancy > 0
            and profit_factor is not None
            and profit_factor > 1.0
            and row["max_drawdown_fraction"] <= MAX_DRAWDOWN_FRACTION
        )
        overall = overall and bool(passes)
        rows[key] = {
            "pass": bool(passes),
            "trade_count": row["trade_count"],
            "net_return": row["net_return"],
            "expectancy_usd": expectancy,
            "profit_factor": profit_factor,
            "max_drawdown_fraction": row["max_drawdown_fraction"],
        }
    diagnostic = _validate_scenario_row(
        scenarios["1.0"],
        field="Phase 8B scenario 1.0",
    )
    rows["1.0"] = {
        "diagnostic_only": True,
        **diagnostic,
    }
    return {"pass": overall, "per_scenario": rows}


def compile_phase8b_acceptance(
    *,
    campaign_evidence: Mapping[str, object],
    spread_reference: Mapping[str, object],
    code_commit: str,
) -> dict[str, object]:
    validate_phase8b_campaign_evidence(campaign_evidence)
    validate_phase8b_spread_reference(spread_reference)
    commit = _validate_commit(
        code_commit,
        field="Phase 8B acceptance code commit",
    )

    for field in (
        "capture_preflight_fingerprint",
        "champion_set_fingerprint",
        "required_symbols",
        "slippage_scenarios",
    ):
        if campaign_evidence.get(field) != spread_reference.get(field):
            raise ValueError(f"Phase 8B acceptance {field} mismatch")

    minimums = _minimums(campaign_evidence)
    operational = _operational_gate(campaign_evidence)
    spread = _spread_gate(campaign_evidence, spread_reference)
    financial = _financial_gate(campaign_evidence)

    if not _safety_passes(campaign_evidence):
        outcome = PHASE8B_REJECT_SAFETY_FAILURE
    elif campaign_evidence["replay_match"] is not True:
        outcome = PHASE8B_REJECT_OPERATIONAL_MISMATCH
    elif not _minimums_pass(minimums):
        outcome = PHASE8B_NEED_MORE_DATA
    elif operational["pass"] is not True:
        outcome = PHASE8B_REJECT_OPERATIONAL_MISMATCH
    elif spread["pass"] is not True:
        outcome = PHASE8B_REJECT_MARKET_MISMATCH
    elif financial["pass"] is not True:
        outcome = PHASE8B_REJECT_FINANCIAL_MISMATCH
    else:
        outcome = PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN

    passed = outcome == PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN
    payload = {
        "protocol": PHASE8B_ACCEPTANCE_PROTOCOL,
        "experiment_id": PHASE8B_ACCEPTANCE_EXPERIMENT_ID,
        "contract_decision": PHASE8B_ACCEPTANCE_CONTRACT_DECISION,
        "acceptance_code_commit": commit,
        "campaign_evidence_fingerprint": campaign_evidence[
            "campaign_evidence_fingerprint"
        ],
        "spread_reference_fingerprint": spread_reference[
            "spread_reference_fingerprint"
        ],
        "capture_preflight_fingerprint": campaign_evidence[
            "capture_preflight_fingerprint"
        ],
        "segment_fingerprint": campaign_evidence["segment_fingerprint"],
        "replay_fingerprint": campaign_evidence["replay_fingerprint"],
        "champion_set_fingerprint": campaign_evidence[
            "champion_set_fingerprint"
        ],
        "strategy_fingerprints": list(
            campaign_evidence["strategy_fingerprints"]
        ),
        "required_symbols": list(campaign_evidence["required_symbols"]),
        "outcome": outcome,
        "minimum_evidence": minimums,
        "operational_gate": operational,
        "spread_gate": spread,
        "financial_gate": financial,
        "shadow_validation_authorized": passed,
        "lifecycle_transition_authorized": passed,
        "lifecycle_transitions": (
            [
                {
                    "strategy_fingerprint": fingerprint,
                    "from": "SHADOW_CANDIDATE",
                    "to": "SHADOW_VALIDATED",
                }
                for fingerprint in campaign_evidence[
                    "strategy_fingerprints"
                ]
            ]
            if passed
            else []
        ),
        "demo_design_eligible": passed,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
    }
    return payload | {
        "acceptance_fingerprint": _canonical_digest(payload)
    }


def validate_phase8b_acceptance(
    acceptance: Mapping[str, object],
) -> None:
    if acceptance.get("protocol") != PHASE8B_ACCEPTANCE_PROTOCOL:
        raise ValueError("Phase 8B acceptance protocol mismatch")
    if acceptance.get("experiment_id") != PHASE8B_ACCEPTANCE_EXPERIMENT_ID:
        raise ValueError("Phase 8B acceptance experiment mismatch")
    if (
        acceptance.get("contract_decision")
        != PHASE8B_ACCEPTANCE_CONTRACT_DECISION
    ):
        raise ValueError("Phase 8B acceptance contract mismatch")
    _validate_commit(
        acceptance.get("acceptance_code_commit"),
        field="Phase 8B acceptance code commit",
    )
    for field in (
        "campaign_evidence_fingerprint",
        "spread_reference_fingerprint",
        "capture_preflight_fingerprint",
        "segment_fingerprint",
        "replay_fingerprint",
        "champion_set_fingerprint",
    ):
        _validate_sha256(
            acceptance.get(field),
            field=f"Phase 8B acceptance {field}",
        )
    strategies = _string_list(
        acceptance.get("strategy_fingerprints"),
        field="Phase 8B acceptance strategy_fingerprints",
        nonempty=True,
        sorted_required=True,
    )
    for fingerprint in strategies:
        _validate_sha256(
            fingerprint,
            field="Phase 8B acceptance strategy fingerprint",
        )
    _string_list(
        acceptance.get("required_symbols"),
        field="Phase 8B acceptance required_symbols",
        nonempty=True,
        sorted_required=True,
    )
    outcomes = {
        PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
        PHASE8B_NEED_MORE_DATA,
        PHASE8B_REJECT_OPERATIONAL_MISMATCH,
        PHASE8B_REJECT_MARKET_MISMATCH,
        PHASE8B_REJECT_FINANCIAL_MISMATCH,
        PHASE8B_REJECT_SAFETY_FAILURE,
    }
    if acceptance.get("outcome") not in outcomes:
        raise ValueError("Phase 8B acceptance outcome is invalid")
    passed = (
        acceptance.get("outcome")
        == PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN
    )
    for field in (
        "shadow_validation_authorized",
        "lifecycle_transition_authorized",
        "demo_design_eligible",
    ):
        if acceptance.get(field) is not passed:
            raise ValueError(f"Phase 8B acceptance {field} mismatch")
    transitions = acceptance.get("lifecycle_transitions")
    if not isinstance(transitions, list):
        raise ValueError("Phase 8B acceptance lifecycle transitions malformed")
    if passed:
        if [row.get("strategy_fingerprint") for row in transitions] != strategies:
            raise ValueError("Phase 8B acceptance lifecycle identity mismatch")
        if any(
            row.get("from") != "SHADOW_CANDIDATE"
            or row.get("to") != "SHADOW_VALIDATED"
            for row in transitions
        ):
            raise ValueError("Phase 8B acceptance lifecycle transition mismatch")
    elif transitions:
        raise ValueError("Phase 8B non-PASS cannot authorize lifecycle transition")
    for field in (
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_execution_authorized",
    ):
        if acceptance.get(field) is not False:
            raise ValueError(f"Phase 8B acceptance requires {field}=false")
    _validate_fingerprint(
        acceptance,
        field="acceptance_fingerprint",
    )


def write_phase8b_acceptance_artifacts(
    acceptance: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    validate_phase8b_acceptance(acceptance)
    root = Path(out_dir)
    result_path = root / "acceptance.json"
    manifest_path = root / "manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError("Phase 8B acceptance artifacts already exist")
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(acceptance))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE8B_ACCEPTANCE_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE8B_ACCEPTANCE_EXPERIMENT_ID,
        "outcome": acceptance["outcome"],
        "shadow_validation_authorized": acceptance[
            "shadow_validation_authorized"
        ],
        "demo_design_eligible": acceptance["demo_design_eligible"],
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
        "artifacts": [
            {
                "path": result_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(manifest_path, _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "MAX_DRAWDOWN_FRACTION",
    "MAX_P99_PROCESSING_LATENCY_MS",
    "MIN_COMPLETE_LONDON_DATES",
    "MIN_COMPLETED_TRADES",
    "MIN_COVERAGE_FRACTION",
    "MIN_ELAPSED_WEEKS",
    "MIN_REPRESENTED_FAMILIES",
    "MIN_REPRESENTED_PAIRS",
    "PHASE8B_ACCEPTANCE_ARTIFACT_PROTOCOL",
    "PHASE8B_ACCEPTANCE_EXPERIMENT_ID",
    "PHASE8B_ACCEPTANCE_PROTOCOL",
    "PHASE8B_CAMPAIGN_EVIDENCE_PROTOCOL",
    "PHASE8B_NEED_MORE_DATA",
    "PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN",
    "PHASE8B_REJECT_FINANCIAL_MISMATCH",
    "PHASE8B_REJECT_MARKET_MISMATCH",
    "PHASE8B_REJECT_OPERATIONAL_MISMATCH",
    "PHASE8B_REJECT_SAFETY_FAILURE",
    "PHASE8B_SPREAD_REFERENCE_PROTOCOL",
    "SPREAD_TOLERANCE_PIPS",
    "compile_phase8b_acceptance",
    "validate_phase8b_acceptance",
    "validate_phase8b_campaign_evidence",
    "validate_phase8b_spread_reference",
    "write_phase8b_acceptance_artifacts",
]
