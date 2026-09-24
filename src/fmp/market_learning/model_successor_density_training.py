from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import polars as pl

from . import model_training as _base
from .contracts import EVIDENCE_LABEL
from .model_protocol import (
    DIAGNOSTIC_SCENARIOS,
    FIT_SPLIT,
    HOLDOUT_GATE_SCENARIOS,
    PROTOCOL_SPLITS,
    RETROSPECTIVE_HOLDOUT_SPLIT,
    SELECTION_GATE_SCENARIOS,
    SELECTION_SPLIT,
    TARGET_CLASSES,
    VALIDATION_GATE_SCENARIOS,
    VALIDATION_SPLIT,
    ModelCell,
)
from .model_successor_density_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
    DENSITY_PROTOCOL_DECISION,
    DENSITY_PROTOCOL_VERSION,
    DENSITY_SUCCESSOR_EXPERIMENT_ID,
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    PRIOR_RESULT_INFORMED,
    TEMPORAL_STABILITY_WINDOWS,
    UNTOUCHED_OOS,
    density_protocol_fingerprint,
)


DENSITY_TRAINING_CORE_VERSION = (
    "fmp-exp047-hgb-density-training-core-v1"
)
DENSITY_TRAINING_CORE_DECISION = "DEC-114"

DEC113_MERGED_COMMIT = (
    "060bde94835158d62d47640aaf1a77ec56b483ff"
)
DEC113_PROTOCOL_BLOB_SHA = (
    "871936729a1090d675f6f5181ef04c8f32494394"
)
BASE_TRAINING_CORE_BLOB_SHA = (
    "34b50a3f907d26b1c5ec50a0a0b444a3417d04f7"
)

