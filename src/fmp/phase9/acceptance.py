from __future__ import annotations

import hashlib
import json
import math
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping, Sequence

from fmp.phase9.design import validate_phase9_demo_design


PHASE9_DEMO_CAMPAIGN_EVIDENCE_PROTOCOL = (
    "fmp-phase9-demo-campaign-evidence-v1"
)
PHASE9_DEMO_ACCEPTANCE_PROTOCOL = "fmp-phase9-demo-acceptance-v1"
PHASE9_DEMO_ACCEPTANCE_ARTIFACT_PROTOCOL = (
    "fmp-phase9-demo-acceptance-artifacts-v1"
)
PHASE9_DEMO_ACCEPTANCE_DECISION = "DEC-066"
PHASE9_DEMO_ACCEPTANCE_EXPERIMENT_ID = "EXP-20260922-037"

PHASE9_DEMO_NEED_MORE_DATA = "PHASE9_DEMO_NEED_MORE_DATA"
PHASE9_DEMO_REJECT_SAFETY_FAILURE = (
    "PHASE9_DEMO_REJECT_SAFETY_FAILURE"
)
PHASE9_DEMO_REJECT_OPERATIONAL_MISMATCH = (
    "PHASE9_DEMO_REJECT_OPERATIONAL_MISMATCH"
)
PHASE9_DEMO_REJECT_EXECUTION_COST_MISMATCH = (
    "PHASE9_DEMO_REJECT_EXECUTION_COST_MISMATCH"
)
PHASE9_DEMO_PASS_ELIGIBLE_FOR_DEPLOYMENT_REVIEW = (
    "PHASE9_DEMO_PASS_ELIGIBLE_FOR_DEPLOYMENT_REVIEW"
)

MIN_COMPLETED_TRADES = 40
MIN_ELAPSED_WEEKS = 8
MIN_DEMO_SESSION_DATES = 30
MIN_REPRESENTED_FAMILIES = 2
MIN_REPRESENTED_PAIRS = 2
MAX_MEDIAN_ADVERSE_SLIPPAGE_PIPS = 0.5
MAX_P95_ADVERSE_SLIPPAGE_PIPS = 1.0

_V1_PAIRS = frozenset({"EURUSD", "GBPUSD", "USDJPY"})
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
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


