from __future__ import annotations

from datetime import date
import hashlib
from pathlib import Path
import struct
from typing import Mapping, Sequence

import numpy as np
import polars as pl

from . import model_training as _base
from .contracts import EVIDENCE_LABEL
from .model_protocol import (
    DIAGNOSTIC_SCENARIOS,
    HOLDOUT_GATE_SCENARIOS,
    MODEL_INPUT_COLUMNS,
    PROTOCOL_SPLITS,
    RETROSPECTIVE_HOLDOUT_SPLIT,
    SELECTION_GATE_SCENARIOS,
    SELECTION_SPLIT,
    TARGET_CLASSES,
    TARGET_COLUMN,
    VALIDATION_GATE_SCENARIOS,
    VALIDATION_SPLIT,
    ModelCell,
    ModelProtocolSplit,
)
from .model_successor_density_training import (
    _canonical_json,
    _git_blob_sha,
    _parse_utc_date,
    _window_gate,
    _window_indices,
)
from .model_successor_regime_consensus_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
    FIT_REGIME_WINDOWS,
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    PRIOR_RESULT_INFORMED,
    REGIME_CONSENSUS_EXPERIMENT_ID,
    REGIME_CONSENSUS_PROTOCOL_DECISION,
    REGIME_CONSENSUS_PROTOCOL_VERSION,
    TEMPORAL_STABILITY_WINDOWS,
    UNTOUCHED_OOS,
    regime_consensus_protocol_fingerprint,
)


REGIME_CONSENSUS_TRAINING_CORE_VERSION = (
    "fmp-exp048-regime-consensus-training-core-v1"
)
REGIME_CONSENSUS_TRAINING_CORE_DECISION = "DEC-124"

DEC123_MERGED_COMMIT = (
    "39674f482e57922ac61fb0a6dff15a5ef621efd3"
)
DEC123_PROTOCOL_BLOB_SHA = (
    "39b6b3f5adc7f34ffd8cebcf881138d6ca3eab84"
)
BASE_TRAINING_CORE_BLOB_SHA = (
    "34b50a3f907d26b1c5ec50a0a0b444a3417d04f7"
)
DENSITY_HELPER_CORE_BLOB_SHA = (
    "8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945"
)

