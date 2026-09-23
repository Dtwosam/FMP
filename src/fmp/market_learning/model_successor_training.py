from __future__ import annotations

import hashlib
import json
from pathlib import Path

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
from .model_successor_protocol import (
    ALL_FAMILIES_UNAVAILABLE_STATUS,
    BASE_PROTOCOL_FINGERPRINT,
    LOGISTIC_NONCONVERGENCE_POLICY,
    NO_FINANCIAL_CHALLENGER_STATUS,
    PREDECESSOR_FAILED_MODEL_RUN_ID,
    PRIOR_RESULT_INFORMED,
    SUCCESSOR_EXPERIMENT_ID,
    SUCCESSOR_PROTOCOL_DECISION,
    SUCCESSOR_PROTOCOL_VERSION,
    UNTOUCHED_OOS,
    successor_protocol_fingerprint,
)


SUCCESSOR_TRAINING_CORE_VERSION = (
    "fmp-exp045-model-training-core-v1"
)
SUCCESSOR_TRAINING_CORE_DECISION = "DEC-096"

BASE_TRAINING_CORE_BLOB_SHA = (
    "34b50a3f907d26b1c5ec50a0a0b444a3417d04f7"
)
SUCCESSOR_PROTOCOL_BLOB_SHA = (
    "44129fc5337fb55b9c7d81f5ba0561ea788bd264"
)

SUCCESSOR_TRAINING_RESULT_EXECUTION_AUTHORIZED = False
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


def validate_successor_training_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "base_training_core": (
            root / "src/fmp/market_learning/model_training.py",
            BASE_TRAINING_CORE_BLOB_SHA,
        ),
        "successor_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_protocol.py",
            SUCCESSOR_PROTOCOL_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-045 training source dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-045 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    protocol_fingerprint = successor_protocol_fingerprint()
    if len(protocol_fingerprint) != 64:
        raise ValueError(
            "EXP-045 successor protocol fingerprint is invalid"
        )

    return {
        "successor_training_core_version": (
            SUCCESSOR_TRAINING_CORE_VERSION
        ),
        "successor_training_core_decision": (
            SUCCESSOR_TRAINING_CORE_DECISION
        ),
        "base_training_core_blob_sha": actual[
            "base_training_core"
        ],
        "successor_protocol_blob_sha": actual[
            "successor_protocol"
        ],
        "successor_protocol_fingerprint": (
            protocol_fingerprint
        ),
        "successor_training_result_execution_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "trading_authorized": False,
    }


def _fit_successor_families(
    fit_frame: pl.DataFrame,
) -> tuple[
    dict[str, _base.FittedMarketModel],
    dict[str, dict[str, object]],
]:
    fitted: dict[str, _base.FittedMarketModel] = {}
    fit_evidence: dict[str, dict[str, object]] = {}

    for family in MODEL_FAMILIES:
        try:
            fitted_model = _base._fit_family(
                family,
                fit_frame,
            )
        except RuntimeError as exc:
            if (
                family == "logistic_regression"
                and str(exc)
                == "EXP-044 logistic regression failed to converge"
            ):
                policy = dict(
                    LOGISTIC_NONCONVERGENCE_POLICY
                )
                fit_evidence[family] = {
                    "status": policy["family_status"],
                    "failure_reason": policy[
                        "failure_reason"
                    ],
                    "fit_attempt_count": 1,
                    "retry_authorized": False,
                }
                continue
            raise

        fitted[family] = fitted_model
        fit_evidence[family] = {
            "status": "FITTED",
            "fit_attempt_count": 1,
            "preprocessor_fingerprint": (
                fitted_model.preprocessor_fingerprint
            ),
            "model_fingerprint": (
                fitted_model.model_fingerprint
            ),
        }

    return fitted, fit_evidence


def _unavailable_variants(
    *,
    family: str,
    fit_record: dict[str, object],
) -> list[dict[str, object]]:
    policy = dict(LOGISTIC_NONCONVERGENCE_POLICY)
    return [
        {
            "model_family": family,
            "confidence_threshold": threshold,
            "family_fit_status": fit_record["status"],
            "evaluation_status": policy[
                "variant_status"
            ],
            "failure_reason": fit_record[
                "failure_reason"
            ],
            "selection_gate_passed": False,
        }
        for threshold in CONFIDENCE_THRESHOLDS
    ]


def run_successor_model_cell_core(
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
            "EXP-045 model cell has empty required "
            f"split(s): {empty}"
        )

    fit_frame = split_frames[FIT_SPLIT.name]
    fit_counts = _base._target_counts(fit_frame)
    if any(
        fit_counts[name] <= 0
        for name in TARGET_CLASSES
    ):
        raise ValueError(
            "EXP-045 fit split must contain all "
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
                _unavailable_variants(
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
            evaluated = _base._evaluate_threshold(
                selection_frame,
                probabilities,
                threshold=threshold,
                scenarios=SELECTION_GATE_SCENARIOS,
                row_ids=row_ids,
            )
            scenario = evaluated["scenarios"]["0.5"]
            variants.append(
                {
                    "model_family": family,
                    "family_fit_status": "FITTED",
                    "evaluation_status": "EVALUATED",
                    **evaluated,
                    "selection_gate_passed": bool(
                        scenario["gate"]["passed"]
                    ),
                }
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
            ALL_FAMILIES_UNAVAILABLE_STATUS
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
            else NO_FINANCIAL_CHALLENGER_STATUS
        )
        validation_status = "LOCKED_NO_SELECTION"
        holdout_status = "LOCKED_NO_SELECTION"

    result: dict[str, object] = {
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "training_core_version": (
            SUCCESSOR_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            SUCCESSOR_TRAINING_CORE_DECISION
        ),
        "base_training_core_blob_sha": (
            BASE_TRAINING_CORE_BLOB_SHA
        ),
        "protocol_decision": (
            SUCCESSOR_PROTOCOL_DECISION
        ),
        "protocol_version": (
            SUCCESSOR_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            successor_protocol_fingerprint()
        ),
        "base_protocol_fingerprint": (
            BASE_PROTOCOL_FINGERPRINT
        ),
        "predecessor_failed_model_run_id": (
            PREDECESSOR_FAILED_MODEL_RUN_ID
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
    "BASE_TRAINING_CORE_BLOB_SHA",
    "MODEL_FIT_AUTHORIZED",
    "SUCCESSOR_PROTOCOL_BLOB_SHA",
    "SUCCESSOR_TRAINING_CORE_DECISION",
    "SUCCESSOR_TRAINING_CORE_VERSION",
    "SUCCESSOR_TRAINING_RESULT_EXECUTION_AUTHORIZED",
    "run_successor_model_cell_core",
    "validate_successor_training_sources",
]
