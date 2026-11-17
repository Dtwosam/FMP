"""Validate a caller-supplied closed-trade ledger.

Governing method: annual pattern catalogue discovery under DEC-469 / DEC-268.
This module is a measurement check for a ledger the caller already holds.
It is not a strategy, a pattern search, or a probability engine.

The functions below do not open market-data files, Phase 7 artifacts, or
network resources. A synthetic fixture is rejected when it is labeled as the
original Phase 7 Stage 2 result. A citation of the public Stage 2 run is not
treated as verification of that result.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from fmp.contracts import SUPPORTED_SYMBOLS, Direction, ExitReason
from fmp.risk.policy import RiskConfig
from fmp.risk.sizing import pnl_usd

_EXACT = 1e-9
_TOLERANCE = 1e-6
_R_TOLERANCE = 1e-8
_HARD_MAX_RISK_FRACTION = RiskConfig().max_risk_fraction

_PHASE7_RUN_ID = "35015277625"
_PHASE7_ARTIFACT_ID = "10414817824"
_PHASE7_SOURCE_SHA = "a1f8a0466463c79fdbceb9d6ebad9e3ea809474d"
_PHASE7_ZIP_SHA256 = "2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4"
_PHASE7_TOKENS = (
    _PHASE7_RUN_ID,
    _PHASE7_ARTIFACT_ID,
    _PHASE7_SOURCE_SHA,
    _PHASE7_ZIP_SHA256,
)

_LIMITATIONS = (
    "Closed-trade equity does not show simultaneous open risk.",
    "Closed-trade equity does not show whether a daily loss halt fired.",
    "This component does not authenticate provenance against the Phase 7 artifact.",
    "Independent windows are not one compounded account.",
)

_NON_BLOCKING = frozenset(
    {
        "DESCRIPTIVE_SAMPLE_MEAN",
        "NOT_CONFIRMATORY",
        "SELECTION_CENSUS_DECLARED_UNAUTHENTICATED",
        "DATA_REUSE_DECLARED_UNAUTHENTICATED",
        "COST_PROVENANCE_DECLARED",
        "DEPENDENCE_BLOCKED_DECLARED",
        "NO_TRADE_CALENDAR_DECLARED_UNAUTHENTICATED",
        "MARK_TO_MARKET_DECLARED",
        "OVERLAP_DECLARED",
        "PROBABILITY_PATH_DECLARED",
        "DOUBLING_BARRIER_DECLARED",
        "LOSS_BARRIER_DECLARED",
        "HORIZON_30_DAYS_DECLARED",
        "PROBABILITY_NOT_COMPUTED",
        "INTERVAL_NOT_COMPUTED",
        "DISTRIBUTION_NOT_COMPUTED",
        "SCENARIO_MEANS_LISTED",
        "NO_SCENARIO_SELECTED",
        "LEVERAGE_NOT_OPTIMIZED",
        "EDGE_NOT_DEMONSTRATED",
    }
)


@dataclass(frozen=True, slots=True)
class EvidenceProvenance:
    role: str
    label: str
    source_run_id: str | None = None
    source_artifact_id: str | None = None
    source_commit: str | None = None


@dataclass(frozen=True, slots=True)
class WindowAggregate:
    window_id: str
    start_utc: datetime
    end_exclusive_utc: datetime
    starting_equity_usd: float
    trade_count: int
    net_pnl_usd: float
    gross_profit_usd: float | None = None
    gross_loss_usd: float | None = None
    slippage_cost_usd: float | None = None
    commission_cost_usd: float | None = None
    financing_cost_usd: float | None = None
    overlap_role: str = "none"


@dataclass(frozen=True, slots=True)
class SubmittedTrade:
    trade_id: str
    decision_id: str
    window_id: str
    symbol: str
    direction: str
    units: int
    entry_timestamp_utc: datetime
    exit_timestamp_utc: datetime
    entry_reference_price: float
    exit_reference_price: float
    entry_price: float
    exit_price: float
    stop_price: float
    target_price: float | None
    exit_reason: str
    intrabar_ambiguous: bool
    intrabar_resolution: str
    gross_pnl_usd: float
    slippage_cost_usd: float
    commission_cost_usd: float
    financing_cost_usd: float
    spread_cost_usd: float
    spread_basis: str
    net_pnl_usd: float
    risk_equity_before_usd: float
    risk_equity_after_usd: float
    claimed_net_r: float


@dataclass(frozen=True, slots=True)
class TradeSubmission:
    provenance: EvidenceProvenance
    requested_risk_fraction: float
    windows: tuple[WindowAggregate, ...]
    trades: tuple[SubmittedTrade, ...]
    expected_trade_ids: tuple[str, ...] | None = None
    claims_trades_from_stage2_zip: bool = False


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    blocking: bool
    trade_id: str | None
    window_id: str | None
    detail: str


@dataclass(frozen=True, slots=True)
class TradeValidation:
    accepted: bool
    original_phase7_trade_ledger_verified: bool
    findings: tuple[Finding, ...]
    limitations: tuple[str, ...]
    per_trade_net_r: tuple[tuple[str, float], ...]
    descriptive_mean_net_r: float | None
    descriptive_mean_net_pnl_usd: float | None
    window_net_pnl_usd: tuple[tuple[str, float], ...]
    sample_size: int
    requested_risk_fraction: float
    provenance_role: str
    probabilities_computed: bool


@dataclass(frozen=True, slots=True)
class StatisticalEvidenceDeclaration:
    dependence: str = "unspecified"
    block_definition: str | None = None
    selection_family_complete: bool = False
    total_hypotheses: int | None = None
    data_reuse: str = "unknown"
    cost_provenance_id: str | None = None
    path_definition: str = "unspecified"
    overlap_declaration: str = "unspecified"
    no_trade_calendar_day_count: int | None = None
    horizon_days: int | None = None
    probability_path: str = "unspecified"
    doubling_barrier_declared: bool = False
    loss_barriers: tuple[float, ...] = ()


@dataclass(frozen=True, slots=True)
class EstimandAssessment:
    name: str
    status: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StatisticalReadiness:
    probabilities_computed: bool
    demonstrated_edge: bool
    leverage_optimized: bool
    selected_scenario: str | None
    descriptive_mean_net_r: float | None
    cost_scenario_mean_net_r: tuple[float, ...]
    frequency_scenario_mean_net_r: tuple[float, ...]
    cost_sign_flip: bool | None
    frequency_sign_flip: bool | None
    estimands: tuple[EstimandAssessment, ...]


def phase7_public_preservation_record() -> dict[str, object]:
    """Return the public identities of the Stage 2 evidence objects.

    The preserved-copy location is an owner statement. This function does not
    open that copy, and it does not download the GitHub artifact.
    """

    return {
        "original_historical_run": {
            "run_id": _PHASE7_RUN_ID,
            "workflow": "phase7-walk-forward",
            "run_attempt": 1,
            "conclusion": "success",
            "head_sha": _PHASE7_SOURCE_SHA,
        },
        "original_artifact": {
            "artifact_id": _PHASE7_ARTIFACT_ID,
            "name": (
                "phase7-stage2-session_breakout-"
                "a1f8a0466463c79fdbceb9d6ebad9e3ea809474d"
            ),
            "zip_sha256": _PHASE7_ZIP_SHA256,
            "github_digest": f"sha256:{_PHASE7_ZIP_SHA256}",
            "created_at": "2026-09-15T19:43:43Z",
            "expires_at": "2026-12-14T19:43:07Z",
            "expired_at_metadata_check": False,
            "size_in_bytes_at_metadata_check": 5711,
            "metadata_checked_on": "2026-11-17",
            "zip_downloaded_by_this_component": False,
            "documented_members": ("manifest.json", "result.json", "windows.json"),
        },
        "preserved_copy": {
            "owner_stated_location": "ChatGPT Library /FMP/Phase7/",
            "inspected_by_this_component": False,
            "hash_recomputed_by_this_component": False,
        },
        "published_aggregates": {
            "document": "docs/phase7-walk-forward-evidence.md",
            "experiment_id": "EXP-20260915-008",
            "published_stage2_trade_count": 199,
            "contains_ordered_r_series": False,
        },
        "individual_trade_records": {
            "available_from_authorized_sources": False,
            "contained_in_documented_stage2_zip": False,
        },
    }


def validate_trade_submission(submission: TradeSubmission) -> TradeValidation:
    """Check internal consistency of an in-memory trade ledger.

    Acceptance means the supplied rows agree with each other and with the
    declared window totals. It does not verify the rows against Phase 7.
    """

    if not isinstance(submission, TradeSubmission):
        raise TypeError("trade evidence must be an in-memory TradeSubmission")

    findings: list[Finding] = []
    fraction = _risk_fraction(submission.requested_risk_fraction, findings)
    _provenance(submission, findings)
    windows = _windows(submission.windows, findings)
    _identities(submission.trades, findings)
    _trades(submission.trades, windows, fraction, findings)
    _expected_ids(submission, findings)
    _aggregates(submission.trades, windows, findings)
    _overlaps(windows, findings)

    accepted = not any(finding.blocking for finding in findings)
    series: tuple[tuple[str, float], ...] = ()
    window_nets: tuple[tuple[str, float], ...] = ()
    mean_r: float | None = None
    mean_pnl: float | None = None
    if accepted and fraction is not None:
        ordered = _ordered_rows(submission.trades, windows)
        series = tuple(
            (
                trade.trade_id,
                trade.net_pnl_usd / (trade.risk_equity_before_usd * fraction),
            )
            for trade in ordered
        )
        window_nets = tuple(
            (
                window.window_id,
                math.fsum(
                    trade.net_pnl_usd
                    for trade in ordered
                    if trade.window_id == window.window_id
                ),
            )
            for window in windows
        )
        if series:
            mean_r = statistics.mean(value for _trade_id, value in series)
            mean_pnl = math.fsum(trade.net_pnl_usd for trade in ordered) / len(ordered)

    findings.sort(key=lambda item: (item.code, item.window_id or "", item.trade_id or "", item.detail))
    stored_fraction = (
        float(submission.requested_risk_fraction)
        if _real_number(submission.requested_risk_fraction)
        else math.nan
    )
    return TradeValidation(
        accepted=accepted,
        original_phase7_trade_ledger_verified=False,
        findings=tuple(findings),
        limitations=_LIMITATIONS,
        per_trade_net_r=series,
        descriptive_mean_net_r=mean_r,
        descriptive_mean_net_pnl_usd=mean_pnl,
        window_net_pnl_usd=window_nets,
        sample_size=len(submission.trades),
        requested_risk_fraction=stored_fraction,
        provenance_role=submission.provenance.role,
        probabilities_computed=False,
    )


def assess_statistical_readiness(
    validation: TradeValidation,
    declaration: StatisticalEvidenceDeclaration,
    cost_scenarios: tuple[TradeValidation, ...] = (),
    frequency_scenarios: tuple[TradeValidation, ...] = (),
) -> StatisticalReadiness:
    """Say which estimands have their inputs, without estimating probabilities.

    A descriptive mean of a valid closed-trade R series is reported as a
    sample description. Confidence intervals, account-loss distributions, and
    30-day doubling or loss probabilities are not calculated.
    """

    if not isinstance(validation, TradeValidation):
        raise TypeError("statistical readiness requires a TradeValidation")
    if not isinstance(declaration, StatisticalEvidenceDeclaration):
        raise TypeError("statistical readiness requires a declaration")
    if not isinstance(cost_scenarios, tuple) or not isinstance(frequency_scenarios, tuple):
        raise TypeError("scenarios must be tuples of TradeValidation")

    core = _core_gap_codes(declaration)
    estimands = [
        _expectancy(validation, core),
        _interval(validation, core),
        _drawdown(validation, declaration, core),
        _probability(validation, declaration, core, "probability_double_within_30_days", "double"),
        _probability(validation, declaration, core, "probability_lose_at_least_50_percent", 0.5),
        _probability(validation, declaration, core, "probability_lose_at_least_90_percent", 0.9),
    ]
    sensitivity, cost_means, frequency_means, cost_flip, frequency_flip = _sensitivity(
        validation, cost_scenarios, frequency_scenarios
    )
    estimands.append(sensitivity)
    return StatisticalReadiness(
        probabilities_computed=False,
        demonstrated_edge=False,
        leverage_optimized=False,
        selected_scenario=None,
        descriptive_mean_net_r=validation.descriptive_mean_net_r if validation.accepted else None,
        cost_scenario_mean_net_r=cost_means,
        frequency_scenario_mean_net_r=frequency_means,
        cost_sign_flip=cost_flip,
        frequency_sign_flip=frequency_flip,
        estimands=tuple(estimands),
    )


def _add(
    findings: list[Finding],
    code: str,
    detail: str,
    *,
    trade_id: str | None = None,
    window_id: str | None = None,
    blocking: bool = True,
) -> None:
    findings.append(
        Finding(
            code=code,
            blocking=blocking,
            trade_id=trade_id,
            window_id=window_id,
            detail=detail,
        )
    )


def _real_number(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _close(left: float, right: float, tolerance: float = _EXACT) -> bool:
    return abs(left - right) <= tolerance


def _risk_fraction(value: object, findings: list[Finding]) -> float | None:
    if not _real_number(value) or float(value) <= 0 or float(value) > _HARD_MAX_RISK_FRACTION:
        _add(
            findings,
            "RISK_FRACTION_INVALID",
            f"requested risk fraction must be inside (0, {_HARD_MAX_RISK_FRACTION}]",
        )
        return None
    return float(value)


def _cites_original_phase7(*parts: object) -> bool:
    text = " ".join(part.lower() for part in parts if isinstance(part, str))
    normalized = text.replace("_", " ").replace("-", " ")
    if "original phase 7" in normalized:
        return True
    return any(token in text for token in _PHASE7_TOKENS)


def _provenance(submission: TradeSubmission, findings: list[Finding]) -> None:
    provenance = submission.provenance
    if provenance.role not in {"synthetic_fixture", "separately_authorized_submission"}:
        _add(findings, "PROVENANCE_INVALID", "provenance role is not recognized")
    if not isinstance(provenance.label, str) or not provenance.label.strip():
        _add(findings, "PROVENANCE_INVALID", "provenance label must be non-empty")
    if provenance.role == "synthetic_fixture":
        if any(
            value is not None
            for value in (
                provenance.source_run_id,
                provenance.source_artifact_id,
                provenance.source_commit,
            )
        ):
            _add(
                findings,
                "SYNTHETIC_CLAIMS_SOURCE",
                "a synthetic fixture cannot carry a historical source identity",
            )
        if _cites_original_phase7(
            provenance.label,
            provenance.source_run_id,
            provenance.source_artifact_id,
            provenance.source_commit,
        ):
            _add(
                findings,
                "FABRICATED_PHASE7_CLAIM",
                "a synthetic fixture cannot be labeled as the original Phase 7 result",
            )
    if submission.claims_trades_from_stage2_zip:
        _add(
            findings,
            "ARCHIVE_HAS_NO_TRADE_LEDGER",
            "the documented Stage 2 ZIP has manifest.json, result.json, and windows.json only",
        )


def _windows(
    windows: tuple[WindowAggregate, ...], findings: list[Finding]
) -> tuple[WindowAggregate, ...]:
    seen: set[str] = set()
    accepted: list[WindowAggregate] = []
    for window in windows:
        if not isinstance(window.window_id, str) or not window.window_id.strip():
            _add(findings, "WINDOW_INVALID", "window id must be non-empty")
            continue
        if window.window_id in seen:
            _add(findings, "DUPLICATE_WINDOW_ID", window.window_id, window_id=window.window_id)
            continue
        seen.add(window.window_id)
        if not _is_utc(window.start_utc) or not _is_utc(window.end_exclusive_utc):
            _add(findings, "WINDOW_INVALID", "window bounds must use UTC", window_id=window.window_id)
        elif window.start_utc >= window.end_exclusive_utc:
            _add(findings, "WINDOW_INVALID", "window start must be before end", window_id=window.window_id)
        if not _real_number(window.starting_equity_usd) or float(window.starting_equity_usd) <= 0:
            _add(findings, "WINDOW_INVALID", "starting equity must be positive", window_id=window.window_id)
        if (
            isinstance(window.trade_count, bool)
            or not isinstance(window.trade_count, int)
            or window.trade_count < 0
        ):
            _add(findings, "WINDOW_INVALID", "trade count must be a non-negative integer", window_id=window.window_id)
        if window.overlap_role not in {"none", "separate_scenario"}:
            _add(findings, "WINDOW_INVALID", "overlap role is not recognized", window_id=window.window_id)
        accepted.append(window)
    return tuple(accepted)


def _identities(trades: tuple[SubmittedTrade, ...], findings: list[Finding]) -> None:
    trade_ids: set[str] = set()
    decision_ids: set[str] = set()
    for trade in trades:
        if not isinstance(trade.trade_id, str) or not trade.trade_id.strip():
            _add(findings, "EMPTY_IDENTITY", "trade id must be non-empty", trade_id=None)
        elif trade.trade_id in trade_ids:
            _add(findings, "DUPLICATE_TRADE_ID", trade.trade_id, trade_id=trade.trade_id)
        else:
            trade_ids.add(trade.trade_id)
        if not isinstance(trade.decision_id, str) or not trade.decision_id.strip():
            _add(findings, "EMPTY_IDENTITY", "decision id must be non-empty", trade_id=trade.trade_id)
        elif trade.decision_id in decision_ids:
            _add(findings, "DUPLICATE_DECISION_ID", trade.decision_id, trade_id=trade.trade_id)
        else:
            decision_ids.add(trade.decision_id)


def _trades(
    trades: tuple[SubmittedTrade, ...],
    windows: tuple[WindowAggregate, ...],
    fraction: float | None,
    findings: list[Finding],
) -> None:
    by_id = {window.window_id: window for window in windows}
    grouped: dict[str, list[SubmittedTrade]] = {window.window_id: [] for window in windows}
    for trade in trades:
        window = by_id.get(trade.window_id)
        if window is None:
            _add(findings, "UNKNOWN_WINDOW", trade.window_id, trade_id=trade.trade_id)
            _price_and_costs(trade, fraction, findings)
            continue
        grouped[window.window_id].append(trade)
        _timestamps(trade, window, findings)
        _price_and_costs(trade, fraction, findings)
        _exit_contract(trade, findings)
    for window in windows:
        rows = grouped[window.window_id]
        if not rows or not all(
            _is_utc(trade.entry_timestamp_utc) and _is_utc(trade.exit_timestamp_utc) for trade in rows
        ):
            continue
        ordered = sorted(rows, key=lambda item: (item.exit_timestamp_utc, item.trade_id))
        if rows != ordered:
            _add(
                findings,
                "NOT_CHRONOLOGICAL",
                "trades in a window must be ordered by exit time then trade id",
                window_id=window.window_id,
            )
        _equity_chain(window, ordered, findings)


def _timestamps(trade: SubmittedTrade, window: WindowAggregate, findings: list[Finding]) -> None:
    entry_ok = _is_utc(trade.entry_timestamp_utc)
    exit_ok = _is_utc(trade.exit_timestamp_utc)
    if not entry_ok or not exit_ok:
        _add(findings, "TIMESTAMP_INVALID", "entry and exit must use UTC", trade_id=trade.trade_id)
        return
    if trade.entry_timestamp_utc >= trade.exit_timestamp_utc:
        _add(findings, "TIMESTAMP_INVALID", "exit must be after entry", trade_id=trade.trade_id)
    if not _is_utc(window.start_utc) or not _is_utc(window.end_exclusive_utc):
        return
    inside = (
        window.start_utc <= trade.entry_timestamp_utc < window.end_exclusive_utc
        and window.start_utc < trade.exit_timestamp_utc < window.end_exclusive_utc
    )
    if not inside:
        _add(
            findings,
            "TIMESTAMP_OUTSIDE_WINDOW",
            "entry and exit must fall inside the half-open window",
            trade_id=trade.trade_id,
            window_id=window.window_id,
        )


def _price_and_costs(
    trade: SubmittedTrade, fraction: float | None, findings: list[Finding]
) -> None:
    if trade.symbol not in SUPPORTED_SYMBOLS:
        _add(findings, "SYMBOL_INVALID", trade.symbol, trade_id=trade.trade_id)
        return
    if trade.direction not in {Direction.LONG.value, Direction.SHORT.value}:
        _add(findings, "DIRECTION_INVALID", trade.direction, trade_id=trade.trade_id)
        return
    if isinstance(trade.units, bool) or not isinstance(trade.units, int) or trade.units <= 0:
        _add(findings, "UNITS_INVALID", "units must be a positive integer", trade_id=trade.trade_id)
        return
    prices = (
        trade.entry_reference_price,
        trade.exit_reference_price,
        trade.entry_price,
        trade.exit_price,
        trade.stop_price,
    )
    if any(not _real_number(price) or float(price) <= 0 for price in prices):
        _add(findings, "PRICE_INVALID", "prices must be finite and positive", trade_id=trade.trade_id)
        return
    if trade.target_price is not None and (
        not _real_number(trade.target_price) or float(trade.target_price) <= 0
    ):
        _add(findings, "PRICE_INVALID", "target price must be finite and positive", trade_id=trade.trade_id)
        return
    entry_reference = float(trade.entry_reference_price)
    if trade.direction == Direction.LONG.value:
        if not float(trade.stop_price) < entry_reference:
            _add(findings, "STOP_GEOMETRY", "long stop must be below the reference entry", trade_id=trade.trade_id)
        if trade.target_price is not None and not float(trade.target_price) > entry_reference:
            _add(findings, "TARGET_GEOMETRY", "long target must be above the reference entry", trade_id=trade.trade_id)
    else:
        if not float(trade.stop_price) > entry_reference:
            _add(findings, "STOP_GEOMETRY", "short stop must be above the reference entry", trade_id=trade.trade_id)
        if trade.target_price is not None and not float(trade.target_price) < entry_reference:
            _add(findings, "TARGET_GEOMETRY", "short target must be below the reference entry", trade_id=trade.trade_id)

    try:
        gross = pnl_usd(
            symbol=trade.symbol,
            direction=Direction(trade.direction),
            units=trade.units,
            entry_price=float(trade.entry_reference_price),
            exit_price=float(trade.exit_reference_price),
        )
        slipped = pnl_usd(
            symbol=trade.symbol,
            direction=Direction(trade.direction),
            units=trade.units,
            entry_price=float(trade.entry_price),
            exit_price=float(trade.exit_price),
        )
    except ValueError as exc:
        _add(findings, "PRICE_INVALID", str(exc), trade_id=trade.trade_id)
        return

    slippage = max(0.0, gross - slipped)
    if not _real_number(trade.gross_pnl_usd) or not _close(float(trade.gross_pnl_usd), gross, _TOLERANCE):
        _add(findings, "PNL_MISMATCH", "gross PnL does not match the reference prices", trade_id=trade.trade_id)
    if not _real_number(trade.slippage_cost_usd) or float(trade.slippage_cost_usd) < 0:
        _add(findings, "COST_INVALID", "slippage cost must be finite and non-negative", trade_id=trade.trade_id)
    elif not _close(float(trade.slippage_cost_usd), slippage, _TOLERANCE):
        _add(
            findings,
            "SLIPPAGE_MISMATCH",
            "slippage must be the adverse gap from reference PnL to execution PnL",
            trade_id=trade.trade_id,
        )
    deduction = _spread_deduction(trade, findings)
    if not _real_number(trade.commission_cost_usd) or float(trade.commission_cost_usd) < 0:
        _add(findings, "COST_INVALID", "commission cost must be finite and non-negative", trade_id=trade.trade_id)
        return
    if not _real_number(trade.financing_cost_usd):
        _add(findings, "COST_INVALID", "financing must be finite", trade_id=trade.trade_id)
        return
    if deduction is None or not _real_number(trade.net_pnl_usd):
        _add(findings, "PNL_MISMATCH", "net PnL must be finite", trade_id=trade.trade_id)
        return
    expected_net = (
        gross - slippage - float(trade.commission_cost_usd) - float(trade.financing_cost_usd) - deduction
    )
    if not _close(float(trade.net_pnl_usd), expected_net, _TOLERANCE):
        _add(
            findings,
            "PNL_MISMATCH",
            "net PnL must equal gross minus slippage, commission, financing, and any separate spread",
            trade_id=trade.trade_id,
        )
    _claimed_r(trade, fraction, findings)


def _spread_deduction(trade: SubmittedTrade, findings: list[Finding]) -> float | None:
    if trade.spread_basis == "included_in_bid_ask_reference":
        if not _real_number(trade.spread_cost_usd):
            _add(findings, "COST_INVALID", "spread cost must be finite", trade_id=trade.trade_id)
            return None
        if float(trade.spread_cost_usd) != 0.0:
            _add(
                findings,
                "DOUBLE_COUNTED_SPREAD",
                "reference bid/ask prices already contain the spread",
                trade_id=trade.trade_id,
            )
        return 0.0
    if trade.spread_basis == "separate_from_reference":
        if not _real_number(trade.spread_cost_usd) or float(trade.spread_cost_usd) < 0:
            _add(findings, "COST_INVALID", "separate spread cost must be finite and non-negative", trade_id=trade.trade_id)
            return None
        return float(trade.spread_cost_usd)
    _add(findings, "SPREAD_BASIS_INVALID", trade.spread_basis, trade_id=trade.trade_id)
    return None


def _claimed_r(trade: SubmittedTrade, fraction: float | None, findings: list[Finding]) -> None:
    if fraction is None:
        return
    if not _real_number(trade.risk_equity_before_usd) or float(trade.risk_equity_before_usd) <= 0:
        _add(findings, "EQUITY_CHAIN", "risk equity before the trade must be positive", trade_id=trade.trade_id)
        return
    if not _real_number(trade.claimed_net_r) or not _real_number(trade.net_pnl_usd):
        _add(findings, "R_MISMATCH", "claimed R must be finite", trade_id=trade.trade_id)
        return
    computed = float(trade.net_pnl_usd) / (float(trade.risk_equity_before_usd) * fraction)
    if not _close(float(trade.claimed_net_r), computed, _R_TOLERANCE):
        _add(
            findings,
            "R_MISMATCH",
            "R must be net PnL divided by pre-trade equity times the requested risk fraction",
            trade_id=trade.trade_id,
        )


def _exit_contract(trade: SubmittedTrade, findings: list[Finding]) -> None:
    try:
        ExitReason(trade.exit_reason)
    except ValueError:
        _add(findings, "EXIT_REASON_INVALID", trade.exit_reason, trade_id=trade.trade_id)
    if not isinstance(trade.intrabar_ambiguous, bool):
        _add(findings, "INTRABAR_RULE", "intrabar ambiguity must be boolean", trade_id=trade.trade_id)
        return
    if trade.intrabar_ambiguous and trade.intrabar_resolution != "conservative_adverse":
        _add(
            findings,
            "INTRABAR_RULE",
            "an ambiguous intrabar exit must use the conservative adverse rule",
            trade_id=trade.trade_id,
        )
    if not trade.intrabar_ambiguous and trade.intrabar_resolution != "not_applicable":
        _add(findings, "INTRABAR_RULE", "an unambiguous exit has no intrabar resolution", trade_id=trade.trade_id)


def _equity_chain(
    window: WindowAggregate, ordered: list[SubmittedTrade], findings: list[Finding]
) -> None:
    if not _real_number(window.starting_equity_usd):
        return
    running = float(window.starting_equity_usd)
    for index, trade in enumerate(ordered):
        if not _real_number(trade.risk_equity_before_usd) or not _real_number(trade.net_pnl_usd):
            _add(findings, "EQUITY_CHAIN", "equity and net PnL must be finite", trade_id=trade.trade_id)
            continue
        before = float(trade.risk_equity_before_usd)
        if not _close(before, running, _TOLERANCE):
            _add(
                findings,
                "EQUITY_NOT_RESET" if index == 0 else "EQUITY_CHAIN",
                "risk equity must restart at the window starting equity and then follow realized net PnL",
                trade_id=trade.trade_id,
                window_id=window.window_id,
            )
        if not _real_number(trade.risk_equity_after_usd) or not _close(
            float(trade.risk_equity_after_usd), before + float(trade.net_pnl_usd), _TOLERANCE
        ):
            _add(
                findings,
                "EQUITY_CHAIN",
                "risk equity after the trade must equal equity before plus net PnL",
                trade_id=trade.trade_id,
                window_id=window.window_id,
            )
        running += float(trade.net_pnl_usd)


def _expected_ids(submission: TradeSubmission, findings: list[Finding]) -> None:
    expected = submission.expected_trade_ids
    if expected is None:
        return
    if not isinstance(expected, tuple) or any(not isinstance(item, str) for item in expected):
        _add(findings, "EXPECTED_IDS_INVALID", "expected trade ids must be a tuple of strings")
        return
    actual = {trade.trade_id for trade in submission.trades}
    missing = [item for item in expected if item not in actual]
    extra = [trade.trade_id for trade in submission.trades if trade.trade_id not in set(expected)]
    if missing:
        _add(findings, "MISSING_TRADES", ",".join(missing))
    if extra:
        _add(findings, "EXTRA_TRADES", ",".join(extra))


def _aggregates(
    trades: tuple[SubmittedTrade, ...],
    windows: tuple[WindowAggregate, ...],
    findings: list[Finding],
) -> None:
    for window in windows:
        rows = [trade for trade in trades if trade.window_id == window.window_id]
        if isinstance(window.trade_count, int) and not isinstance(window.trade_count, bool):
            if len(rows) < window.trade_count:
                _add(
                    findings,
                    "MISSING_TRADES",
                    f"declared {window.trade_count} trades and found {len(rows)}",
                    window_id=window.window_id,
                )
            elif len(rows) > window.trade_count:
                _add(
                    findings,
                    "EXTRA_TRADES",
                    f"declared {window.trade_count} trades and found {len(rows)}",
                    window_id=window.window_id,
                )
        nets = [float(trade.net_pnl_usd) for trade in rows if _real_number(trade.net_pnl_usd)]
        _compare_total(findings, window, "net_pnl_usd", window.net_pnl_usd, math.fsum(nets))
        _compare_total(
            findings,
            window,
            "gross_profit_usd",
            window.gross_profit_usd,
            math.fsum(value for value in nets if value > 0),
        )
        _compare_total(
            findings,
            window,
            "gross_loss_usd",
            window.gross_loss_usd,
            math.fsum(value for value in nets if value < 0),
        )
        _compare_total(
            findings,
            window,
            "slippage_cost_usd",
            window.slippage_cost_usd,
            math.fsum(float(trade.slippage_cost_usd) for trade in rows if _real_number(trade.slippage_cost_usd)),
        )
        _compare_total(
            findings,
            window,
            "commission_cost_usd",
            window.commission_cost_usd,
            math.fsum(float(trade.commission_cost_usd) for trade in rows if _real_number(trade.commission_cost_usd)),
        )
        _compare_total(
            findings,
            window,
            "financing_cost_usd",
            window.financing_cost_usd,
            math.fsum(float(trade.financing_cost_usd) for trade in rows if _real_number(trade.financing_cost_usd)),
        )


def _compare_total(
    findings: list[Finding],
    window: WindowAggregate,
    field: str,
    declared: object,
    actual: float,
) -> None:
    if declared is None:
        return
    if not _real_number(declared):
        _add(findings, "AGGREGATE_MISMATCH", f"{field} must be finite", window_id=window.window_id)
        return
    difference = abs(float(declared) - actual)
    if difference <= _EXACT:
        return
    if difference <= _TOLERANCE:
        _add(
            findings,
            "RESIDUAL",
            f"{field} differs by {difference}",
            window_id=window.window_id,
            blocking=False,
        )
        return
    _add(findings, "AGGREGATE_MISMATCH", f"{field} does not match the trade rows", window_id=window.window_id)


def _overlaps(windows: tuple[WindowAggregate, ...], findings: list[Finding]) -> None:
    usable = [
        window
        for window in windows
        if _is_utc(window.start_utc) and _is_utc(window.end_exclusive_utc) and window.start_utc < window.end_exclusive_utc
    ]
    for index, left in enumerate(usable):
        for right in usable[index + 1 :]:
            if left.start_utc < right.end_exclusive_utc and right.start_utc < left.end_exclusive_utc:
                if left.overlap_role != "separate_scenario" or right.overlap_role != "separate_scenario":
                    _add(
                        findings,
                        "OVERLAPPING_WINDOWS",
                        f"{left.window_id} overlaps {right.window_id}",
                        window_id=left.window_id,
                    )


def _ordered_rows(
    trades: tuple[SubmittedTrade, ...], windows: tuple[WindowAggregate, ...]
) -> list[SubmittedTrade]:
    ordered: list[SubmittedTrade] = []
    for window in windows:
        rows = [trade for trade in trades if trade.window_id == window.window_id]
        ordered.extend(sorted(rows, key=lambda item: (item.exit_timestamp_utc, item.trade_id)))
    return ordered


def _is_utc(value: object) -> bool:
    return (
        isinstance(value, datetime)
        and value.tzinfo is not None
        and value.utcoffset() == timedelta(0)
    )


def _core_gap_codes(declaration: StatisticalEvidenceDeclaration) -> list[str]:
    codes: list[str] = []
    if declaration.dependence == "iid":
        codes.append("INDEPENDENCE_ASSUMED")
    elif (
        declaration.dependence == "blocked"
        and isinstance(declaration.block_definition, str)
        and declaration.block_definition.strip()
    ):
        codes.append("DEPENDENCE_BLOCKED_DECLARED")
    else:
        codes.append("DEPENDENCE_UNSPECIFIED")
    total = declaration.total_hypotheses
    if (
        declaration.selection_family_complete is True
        and isinstance(total, int)
        and not isinstance(total, bool)
        and total >= 1
    ):
        codes.append("SELECTION_CENSUS_DECLARED_UNAUTHENTICATED")
    else:
        codes.append("SELECTION_CENSUS_UNKNOWN")
    if declaration.data_reuse == "already_scored":
        codes.append("DATA_ALREADY_SCORED")
    elif declaration.data_reuse in {"untouched_predeclared", "prospective"}:
        codes.append("DATA_REUSE_DECLARED_UNAUTHENTICATED")
    else:
        codes.append("DATA_REUSE_UNKNOWN")
    if isinstance(declaration.cost_provenance_id, str) and declaration.cost_provenance_id.strip():
        codes.append("COST_PROVENANCE_DECLARED")
    else:
        codes.append("COST_PROVENANCE_MISSING")
    return codes


def _estimand(name: str, codes: list[str], *, force_descriptive: bool = False) -> EstimandAssessment:
    blocking = [code for code in codes if code not in _NON_BLOCKING]
    if force_descriptive and "DESCRIPTIVE_SAMPLE_MEAN" in codes:
        status = "DESCRIPTIVE_ONLY"
    elif blocking:
        status = "BLOCKED"
    else:
        status = "INPUTS_PRESENT_NOT_COMPUTED"
    return EstimandAssessment(name, status, tuple(codes))


def _expectancy(validation: TradeValidation, core: list[str]) -> EstimandAssessment:
    if not validation.accepted:
        return _estimand("after_cost_expectancy", ["LEDGER_REJECTED"])
    if validation.descriptive_mean_net_r is None:
        return _estimand("after_cost_expectancy", ["NO_CLOSED_TRADES"])
    return _estimand(
        "after_cost_expectancy",
        ["DESCRIPTIVE_SAMPLE_MEAN", "NOT_CONFIRMATORY", *core],
        force_descriptive=True,
    )


def _interval(validation: TradeValidation, core: list[str]) -> EstimandAssessment:
    codes: list[str] = []
    if not validation.accepted:
        codes.append("LEDGER_REJECTED")
    elif validation.sample_size < 2:
        codes.append("SAMPLE_TOO_SMALL_FOR_INTERVAL")
    codes.extend(core)
    codes.append("INTERVAL_NOT_COMPUTED")
    return _estimand("confidence_interval", codes)


def _drawdown(
    validation: TradeValidation,
    declaration: StatisticalEvidenceDeclaration,
    core: list[str],
) -> EstimandAssessment:
    codes: list[str] = []
    if not validation.accepted:
        codes.append("LEDGER_REJECTED")
    codes.extend(core)
    codes.extend(_overlap_codes(declaration))
    if declaration.path_definition == "mark_to_market":
        codes.append("MARK_TO_MARKET_DECLARED")
    elif declaration.path_definition == "realized_exit_only":
        codes.append("EXIT_ONLY_PATH")
    else:
        codes.append("PATH_UNSPECIFIED")
    codes.append("DISTRIBUTION_NOT_COMPUTED")
    return _estimand("loss_and_drawdown_distribution", codes)


def _probability(
    validation: TradeValidation,
    declaration: StatisticalEvidenceDeclaration,
    core: list[str],
    name: str,
    barrier: str | float,
) -> EstimandAssessment:
    codes: list[str] = []
    if not validation.accepted:
        codes.append("LEDGER_REJECTED")
    elif validation.sample_size < 1:
        codes.append("NO_CLOSED_TRADES")
    codes.extend(core)
    codes.extend(_overlap_codes(declaration))
    codes.extend(_horizon_codes(declaration))
    if barrier == "double":
        if declaration.doubling_barrier_declared is True:
            codes.append("DOUBLING_BARRIER_DECLARED")
        else:
            codes.append("DOUBLING_BARRIER_MISSING")
    elif barrier in declaration.loss_barriers:
        codes.append("LOSS_BARRIER_DECLARED")
    else:
        codes.append("LOSS_BARRIER_MISSING")
    codes.append("PROBABILITY_NOT_COMPUTED")
    return _estimand(name, codes)


def _overlap_codes(declaration: StatisticalEvidenceDeclaration) -> list[str]:
    if declaration.overlap_declaration in {"no_overlap", "overlaps_modeled"}:
        return ["OVERLAP_DECLARED"]
    return ["OVERLAP_UNSPECIFIED"]


def _horizon_codes(declaration: StatisticalEvidenceDeclaration) -> list[str]:
    codes: list[str] = []
    if declaration.horizon_days == 30:
        codes.append("HORIZON_30_DAYS_DECLARED")
    else:
        codes.append("HORIZON_NOT_30_DAYS")
    count = declaration.no_trade_calendar_day_count
    if isinstance(count, int) and not isinstance(count, bool) and count >= 30:
        codes.append("NO_TRADE_CALENDAR_DECLARED_UNAUTHENTICATED")
    else:
        codes.append("NO_TRADE_CALENDAR_MISSING")
    if declaration.probability_path in {"terminal", "touch"}:
        codes.append("PROBABILITY_PATH_DECLARED")
    else:
        codes.append("PROBABILITY_PATH_UNSPECIFIED")
    return codes


def _sensitivity(
    validation: TradeValidation,
    cost_scenarios: tuple[TradeValidation, ...],
    frequency_scenarios: tuple[TradeValidation, ...],
) -> tuple[EstimandAssessment, tuple[float, ...], tuple[float, ...], bool | None, bool | None]:
    if not validation.accepted:
        assessment = _estimand("cost_and_frequency_sensitivity", ["LEDGER_REJECTED"])
        return assessment, (), (), None, None
    cost_codes, cost_means = _scenario_means(validation, cost_scenarios, "NO_COST_SCENARIO")
    frequency_codes, frequency_means = _scenario_means(
        validation, frequency_scenarios, "NO_FREQUENCY_SCENARIO"
    )
    blocking = [code for code in (*cost_codes, *frequency_codes) if code not in _NON_BLOCKING]
    if blocking:
        return (
            _estimand("cost_and_frequency_sensitivity", [*cost_codes, *frequency_codes]),
            (),
            (),
            None,
            None,
        )
    codes = [
        *cost_codes,
        *frequency_codes,
        "SCENARIO_MEANS_LISTED",
        "NO_SCENARIO_SELECTED",
        "LEVERAGE_NOT_OPTIMIZED",
        "PROBABILITY_NOT_COMPUTED",
    ]
    return (
        EstimandAssessment("cost_and_frequency_sensitivity", "DESCRIPTIVE_ONLY", tuple(codes)),
        cost_means,
        frequency_means,
        _sign_flip(validation.descriptive_mean_net_r, cost_means),
        _sign_flip(validation.descriptive_mean_net_r, frequency_means),
    )


def _scenario_means(
    primary: TradeValidation,
    scenarios: tuple[TradeValidation, ...],
    missing_code: str,
) -> tuple[list[str], tuple[float, ...]]:
    if not scenarios:
        return [missing_code], ()
    codes: list[str] = []
    means: list[float] = []
    for scenario in scenarios:
        if not isinstance(scenario, TradeValidation) or not scenario.accepted or scenario.descriptive_mean_net_r is None:
            codes.append("SCENARIO_LEDGER_REJECTED")
            continue
        if abs(scenario.requested_risk_fraction - primary.requested_risk_fraction) > 1e-12:
            codes.append("SCENARIO_RISK_FRACTION_CHANGED")
        if scenario.provenance_role != primary.provenance_role:
            codes.append("SCENARIO_PROVENANCE_MISMATCH")
        means.append(scenario.descriptive_mean_net_r)
    if codes:
        return codes, ()
    return codes, tuple(means)


def _sign_flip(primary: float | None, scenarios: tuple[float, ...]) -> bool:
    if primary is None:
        return False
    return any(primary * value < 0 for value in scenarios)