def _sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _nonnegative_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _finite(
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


def _utc(value: object, *, field: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise ValueError(f"{field} must use UTC")
    return value


def _utc_string(value: datetime) -> str:
    _utc(value, field="timestamp")
    return value.isoformat().replace("+00:00", "Z")


def _parse_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp") from exc
    return _utc(parsed, field=field)


def _sorted_strings(
    value: Sequence[str],
    *,
    field: str,
) -> list[str]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{field} must be a sequence")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError(f"{field} contains invalid value")
        result.append(item)
    if len(set(result)) != len(result):
        raise ValueError(f"{field} contains duplicates")
    return sorted(result)


def _validated_dates(value: Sequence[str]) -> list[str]:
    dates = _sorted_strings(value, field="Phase 9 demo-session dates")
    for item in dates:
        if not _DATE_RE.fullmatch(item):
            raise ValueError("Phase 9 demo-session date is malformed")
        try:
            datetime.fromisoformat(item)
        except ValueError as exc:
            raise ValueError("Phase 9 demo-session date is invalid") from exc
    return dates


def _design_identities(
    design: Mapping[str, object],
) -> tuple[Mapping[str, object], list[str], set[str], set[str]]:
    validate_phase9_demo_design(design)
    execution = design.get("execution_path")
    if not isinstance(execution, Mapping):
        raise ValueError("Phase 9 demo execution path is malformed")
    if execution.get("account_mode") != "DEMO":
        raise ValueError("Phase 9 demo acceptance requires DEMO account")

    fingerprints = design.get("strategy_fingerprints")
    strategies = design.get("strategies")
    if not isinstance(fingerprints, list) or not isinstance(strategies, list):
        raise ValueError("Phase 9 demo strategy identities are malformed")
    frozen_fingerprints = sorted(
        _sha256(item, field="Phase 9 strategy fingerprint")
        for item in fingerprints
    )
    families: set[str] = set()
    pairs: set[str] = set()
    for row in strategies:
        if not isinstance(row, Mapping):
            raise ValueError("Phase 9 demo strategy row is malformed")
        family = row.get("family")
        symbol = row.get("symbol")
        if not isinstance(family, str) or not family:
            raise ValueError("Phase 9 demo strategy family is malformed")
        if not isinstance(symbol, str) or symbol not in _V1_PAIRS:
            raise ValueError("Phase 9 demo strategy symbol is invalid")
        families.add(family)
        pairs.add(symbol)
    return execution, frozen_fingerprints, families, pairs


def _normalize_slippage(
    value: Mapping[str, object],
) -> dict[str, dict[str, object]]:
    if not isinstance(value, Mapping):
        raise ValueError("Phase 9 demo slippage summary must be an object")
    result: dict[str, dict[str, object]] = {}
    for pair, raw in value.items():
        if not isinstance(pair, str) or pair not in _V1_PAIRS:
            raise ValueError("Phase 9 demo slippage pair is invalid")
        if not isinstance(raw, Mapping):
            raise ValueError("Phase 9 demo slippage row is malformed")
        count = _nonnegative_int(
            raw.get("sample_count"),
            field=f"Phase 9 {pair} slippage sample count",
        )
        median_raw = raw.get("median_adverse_entry_slippage_pips")
        p95_raw = raw.get("p95_adverse_entry_slippage_pips")
        if count == 0:
            if median_raw is not None or p95_raw is not None:
                raise ValueError(
                    f"Phase 9 {pair} zero-sample slippage must use null metrics"
                )
            median = None
            p95 = None
        else:
            median = _finite(
                median_raw,
                field=f"Phase 9 {pair} median adverse slippage",
                nonnegative=True,
            )
            p95 = _finite(
                p95_raw,
                field=f"Phase 9 {pair} p95 adverse slippage",
                nonnegative=True,
            )
            if p95 < median:
                raise ValueError(
                    f"Phase 9 {pair} p95 slippage cannot be below median"
                )
        result[pair] = {
            "sample_count": count,
            "median_adverse_entry_slippage_pips": median,
            "p95_adverse_entry_slippage_pips": p95,
        }
    return dict(sorted(result.items()))


def build_phase9_demo_campaign_evidence(
    *,
    design: Mapping[str, object],
    first_observation_utc: datetime,
    last_observation_utc: datetime,
    demo_session_dates: Sequence[str],
    completed_trade_count: int,
    represented_strategy_families: Sequence[str],
    represented_pairs: Sequence[str],
    order_attempt_count: int,
    completed_send_count: int,
    broker_noncompleted_send_count: int,
    ambiguous_send_count: int,
    retry_after_send_attempt_count: int,
    duplicate_client_order_count: int,
    completed_send_without_protective_stop_count: int,
    startup_reconciliation_failure_count: int,
    post_send_reconciliation_failure_count: int,
    practice_account_assertion_failure_count: int,
    daily_halt_violation_count: int,
    journal_integrity_failure_count: int,
    unauthorized_broker_mutation_count: int,
    live_order_count: int,
    real_money_access_count: int,
    restart_recovery_drill_count: int,
    restart_recovery_failure_count: int,
    requested_vs_fill_missing_count: int,
    slippage_by_pair: Mapping[str, object],
    financial_metrics: Mapping[str, object],
    equity_series_fingerprint: str,
    code_commit: str,
) -> dict[str, object]:
    execution, strategy_fingerprints, allowed_families, allowed_pairs = (
        _design_identities(design)
    )
    start = _utc(
        first_observation_utc,
        field="Phase 9 first demo observation",
    )
    end = _utc(
        last_observation_utc,
        field="Phase 9 last demo observation",
    )
    if end < start:
        raise ValueError("Phase 9 last demo observation precedes first")
    dates = _validated_dates(demo_session_dates)
    families = _sorted_strings(
        represented_strategy_families,
        field="Phase 9 represented strategy families",
    )
    pairs = _sorted_strings(
        represented_pairs,
        field="Phase 9 represented pairs",
    )
    if not set(families).issubset(allowed_families):
        raise ValueError("Phase 9 represented strategy family is not frozen")
    if not set(pairs).issubset(allowed_pairs):
        raise ValueError("Phase 9 represented pair is not in frozen champion")

    counts = {
        "completed_trade_count": completed_trade_count,
        "order_attempt_count": order_attempt_count,
        "completed_send_count": completed_send_count,
        "broker_noncompleted_send_count": broker_noncompleted_send_count,
        "ambiguous_send_count": ambiguous_send_count,
        "retry_after_send_attempt_count": retry_after_send_attempt_count,
        "duplicate_client_order_count": duplicate_client_order_count,
        "completed_send_without_protective_stop_count": (
            completed_send_without_protective_stop_count
        ),
        "startup_reconciliation_failure_count": (
            startup_reconciliation_failure_count
        ),
        "post_send_reconciliation_failure_count": (
            post_send_reconciliation_failure_count
        ),
        "practice_account_assertion_failure_count": (
            practice_account_assertion_failure_count
        ),
        "daily_halt_violation_count": daily_halt_violation_count,
        "journal_integrity_failure_count": journal_integrity_failure_count,
        "unauthorized_broker_mutation_count": unauthorized_broker_mutation_count,
        "live_order_count": live_order_count,
        "real_money_access_count": real_money_access_count,
        "restart_recovery_drill_count": restart_recovery_drill_count,
        "restart_recovery_failure_count": restart_recovery_failure_count,
        "requested_vs_fill_missing_count": requested_vs_fill_missing_count,
    }
    normalized_counts = {
        field: _nonnegative_int(value, field=f"Phase 9 {field}")
        for field, value in counts.items()
    }
    normalized_slippage = _normalize_slippage(slippage_by_pair)
    if not isinstance(financial_metrics, Mapping):
        raise ValueError("Phase 9 financial metrics must be an object")
    metrics = dict(financial_metrics)
    for field in (
        "demo_net_return",
        "expectancy_per_completed_trade",
        "profit_factor",
        "maximum_drawdown_fraction",
    ):
        if field not in metrics:
            raise ValueError(f"Phase 9 financial metrics missing {field}")
        _finite(
            metrics[field],
            field=f"Phase 9 financial metric {field}",
            nonnegative=field in {"profit_factor", "maximum_drawdown_fraction"},
        )

    commit = _commit(
        code_commit,
        field="Phase 9 demo evidence builder code commit",
    )
    equity_fp = _sha256(
        equity_series_fingerprint,
        field="Phase 9 equity-series fingerprint",
    )
    account_fp = _sha256(
        execution.get("account_fingerprint"),
        field="Phase 9 demo account fingerprint",
    )
    server = execution.get("server")
    if not isinstance(server, str) or not server:
        raise ValueError("Phase 9 demo server is malformed")

    payload = {
        "protocol": PHASE9_DEMO_CAMPAIGN_EVIDENCE_PROTOCOL,
        "experiment_id": PHASE9_DEMO_ACCEPTANCE_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_ACCEPTANCE_DECISION,
        "demo_campaign_evidence_builder_code_commit": commit,
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "strategy_fingerprints": strategy_fingerprints,
        "account_fingerprint": account_fp,
        "server": server,
        "practice_only": True,
        "first_observation_utc": _utc_string(start),
        "last_observation_utc": _utc_string(end),
        "demo_session_dates": dates,
        "represented_strategy_families": families,
        "represented_pairs": pairs,
        **normalized_counts,
        "slippage_by_pair": normalized_slippage,
        "financial_metrics": metrics,
        "equity_series_fingerprint": equity_fp,
        "demo_execution_source_armed": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_decision_authorized": False,
        "phase11_authorized": False,
    }
    result = payload | {"demo_campaign_evidence_fingerprint": _digest(payload)}
    validate_phase9_demo_campaign_evidence(result, design=design)
    return result


def validate_phase9_demo_campaign_evidence(
    value: Mapping[str, object],
    *,
    design: Mapping[str, object],
) -> None:
    execution, strategy_fingerprints, allowed_families, allowed_pairs = (
        _design_identities(design)
    )
    if value.get("protocol") != PHASE9_DEMO_CAMPAIGN_EVIDENCE_PROTOCOL:
        raise ValueError("Phase 9 demo-campaign evidence protocol mismatch")
    if value.get("experiment_id") != PHASE9_DEMO_ACCEPTANCE_EXPERIMENT_ID:
        raise ValueError("Phase 9 demo-campaign evidence experiment mismatch")
    if value.get("decision") != PHASE9_DEMO_ACCEPTANCE_DECISION:
        raise ValueError("Phase 9 demo-campaign evidence decision mismatch")
    _commit(
        value.get("demo_campaign_evidence_builder_code_commit"),
        field="Phase 9 demo evidence builder code commit",
    )

    identities = {
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "strategy_fingerprints": strategy_fingerprints,
        "account_fingerprint": execution["account_fingerprint"],
        "server": execution["server"],
    }
    for field, expected in identities.items():
        if value.get(field) != expected:
            raise ValueError(f"Phase 9 demo-campaign {field} mismatch")
    for field in (
        "demo_design_fingerprint",
        "champion_set_fingerprint",
        "account_fingerprint",
        "equity_series_fingerprint",
        "demo_campaign_evidence_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 demo-campaign {field}")
    if value.get("practice_only") is not True:
        raise ValueError("Phase 9 demo campaign must be practice-only")

    start = _parse_utc(
        value.get("first_observation_utc"),
        field="Phase 9 first demo observation",
    )
    end = _parse_utc(
        value.get("last_observation_utc"),
        field="Phase 9 last demo observation",
    )
    if end < start:
        raise ValueError("Phase 9 demo observation range is reversed")

    dates_raw = value.get("demo_session_dates")
    families_raw = value.get("represented_strategy_families")
    pairs_raw = value.get("represented_pairs")
    if not isinstance(dates_raw, list):
        raise ValueError("Phase 9 demo-session dates must be a list")
    if not isinstance(families_raw, list):
        raise ValueError("Phase 9 represented families must be a list")
    if not isinstance(pairs_raw, list):
        raise ValueError("Phase 9 represented pairs must be a list")
    dates = _validated_dates(dates_raw)
    families = _sorted_strings(
        families_raw,
        field="Phase 9 represented strategy families",
    )
    pairs = _sorted_strings(
        pairs_raw,
        field="Phase 9 represented pairs",
    )
    if dates != dates_raw or families != families_raw or pairs != pairs_raw:
        raise ValueError("Phase 9 demo evidence lists must be sorted")
    if not set(families).issubset(allowed_families):
        raise ValueError("Phase 9 represented strategy family is not frozen")
    if not set(pairs).issubset(allowed_pairs):
        raise ValueError("Phase 9 represented pair is not in frozen champion")

    count_fields = (
        "completed_trade_count",
        "order_attempt_count",
        "completed_send_count",
        "broker_noncompleted_send_count",
        "ambiguous_send_count",
        "retry_after_send_attempt_count",
        "duplicate_client_order_count",
        "completed_send_without_protective_stop_count",
        "startup_reconciliation_failure_count",
        "post_send_reconciliation_failure_count",
        "practice_account_assertion_failure_count",
        "daily_halt_violation_count",
        "journal_integrity_failure_count",
        "unauthorized_broker_mutation_count",
        "live_order_count",
        "real_money_access_count",
        "restart_recovery_drill_count",
        "restart_recovery_failure_count",
        "requested_vs_fill_missing_count",
    )
    for field in count_fields:
        _nonnegative_int(value.get(field), field=f"Phase 9 {field}")

    slippage = value.get("slippage_by_pair")
    if not isinstance(slippage, Mapping):
        raise ValueError("Phase 9 demo slippage summary must be an object")
    normalized_slippage = _normalize_slippage(slippage)
    if dict(slippage) != normalized_slippage:
        raise ValueError("Phase 9 demo slippage summary is not canonical")

    metrics = value.get("financial_metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("Phase 9 financial metrics must be an object")
    for field in (
        "demo_net_return",
        "expectancy_per_completed_trade",
        "profit_factor",
        "maximum_drawdown_fraction",
    ):
        if field not in metrics:
            raise ValueError(f"Phase 9 financial metrics missing {field}")
        _finite(
            metrics[field],
            field=f"Phase 9 financial metric {field}",
            nonnegative=field in {"profit_factor", "maximum_drawdown_fraction"},
        )

    for field in (
        "demo_execution_source_armed",
        "live_order_authorized",
        "real_money_authorized",
        "phase10_decision_authorized",
        "phase11_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 9 demo campaign requires {field}=false")

    fingerprint = value["demo_campaign_evidence_fingerprint"]
    payload = dict(value)
    payload.pop("demo_campaign_evidence_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 demo-campaign evidence fingerprint mismatch")


def _minimum_checks(evidence: Mapping[str, object]) -> dict[str, object]:
    start = _parse_utc(
        evidence["first_observation_utc"],
        field="Phase 9 first demo observation",
    )
    end = _parse_utc(
        evidence["last_observation_utc"],
        field="Phase 9 last demo observation",
    )
    elapsed_days = (end - start).total_seconds() / 86400.0
    checks = {
        "completed_trades_pass": (
            evidence["completed_trade_count"] >= MIN_COMPLETED_TRADES
        ),
        "elapsed_weeks_pass": elapsed_days >= MIN_ELAPSED_WEEKS * 7,
        "demo_session_dates_pass": (
            len(evidence["demo_session_dates"]) >= MIN_DEMO_SESSION_DATES
        ),
        "strategy_family_representation_pass": (
            len(evidence["represented_strategy_families"])
            >= MIN_REPRESENTED_FAMILIES
        ),
        "pair_representation_pass": (
            len(evidence["represented_pairs"]) >= MIN_REPRESENTED_PAIRS
        ),
    }
    checks["pass"] = all(bool(value) for value in checks.values())
    return checks


def _safety_checks(evidence: Mapping[str, object]) -> dict[str, object]:
    checks = {
        "practice_account_pass": (
            evidence["practice_account_assertion_failure_count"] == 0
        ),
        "live_order_pass": evidence["live_order_count"] == 0,
        "real_money_pass": evidence["real_money_access_count"] == 0,
        "unauthorized_mutation_pass": (
            evidence["unauthorized_broker_mutation_count"] == 0
        ),
        "duplicate_client_order_pass": (
            evidence["duplicate_client_order_count"] == 0
        ),
        "no_retry_after_attempt_pass": (
            evidence["retry_after_send_attempt_count"] == 0
        ),
        "protective_stop_pass": (
            evidence["completed_send_without_protective_stop_count"] == 0
        ),
        "daily_halt_pass": evidence["daily_halt_violation_count"] == 0,
    }
    checks["pass"] = all(bool(value) for value in checks.values())
    return checks


def _operational_checks(evidence: Mapping[str, object]) -> dict[str, object]:
    attempts = evidence["order_attempt_count"]
    accounted = (
        evidence["completed_send_count"]
        + evidence["broker_noncompleted_send_count"]
        + evidence["ambiguous_send_count"]
    )
    slippage = evidence["slippage_by_pair"]
    represented_pairs = evidence["represented_pairs"]
    assert isinstance(slippage, Mapping)
    pair_samples = {
        pair: (
            isinstance(slippage.get(pair), Mapping)
            and int(slippage[pair]["sample_count"]) > 0
        )
        for pair in represented_pairs
    }
    checks = {
        "journal_integrity_pass": (
            evidence["journal_integrity_failure_count"] == 0
        ),
        "ambiguity_resolved_pass": evidence["ambiguous_send_count"] == 0,
        "startup_reconciliation_pass": (
            evidence["startup_reconciliation_failure_count"] == 0
        ),
        "post_send_reconciliation_pass": (
            evidence["post_send_reconciliation_failure_count"] == 0
        ),
        "restart_recovery_drill_present": (
            evidence["restart_recovery_drill_count"] >= 1
        ),
        "restart_recovery_pass": (
            evidence["restart_recovery_failure_count"] == 0
        ),
        "attempt_accounting_pass": accounted == attempts,
        "completed_trade_count_pass": (
            evidence["completed_trade_count"]
            <= evidence["completed_send_count"]
        ),
        "requested_vs_fill_pass": (
            evidence["requested_vs_fill_missing_count"] == 0
        ),
        "represented_pair_samples_pass": all(pair_samples.values()),
    }
    checks["represented_pair_sample_checks"] = pair_samples
    checks["pass"] = all(
        bool(value)
        for key, value in checks.items()
        if key != "represented_pair_sample_checks"
    )
    return checks


def _cost_checks(evidence: Mapping[str, object]) -> dict[str, object]:
    slippage = evidence["slippage_by_pair"]
    assert isinstance(slippage, Mapping)
    pair_checks: dict[str, dict[str, object]] = {}
    for pair in evidence["represented_pairs"]:
        row = slippage.get(pair)
        if not isinstance(row, Mapping) or row.get("sample_count", 0) <= 0:
            pair_checks[pair] = {
                "sample_present": False,
                "median_pass": False,
                "p95_pass": False,
                "pass": False,
            }
            continue
        median = float(row["median_adverse_entry_slippage_pips"])
        p95 = float(row["p95_adverse_entry_slippage_pips"])
        pair_checks[pair] = {
            "sample_present": True,
            "median_pass": median <= MAX_MEDIAN_ADVERSE_SLIPPAGE_PIPS,
            "p95_pass": p95 <= MAX_P95_ADVERSE_SLIPPAGE_PIPS,
            "pass": (
                median <= MAX_MEDIAN_ADVERSE_SLIPPAGE_PIPS
                and p95 <= MAX_P95_ADVERSE_SLIPPAGE_PIPS
            ),
        }
    return {
        "pair_checks": pair_checks,
        "pass": bool(pair_checks)
        and all(bool(row["pass"]) for row in pair_checks.values()),
    }


def compile_phase9_demo_acceptance(
    *,
    evidence: Mapping[str, object],
    design: Mapping[str, object],
    code_commit: str,
) -> dict[str, object]:
    validate_phase9_demo_campaign_evidence(evidence, design=design)
    commit = _commit(
        code_commit,
        field="Phase 9 demo acceptance compiler code commit",
    )

    minimum = _minimum_checks(evidence)
    safety = _safety_checks(evidence)
    operational = _operational_checks(evidence)
    cost = _cost_checks(evidence)

    if safety["pass"] is not True:
        outcome = PHASE9_DEMO_REJECT_SAFETY_FAILURE
    elif minimum["pass"] is not True:
        outcome = PHASE9_DEMO_NEED_MORE_DATA
    elif operational["pass"] is not True:
        outcome = PHASE9_DEMO_REJECT_OPERATIONAL_MISMATCH
    elif cost["pass"] is not True:
        outcome = PHASE9_DEMO_REJECT_EXECUTION_COST_MISMATCH
    else:
        outcome = PHASE9_DEMO_PASS_ELIGIBLE_FOR_DEPLOYMENT_REVIEW

    payload = {
        "protocol": PHASE9_DEMO_ACCEPTANCE_PROTOCOL,
        "experiment_id": PHASE9_DEMO_ACCEPTANCE_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_ACCEPTANCE_DECISION,
        "demo_acceptance_compiler_code_commit": commit,
        "demo_campaign_evidence_fingerprint": evidence[
            "demo_campaign_evidence_fingerprint"
        ],
        "demo_design_fingerprint": evidence["demo_design_fingerprint"],
        "champion_set_fingerprint": evidence["champion_set_fingerprint"],
        "account_fingerprint": evidence["account_fingerprint"],
        "server": evidence["server"],
        "thresholds": {
            "min_completed_trades": MIN_COMPLETED_TRADES,
            "min_elapsed_weeks": MIN_ELAPSED_WEEKS,
            "min_demo_session_dates": MIN_DEMO_SESSION_DATES,
            "min_represented_strategy_families": MIN_REPRESENTED_FAMILIES,
            "min_represented_pairs": MIN_REPRESENTED_PAIRS,
            "max_median_adverse_entry_slippage_pips": (
                MAX_MEDIAN_ADVERSE_SLIPPAGE_PIPS
            ),
            "max_p95_adverse_entry_slippage_pips": (
                MAX_P95_ADVERSE_SLIPPAGE_PIPS
            ),
        },
        "minimum_evidence_checks": minimum,
        "safety_checks": safety,
        "operational_checks": operational,
        "execution_cost_checks": cost,
        "financial_metrics_diagnostic": dict(evidence["financial_metrics"]),
        "outcome": outcome,
        "phase10_deployment_review_eligible": (
            outcome
            == PHASE9_DEMO_PASS_ELIGIBLE_FOR_DEPLOYMENT_REVIEW
        ),
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase11_authorized": False,
    }
    result = payload | {"demo_acceptance_fingerprint": _digest(payload)}
    validate_phase9_demo_acceptance(
        result,
        evidence=evidence,
        design=design,
    )
    return result


def validate_phase9_demo_acceptance(
    value: Mapping[str, object],
    *,
    evidence: Mapping[str, object],
    design: Mapping[str, object],
) -> None:
    validate_phase9_demo_campaign_evidence(evidence, design=design)
    if value.get("protocol") != PHASE9_DEMO_ACCEPTANCE_PROTOCOL:
        raise ValueError("Phase 9 demo acceptance protocol mismatch")
    if value.get("experiment_id") != PHASE9_DEMO_ACCEPTANCE_EXPERIMENT_ID:
        raise ValueError("Phase 9 demo acceptance experiment mismatch")
    if value.get("decision") != PHASE9_DEMO_ACCEPTANCE_DECISION:
        raise ValueError("Phase 9 demo acceptance decision mismatch")
    _commit(
        value.get("demo_acceptance_compiler_code_commit"),
        field="Phase 9 demo acceptance compiler code commit",
    )
    identities = {
        "demo_campaign_evidence_fingerprint": evidence[
            "demo_campaign_evidence_fingerprint"
        ],
        "demo_design_fingerprint": evidence["demo_design_fingerprint"],
        "champion_set_fingerprint": evidence["champion_set_fingerprint"],
        "account_fingerprint": evidence["account_fingerprint"],
        "server": evidence["server"],
    }
    for field, expected in identities.items():
        if value.get(field) != expected:
            raise ValueError(f"Phase 9 demo acceptance {field} mismatch")
    for field in (
        "demo_campaign_evidence_fingerprint",
        "demo_design_fingerprint",
        "champion_set_fingerprint",
        "account_fingerprint",
        "demo_acceptance_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 demo acceptance {field}")

    thresholds = value.get("thresholds")
    expected_thresholds = {
        "min_completed_trades": MIN_COMPLETED_TRADES,
        "min_elapsed_weeks": MIN_ELAPSED_WEEKS,
        "min_demo_session_dates": MIN_DEMO_SESSION_DATES,
        "min_represented_strategy_families": MIN_REPRESENTED_FAMILIES,
        "min_represented_pairs": MIN_REPRESENTED_PAIRS,
        "max_median_adverse_entry_slippage_pips": (
            MAX_MEDIAN_ADVERSE_SLIPPAGE_PIPS
        ),
        "max_p95_adverse_entry_slippage_pips": (
            MAX_P95_ADVERSE_SLIPPAGE_PIPS
        ),
    }
    if thresholds != expected_thresholds:
        raise ValueError("Phase 9 demo acceptance thresholds mismatch")

    minimum = _minimum_checks(evidence)
    safety = _safety_checks(evidence)
    operational = _operational_checks(evidence)
    cost = _cost_checks(evidence)
    if value.get("minimum_evidence_checks") != minimum:
        raise ValueError("Phase 9 minimum-evidence checks mismatch")
    if value.get("safety_checks") != safety:
        raise ValueError("Phase 9 safety checks mismatch")
    if value.get("operational_checks") != operational:
        raise ValueError("Phase 9 operational checks mismatch")
    if value.get("execution_cost_checks") != cost:
        raise ValueError("Phase 9 execution-cost checks mismatch")
    if value.get("financial_metrics_diagnostic") != evidence["financial_metrics"]:
        raise ValueError("Phase 9 financial diagnostics mismatch")

    if safety["pass"] is not True:
        expected_outcome = PHASE9_DEMO_REJECT_SAFETY_FAILURE
    elif minimum["pass"] is not True:
        expected_outcome = PHASE9_DEMO_NEED_MORE_DATA
    elif operational["pass"] is not True:
        expected_outcome = PHASE9_DEMO_REJECT_OPERATIONAL_MISMATCH
    elif cost["pass"] is not True:
        expected_outcome = PHASE9_DEMO_REJECT_EXECUTION_COST_MISMATCH
    else:
        expected_outcome = PHASE9_DEMO_PASS_ELIGIBLE_FOR_DEPLOYMENT_REVIEW
    if value.get("outcome") != expected_outcome:
        raise ValueError("Phase 9 demo acceptance outcome mismatch")
    eligible = (
        expected_outcome
        == PHASE9_DEMO_PASS_ELIGIBLE_FOR_DEPLOYMENT_REVIEW
    )
    if value.get("phase10_deployment_review_eligible") is not eligible:
        raise ValueError("Phase 9 deployment-review eligibility mismatch")
    for field in (
        "live_order_authorized",
        "real_money_authorized",
        "phase11_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 9 demo acceptance requires {field}=false")

    fingerprint = value["demo_acceptance_fingerprint"]
    payload = dict(value)
    payload.pop("demo_acceptance_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 demo acceptance fingerprint mismatch")


def write_phase9_demo_acceptance(
    value: Mapping[str, object],
    *,
    out_dir: Path,
    evidence: Mapping[str, object],
    design: Mapping[str, object],
) -> dict[str, object]:
    validate_phase9_demo_acceptance(
        value,
        evidence=evidence,
        design=design,
    )
    root = Path(out_dir)
    acceptance_path = root / "acceptance.json"
    manifest_path = root / "manifest.json"
    if acceptance_path.exists() or manifest_path.exists():
        raise FileExistsError("Phase 9 demo acceptance artifacts already exist")
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(value))
    _atomic_write(acceptance_path, payload)
    manifest = {
        "protocol": PHASE9_DEMO_ACCEPTANCE_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE9_DEMO_ACCEPTANCE_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_ACCEPTANCE_DECISION,
        "outcome": value["outcome"],
        "demo_campaign_evidence_fingerprint": value[
            "demo_campaign_evidence_fingerprint"
        ],
        "demo_acceptance_fingerprint": value["demo_acceptance_fingerprint"],
        "phase10_deployment_review_eligible": value[
            "phase10_deployment_review_eligible"
        ],
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase11_authorized": False,
        "artifacts": [
            {
                "path": acceptance_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(manifest_path, _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "MAX_MEDIAN_ADVERSE_SLIPPAGE_PIPS",
    "MAX_P95_ADVERSE_SLIPPAGE_PIPS",
    "MIN_COMPLETED_TRADES",
    "MIN_DEMO_SESSION_DATES",
    "MIN_ELAPSED_WEEKS",
    "MIN_REPRESENTED_FAMILIES",
    "MIN_REPRESENTED_PAIRS",
    "PHASE9_DEMO_ACCEPTANCE_ARTIFACT_PROTOCOL",
    "PHASE9_DEMO_ACCEPTANCE_DECISION",
    "PHASE9_DEMO_ACCEPTANCE_EXPERIMENT_ID",
    "PHASE9_DEMO_ACCEPTANCE_PROTOCOL",
    "PHASE9_DEMO_CAMPAIGN_EVIDENCE_PROTOCOL",
    "PHASE9_DEMO_NEED_MORE_DATA",
    "PHASE9_DEMO_PASS_ELIGIBLE_FOR_DEPLOYMENT_REVIEW",
    "PHASE9_DEMO_REJECT_EXECUTION_COST_MISMATCH",
    "PHASE9_DEMO_REJECT_OPERATIONAL_MISMATCH",
    "PHASE9_DEMO_REJECT_SAFETY_FAILURE",
    "build_phase9_demo_campaign_evidence",
    "compile_phase9_demo_acceptance",
    "validate_phase9_demo_acceptance",
    "validate_phase9_demo_campaign_evidence",
    "write_phase9_demo_acceptance",
]