DENSITY_TRAINING_RESULT_EXECUTION_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def validate_density_training_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec113_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_density_protocol.py",
            DEC113_PROTOCOL_BLOB_SHA,
        ),
        "base_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_training.py",
            BASE_TRAINING_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-047 training dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-047 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    protocol_fingerprint = density_protocol_fingerprint()
    if len(protocol_fingerprint) != 64:
        raise ValueError(
            "EXP-047 density protocol fingerprint is invalid"
        )

    return {
        "density_training_core_version": (
            DENSITY_TRAINING_CORE_VERSION
        ),
        "density_training_core_decision": (
            DENSITY_TRAINING_CORE_DECISION
        ),
        "dec113_merged_commit": DEC113_MERGED_COMMIT,
        "dec113_protocol_blob_sha": actual[
            "dec113_protocol"
        ],
        "base_training_core_blob_sha": actual[
            "base_training_core"
        ],
        "density_protocol_fingerprint": (
            protocol_fingerprint
        ),
        "density_training_result_execution_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _directional_top(
    probabilities: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if (
        probabilities.ndim != 2
        or probabilities.shape[1] != len(TARGET_CLASSES)
    ):
        raise ValueError(
            "EXP-047 probability matrix shape is invalid"
        )

    top = _base._top_classes(probabilities)
    directions = np.full(
        probabilities.shape[0],
        "NO_TRADE",
        dtype=object,
    )
    confidence = np.full(
        probabilities.shape[0],
        float("-inf"),
        dtype=np.float64,
    )
    class_index = {
        name: index
        for index, name in enumerate(TARGET_CLASSES)
    }

    for row_index, label in enumerate(top.tolist()):
        name = str(label)
        if name not in {"LONG", "SHORT"}:
            continue
        directions[row_index] = name
        confidence[row_index] = float(
            probabilities[
                row_index,
                class_index[name],
            ]
        )

    return directions, confidence


def _derive_density_cutoff(
    *,
    probabilities: np.ndarray,
    row_ids: Sequence[str],
    budget: int,
) -> dict[str, object]:
    if budget not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError(
            "unsupported EXP-047 candidate budget"
        )
    if len(row_ids) != probabilities.shape[0]:
        raise ValueError(
            "EXP-047 density cutoff row mismatch"
        )

    directions, confidence = _directional_top(
        probabilities
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
            "status": "UNAVAILABLE_INSUFFICIENT_DIRECTIONAL_ROWS",
            "candidate_budget_anchor": budget,
            "eligible_directional_row_count": len(eligible),
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
        "eligible_directional_row_count": len(eligible),
        "selection_derived_cutoff": cutoff,
        "selection_candidate_count_at_cutoff": (
            selected_count
        ),
    }


def _density_candidate_directions(
    probabilities: np.ndarray,
    *,
    cutoff: float,
) -> np.ndarray:
    if (
        not np.isfinite(cutoff)
        or cutoff < 0.0
        or cutoff > 1.0
    ):
        raise ValueError(
            "EXP-047 density cutoff is invalid"
        )

    directions, confidence = _directional_top(
        probabilities
    )
    out = np.full(
        probabilities.shape[0],
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


def _evaluate_density_cutoff(
    frame: pl.DataFrame,
    probabilities: np.ndarray,
    *,
    cutoff: float,
    budget: int,
    scenarios: Sequence[float],
    row_ids: Sequence[str],
) -> dict[str, object]:
    directions = _density_candidate_directions(
        probabilities,
        cutoff=cutoff,
    )
    scenario_results: dict[str, object] = {}
    for scenario in scenarios:
        metrics = _base._financial_metrics(
            frame,
            directions,
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


def _parse_utc_date(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(
        tzinfo=timezone.utc
    )


def _window_indices(
    frame: pl.DataFrame,
    *,
    start: datetime,
    end_exclusive: datetime,
) -> list[int]:
    available = frame["available_at_utc"].to_list()
    exits = frame["exit_timestamp_utc"].to_list()
    indices: list[int] = []
    for index, (available_at, exit_at) in enumerate(
        zip(available, exits, strict=True)
    ):
        if not isinstance(available_at, datetime):
            raise ValueError(
                "EXP-047 stability available_at_utc is invalid"
            )
        if not isinstance(exit_at, datetime):
            raise ValueError(
                "EXP-047 stability exit_timestamp_utc is invalid"
            )
        if (
            start <= available_at < end_exclusive
            and exit_at < end_exclusive
        ):
            indices.append(index)
    if not indices:
        raise ValueError(
            "EXP-047 temporal stability window is empty"
        )
    return indices


def _window_gate(
    metrics: Mapping[str, object],
    *,
    full_selection_candidate_count: int,
) -> dict[str, object]:
    if full_selection_candidate_count <= 0:
        raise ValueError(
            "EXP-047 stability denominator must be positive"
        )

    count = int(metrics["directional_candidate_count"])
    share = float(
        count / full_selection_candidate_count
    )
    total = float(metrics["total_net_pips"])
    mean_raw = metrics["mean_net_pips"]
    mean = (
        float(mean_raw)
        if mean_raw is not None
        else float("-inf")
    )
    gross_positive = float(
        metrics["gross_positive_pips"]
    )
    gross_negative = float(
        metrics["absolute_gross_negative_pips"]
    )

    criteria = {
        "directional_candidate_share>=0.10": (
            share >= MIN_STABILITY_WINDOW_CANDIDATE_SHARE
        ),
        "total_net_pips>0": total > 0.0,
        "mean_net_pips>0": mean > 0.0,
        "gross_positive_pips>absolute_gross_negative_pips": (
            gross_positive > gross_negative
        ),
    }
    return {
        "passed": all(criteria.values()),
        "criteria": criteria,
        "directional_candidate_share": share,
    }


def _evaluate_temporal_stability(
    *,
    selection_frame: pl.DataFrame,
    probabilities: np.ndarray,
    cutoff: float,
    budget: int,
    cell: ModelCell,
    full_selection_candidate_count: int,
) -> dict[str, object]:
    if probabilities.shape[0] != selection_frame.height:
        raise ValueError(
            "EXP-047 stability probability row mismatch"
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
        window_probabilities = probabilities[
            np.asarray(indices, dtype=np.int64)
        ]
        row_ids = _base._row_identity(
            window_frame,
            cell=cell,
        )
        evaluated = _evaluate_density_cutoff(
            window_frame,
            window_probabilities,
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


def _density_selection_key(
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
    fitted: _base.FittedMarketModel,
    frame: pl.DataFrame,
    cell: ModelCell,
    cutoff: float,
    budget: int,
    gate_scenarios: Sequence[float],
) -> dict[str, object]:
    (
        probabilities,
        diagnostics,
        probability_digest,
        row_ids,
    ) = _base._score_split(
        fitted,
        frame,
        cell=cell,
    )
    all_scenarios = tuple(
        sorted(
            set(
                float(value)
                for value in (
                    *DIAGNOSTIC_SCENARIOS,
                    *gate_scenarios,
                )
            )
        )
    )
    evaluated = _evaluate_density_cutoff(
        frame,
        probabilities,
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
        "classification": diagnostics,
        "probability_digest": probability_digest,
        **evaluated,
    }


def run_density_model_cell_core(
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
            "EXP-047 model cell has empty required "
            f"split(s): {empty}"
        )

    fit_frame = split_frames[FIT_SPLIT.name]
    fit_counts = _base._target_counts(fit_frame)
    if any(
        fit_counts[name] <= 0
        for name in TARGET_CLASSES
    ):
        raise ValueError(
            "EXP-047 fit split must contain all "
            "three target classes"
        )

    fitted = _base._fit_family(
        "hist_gradient_boosting",
        fit_frame,
    )
    fit_evidence = {
        "status": "FITTED",
        "fit_attempt_count": 1,
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
        selection_probabilities,
        selection_diagnostics,
        selection_probability_digest,
        selection_row_ids,
    ) = _base._score_split(
        fitted,
        selection_frame,
        cell=cell,
    )

    variants: list[dict[str, object]] = []
    for budget in CANDIDATE_BUDGET_ANCHORS:
        cutoff_record = _derive_density_cutoff(
            probabilities=selection_probabilities,
            row_ids=selection_row_ids,
            budget=budget,
        )
        if cutoff_record["status"] != "AVAILABLE":
            variants.append(
                {
                    "model_family": "hist_gradient_boosting",
                    "candidate_budget_anchor": budget,
                    "evaluation_status": (
                        "BUDGET_UNAVAILABLE"
                    ),
                    **cutoff_record,
                    "aggregate_selection_gate_passed": False,
                    "temporal_stability": {
                        "status": "BUDGET_UNAVAILABLE",
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
            cutoff_record["selection_derived_cutoff"]
        )
        evaluated = _evaluate_density_cutoff(
            selection_frame,
            selection_probabilities,
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
                probabilities=selection_probabilities,
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
                "model_family": "hist_gradient_boosting",
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
        max(passing, key=_density_selection_key)
        if passing
        else None
    )

    result: dict[str, object] = {
        "experiment_id": DENSITY_SUCCESSOR_EXPERIMENT_ID,
        "training_core_version": (
            DENSITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            DENSITY_TRAINING_CORE_DECISION
        ),
        "dec113_merged_commit": DEC113_MERGED_COMMIT,
        "dec113_protocol_blob_sha": (
            DEC113_PROTOCOL_BLOB_SHA
        ),
        "base_training_core_blob_sha": (
            BASE_TRAINING_CORE_BLOB_SHA
        ),
        "protocol_decision": DENSITY_PROTOCOL_DECISION,
        "protocol_version": DENSITY_PROTOCOL_VERSION,
        "protocol_fingerprint": (
            density_protocol_fingerprint()
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
            "row_count": fit_frame.height,
            "target_class_counts": fit_counts,
            "families": {
                "hist_gradient_boosting": fit_evidence,
                "logistic_regression": {
                    "status": "EXCLUDED_BY_DEC112_DEC113",
                    "fit_attempt_count": 0,
                },
            },
        },
        "selection": {
            "status": (
                "SELECTED"
                if selected is not None
                else "NO_DENSITY_STABLE_MODEL_CHALLENGER"
            ),
            "row_count": selection_frame.height,
            "classification": selection_diagnostics,
            "probability_digest": (
                selection_probability_digest
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
        result["result_fingerprint"] = _sha256(result)
        return result

    selected_cutoff = float(
        selected["selection_derived_cutoff"]
    )
    selected_budget = int(
        selected["candidate_budget_anchor"]
    )

    validation = _evaluate_forward_split(
        fitted=fitted,
        frame=split_frames[VALIDATION_SPLIT.name],
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
        result["result_fingerprint"] = _sha256(result)
        return result

    holdout = _evaluate_forward_split(
        fitted=fitted,
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
    "DEC113_MERGED_COMMIT",
    "DEC113_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "DENSITY_TRAINING_CORE_DECISION",
    "DENSITY_TRAINING_CORE_VERSION",
    "DENSITY_TRAINING_RESULT_EXECUTION_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "run_density_model_cell_core",
    "validate_density_training_sources",
]
