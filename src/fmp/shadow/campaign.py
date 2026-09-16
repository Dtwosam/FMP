from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Mapping, Sequence
from zoneinfo import ZoneInfo

from .contracts import (
    BREAKOUT_BUFFER_PIPS,
    FMP_SYMBOL,
    LIVENESS_TIMEOUT_SECONDS,
    PHASE7_CHECKPOINT_SHA,
    PHASE7_CHECKPOINT_TAG,
    PHASE8_EXPERIMENT_ID,
    PRACTICE_STREAM_HOST,
    PROVIDER_INSTRUMENT,
    QUOTE_DEADLINE_SECONDS,
    SLIPPAGE_SCENARIOS,
    STARTING_EQUITY_USD,
    STRATEGY_FAMILY,
    TARGET_RANGE_MULTIPLE,
    TIMEFRAME,
)


LONDON = ZoneInfo("Europe/London")
FULL_MARKET_CLOSURE_REASON = "PROVIDER_DOCUMENTED_FULL_MARKET_CLOSURE"
GATING_SLIPPAGE_SCENARIOS = (0.2, 0.5)

MINIMUM_COMPLETED_SCORABLE_TRADES_0P2 = 40
MINIMUM_ELAPSED_CALENDAR_WEEKS = 8
MINIMUM_FULLY_OBSERVED_LONDON_DATES = 30
MINIMUM_VALID_DATE_COVERAGE_FRACTION = 0.90
MAXIMUM_PROCESSING_LATENCY_P99_MS = 250.0
MAXIMUM_QUOTE_DELAY_SECONDS = 5.0
MAXIMUM_SPREAD_PARITY_DELTA_PIPS = 0.5
MAXIMUM_DRAWDOWN_FRACTION = 0.05
MINIMUM_NET_RETURN = 0.0
MINIMUM_EXPECTANCY_USD = 0.0
MINIMUM_PROFIT_FACTOR = 1.0

_REFERENCE_METHOD_VERSION = "fmp-phase8-spread-reference-v1"
_PHASE7_EXPERIMENT = "EXP-20260915-008"
_PHASE7_OUTCOME = "PASS / PROMOTE"
_PHASE7_STAGE2_RUN_ID = 35015277625
_PHASE2_ARTIFACT_ID = 10327600628
_PHASE2_ZIP_SHA256 = "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72"
_PROCESSED_MANIFEST_SHA256 = "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d"


