from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2015_execution_authorization import (
    require_2015_execution_authorized,
)
from .annual_pattern_catalogue_2015_replacement_execution_authorization import (
    require_2015_replacement_execution_authorized,
)
from .annual_pattern_catalogue_2015_run377_execution_authorization import (
    require_2015_run377_execution_authorized,
)
from .annual_pattern_catalogue_2016_runtime_authorization import (
    require_2016_execution_authorized,
)
from .annual_pattern_catalogue_2017_runtime_authorization import (
    require_2017_execution_authorized,
)
from .annual_pattern_catalogue_2018_runtime_authorization import (
    require_2018_execution_authorized,
)
from .annual_pattern_catalogue_adapter import (
    AdaptedAnnualCatalogueSegmentInputs,
    adapt_verified_annual_catalogue_segment,
)
from .annual_pattern_catalogue_evidence import compile_cell_evidence
from .annual_pattern_catalogue_loader import (
    load_verified_annual_catalogue_segment_from_indexes,
)
from .annual_pattern_catalogue_miner import (
    AnnualCatalogueCellResult,
    mine_annual_catalogue_cell,
)
from .pattern_protocol import HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


ANNUAL_CATALOGUE_RUNTIME_WIRING_DECISION = "DEC-475"
ANNUAL_CATALOGUE_RUNTIME_WIRING_VERSION = (
    "fmp-annual-pattern-catalogue-runtime-wiring-v1"
)
SOURCE_ADAPTER_DECISION = "DEC-474"
SOURCE_ADAPTER_MERGE_SHA = "d88d5bb2f5d1f76278c4d588136bbcc5e65731a7"

HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED = False
STRATEGY_V1_SYNTHESIS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


@dataclass(frozen=True, slots=True)
class LockedAnnualCatalogueCellProduct:
    annual_segment_label: str
    symbol: str
    timeframe: str
    horizon_minutes: int
    adapted_inputs: AdaptedAnnualCatalogueSegmentInputs
    result: AnnualCatalogueCellResult
    evidence: Mapping[str, object]
    catalogue_payload_bytes: bytes


def _validate_commit(value: object, *, field: str = "code_commit") -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_cell(symbol: str, timeframe: str, horizon_minutes: int) -> None:
    if symbol not in SYMBOLS:
        raise ValueError("DEC-475 unsupported symbol")
    if timeframe not in TIMEFRAMES:
        raise ValueError("DEC-475 unsupported timeframe")
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("DEC-475 unsupported horizon")


def _workflow_dispatch_inputs_from_event() -> tuple[str | None, int | None]:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        return None, None
    try:
        value = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PermissionError("annual catalogue workflow dispatch metadata is invalid") from exc
    if not isinstance(value, Mapping):
        raise PermissionError("annual catalogue workflow dispatch metadata is malformed")
    inputs = value.get("inputs")
    if not isinstance(inputs, Mapping):
        return None, None
    segment = inputs.get("annual_segment_label")
    raw_previous = inputs.get("previous_annual_freeze_run_id")
    previous: int | None = None
    if isinstance(raw_previous, str) and raw_previous:
        try:
            previous = int(raw_previous)
        except ValueError as exc:
            raise PermissionError(
                "annual catalogue previous freeze run id is invalid"
            ) from exc
    return (segment if isinstance(segment, str) else None), previous


def _workflow_run_identity() -> tuple[int | None, int | None]:
    raw_number = os.environ.get("GITHUB_RUN_NUMBER")
    raw_attempt = os.environ.get("GITHUB_RUN_ATTEMPT")
    try:
        run_number = int(raw_number) if raw_number is not None else None
        run_attempt = int(raw_attempt) if raw_attempt is not None else None
    except ValueError as exc:
        raise PermissionError("DEC-493 workflow run identity is invalid") from exc
    return run_number, run_attempt


