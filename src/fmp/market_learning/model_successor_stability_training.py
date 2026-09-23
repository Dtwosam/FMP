from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Mapping

import numpy as np
import polars as pl

from . import model_training as _base
from .contracts import EVIDENCE_LABEL
from .model_protocol import (
    CONFIDENCE_THRESHOLDS,
    FIT_SPLIT,
    HOLDOUT_GATE_SCENARIOS,
    MODEL_FAMILIES,
    PROTOCOL_SPLITS,
    RETROSPECTIVE_HOLDOUT_SPLIT,
    SELECTION_GATE_SCENARIOS,
    SELECTION_SPLIT,
    TARGET_CLASSES,
    VALIDATION_GATE_SCENARIOS,
    VALIDATION_SPLIT,
    ModelCell,
)
from .model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    PRIOR_RESULT_INFORMED,
    STABILITY_PROTOCOL_DECISION,
    STABILITY_PROTOCOL_VERSION,
    STABILITY_SUCCESSOR_EXPERIMENT_ID,
    TEMPORAL_STABILITY_WINDOWS,
    UNTOUCHED_OOS,
    stability_protocol_fingerprint,
)
from .model_successor_training import (
    _fit_successor_families,
    _unavailable_variants,
)


STABILITY_TRAINING_CORE_VERSION = (
    "fmp-exp046-stability-training-core-v1"
)
STABILITY_TRAINING_CORE_DECISION = "DEC-105"

DEC104_MERGED_COMMIT = (
    "bb2ee82a7d081138e1c0847e8c406d6c3ac68589"
)
DEC104_PROTOCOL_BLOB_SHA = (
    "4c8da2259f1fd6d27862a50a47a0d8108b58bc2e"
)
DEC096_SUCCESSOR_TRAINING_BLOB_SHA = (
    "3f0bc1bfa9640d08175e72cdf131bb97c94d562c"
)

STABILITY_TRAINING_RESULT_EXECUTION_AUTHORIZED = False
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


