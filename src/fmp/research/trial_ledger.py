"""Append-only research trial ledger.

The human-readable registry remains ``docs/experiment-log.md``. This ledger
stores the fields needed to count a trial without pretending that every
historical heading has been transcribed. Unknown trial counts stay null.
Data from 2015 through 2022 is explored research, not untouched validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

REQUIRED_FIELDS = (
    "trial_id",
    "recorded_on",
    "hypothesis",
    "version",
    "parameters",
    "data_exposure",
    "cost_assumptions",
    "source_commit",
    "outcome",
    "statistical_evidence",
)

LEDGER_PATH = Path(__file__).resolve().parents[3] / "docs" / "trial-ledger.jsonl"


def _exposure(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("data_exposure must be an object")
    exposure = dict(value)
    if "untouched_validation" not in exposure or not isinstance(exposure["untouched_validation"], bool):
        raise ValueError("data_exposure.untouched_validation must be true or false")
    if exposure.get("overlaps_2015_2022") and exposure["untouched_validation"]:
        raise ValueError("2015-2022 overlap cannot be marked as untouched validation")
    if "overlaps_2015_2022" not in exposure:
        raise ValueError("data_exposure.overlaps_2015_2022 must be stated")
    return exposure


def _evidence(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("statistical_evidence must be an object")
    evidence = dict(value)
    if "available" not in evidence or not isinstance(evidence["available"], bool):
        raise ValueError("statistical_evidence.available must be true or false")
    if "trial_count" not in evidence:
        raise ValueError("statistical_evidence.trial_count must be present and may be null")
    count = evidence["trial_count"]
    if count is not None and (isinstance(count, bool) or not isinstance(count, int) or count < 0):
        raise ValueError("trial_count must be a non-negative integer or null")
    return evidence


def validate_trial(record: Mapping[str, object]) -> dict[str, object]:
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    if missing:
        raise ValueError("missing trial fields: " + ", ".join(missing))
    normalized: dict[str, object] = {}
    for field in REQUIRED_FIELDS:
        value = record[field]
        if field == "data_exposure":
            value = _exposure(value)
        elif field == "statistical_evidence":
            value = _evidence(value)
        elif field in {"parameters"}:
            if not isinstance(value, Mapping):
                raise ValueError("parameters must be an object")
            value = dict(value)
        elif not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        normalized[field] = value
    return normalized


def load_trials(path: Path | None = None) -> tuple[dict[str, object], ...]:
    ledger = LEDGER_PATH if path is None else path
    if not ledger.exists():
        return ()
    text = ledger.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        raise ValueError("ledger must end with a newline")
    rows = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"blank line in ledger at {line_number}")
        rows.append(validate_trial(json.loads(line)))
    return tuple(rows)


def append_trial(record: Mapping[str, object], path: Path | None = None) -> dict[str, object]:
    """Append one record. Existing lines are not rewritten."""
    ledger = LEDGER_PATH if path is None else path
    normalized = validate_trial(record)
    existing = load_trials(ledger)
    if any(row["trial_id"] == normalized["trial_id"] for row in existing):
        raise ValueError(f"trial_id already recorded: {normalized['trial_id']}")
    line = json.dumps(normalized, sort_keys=True, ensure_ascii=True) + "\n"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(line)
    return normalized


def documented_backfill() -> tuple[dict[str, object], ...]:
    """Records whose fields are supported by the repository documents.

    This is not a census of ``docs/experiment-log.md``. The programme-wide
    trial count is unknown.
    """
    return (
        {
            "trial_id": "CENSUS-20261117",
            "recorded_on": "2026-11-17",
            "hypothesis": "The experiment log is already a complete counted trial registry.",
            "version": "not-a-trial",
            "parameters": {"scope": "docs/experiment-log.md was not fully transcribed"},
            "data_exposure": {
                "overlaps_2015_2022": True,
                "untouched_validation": False,
                "role": "explored_in_multiple_experiments_not_untouched_validation",
            },
            "cost_assumptions": "not applicable",
            "source_commit": "53e203133bbc141b2f48c7b8b8241d56b35166a3 plus uncommitted measurement source",
            "outcome": "NOT_A_RESULT. The unlisted remainder of the experiment log is unknown, not zero.",
            "statistical_evidence": {
                "available": False,
                "trial_count": None,
                "note": "Duplicate experiment IDs exist in the log. A heading count is not a validated trial count.",
            },
        },
        {
            "trial_id": "EXP-20260914-001",
            "recorded_on": "2026-09-14",
            "hypothesis": "A confirmed early-London break of the pre-London range can overcome historical spread and adverse slippage under fixed risk.",
            "version": "session_breakout buffer {0,2,5} x target {0.5,1.0,1.5}",
            "parameters": {
                "pairs": "EURUSD, GBPUSD, USDJPY",
                "timeframes": "5m, 15m, 1h",
                "configurations_per_pair_timeframe": 9,
            },
            "data_exposure": {
                "overlaps_2015_2022": True,
                "untouched_validation": False,
                "development": "2015-01-01 through 2020-12-31",
                "validation": "2021-01-01 through 2023-12-31",
                "final_test_touched": False,
            },
            "cost_assumptions": "Historical bid/ask spread, zero commission, zero financing, adverse slippage of 0.2, 0.5 and 1.0 pips per fill.",
            "source_commit": "cc01929b80cbd1d5619de8476caa8f3d3410262e",
            "outcome": "PASS for promotion of USDJPY 15m buffer 5 target 1.5 as a Phase 4 candidate. The 1.0-pip stress does not stay positive on both splits.",
            "statistical_evidence": {
                "available": True,
                "trial_count": 81,
                "result_rows": 486,
                "note": "81 is 9 configurations times 3 pairs times 3 timeframes. 486 rows are that grid times two splits times three slippage levels. This is not the programme-wide count.",
            },
        },
        {
            "trial_id": "EXP-20260915-008",
            "recorded_on": "2026-09-15",
            "hypothesis": "The frozen USDJPY 15m session-breakout candidate keeps a positive after-cost expectancy on the predeclared forward windows.",
            "version": "USDJPY 15m session_breakout buffer_pips=5 target_range_multiple=1.5",
            "parameters": {
                "stage1_trades": 122,
                "stage2_trades": 199,
                "window_start_equity_usd": 100000,
                "risk_fraction": 0.0025,
            },
            "data_exposure": {
                "overlaps_2015_2022": False,
                "untouched_validation": False,
                "scored_window": "2024-01-01 through 2026-08-20",
                "note": "2024 was the selection window. 2025-01-01 through 2026-08-21 exclusive was scored. Not an untouched holdout.",
            },
            "cost_assumptions": "Historical bid/ask spread already in the fill. Zero commission. Zero financing. Adverse slippage 0.2, 0.5 and 1.0 pips per fill.",
            "source_commit": "a1f8a0466463c79fdbceb9d6ebad9e3ea809474d",
            "outcome": "Stage 2 status PHASE7_PROMOTE_TO_SHADOW_DESIGN at the frozen 0.2 and 0.5 pip gates. Stage 2 expectancy at 1.0 pip is negative, so the later edge-first doubling check fails.",
            "statistical_evidence": {
                "available": True,
                "trial_count": 1,
                "stage2_expectancy_usd": {"0.2": 3.8054, "0.5": 1.3175, "1.0": -2.8247},
                "trade_level_r_series": False,
                "note": "The trial count is the one frozen candidate carried into Phase 7, not the earlier 81-configuration search. Aggregate expectancy is not a trade-level distribution.",
            },
        },
        {
            "trial_id": "EXP-20261117-001",
            "recorded_on": "2026-11-17",
            "hypothesis": "A repeatable after-cost edge under FMP constraints can support a 100 percent net return within 30 calendar days.",
            "version": "return_vs_ruin DEC-627",
            "parameters": {"scenarios": "S1-S11 printed study assumptions", "risk_fraction_searched": False},
            "data_exposure": {
                "overlaps_2015_2022": False,
                "untouched_validation": False,
                "market_data_opened": False,
            },
            "cost_assumptions": "Study assumption of 0.08R round trip. Not a broker-page table.",
            "source_commit": "uncommitted DEC-627 source on 53e203133bbc141b2f48c7b8b8241d56b35166a3",
            "outcome": "INCONCLUSIVE. Exact printed scenarios reproduce within rounding. The documented Phase 7 aggregate fails the edge-first check. No trading authority.",
            "statistical_evidence": {
                "available": False,
                "trial_count": None,
                "note": "The scenario table is hypothetical. It is not a market trial count.",
            },
        },
        {
            "trial_id": "EXP-20261117-002",
            "recorded_on": "2026-11-17",
            "hypothesis": "A source-backed retail cost changes the after-cost expectancy of the documented Phase 7 candidate enough to identify its 30-day doubling and loss probabilities.",
            "version": "retail_costs DEC-628",
            "parameters": {
                "symbols": "EURUSD, GBPUSD, USDJPY",
                "brokers_quoted": "OANDA US spread-only, IC Markets EU Raw and Standard, Pepperstone Razor",
                "hourly_spreads_invented": False,
            },
            "data_exposure": {
                "overlaps_2015_2022": False,
                "untouched_validation": False,
                "market_data_opened": False,
                "note": "Phase 7 aggregates were re-read. No new historical sample was opened.",
            },
            "cost_assumptions": "Published broker quotations accessed 2026-11-17, plus labeled slippage assumptions. Advertised minimum spreads are not treated as typical. Phase 7 bid/ask spread is not charged again.",
            "source_commit": "uncommitted DEC-628 source on 53e203133bbc141b2f48c7b8b8241d56b35166a3",
            "outcome": "INCONCLUSIVE. Published costs are recorded. Phase 7 doubling and loss probabilities remain unavailable because the evidence is aggregate. No edge is demonstrated.",
            "statistical_evidence": {
                "available": False,
                "trial_count": None,
                "reliable_probability_estimate": False,
                "note": "Stage 2 mean R at 0.2, 0.5 and 1.0 pip is an aggregate. Stop distance and overnight share are not in that aggregate.",
            },
        },
    )
