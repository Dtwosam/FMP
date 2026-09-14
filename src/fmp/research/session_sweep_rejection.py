from __future__ import annotations

import hashlib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.backtest.engine import BacktestConfig, run_backtest
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.research.adapter import candidate_to_decision
from fmp.research.contracts import allowed_split
from fmp.research.data import load_processed_bars
from fmp.research.reporting import compute_research_metrics
from fmp.risk import RiskConfig
from fmp.strategies.contracts import SignalCandidate
from fmp.strategies.session_sweep_rejection import (
    SessionSweepRejectionConfig,
    generate_session_sweep_rejection_candidates,
)


SESSION_SWEEP_REJECTION_GRID = (0, 2, 5)
SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)
STARTING_EQUITY_USD = 100_000.0
REQUESTED_RISK_FRACTION = 0.0025
SESSION_SWEEP_REJECTION_FAMILY_ID = "session_sweep_rejection"
SESSION_SWEEP_REJECTION_STRATEGY_VERSION = "fmp-session-sweep-rejection-v1"
RESULT_PROTOCOL = "fmp-phase4-session-sweep-rejection-grid-v1"


def _utc_start(day) -> datetime:
    return datetime(day.year, day.month, day.day, tzinfo=timezone.utc)


def _candidate_sha256(candidates: tuple[SignalCandidate, ...]) -> str:
    digest = hashlib.sha256()
    for candidate in candidates:
        payload = candidate.stable_json_bytes()
        digest.update(len(payload).to_bytes(8, byteorder="big", signed=False))
        digest.update(payload)
    return digest.hexdigest()


def _adapt_candidates(candidates: tuple[SignalCandidate, ...]):
    decisions = []
    scheduled_exits = []
    for candidate in candidates:
        decision, scheduled_exit = candidate_to_decision(
            candidate,
            next_bar_timestamp_utc=candidate.signal_known_timestamp_utc,
            requested_risk_fraction=REQUESTED_RISK_FRACTION,
        )
        decisions.append(decision)
        if scheduled_exit is not None:
            scheduled_exits.append(scheduled_exit)
    return tuple(decisions), tuple(scheduled_exits)


def run_session_sweep_rejection_grid(
    *,
    dataset_root: Path,
    manifest_path: Path,
    symbol: str,
    timeframe: str,
    split_name: str,
    code_commit: str,
) -> dict[str, object]:
    split = allowed_split(split_name)
    if not code_commit.strip():
        raise ValueError("code_commit must be non-empty")

    manifest_bytes = Path(manifest_path).read_bytes()
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    loaded = load_processed_bars(
        dataset_root=Path(dataset_root),
        manifest_path=Path(manifest_path),
        symbol=symbol,
        timeframe=timeframe,
        split_name=split_name,
    )

    risk_config = RiskConfig()
    commission_model = ZeroCommission()
    financing_model = ZeroFinancing()
    configuration_rows: list[dict[str, object]] = []

    for buffer_pips in SESSION_SWEEP_REJECTION_GRID:
        strategy_config = SessionSweepRejectionConfig(
            buffer_pips=buffer_pips,
            timeframe=timeframe,
        )
        candidates = generate_session_sweep_rejection_candidates(
            loaded.bars,
            config=strategy_config,
        )
        candidate_sha256 = _candidate_sha256(candidates)
        decisions, scheduled_exits = _adapt_candidates(candidates)
        candidate_metadata = {
            candidate.candidate_id: dict(candidate.metadata)
            for candidate in candidates
        }
        candidate_reason_counts = dict(
            sorted(Counter(candidate.reason_code for candidate in candidates).items())
        )

        for slippage_pips in SLIPPAGE_SCENARIOS:
            backtest_config = BacktestConfig(
                starting_equity_usd=STARTING_EQUITY_USD,
                slippage_pips=slippage_pips,
                risk_config=risk_config,
                commission_model=commission_model,
                financing_model=financing_model,
                processed_data_manifest_id=manifest_sha256,
                schema_version=CANONICAL_SCHEMA_VERSION,
                timeframe=timeframe,
                requested_start_utc=_utc_start(split.start),
                requested_end_utc=_utc_start(split.end_exclusive),
                code_commit=code_commit,
                decision_config={
                    "family_id": SESSION_SWEEP_REJECTION_FAMILY_ID,
                    "strategy_version": SESSION_SWEEP_REJECTION_STRATEGY_VERSION,
                    "split_name": split_name,
                    "buffer_pips": buffer_pips,
                    "candidate_sha256": candidate_sha256,
                },
            )
            run = run_backtest(
                bars=loaded.bars,
                decisions=decisions,
                config=backtest_config,
                scheduled_exits=scheduled_exits,
            )
            metrics = compute_research_metrics(
                run,
                starting_equity_usd=STARTING_EQUITY_USD,
                requested_risk_fraction=REQUESTED_RISK_FRACTION,
                candidate_metadata=candidate_metadata,
                eligible_utc_dates=loaded.eligible_utc_dates,
            )
            configuration_rows.append(
                {
                    "buffer_pips": buffer_pips,
                    "slippage_pips": slippage_pips,
                    "requested_risk_fraction": REQUESTED_RISK_FRACTION,
                    "candidate_count": len(candidates),
                    "candidate_sha256": candidate_sha256,
                    "candidate_reason_counts": candidate_reason_counts,
                    "run_identity": dict(run.run_identity),
                    "metrics": metrics,
                }
            )

    return {
        "protocol": RESULT_PROTOCOL,
        "family_id": SESSION_SWEEP_REJECTION_FAMILY_ID,
        "strategy_version": SESSION_SWEEP_REJECTION_STRATEGY_VERSION,
        "symbol": symbol,
        "timeframe": timeframe,
        "split_name": split_name,
        "split_start": split.start,
        "split_end_exclusive": split.end_exclusive,
        "code_commit": code_commit,
        "processed_manifest_sha256": manifest_sha256,
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "starting_equity_usd": STARTING_EQUITY_USD,
        "requested_risk_fraction": REQUESTED_RISK_FRACTION,
        "excluded_incomplete_bar_count": loaded.excluded_incomplete_count,
        "eligible_utc_date_count": len(loaded.eligible_utc_dates),
        "configuration_rows": configuration_rows,
    }