def _require_utc(value: datetime, *, field: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError(f"{field} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


def _require_sha256(value: str, *, field: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a SHA-256 digest")
    if any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")


def _require_commit(value: str) -> None:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError("code_commit must be a 40-character git SHA")
    if any(character not in "0123456789abcdef" for character in value):
        raise ValueError("code_commit must be lowercase hexadecimal")


def _iso_utc(value: datetime) -> str:
    _require_utc(value, field="timestamp")
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ").replace(".000000Z", "Z")


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


def _load_reference(reference_dir: Path, *, code_commit: str) -> tuple[Mapping[str, object], str]:
    reference_dir = Path(reference_dir)
    json_path = reference_dir / "reference.json"
    sha_path = reference_dir / "reference.sha256"
    try:
        payload = json_path.read_bytes()
        expected_digest = sha_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ValueError("Phase 8 reference artifact is incomplete") from exc
    _require_sha256(expected_digest, field="reference digest")
    actual_digest = hashlib.sha256(payload).hexdigest()
    if actual_digest != expected_digest:
        raise ValueError("Phase 8 reference digest mismatch")
    try:
        record = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError("Phase 8 reference is not valid JSON") from exc
    if not isinstance(record, dict):
        raise ValueError("Phase 8 reference root must be an object")

    exact = {
        "method_version": _REFERENCE_METHOD_VERSION,
        "phase7_checkpoint_tag": PHASE7_CHECKPOINT_TAG,
        "phase7_checkpoint_sha": PHASE7_CHECKPOINT_SHA,
        "phase7_experiment": _PHASE7_EXPERIMENT,
        "phase7_outcome": _PHASE7_OUTCOME,
        "phase7_stage2_run_id": _PHASE7_STAGE2_RUN_ID,
        "phase2_artifact_id": _PHASE2_ARTIFACT_ID,
        "phase2_zip_sha256": _PHASE2_ZIP_SHA256,
        "processed_manifest_sha256": _PROCESSED_MANIFEST_SHA256,
        "code_commit": code_commit,
        "historical_slippage_pips": 0.2,
    }
    for key, expected in exact.items():
        if record.get(key) != expected:
            raise ValueError(f"Phase 8 reference identity mismatch: {key}")

    strategy = record.get("strategy")
    if not isinstance(strategy, Mapping):
        raise ValueError("Phase 8 reference strategy identity is missing")
    expected_strategy = {
        "id": STRATEGY_FAMILY,
        "symbol": FMP_SYMBOL,
        "timeframe": TIMEFRAME,
        "buffer_pips": BREAKOUT_BUFFER_PIPS,
        "target_range_multiple": TARGET_RANGE_MULTIPLE,
    }
    if dict(strategy) != expected_strategy:
        raise ValueError("Phase 8 reference strategy identity mismatch")
    return record, actual_digest


@dataclass(frozen=True, slots=True)
class ProviderClosure:
    london_date: date
    reason: str
    documentation: str
    recorded_at_utc: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.london_date, date) or isinstance(self.london_date, datetime):
            raise TypeError("london_date must be a date")
        if self.reason != FULL_MARKET_CLOSURE_REASON:
            raise ValueError("provider exclusion must be a documented full-market closure")
        if not isinstance(self.documentation, str) or not self.documentation.strip():
            raise ValueError("full-market closure documentation must be non-empty")
        _require_utc(self.recorded_at_utc, field="recorded_at_utc")


@dataclass(frozen=True, slots=True)
class CampaignEvidenceSummary:
    completed_scorable_trades_0p2: int
    first_observation_utc: datetime
    last_observation_utc: datetime
    fully_observed_london_dates: int
    all_scored_trades_have_complete_path: bool
    all_three_scenarios_share_candidate_sequence: bool

    def __post_init__(self) -> None:
        if (
            isinstance(self.completed_scorable_trades_0p2, bool)
            or not isinstance(self.completed_scorable_trades_0p2, int)
            or self.completed_scorable_trades_0p2 < 0
        ):
            raise ValueError("completed_scorable_trades_0p2 must be a non-negative integer")
        if (
            isinstance(self.fully_observed_london_dates, bool)
            or not isinstance(self.fully_observed_london_dates, int)
            or self.fully_observed_london_dates < 0
        ):
            raise ValueError("fully_observed_london_dates must be a non-negative integer")
        _require_utc(self.first_observation_utc, field="first_observation_utc")
        _require_utc(self.last_observation_utc, field="last_observation_utc")
        if self.last_observation_utc < self.first_observation_utc:
            raise ValueError("last_observation_utc must not precede first_observation_utc")
        if type(self.all_scored_trades_have_complete_path) is not bool:
            raise TypeError("all_scored_trades_have_complete_path must be bool")
        if type(self.all_three_scenarios_share_candidate_sequence) is not bool:
            raise TypeError("all_three_scenarios_share_candidate_sequence must be bool")


def acceptance_thresholds() -> dict[str, object]:
    return {
        "minimum_completed_scorable_trades_0p2": MINIMUM_COMPLETED_SCORABLE_TRADES_0P2,
        "minimum_elapsed_calendar_weeks": MINIMUM_ELAPSED_CALENDAR_WEEKS,
        "minimum_fully_observed_london_dates": MINIMUM_FULLY_OBSERVED_LONDON_DATES,
        "minimum_valid_date_coverage_fraction": MINIMUM_VALID_DATE_COVERAGE_FRACTION,
        "maximum_processing_latency_p99_ms": MAXIMUM_PROCESSING_LATENCY_P99_MS,
        "maximum_quote_delay_seconds": MAXIMUM_QUOTE_DELAY_SECONDS,
        "maximum_spread_parity_delta_pips": MAXIMUM_SPREAD_PARITY_DELTA_PIPS,
        "minimum_net_return_exclusive": MINIMUM_NET_RETURN,
        "minimum_expectancy_usd_exclusive": MINIMUM_EXPECTANCY_USD,
        "minimum_profit_factor_exclusive": MINIMUM_PROFIT_FACTOR,
        "maximum_drawdown_fraction": MAXIMUM_DRAWDOWN_FRACTION,
        "stream_liveness_timeout_seconds": LIVENESS_TIMEOUT_SECONDS,
    }


def register_campaign(
    *,
    reference_dir: Path,
    campaign_dir: Path,
    code_commit: str,
    campaign_start_utc: datetime,
) -> dict[str, object]:
    _require_commit(code_commit)
    _require_utc(campaign_start_utc, field="campaign_start_utc")
    campaign_dir = Path(campaign_dir)
    registration_path = campaign_dir / "registration.json"
    if registration_path.exists():
        raise FileExistsError("Phase 8 campaign registration already exists")

    reference, reference_digest = _load_reference(Path(reference_dir), code_commit=code_commit)
    first_london_date = campaign_start_utc.astimezone(LONDON).date()
    record: dict[str, object] = {
        "registration_version": 1,
        "phase8_experiment": PHASE8_EXPERIMENT_ID,
        "campaign_start_utc": _iso_utc(campaign_start_utc),
        "first_london_date": first_london_date.isoformat(),
        "code_commit": code_commit,
        "reference_sha256": reference_digest,
        "reference_identity": {
            "method_version": reference["method_version"],
            "phase7_checkpoint_tag": reference["phase7_checkpoint_tag"],
            "phase7_checkpoint_sha": reference["phase7_checkpoint_sha"],
            "phase7_stage2_run_id": reference["phase7_stage2_run_id"],
            "phase2_artifact_id": reference["phase2_artifact_id"],
            "processed_manifest_sha256": reference["processed_manifest_sha256"],
        },
        "provider": "OANDA_PRACTICE_PRICING_STREAM",
        "host": PRACTICE_STREAM_HOST,
        "path_template": "/v3/accounts/{account_id}/pricing/stream",
        "instrument": PROVIDER_INSTRUMENT,
        "strategy": {
            "id": STRATEGY_FAMILY,
            "symbol": FMP_SYMBOL,
            "timeframe": TIMEFRAME,
            "buffer_pips": BREAKOUT_BUFFER_PIPS,
            "target_range_multiple": TARGET_RANGE_MULTIPLE,
        },
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "gating_slippage_scenarios": list(GATING_SLIPPAGE_SCENARIOS),
        "starting_equity_usd": STARTING_EQUITY_USD,
        "acceptance_thresholds": acceptance_thresholds(),
    }
    payload = _canonical_bytes(record)
    campaign_dir.mkdir(parents=True, exist_ok=True)
    try:
        with registration_path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
    except FileExistsError:
        raise FileExistsError("Phase 8 campaign registration already exists") from None
    return record


def denominator_london_dates(
    *,
    first_london_date: date,
    review_cutoff_utc: datetime,
    provider_closures: Sequence[ProviderClosure] = (),
) -> tuple[date, ...]:
    if not isinstance(first_london_date, date) or isinstance(first_london_date, datetime):
        raise TypeError("first_london_date must be a date")
    _require_utc(review_cutoff_utc, field="review_cutoff_utc")
    cutoff_date = review_cutoff_utc.astimezone(LONDON).date()
    if cutoff_date < first_london_date:
        raise ValueError("review cutoff precedes registered campaign start")

    excluded: set[date] = set()
    for closure in provider_closures:
        if not isinstance(closure, ProviderClosure):
            raise TypeError("provider_closures must contain ProviderClosure values")
        if closure.london_date in excluded:
            raise ValueError("duplicate provider full-market closure date")
        london_midnight = datetime.combine(
            closure.london_date, time.min, tzinfo=LONDON
        ).astimezone(timezone.utc)
        if closure.recorded_at_utc >= london_midnight:
            raise ValueError("provider full-market closure must be recorded before the London date begins")
        excluded.add(closure.london_date)

    dates: list[date] = []
    cursor = first_london_date
    while cursor <= cutoff_date:
        if cursor.weekday() < 5 and cursor not in excluded:
            dates.append(cursor)
        cursor += timedelta(days=1)
    return tuple(dates)


def minimum_review_evidence_met(summary: CampaignEvidenceSummary) -> bool:
    if not isinstance(summary, CampaignEvidenceSummary):
        raise TypeError("summary must be CampaignEvidenceSummary")
    elapsed = summary.last_observation_utc - summary.first_observation_utc
    return (
        summary.completed_scorable_trades_0p2 >= MINIMUM_COMPLETED_SCORABLE_TRADES_0P2
        and elapsed >= timedelta(weeks=MINIMUM_ELAPSED_CALENDAR_WEEKS)
        and summary.fully_observed_london_dates >= MINIMUM_FULLY_OBSERVED_LONDON_DATES
        and summary.all_scored_trades_have_complete_path
        and summary.all_three_scenarios_share_candidate_sequence
    )


__all__ = [
    "CampaignEvidenceSummary",
    "FULL_MARKET_CLOSURE_REASON",
    "GATING_SLIPPAGE_SCENARIOS",
    "ProviderClosure",
    "acceptance_thresholds",
    "denominator_london_dates",
    "minimum_review_evidence_met",
    "register_campaign",
]