def require_historical_catalogue_execution_authorized(
    *,
    code_commit: str,
    annual_segment_label: str | None = None,
    run_number: int | None = None,
    run_attempt: int | None = None,
    previous_annual_freeze_run_id: int | None = None,
) -> None:
    code_commit = _validate_commit(code_commit)

    event_segment, event_previous_freeze_run_id = (
        _workflow_dispatch_inputs_from_event()
    )
    segment = annual_segment_label or event_segment
    env_run_number, env_run_attempt = _workflow_run_identity()
    effective_run_number = run_number if run_number is not None else env_run_number
    effective_run_attempt = run_attempt if run_attempt is not None else env_run_attempt
    effective_previous_freeze_run_id = (
        previous_annual_freeze_run_id
        if previous_annual_freeze_run_id is not None
        else event_previous_freeze_run_id
    )

    if (
        segment is not None
        and effective_run_number is not None
        and effective_run_attempt is not None
    ):
        if segment == "2018" and effective_run_number == 380:
            if effective_previous_freeze_run_id is None:
                raise PermissionError(
                    "DEC-547 2018 execution requires previous annual freeze run id"
                )
            require_2018_execution_authorized(
                annual_segment_label=segment,
                code_commit=code_commit,
                run_number=effective_run_number,
                run_attempt=effective_run_attempt,
                previous_annual_freeze_run_id=effective_previous_freeze_run_id,
            )
            return
        if segment == "2017" and effective_run_number == 379:
            if effective_previous_freeze_run_id is None:
                raise PermissionError(
                    "DEC-536 2017 execution requires previous annual freeze run id"
                )
            require_2017_execution_authorized(
                annual_segment_label=segment,
                code_commit=code_commit,
                run_number=effective_run_number,
                run_attempt=effective_run_attempt,
                previous_annual_freeze_run_id=effective_previous_freeze_run_id,
            )
            return
        if segment == "2016" and effective_run_number == 378:
            if effective_previous_freeze_run_id is None:
                raise PermissionError(
                    "DEC-505 2016 execution requires previous annual freeze run id"
                )
            require_2016_execution_authorized(
                annual_segment_label=segment,
                code_commit=code_commit,
                run_number=effective_run_number,
                run_attempt=effective_run_attempt,
                previous_annual_freeze_run_id=effective_previous_freeze_run_id,
            )
            return
        if effective_run_number == 376:
            require_2015_replacement_execution_authorized(
                annual_segment_label=segment,
                code_commit=code_commit,
                run_number=effective_run_number,
                run_attempt=effective_run_attempt,
            )
            return
        if effective_run_number == 377:
            require_2015_run377_execution_authorized(
                annual_segment_label=segment,
                code_commit=code_commit,
                run_number=effective_run_number,
                run_attempt=effective_run_attempt,
            )
            return
        require_2015_execution_authorized(
            annual_segment_label=segment,
            code_commit=code_commit,
            run_number=effective_run_number,
            run_attempt=effective_run_attempt,
        )
        return

    if not HISTORICAL_ARTIFACT_READ_AUTHORIZED:
        raise PermissionError(
            "DEC-475 annual catalogue historical artifact reads remain locked"
        )
    if not HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED:
        raise PermissionError(
            "DEC-475 annual catalogue historical execution remains locked"
        )
    if not HISTORICAL_RESULT_PRODUCTION_AUTHORIZED:
        raise PermissionError(
            "DEC-475 annual catalogue historical result production remains locked"
        )


def run_locked_annual_catalogue_cell(
    *,
    feature_root: Path,
    outcome_root: Path,
    feature_evidence_path: Path,
    outcome_evidence_path: Path,
    annual_segment_label: str,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    code_commit: str,
) -> LockedAnnualCatalogueCellProduct:
    # This gate must remain before every filesystem-backed historical read.
    require_historical_catalogue_execution_authorized(
        code_commit=code_commit,
        annual_segment_label=annual_segment_label,
    )
    _validate_cell(symbol, timeframe, horizon_minutes)

    bundle = load_verified_annual_catalogue_segment_from_indexes(
        feature_root=Path(feature_root),
        outcome_root=Path(outcome_root),
        feature_evidence_path=Path(feature_evidence_path),
        outcome_evidence_path=Path(outcome_evidence_path),
        symbol=symbol,
        timeframe=timeframe,
        annual_segment_label=annual_segment_label,
    )
    adapted = adapt_verified_annual_catalogue_segment(bundle)
    result = mine_annual_catalogue_cell(
        adapted.feature_observations,
        adapted.outcome_observations,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        annual_segment_label=annual_segment_label,
    )
    evidence, payload_bytes = compile_cell_evidence(
        result,
        code_commit=_validate_commit(code_commit),
        processed_manifest_sha256=adapted.processed_manifest_sha256,
        feature_manifest_sha256=adapted.feature_manifest_sha256,
        outcome_manifest_sha256=adapted.outcome_manifest_sha256,
        feature_evidence_fingerprint=adapted.feature_evidence_fingerprint,
        outcome_evidence_fingerprint=adapted.outcome_evidence_fingerprint,
    )
    return LockedAnnualCatalogueCellProduct(
        annual_segment_label=annual_segment_label,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        adapted_inputs=adapted,
        result=result,
        evidence=evidence,
        catalogue_payload_bytes=payload_bytes,
    )


def runtime_wiring_contract_payload() -> dict[str, object]:
    return {
        "decision": ANNUAL_CATALOGUE_RUNTIME_WIRING_DECISION,
        "version": ANNUAL_CATALOGUE_RUNTIME_WIRING_VERSION,
        "source_adapter_decision": SOURCE_ADAPTER_DECISION,
        "source_adapter_merge_sha": SOURCE_ADAPTER_MERGE_SHA,
        "call_order": [
            "require_historical_catalogue_execution_authorized",
            "load_verified_annual_catalogue_segment_from_indexes",
            "adapt_verified_annual_catalogue_segment",
            "mine_annual_catalogue_cell",
            "compile_cell_evidence",
        ],
        "authorization_gate_precedes_historical_read": True,
        "unit_of_work": (
            "annual_segment_x_symbol_x_timeframe_x_horizon"
        ),
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": (
            HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED
        ),
        "historical_result_production_authorized": (
            HISTORICAL_RESULT_PRODUCTION_AUTHORIZED
        ),
        "cross_year_result_production_authorized": (
            CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED
        ),
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "workflow_installed": False,
        "workflow_dispatch_authorized": False,
        "next_gate": "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_PLAN",
    }


__all__ = [
    "ANNUAL_CATALOGUE_RUNTIME_WIRING_DECISION",
    "ANNUAL_CATALOGUE_RUNTIME_WIRING_VERSION",
    "HISTORICAL_ARTIFACT_READ_AUTHORIZED",
    "HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED",
    "HISTORICAL_RESULT_PRODUCTION_AUTHORIZED",
    "LockedAnnualCatalogueCellProduct",
    "require_historical_catalogue_execution_authorized",
    "run_locked_annual_catalogue_cell",
    "runtime_wiring_contract_payload",
]
