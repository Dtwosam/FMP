from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Mapping

import polars as pl

from . import market_learning_adapter as _predecessor
from .nan_null_repair_protocol import (
    EXP062_EXPERIMENT_ID,
    EXP062_REPAIR_PROTOCOL_DECISION,
    EXP062_REPAIR_PROTOCOL_VERSION,
    exp062_repair_protocol_fingerprint,
)
from .pattern_protocol import (
    CONTINUOUS_FEATURES,
    EXPERIMENT_ID as EXP061_EXPERIMENT_ID,
    protocol_fingerprint as exp061_protocol_fingerprint,
)


EXP062_ADAPTER_EVIDENCE_DECISION = "DEC-293"
EXP062_CELL_EVIDENCE_VERSION = 1
EXP062_CELL_EVIDENCE_PROTOCOL = "fmp-exp062-cell-evidence-v1"

DEC292_PROTOCOL_BLOB_SHA = "1d26da24134c825e2f405224316e1dd3136a38fb"
EXP061_ADAPTER_BLOB_SHA = "978a33554fad7e9d78b002778c4896be0af3333a"

HISTORICAL_RESULT_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def validate_exp062_adapter_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec292_protocol": (
            root / "src/fmp/discovery/nan_null_repair_protocol.py",
            DEC292_PROTOCOL_BLOB_SHA,
        ),
        "exp061_adapter": (
            root / "src/fmp/discovery/market_learning_adapter.py",
            EXP061_ADAPTER_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing EXP-062 adapter dependency: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(
                f"EXP-062 {label} Git blob mismatch: {sha} != {expected_sha}"
            )
        actual[label] = sha

    if EXP062_REPAIR_PROTOCOL_DECISION != "DEC-292":
        raise ValueError("EXP-062 repair protocol decision drift")
    if EXP062_EXPERIMENT_ID != "EXP-20260927-062":
        raise ValueError("EXP-062 experiment identity drift")

    return {
        "adapter_evidence_decision": EXP062_ADAPTER_EVIDENCE_DECISION,
        "dec292_protocol_blob_sha": actual["dec292_protocol"],
        "exp061_adapter_blob_sha": actual["exp061_adapter"],
        "repair_protocol_fingerprint": exp062_repair_protocol_fingerprint(),
        "historical_result_execution_authorized": False,
        "discovery_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def normalize_continuous_feature_value(value: object) -> object:
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def adapt_feature_frame(
    frame: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
) -> tuple[tuple[_predecessor.FeatureObservation, ...], str]:
    _predecessor._validate_cell_identity(symbol, timeframe)
    required = (
        *_predecessor._FEATURE_IDENTITY_COLUMNS,
        *CONTINUOUS_FEATURES,
        *_predecessor._SESSION_FLAG_COLUMNS,
    )
    _predecessor._require_columns(
        frame,
        required,
        label="EXP-062 feature frame",
    )
    processed_sha = _predecessor._validate_common_frame_identity(
        frame,
        symbol=symbol,
        timeframe=timeframe,
        label="EXP-062 feature frame",
    )

    unique = frame.select(
        pl.struct(["symbol", "timeframe", "bar_start_utc"]).n_unique()
    ).item()
    if unique != frame.height:
        raise ValueError("duplicate EXP-062 feature-frame identity")

    rows = frame.sort(["bar_start_utc"]).iter_rows(named=True)
    observations: list[_predecessor.FeatureObservation] = []
    seen: set[str] = set()
    for row in rows:
        available = _predecessor._require_utc(
            row["available_at_utc"],
            field="available_at_utc",
        )
        if not (
            _predecessor.EXP061_INPUT_START_UTC
            <= available
            < _predecessor.EXP061_INPUT_END_EXCLUSIVE_UTC
        ):
            raise ValueError(
                "EXP-062 feature adapter received row outside 2015-2022 input range"
            )
        observation_id = _predecessor._observation_id(row)
        if observation_id in seen:
            raise ValueError("duplicate EXP-062 adapted feature observation id")
        seen.add(observation_id)

        values = {
            name: normalize_continuous_feature_value(row[name])
            for name in CONTINUOUS_FEATURES
        }
        values.update(
            {
                name: row[name]
                for name in _predecessor._SESSION_FLAG_COLUMNS
            }
        )
        observations.append(
            _predecessor.FeatureObservation(
                observation_id=observation_id,
                symbol=symbol,
                timeframe=timeframe,
                available_at_utc=available,
                values=values,
            )
        )
    return tuple(observations), processed_sha


def adapt_market_learning_cell(
    *,
    feature_frame: pl.DataFrame,
    outcome_frame: pl.DataFrame,
    symbol: str,
    timeframe: str,
) -> _predecessor.AdaptedCellInputs:
    feature_observations, processed_sha = adapt_feature_frame(
        feature_frame,
        symbol=symbol,
        timeframe=timeframe,
    )
    outcome_observations = _predecessor.adapt_outcome_frame(
        outcome_frame,
        symbol=symbol,
        timeframe=timeframe,
        expected_processed_manifest_sha256=processed_sha,
    )
    feature_ids = {row.observation_id for row in feature_observations}
    missing = {
        row.observation_id
        for row in outcome_observations
        if row.observation_id not in feature_ids
    }
    if missing:
        raise ValueError("EXP-062 adapted outcome has no matching feature observation")
    return _predecessor.AdaptedCellInputs(
        symbol=symbol,
        timeframe=timeframe,
        processed_manifest_sha256=processed_sha,
        feature_observations=feature_observations,
        outcome_observations=outcome_observations,
    )


def compile_cell_evidence(
    result: _predecessor.InMemoryDiscoveryResult,
    *,
    code_commit: str,
    processed_manifest_sha256: str,
    feature_manifest_sha256: str,
    outcome_manifest_sha256: str,
    feature_evidence_fingerprint: str,
    outcome_evidence_fingerprint: str,
) -> dict[str, object]:
    predecessor = _predecessor.compile_cell_evidence(
        result,
        code_commit=code_commit,
        processed_manifest_sha256=processed_manifest_sha256,
        feature_manifest_sha256=feature_manifest_sha256,
        outcome_manifest_sha256=outcome_manifest_sha256,
        feature_evidence_fingerprint=feature_evidence_fingerprint,
        outcome_evidence_fingerprint=outcome_evidence_fingerprint,
    )
    predecessor_fingerprint = str(predecessor["evidence_fingerprint"])

    value = dict(predecessor)
    value.pop("evidence_fingerprint", None)
    value["evidence_version"] = EXP062_CELL_EVIDENCE_VERSION
    value["evidence_protocol"] = EXP062_CELL_EVIDENCE_PROTOCOL
    value["experiment_id"] = EXP062_EXPERIMENT_ID
    value["protocol_fingerprint"] = exp062_repair_protocol_fingerprint()
    value["repair_protocol_decision"] = EXP062_REPAIR_PROTOCOL_DECISION
    value["repair_protocol_version"] = EXP062_REPAIR_PROTOCOL_VERSION
    value["semantic_predecessor_experiment_id"] = EXP061_EXPERIMENT_ID
    value["semantic_predecessor_protocol_fingerprint"] = (
        exp061_protocol_fingerprint()
    )
    value["semantic_predecessor_cell_evidence_fingerprint"] = (
        predecessor_fingerprint
    )
    value["nan_to_null_adapter_repair_applied"] = True
    value["positive_negative_infinity_normalization_authorized"] = False
    value["evidence_fingerprint"] = _predecessor._sha256_bytes(
        _predecessor._canonical_json(value)
    )
    return value


def _reconstruct_predecessor_evidence(
    value: Mapping[str, object],
) -> dict[str, object]:
    predecessor = dict(value)
    predecessor.pop("evidence_fingerprint", None)
    predecessor.pop("repair_protocol_decision", None)
    predecessor.pop("repair_protocol_version", None)
    predecessor.pop("semantic_predecessor_experiment_id", None)
    predecessor.pop("semantic_predecessor_protocol_fingerprint", None)
    stored_predecessor_fingerprint = predecessor.pop(
        "semantic_predecessor_cell_evidence_fingerprint",
        None,
    )
    predecessor.pop("nan_to_null_adapter_repair_applied", None)
    predecessor.pop(
        "positive_negative_infinity_normalization_authorized",
        None,
    )
    predecessor["evidence_version"] = _predecessor.EXP061_CELL_EVIDENCE_VERSION
    predecessor["evidence_protocol"] = _predecessor.EXP061_CELL_EVIDENCE_PROTOCOL
    predecessor["experiment_id"] = EXP061_EXPERIMENT_ID
    predecessor["protocol_fingerprint"] = exp061_protocol_fingerprint()
    predecessor["evidence_fingerprint"] = _predecessor._sha256_bytes(
        _predecessor._canonical_json(predecessor)
    )
    if predecessor["evidence_fingerprint"] != stored_predecessor_fingerprint:
        raise ValueError(
            "EXP-062 semantic predecessor cell evidence fingerprint mismatch"
        )
    return predecessor


def validate_cell_evidence(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _predecessor._validate_sha256(
        value.get("evidence_fingerprint"),
        field="EXP-062 cell evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _predecessor._sha256_bytes(
        _predecessor._canonical_json(unsigned)
    ) != fingerprint:
        raise ValueError("EXP-062 cell evidence fingerprint mismatch")

    if value.get("evidence_version") != EXP062_CELL_EVIDENCE_VERSION:
        raise ValueError("EXP-062 cell evidence version mismatch")
    if value.get("evidence_protocol") != EXP062_CELL_EVIDENCE_PROTOCOL:
        raise ValueError("EXP-062 cell evidence protocol mismatch")
    if value.get("experiment_id") != EXP062_EXPERIMENT_ID:
        raise ValueError("EXP-062 cell evidence experiment mismatch")
    if value.get("protocol_fingerprint") != exp062_repair_protocol_fingerprint():
        raise ValueError("EXP-062 repair protocol fingerprint mismatch")
    if value.get("repair_protocol_decision") != EXP062_REPAIR_PROTOCOL_DECISION:
        raise ValueError("EXP-062 repair decision mismatch")
    if value.get("repair_protocol_version") != EXP062_REPAIR_PROTOCOL_VERSION:
        raise ValueError("EXP-062 repair version mismatch")
    if value.get("semantic_predecessor_experiment_id") != EXP061_EXPERIMENT_ID:
        raise ValueError("EXP-062 semantic predecessor experiment mismatch")
    if value.get("semantic_predecessor_protocol_fingerprint") != (
        exp061_protocol_fingerprint()
    ):
        raise ValueError("EXP-062 semantic predecessor protocol mismatch")
    if value.get("nan_to_null_adapter_repair_applied") is not True:
        raise ValueError("EXP-062 NaN-to-null repair marker missing")
    if value.get(
        "positive_negative_infinity_normalization_authorized"
    ) is not False:
        raise ValueError("EXP-062 infinity normalization must remain forbidden")

    predecessor = _reconstruct_predecessor_evidence(value)
    _predecessor.validate_cell_evidence(predecessor)
    return value


__all__ = [
    "EXP062_ADAPTER_EVIDENCE_DECISION",
    "EXP062_CELL_EVIDENCE_PROTOCOL",
    "EXP062_CELL_EVIDENCE_VERSION",
    "adapt_feature_frame",
    "adapt_market_learning_cell",
    "compile_cell_evidence",
    "normalize_continuous_feature_value",
    "validate_cell_evidence",
    "validate_exp062_adapter_sources",
]
