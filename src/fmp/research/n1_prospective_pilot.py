"""Record one N1-v0 prospective pilot observation.

DEC-638 authorizes two future quote windows. This module does not download
market data, does not contact a broker, and does not change the frozen
signal. The engine trade or rejection is stored separately from the
quality label.

The signal file must match commit 78185a1aded7f5d97c296c16fdfd615f46934353.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Sequence

from fmp.backtest.costs import ZeroFinancing
from fmp.backtest.engine import NEXT_SUPPLIED_BAR, BacktestConfig, run_backtest
from fmp.contracts import QuoteBar
from fmp.research.n1_news_shock import (
    HYPOTHETICAL_COST_LABEL,
    RULE_ID,
    RULE_NAME,
    TRADED_SYMBOL,
    N1Release,
    ReleaseKind,
    ReleaseStatus,
    evaluate_n1_v0,
    hypothetical_published_commission_model,
    new_york_clock_utc,
    required_n1_observation_keys,
    review_n1_observation,
)
from fmp.risk import RiskConfig

FROZEN_SIGNAL_COMMIT = "78185a1aded7f5d97c296c16fdfd615f46934353"
AUTHORIZATION_COMMIT = "09ca49abbd6478db44bf070ebed5e9f77db705b1"
AUTHORIZATION_EFFECTIVE_UTC = "2026-11-23T15:13:54+01:00"
EVIDENCE_CLASS = "prospective_quote_observation_not_broker_fill"
PILOT_ACCOUNTING_EQUITY_USD = 100_000.0
LABELED_SLIPPAGE_PIPS = (0.5, 0.2, 1.0)
SIGNAL_PATH = "src/fmp/research/n1_news_shock.py"

_APPROVED_WINDOWS: dict[date, tuple[str, str]] = {
    date(2026, 12, 4): ("bls-empsit-2026-12-04", ReleaseKind.EMPLOYMENT_SITUATION.value),
    date(2026, 12, 10): ("bls-cpi-2026-12-10", ReleaseKind.CPI.value),
}


class PilotWindowClosed(RuntimeError):
    """The release is outside the two approved prospective windows."""


@dataclass(frozen=True, slots=True)
class N1PilotRecord:
    """One stored observation. Quality does not overwrite the raw result."""

    release_id: str
    new_york_date: date
    qualifying_publication: bool
    reason_code: str
    direction: str
    engine_ran: bool
    raw_exit_reason: str | None
    raw_rejection_code: str | None
    raw_stop_price: float | None
    raw_entry_price: float | None
    raw_net_pnl_usd: float | None
    raw_commission_usd: float | None
    slippage_pips: float
    quality: str
    ordinary_n1_time_exit: bool
    missing_labels: tuple[str, ...]
    evidence_class: str
    quality_replaces_raw_result: bool = False

    def __post_init__(self) -> None:
        if self.quality_replaces_raw_result:
            raise ValueError("quality classification must not replace the raw result")


def assert_frozen_signal_blob(repo_root: Path | None = None) -> None:
    """Refuse collection when the signal file is not the reviewed blob."""

    root = _repo_root(repo_root)
    expected = _git(root, "rev-parse", f"{FROZEN_SIGNAL_COMMIT}:{SIGNAL_PATH}")
    actual = _git(root, "hash-object", SIGNAL_PATH)
    if actual != expected:
        raise RuntimeError("N1 signal file does not match the frozen research commit")


def record_pilot_observation(
    release: N1Release,
    bars: Sequence[QuoteBar],
    *,
    slippage_pips: float,
) -> N1PilotRecord:
    """Record one supplied window. Bars must already be in memory."""

    assert_frozen_signal_blob()
    if not isinstance(release, N1Release):
        raise TypeError("release must be an N1Release")
    slippage = _require_labeled_slippage(slippage_pips)
    _require_approved_release(release)
    supplied = tuple(bars)
    _require_timestamps_after_authorization(supplied)
    _require_window_keys(release.new_york_date, supplied)
    signal = evaluate_n1_v0(release, supplied)
    review_reason = None
    raw_exit_reason = None
    raw_rejection_code = None
    raw_stop_price = signal.decision.stop_price
    raw_entry_price = None
    raw_net_pnl = None
    raw_commission = None
    engine_ran = False
    if supplied:
        scheduled = () if signal.scheduled_exit is None else (signal.scheduled_exit,)
        result = run_backtest(
            bars=supplied,
            decisions=(signal.decision,),
            scheduled_exits=scheduled,
            config=_pilot_config(supplied, slippage),
        )
        engine_ran = True
        if len(result.trades) > 1 or len(result.rejections) > 1:
            raise RuntimeError("one N1 event must keep a single raw engine result")
        if result.trades and result.rejections:
            raise RuntimeError("refusing to drop either the raw trade or the raw rejection")
        if result.trades:
            trade = result.trades[0]
            raw_exit_reason = trade.exit_reason.value
            raw_stop_price = trade.stop_price
            raw_entry_price = trade.entry_price
            raw_net_pnl = trade.net_pnl_usd
            raw_commission = trade.commission_cost_usd
            review_reason = trade.exit_reason
        elif result.rejections:
            raw_rejection_code = result.rejections[0].code.value
    review = review_n1_observation(
        release.new_york_date,
        supplied,
        exit_reason=review_reason,
    )
    return N1PilotRecord(
        release_id=release.release_id,
        new_york_date=release.new_york_date,
        qualifying_publication=_qualifies(release),
        reason_code=signal.reason_code,
        direction=signal.decision.direction.value,
        engine_ran=engine_ran,
        raw_exit_reason=raw_exit_reason,
        raw_rejection_code=raw_rejection_code,
        raw_stop_price=raw_stop_price,
        raw_entry_price=raw_entry_price,
        raw_net_pnl_usd=raw_net_pnl,
        raw_commission_usd=raw_commission,
        slippage_pips=slippage,
        quality=review.quality,
        ordinary_n1_time_exit=review.ordinary_n1_time_exit,
        missing_labels=review.missing_labels,
        evidence_class=EVIDENCE_CLASS,
    )


def record_labeled_slippage_runs(
    release: N1Release,
    bars: Sequence[QuoteBar],
) -> tuple[N1PilotRecord, ...]:
    """Three separately labeled runs. They are not one combined fill."""

    return tuple(
        record_pilot_observation(release, bars, slippage_pips=pips)
        for pips in LABELED_SLIPPAGE_PIPS
    )


def record_pilot(
    observations: Sequence[tuple[N1Release, Sequence[QuoteBar], float]],
) -> tuple[N1PilotRecord, ...]:
    """Record distinct approved releases. Two qualifying publications is the limit."""

    records: list[N1PilotRecord] = []
    seen_ids: set[str] = set()
    qualifying = 0
    for release, bars, slippage_pips in observations:
        if not isinstance(release, N1Release):
            raise TypeError("release must be an N1Release")
        if release.release_id in seen_ids:
            raise ValueError("duplicate release_id")
        if _qualifies(release) and qualifying >= 2:
            raise PilotWindowClosed("the two qualifying publications are already recorded")
        record = record_pilot_observation(release, bars, slippage_pips=slippage_pips)
        seen_ids.add(release.release_id)
        if record.qualifying_publication:
            qualifying += 1
        records.append(record)
    return tuple(records)


def _qualifies(release: N1Release) -> bool:
    approved = _APPROVED_WINDOWS.get(release.new_york_date)
    if approved is None or release.release_id != approved[0] or release.kind != approved[1]:
        return False
    if release.status != ReleaseStatus.PUBLISHED.value:
        return False
    return release.actual_release_utc == new_york_clock_utc(release.new_york_date, 8, 30)


def _require_approved_release(release: N1Release) -> None:
    approved = _APPROVED_WINDOWS.get(release.new_york_date)
    if approved is None or release.release_id != approved[0] or release.kind != approved[1]:
        raise PilotWindowClosed(
            "quote collection is limited to the 2026-12-04 Employment Situation "
            "and the 2026-12-10 CPI windows"
        )


def _require_labeled_slippage(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("slippage_pips must be a number")
    for allowed in LABELED_SLIPPAGE_PIPS:
        if value == allowed:
            return allowed
    raise ValueError("slippage must be one labeled pilot run: 0.5, 0.2, or 1.0")


def _require_timestamps_after_authorization(bars: Sequence[QuoteBar]) -> None:
    effective = datetime.fromisoformat(AUTHORIZATION_EFFECTIVE_UTC).astimezone(timezone.utc)
    for bar in bars:
        if bar.timestamp_utc <= effective:
            raise ValueError("bar timestamp is not strictly after the authorization timestamp")


def _require_window_keys(day: date, bars: Sequence[QuoteBar]) -> None:
    allowed = set(required_n1_observation_keys(day))
    allowed.add((new_york_clock_utc(day, 8, 35), TRADED_SYMBOL))
    for bar in bars:
        if (bar.timestamp_utc, bar.symbol) not in allowed:
            raise ValueError("bar is outside the approved N1 window")


def _pilot_config(bars: Sequence[QuoteBar], slippage_pips: float) -> BacktestConfig:
    start = min(bar.timestamp_utc for bar in bars)
    end = max(bar.timestamp_utc for bar in bars)
    return BacktestConfig(
        starting_equity_usd=PILOT_ACCOUNTING_EQUITY_USD,
        slippage_pips=slippage_pips,
        risk_config=RiskConfig(),
        commission_model=hypothetical_published_commission_model(),
        financing_model=ZeroFinancing(),
        processed_data_manifest_id="n1-v0-prospective-supplied-bars",
        schema_version="fmp-n1-v0-prospective-pilot",
        timeframe="1m",
        requested_start_utc=start,
        requested_end_utc=end,
        code_commit=FROZEN_SIGNAL_COMMIT,
        decision_config={
            "rule_id": RULE_ID,
            "rule_name": RULE_NAME,
            "cost_package": "hypothetical_quote_spread_plus_published_commission",
            "cost_package_label": HYPOTHETICAL_COST_LABEL,
            "slippage": "one_adverse_pips_value_per_run",
            "evidence_class": EVIDENCE_CLASS,
            "frozen_signal_commit": FROZEN_SIGNAL_COMMIT,
            "authorization_commit": AUTHORIZATION_COMMIT,
        },
        execution_timing_mode=NEXT_SUPPLIED_BAR,
    )


def _repo_root(repo_root: Path | None) -> Path:
    if repo_root is not None:
        return repo_root
    return Path(__file__).resolve().parents[3]


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()