def validate_stability_training_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec104_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_stability_protocol.py",
            DEC104_PROTOCOL_BLOB_SHA,
        ),
        "dec096_successor_training": (
            root
            / "src/fmp/market_learning/"
            "model_successor_training.py",
            DEC096_SUCCESSOR_TRAINING_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-046 training dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-046 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    protocol_fingerprint = stability_protocol_fingerprint()
    if len(protocol_fingerprint) != 64:
        raise ValueError(
            "EXP-046 stability protocol fingerprint is invalid"
        )

    return {
        "stability_training_core_version": (
            STABILITY_TRAINING_CORE_VERSION
        ),
        "stability_training_core_decision": (
            STABILITY_TRAINING_CORE_DECISION
        ),
        "dec104_merged_commit": DEC104_MERGED_COMMIT,
        "dec104_protocol_blob_sha": actual[
            "dec104_protocol"
        ],
        "dec096_successor_training_blob_sha": actual[
            "dec096_successor_training"
        ],
        "stability_protocol_fingerprint": (
            protocol_fingerprint
        ),
        "stability_training_result_execution_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
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
                "EXP-046 stability available_at_utc is invalid"
            )
        if not isinstance(exit_at, datetime):
            raise ValueError(
                "EXP-046 stability exit_timestamp_utc is invalid"
            )
        if (
            start <= available_at < end_exclusive
            and exit_at < end_exclusive
        ):
            indices.append(index)
    if not indices:
        raise ValueError(
            "EXP-046 temporal stability window is empty"
        )
    return indices


def _window_gate(
    metrics: Mapping[str, object],
    *,
    full_selection_candidate_count: int,
) -> dict[str, object]:
    if full_selection_candidate_count <= 0:
        raise ValueError(
            "EXP-046 stability denominator must be positive"
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
    threshold: float,
    cell: ModelCell,
    full_selection_candidate_count: int,
) -> dict[str, object]:
    if probabilities.shape[0] != selection_frame.height:
        raise ValueError(
            "EXP-046 stability probability row mismatch"
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
        evaluated = _base._evaluate_threshold(
            window_frame,
            window_probabilities,
            threshold=threshold,
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


def _evaluated_variant(
    *,
    family: str,
    selection_frame: pl.DataFrame,
    probabilities: np.ndarray,
    row_ids: tuple[str, ...],
    threshold: float,
    cell: ModelCell,
) -> dict[str, object]:
    evaluated = _base._evaluate_threshold(
        selection_frame,
        probabilities,
        threshold=threshold,
        scenarios=SELECTION_GATE_SCENARIOS,
        row_ids=row_ids,
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
            probabilities=probabilities,
            threshold=threshold,
            cell=cell,
            full_selection_candidate_count=full_count,
        )
        stability_passed = stability["status"] == "PASS"
    else:
        stability = {
            "status": "LOCKED_AGGREGATE_REJECT",
            "minimum_directional_candidate_share_per_window": (
                MIN_STABILITY_WINDOW_CANDIDATE_SHARE
            ),
            "windows": [],
        }
        stability_passed = False

    return {
        "model_family": family,
        "family_fit_status": "FITTED",
        "evaluation_status": "EVALUATED",
        **evaluated,
        "aggregate_selection_gate_passed": (
            aggregate_passed
        ),
        "temporal_stability": stability,
        "selection_gate_passed": bool(
            aggregate_passed and stability_passed
        ),
    }


def _unavailable_stability_variants(
    *,
    family: str,
    fit_record: dict[str, object],
) -> list[dict[str, object]]:
    rows = _unavailable_variants(
        family=family,
        fit_record=fit_record,
    )
    return [
        {
            **row,
            "aggregate_selection_gate_passed": False,
            "temporal_stability": {
                "status": "FAMILY_UNAVAILABLE",
                "minimum_directional_candidate_share_per_window": (
                    MIN_STABILITY_WINDOW_CANDIDATE_SHARE
                ),
                "windows": [],
            },
            "selection_gate_passed": False,
        }
        for row in rows
    ]


def run_stability_model_cell_core(
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
            "EXP-046 model cell has empty required "
            f"split(s): {empty}"
        )

    fit_frame = split_frames[FIT_SPLIT.name]
    fit_counts = _base._target_counts(fit_frame)
    if any(
        fit_counts[name] <= 0
        for name in TARGET_CLASSES
    ):
        raise ValueError(
            "EXP-046 fit split must contain all "
            "three target classes"
        )

    fitted, family_fit = _fit_successor_families(
        fit_frame
    )

    selection_frame = split_frames[
        SELECTION_SPLIT.name
    ]
    variants: list[dict[str, object]] = []
    selection_diagnostics: dict[str, object] = {}
    selection_probability_digests: dict[
        str, str | None
    ] = {}

    for family in MODEL_FAMILIES:
        if family not in fitted:
            fit_record = family_fit[family]
            selection_diagnostics[family] = {
                "status": "FAMILY_UNAVAILABLE",
                "failure_reason": fit_record[
                    "failure_reason"
                ],
            }
            selection_probability_digests[
                family
            ] = None
            variants.extend(
                _unavailable_stability_variants(
                    family=family,
                    fit_record=fit_record,
                )
            )
            continue

        (
            probabilities,
            diagnostics,
            probability_digest,
            row_ids,
        ) = _base._score_split(
            fitted[family],
            selection_frame,
            cell=cell,
        )
        selection_diagnostics[family] = diagnostics
        selection_probability_digests[
            family
        ] = probability_digest

        for threshold in CONFIDENCE_THRESHOLDS:
            variants.append(
                _evaluated_variant(
                    family=family,
                    selection_frame=selection_frame,
                    probabilities=probabilities,
                    row_ids=row_ids,
                    threshold=threshold,
                    cell=cell,
                )
            )

    passing = [
        row
        for row in variants
        if row["selection_gate_passed"]
    ]
    selected = (
        max(passing, key=_base._selection_key)
        if passing
        else None
    )

    if not fitted:
        selection_status = (
            "NO_MODEL_FAMILY_AVAILABLE"
        )
        validation_status = (
            "LOCKED_NO_MODEL_FAMILY"
        )
        holdout_status = (
            "LOCKED_NO_MODEL_FAMILY"
        )
    else:
        selection_status = (
            "SELECTED"
            if selected is not None
            else "NO_STABLE_MODEL_CHALLENGER"
        )
        validation_status = "LOCKED_NO_SELECTION"
        holdout_status = "LOCKED_NO_SELECTION"

    result: dict[str, object] = {
        "experiment_id": STABILITY_SUCCESSOR_EXPERIMENT_ID,
        "training_core_version": (
            STABILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            STABILITY_TRAINING_CORE_DECISION
        ),
        "dec104_merged_commit": DEC104_MERGED_COMMIT,
        "dec104_protocol_blob_sha": (
            DEC104_PROTOCOL_BLOB_SHA
        ),
        "dec096_successor_training_blob_sha": (
            DEC096_SUCCESSOR_TRAINING_BLOB_SHA
        ),
        "protocol_decision": (
            STABILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            STABILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            stability_protocol_fingerprint()
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
            "families": family_fit,
        },
        "selection": {
            "status": selection_status,
            "row_count": selection_frame.height,
            "classification_by_family": (
                selection_diagnostics
            ),
            "probability_digest_by_family": (
                selection_probability_digests
            ),
            "variants": variants,
            "selected_variant": (
                {
                    "model_family": selected[
                        "model_family"
                    ],
                    "confidence_threshold": selected[
                        "confidence_threshold"
                    ],
                }
                if selected is not None
                else None
            ),
        },
        "validation": {
            "status": validation_status,
        },
        "retrospective_holdout": {
            "status": holdout_status,
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

    selected_family = str(
        selected["model_family"]
    )
    selected_threshold = float(
        selected["confidence_threshold"]
    )

    validation = _base._evaluate_selected_split(
        fitted=fitted[selected_family],
        frame=split_frames[
            VALIDATION_SPLIT.name
        ],
        cell=cell,
        threshold=selected_threshold,
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

    result["retrospective_holdout"] = (
        _base._evaluate_selected_split(
            fitted=fitted[selected_family],
            frame=split_frames[
                RETROSPECTIVE_HOLDOUT_SPLIT.name
            ],
            cell=cell,
            threshold=selected_threshold,
            gate_scenarios=HOLDOUT_GATE_SCENARIOS,
        )
    )
    result["result_fingerprint"] = _sha256(result)
    return result


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "DEC096_SUCCESSOR_TRAINING_BLOB_SHA",
    "DEC104_MERGED_COMMIT",
    "DEC104_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "STABILITY_TRAINING_CORE_DECISION",
    "STABILITY_TRAINING_CORE_VERSION",
    "STABILITY_TRAINING_RESULT_EXECUTION_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "run_stability_model_cell_core",
    "validate_stability_training_sources",
]