REGIME_CONSENSUS_RESULT_EXECUTION_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def validate_regime_consensus_training_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec123_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_consensus_protocol.py",
            DEC123_PROTOCOL_BLOB_SHA,
        ),
        "base_training_core": (
            root
            / "src/fmp/market_learning/model_training.py",
            BASE_TRAINING_CORE_BLOB_SHA,
        ),
        "density_helper_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_density_training.py",
            DENSITY_HELPER_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-048 training dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-048 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    protocol_fingerprint = (
        regime_consensus_protocol_fingerprint()
    )
    if len(protocol_fingerprint) != 64:
        raise ValueError(
            "EXP-048 regime-consensus protocol fingerprint is invalid"
        )

    return {
        "regime_consensus_training_core_version": (
            REGIME_CONSENSUS_TRAINING_CORE_VERSION
        ),
        "regime_consensus_training_core_decision": (
            REGIME_CONSENSUS_TRAINING_CORE_DECISION
        ),
        "dec123_merged_commit": DEC123_MERGED_COMMIT,
        "dec123_protocol_blob_sha": actual[
            "dec123_protocol"
        ],
        "base_training_core_blob_sha": actual[
            "base_training_core"
        ],
        "density_helper_core_blob_sha": actual[
            "density_helper_core"
        ],
        "regime_consensus_protocol_fingerprint": (
            protocol_fingerprint
        ),
        "regime_consensus_result_execution_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _fit_regime_splits() -> tuple[ModelProtocolSplit, ...]:
    return tuple(
        ModelProtocolSplit(
            name=str(window["name"]),
            start=date.fromisoformat(str(window["start"])),
            end_exclusive=date.fromisoformat(
                str(window["end_exclusive"])
            ),
        )
        for window in FIT_REGIME_WINDOWS
    )


def _consensus_direction_confidence(
    probability_matrices: Sequence[np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    if len(probability_matrices) != 3:
        raise ValueError(
            "EXP-048 consensus requires exactly three probability matrices"
        )
    first = probability_matrices[0]
    if (
        first.ndim != 2
        or first.shape[1] != len(TARGET_CLASSES)
    ):
        raise ValueError(
            "EXP-048 probability matrix shape is invalid"
        )
    for value in probability_matrices[1:]:
        if value.shape != first.shape:
            raise ValueError(
                "EXP-048 regime probability shape mismatch"
            )

    tops = [
        _base._top_classes(value)
        for value in probability_matrices
    ]
    directions = np.full(
        first.shape[0],
        "NO_TRADE",
        dtype=object,
    )
    confidence = np.full(
        first.shape[0],
        float("-inf"),
        dtype=np.float64,
    )
    class_index = {
        name: index
        for index, name in enumerate(TARGET_CLASSES)
    }

    for row_index in range(first.shape[0]):
        labels = tuple(
            str(top[row_index])
            for top in tops
        )
        if len(set(labels)) != 1:
            continue
        agreed = labels[0]
        if agreed not in {"LONG", "SHORT"}:
            continue
        index = class_index[agreed]
        directions[row_index] = agreed
        confidence[row_index] = min(
            float(value[row_index, index])
            for value in probability_matrices
        )

    return directions, confidence


def _consensus_digest(
    *,
    row_ids: Sequence[str],
    directions: np.ndarray,
    confidence: np.ndarray,
) -> str:
    if (
        len(row_ids) != len(directions)
        or len(row_ids) != len(confidence)
    ):
        raise ValueError(
            "EXP-048 consensus digest row mismatch"
        )
    digest = hashlib.sha256()
    for row_id, direction, value in zip(
        row_ids,
        directions.tolist(),
        confidence.tolist(),
        strict=True,
    ):
        encoded = str(row_id).encode("utf-8")
        digest.update(
            len(encoded).to_bytes(8, "big", signed=False)
        )
        digest.update(encoded)
        label = str(direction).encode("ascii")
        digest.update(
            len(label).to_bytes(8, "big", signed=False)
        )
        digest.update(label)
        if direction in {"LONG", "SHORT"}:
            digest.update(struct.pack(">d", float(value)))
        else:
            digest.update(b"NO_CONFIDENCE")
    return digest.hexdigest()


def _derive_consensus_cutoff(
    *,
    directions: np.ndarray,
    confidence: np.ndarray,
    row_ids: Sequence[str],
    budget: int,
) -> dict[str, object]:
    if budget not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError(
            "unsupported EXP-048 candidate budget"
        )
    if (
        len(row_ids) != len(directions)
        or len(row_ids) != len(confidence)
    ):
        raise ValueError(
            "EXP-048 consensus cutoff row mismatch"
        )

    eligible = [
        index
        for index, direction in enumerate(
            directions.tolist()
        )
        if direction in {"LONG", "SHORT"}
    ]
    if len(eligible) < budget:
        return {
            "status": (
                "UNAVAILABLE_INSUFFICIENT_CONSENSUS_ROWS"
            ),
            "candidate_budget_anchor": budget,
            "eligible_consensus_row_count": len(eligible),
            "selection_derived_cutoff": None,
        }

    ranked = sorted(
        eligible,
        key=lambda index: (
            -float(confidence[index]),
            str(row_ids[index]),
        ),
    )
    cutoff = float(
        confidence[ranked[budget - 1]]
    )
    selected_count = sum(
        1
        for index in eligible
        if float(confidence[index]) >= cutoff
    )
    return {
        "status": "AVAILABLE",
        "candidate_budget_anchor": budget,
        "eligible_consensus_row_count": len(eligible),
        "selection_derived_cutoff": cutoff,
        "selection_candidate_count_at_cutoff": (
            selected_count
        ),
    }


def _candidate_directions(
    *,
    directions: np.ndarray,
    confidence: np.ndarray,
    cutoff: float,
) -> np.ndarray:
    if (
        not np.isfinite(cutoff)
        or cutoff < 0.0
        or cutoff > 1.0
    ):
        raise ValueError(
            "EXP-048 consensus cutoff is invalid"
        )
    if len(directions) != len(confidence):
        raise ValueError(
            "EXP-048 candidate row mismatch"
        )

    out = np.full(
        len(directions),
        "NO_TRADE",
        dtype=object,
    )
    for index, direction in enumerate(
        directions.tolist()
    ):
        if (
            direction in {"LONG", "SHORT"}
            and float(confidence[index]) >= cutoff
        ):
            out[index] = direction
    return out


def _evaluate_consensus_cutoff(
    frame: pl.DataFrame,
    *,
    directions: np.ndarray,
    confidence: np.ndarray,
    cutoff: float,
    budget: int,
    scenarios: Sequence[float],
    row_ids: Sequence[str],
) -> dict[str, object]:
    candidates = _candidate_directions(
        directions=directions,
        confidence=confidence,
        cutoff=cutoff,
    )
    scenario_results: dict[str, object] = {}
    for scenario in scenarios:
        metrics = _base._financial_metrics(
            frame,
            candidates,
            scenario=float(scenario),
            row_ids=row_ids,
        )
        scenario_results[str(float(scenario))] = {
            "metrics": metrics,
            "gate": _base._financial_gate(metrics),
        }

    return {
        "candidate_budget_anchor": budget,
        "selection_derived_cutoff": cutoff,
        "scenarios": scenario_results,
    }


def _consensus_diagnostics(
    *,
    directions: np.ndarray,
    confidence: np.ndarray,
    regime_probability_digests: Mapping[str, str],
) -> dict[str, object]:
    counts = {
        name: int(
            sum(
                direction == name
                for direction in directions.tolist()
            )
        )
        for name in TARGET_CLASSES
    }
    eligible = counts["LONG"] + counts["SHORT"]
    finite = [
        float(value)
        for direction, value in zip(
            directions.tolist(),
            confidence.tolist(),
            strict=True,
        )
        if direction in {"LONG", "SHORT"}
    ]
    return {
        "row_count": len(directions),
        "consensus_direction_counts": counts,
        "consensus_eligible_row_count": eligible,
        "consensus_eligible_rate": (
            float(eligible / len(directions))
            if len(directions)
            else 0.0
        ),
        "minimum_consensus_confidence": (
            min(finite) if finite else None
        ),
        "maximum_consensus_confidence": (
            max(finite) if finite else None
        ),
        "regime_probability_digests": dict(
            regime_probability_digests
        ),
    }


def _score_consensus(
    *,
    fitted_models: Mapping[str, _base.FittedMarketModel],
    frame: pl.DataFrame,
    cell: ModelCell,
) -> tuple[
    np.ndarray,
    np.ndarray,
    dict[str, object],
    tuple[str, ...],
    str,
]:
    if set(fitted_models) != {
        str(window["name"])
        for window in FIT_REGIME_WINDOWS
    }:
        raise ValueError(
            "EXP-048 fitted regime model set mismatch"
        )

    probabilities: list[np.ndarray] = []
    digests: dict[str, str] = {}
    row_ids_reference: tuple[str, ...] | None = None
    for regime_name in (
        str(window["name"])
        for window in FIT_REGIME_WINDOWS
    ):
        (
            scored,
            _diagnostics,
            digest,
            row_ids,
        ) = _base._score_split(
            fitted_models[regime_name],
            frame,
            cell=cell,
        )
        if row_ids_reference is None:
            row_ids_reference = tuple(row_ids)
        elif tuple(row_ids) != row_ids_reference:
            raise ValueError(
                "EXP-048 regime score row identity mismatch"
            )
        probabilities.append(scored)
        digests[regime_name] = digest

    if row_ids_reference is None:
        raise ValueError(
            "EXP-048 regime scoring produced no row identity"
        )

    directions, confidence = (
        _consensus_direction_confidence(
            probabilities
        )
    )
    diagnostics = _consensus_diagnostics(
        directions=directions,
        confidence=confidence,
        regime_probability_digests=digests,
    )
    consensus_digest = _consensus_digest(
        row_ids=row_ids_reference,
        directions=directions,
        confidence=confidence,
    )
    return (
        directions,
        confidence,
        diagnostics,
        row_ids_reference,
        consensus_digest,
    )


def _evaluate_temporal_stability(
    *,
    selection_frame: pl.DataFrame,
    directions: np.ndarray,
    confidence: np.ndarray,
    cutoff: float,
    budget: int,
    cell: ModelCell,
    full_selection_candidate_count: int,
) -> dict[str, object]:
    if (
        len(directions) != selection_frame.height
        or len(confidence) != selection_frame.height
    ):
        raise ValueError(
            "EXP-048 stability row mismatch"
        )

    windows: list[dict[str, object]] = []
    for raw_window in TEMPORAL_STABILITY_WINDOWS:
        window = dict(raw_window)
        start = _parse_utc_date(str(window["start"]))
        end_exclusive = _parse_utc_date(
            str(window["end_exclusive"])
        )
        indices = _window_indices(
            selection_frame,
            start=start,
            end_exclusive=end_exclusive,
        )
        window_frame = selection_frame[indices]
        index_array = np.asarray(
            indices,
            dtype=np.int64,
        )
        window_directions = directions[index_array]
        window_confidence = confidence[index_array]
        row_ids = _base._row_identity(
            window_frame,
            cell=cell,
        )
        evaluated = _evaluate_consensus_cutoff(
            window_frame,
            directions=window_directions,
            confidence=window_confidence,
            cutoff=cutoff,
            budget=budget,
            scenarios=SELECTION_GATE_SCENARIOS,
            row_ids=row_ids,
        )
        scenario = evaluated["scenarios"]["0.5"]
        metrics = scenario["metrics"]
        gate = _window_gate(
            metrics,
            full_selection_candidate_count=(
                full_selection_candidate_count
            ),
        )
        windows.append(
            {
                "name": str(window["name"]),
                "start": str(window["start"]),
                "end_exclusive": str(
                    window["end_exclusive"]
                ),
                "row_count": window_frame.height,
                "metrics": metrics,
                "gate": gate,
            }
        )

    return {
        "status": (
            "PASS"
            if all(
                bool(window["gate"]["passed"])
                for window in windows
            )
            else "REJECT"
        ),
        "minimum_directional_candidate_share_per_window": (
            MIN_STABILITY_WINDOW_CANDIDATE_SHARE
        ),
        "windows": windows,
    }


def _selection_key(
    row: Mapping[str, object],
) -> tuple[float, int, int]:
    scenario = row["scenarios"]["0.5"]
    metrics = scenario["metrics"]
    return (
        float(metrics["total_net_pips"]),
        int(metrics["directional_candidate_count"]),
        -int(row["candidate_budget_anchor"]),
    )


def _evaluate_forward_split(
    *,
    fitted_models: Mapping[str, _base.FittedMarketModel],
    frame: pl.DataFrame,
    cell: ModelCell,
    cutoff: float,
    budget: int,
    gate_scenarios: Sequence[float],
) -> dict[str, object]:
    (
        directions,
        confidence,
        diagnostics,
        row_ids,
        consensus_digest,
    ) = _score_consensus(
        fitted_models=fitted_models,
        frame=frame,
        cell=cell,
    )
    all_scenarios = tuple(
        sorted(
            {
                *(
                    float(value)
                    for value in DIAGNOSTIC_SCENARIOS
                ),
                *(
                    float(value)
                    for value in gate_scenarios
                ),
            }
        )
    )
    evaluated = _evaluate_consensus_cutoff(
        frame,
        directions=directions,
        confidence=confidence,
        cutoff=cutoff,
        budget=budget,
        scenarios=all_scenarios,
        row_ids=row_ids,
    )
    gating = [
        bool(
            evaluated["scenarios"][
                str(float(value))
            ]["gate"]["passed"]
        )
        for value in gate_scenarios
    ]
    return {
        "status": (
            "PASS" if all(gating) else "REJECT"
        ),
        "row_count": frame.height,
        "consensus": diagnostics,
        "consensus_digest": consensus_digest,
        **evaluated,
    }


def run_regime_consensus_model_cell_core(
    *,
    features: pl.DataFrame,
    outcomes: pl.DataFrame,
    cell: ModelCell,
) -> dict[str, object]:
    joined, processed_manifest_sha256 = (
        _base._validate_frames(
            features,
            outcomes,
            cell=cell,
        )
    )
    split_frames = {
        split.name: _base._split_frame(joined, split)
        for split in PROTOCOL_SPLITS
    }
    if any(
        frame.is_empty()
        for frame in split_frames.values()
    ):
        empty = [
            name
            for name, frame in split_frames.items()
            if frame.is_empty()
        ]
        raise ValueError(
            "EXP-048 model cell has empty required "
            f"split(s): {empty}"
        )

    regime_frames = {
        split.name: _base._split_frame(
            joined,
            split,
        )
        for split in _fit_regime_splits()
    }
    if any(
        frame.is_empty()
        for frame in regime_frames.values()
    ):
        empty = [
            name
            for name, frame in regime_frames.items()
            if frame.is_empty()
        ]
        raise ValueError(
            "EXP-048 model cell has empty fit "
            f"regime(s): {empty}"
        )

    fitted_models: dict[
        str,
        _base.FittedMarketModel,
    ] = {}
    fit_evidence: dict[str, object] = {}
    for regime_name, fit_frame in regime_frames.items():
        counts = _base._target_counts(fit_frame)
        if any(
            counts[name] <= 0
            for name in TARGET_CLASSES
        ):
            raise ValueError(
                "EXP-048 fit regime must contain all "
                "three target classes"
            )
        fitted = _base._fit_family(
            "hist_gradient_boosting",
            fit_frame,
        )
        fitted_models[regime_name] = fitted
        fit_evidence[regime_name] = {
            "status": "FITTED",
            "row_count": fit_frame.height,
            "target_class_counts": counts,
            "preprocessor_fingerprint": (
                fitted.preprocessor_fingerprint
            ),
            "model_fingerprint": (
                fitted.model_fingerprint
            ),
        }

    selection_frame = split_frames[
        SELECTION_SPLIT.name
    ]
    (
        selection_directions,
        selection_confidence,
        selection_diagnostics,
        selection_row_ids,
        selection_consensus_digest,
    ) = _score_consensus(
        fitted_models=fitted_models,
        frame=selection_frame,
        cell=cell,
    )

    variants: list[dict[str, object]] = []
    for budget in CANDIDATE_BUDGET_ANCHORS:
        cutoff_record = _derive_consensus_cutoff(
            directions=selection_directions,
            confidence=selection_confidence,
            row_ids=selection_row_ids,
            budget=budget,
        )
        if cutoff_record["status"] != "AVAILABLE":
            variants.append(
                {
                    "model_family": (
                        "hist_gradient_boosting"
                    ),
                    "candidate_budget_anchor": budget,
                    "evaluation_status": (
                        "BUDGET_UNAVAILABLE"
                    ),
                    **cutoff_record,
                    "aggregate_selection_gate_passed": False,
                    "temporal_stability": {
                        "status": (
                            "BUDGET_UNAVAILABLE"
                        ),
                        "minimum_directional_candidate_share_per_window": (
                            MIN_STABILITY_WINDOW_CANDIDATE_SHARE
                        ),
                        "windows": [],
                    },
                    "selection_gate_passed": False,
                }
            )
            continue

        cutoff = float(
            cutoff_record[
                "selection_derived_cutoff"
            ]
        )
        evaluated = _evaluate_consensus_cutoff(
            selection_frame,
            directions=selection_directions,
            confidence=selection_confidence,
            cutoff=cutoff,
            budget=budget,
            scenarios=SELECTION_GATE_SCENARIOS,
            row_ids=selection_row_ids,
        )
        scenario = evaluated["scenarios"]["0.5"]
        aggregate_passed = bool(
            scenario["gate"]["passed"]
        )
        full_count = int(
            scenario["metrics"][
                "directional_candidate_count"
            ]
        )

        if aggregate_passed:
            stability = _evaluate_temporal_stability(
                selection_frame=selection_frame,
                directions=selection_directions,
                confidence=selection_confidence,
                cutoff=cutoff,
                budget=budget,
                cell=cell,
                full_selection_candidate_count=full_count,
            )
            stability_passed = (
                stability["status"] == "PASS"
            )
        else:
            stability = {
                "status": "LOCKED_AGGREGATE_REJECT",
                "minimum_directional_candidate_share_per_window": (
                    MIN_STABILITY_WINDOW_CANDIDATE_SHARE
                ),
                "windows": [],
            }
            stability_passed = False

        variants.append(
            {
                "model_family": (
                    "hist_gradient_boosting"
                ),
                "evaluation_status": "EVALUATED",
                **cutoff_record,
                **evaluated,
                "aggregate_selection_gate_passed": (
                    aggregate_passed
                ),
                "temporal_stability": stability,
                "selection_gate_passed": bool(
                    aggregate_passed
                    and stability_passed
                ),
            }
        )

    passing = [
        row
        for row in variants
        if row["selection_gate_passed"]
    ]
    selected = (
        max(passing, key=_selection_key)
        if passing
        else None
    )

    result: dict[str, object] = {
        "experiment_id": (
            REGIME_CONSENSUS_EXPERIMENT_ID
        ),
        "training_core_version": (
            REGIME_CONSENSUS_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            REGIME_CONSENSUS_TRAINING_CORE_DECISION
        ),
        "dec123_merged_commit": DEC123_MERGED_COMMIT,
        "dec123_protocol_blob_sha": (
            DEC123_PROTOCOL_BLOB_SHA
        ),
        "base_training_core_blob_sha": (
            BASE_TRAINING_CORE_BLOB_SHA
        ),
        "density_helper_core_blob_sha": (
            DENSITY_HELPER_CORE_BLOB_SHA
        ),
        "protocol_decision": (
            REGIME_CONSENSUS_PROTOCOL_DECISION
        ),
        "protocol_version": (
            REGIME_CONSENSUS_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            regime_consensus_protocol_fingerprint()
        ),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": UNTOUCHED_OOS,
        "cell": {
            "symbol": cell.symbol,
            "timeframe": cell.timeframe,
            "horizon_minutes": cell.horizon_minutes,
        },
        "processed_manifest_sha256": (
            processed_manifest_sha256
        ),
        "joined_row_count": joined.height,
        "split_row_counts": {
            name: frame.height
            for name, frame in split_frames.items()
        },
        "fit": {
            "regime_models": fit_evidence,
            "regime_model_count": len(
                fitted_models
            ),
            "full_fit_single_model": {
                "status": "FORBIDDEN_BY_DEC123",
                "fit_attempt_count": 0,
            },
            "logistic_regression": {
                "status": (
                    "EXCLUDED_BY_DEC112_DEC123"
                ),
                "fit_attempt_count": 0,
            },
        },
        "selection": {
            "status": (
                "SELECTED"
                if selected is not None
                else (
                    "NO_REGIME_CONSENSUS_"
                    "STABLE_MODEL_CHALLENGER"
                )
            ),
            "row_count": selection_frame.height,
            "consensus": selection_diagnostics,
            "consensus_digest": (
                selection_consensus_digest
            ),
            "variants": variants,
            "selected_variant": (
                {
                    "model_family": (
                        "hist_gradient_boosting"
                    ),
                    "candidate_budget_anchor": int(
                        selected[
                            "candidate_budget_anchor"
                        ]
                    ),
                    "selection_derived_cutoff": float(
                        selected[
                            "selection_derived_cutoff"
                        ]
                    ),
                }
                if selected is not None
                else None
            ),
        },
        "validation": {
            "status": "LOCKED_NO_SELECTION",
        },
        "retrospective_holdout": {
            "status": "LOCKED_NO_SELECTION",
        },
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }

    if selected is None:
        result["result_fingerprint"] = _sha256(
            result
        )
        return result

    selected_cutoff = float(
        selected["selection_derived_cutoff"]
    )
    selected_budget = int(
        selected["candidate_budget_anchor"]
    )

    validation = _evaluate_forward_split(
        fitted_models=fitted_models,
        frame=split_frames[
            VALIDATION_SPLIT.name
        ],
        cell=cell,
        cutoff=selected_cutoff,
        budget=selected_budget,
        gate_scenarios=VALIDATION_GATE_SCENARIOS,
    )
    result["validation"] = validation

    if validation["status"] != "PASS":
        result["retrospective_holdout"] = {
            "status": "LOCKED_VALIDATION_REJECT",
        }
        result["result_fingerprint"] = _sha256(
            result
        )
        return result

    holdout = _evaluate_forward_split(
        fitted_models=fitted_models,
        frame=split_frames[
            RETROSPECTIVE_HOLDOUT_SPLIT.name
        ],
        cell=cell,
        cutoff=selected_cutoff,
        budget=selected_budget,
        gate_scenarios=HOLDOUT_GATE_SCENARIOS,
    )
    result["retrospective_holdout"] = holdout
    result["result_fingerprint"] = _sha256(result)
    return result


__all__ = [
    "BASE_TRAINING_CORE_BLOB_SHA",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC123_MERGED_COMMIT",
    "DEC123_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "DENSITY_HELPER_CORE_BLOB_SHA",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REGIME_CONSENSUS_RESULT_EXECUTION_AUTHORIZED",
    "REGIME_CONSENSUS_TRAINING_CORE_DECISION",
    "REGIME_CONSENSUS_TRAINING_CORE_VERSION",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "run_regime_consensus_model_cell_core",
    "validate_regime_consensus_training_sources",
]
