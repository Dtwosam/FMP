from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .artifacts import (
    EVIDENCE_CONTRACT_VERSION,
    PHASE6_ARTIFACT_PROTOCOL,
    _artifact_record,
    _atomic_write,
    _runtime_versions,
    _scan_final_test_lock,
    _stable_json_bytes,
)
from .contracts import (
    EXPERIMENT_ID,
    FEATURE_SET_VERSION,
    FIT_SPLIT,
    FROZEN_STRATEGIES,
    PHASE5_CHECKPOINT_SHA,
    SELECTION_SPLIT,
    USDJPY_PROCESSED_MANIFEST_SHA256,
    ModelFamily,
)
from .data import MODEL_INPUT_COLUMNS
from .estimators import EXPERIMENT_SEED, build_estimator
from .evaluation import (
    _dataset_digest,
    _input_null_counts,
    _labeled_model_rows,
    _load_split_dataset,
    _research_split,
    _serialize_financial,
    _split_evidence,
    _strategy_evidence,
    run_candidate_backtest,
    run_phase6_strategy_cell,
)
from .preprocessing import PreprocessingFitFailure


FAIL_CLOSED_EXECUTION_STATUS = "FAIL_CLOSED_MODEL_FAILURE"
FAIL_CLOSED_VARIANT_STATUS = "NOT_EVALUATED_MODEL_FIT_FAILED"


def _model_config(family: ModelFamily) -> dict[str, object]:
    estimator = build_estimator(family)
    params = estimator.get_params(deep=False)
    if family is ModelFamily.LOGISTIC_REGRESSION:
        keys = (
            "penalty",
            "C",
            "solver",
            "tol",
            "fit_intercept",
            "class_weight",
            "max_iter",
            "warm_start",
        )
    else:
        keys = (
            "loss",
            "learning_rate",
            "max_iter",
            "max_leaf_nodes",
            "max_depth",
            "min_samples_leaf",
            "l2_regularization",
            "max_features",
            "max_bins",
            "early_stopping",
            "warm_start",
            "class_weight",
            "random_state",
        )
    return {key: params[key] for key in keys}


def _failure_model_evidence(
    family: ModelFamily,
    *,
    failure: PreprocessingFitFailure,
    fit_row_count: int,
    null_counts: list[int],
) -> dict[str, object]:
    return {
        "preprocessing": {
            "status": "FAILED",
            "input_columns": list(MODEL_INPUT_COLUMNS),
            "null_counts": list(null_counts),
            "medians": None,
            "scaler_mean": None,
            "scaler_scale": None,
            "failure_reason_code": failure.reason_code,
            "failure_column": failure.column,
        },
        "model_config": _model_config(family),
        "random_seed": EXPERIMENT_SEED,
        "fit_row_count": fit_row_count,
        "fit_status": {
            "status": "PREPROCESSING_FAILED",
            "reason_code": failure.reason_code,
            "column": failure.column,
            "fit_count": 0,
            "fit_split": FIT_SPLIT.name,
            "refit_after_selection": False,
        },
        "transforms": {},
        "fit_score_digest": None,
        "selection_score_digest": None,
        "cutoffs": [],
        "fit_diagnostics": None,
        "selection_diagnostics": None,
    }


def _failure_variants() -> list[dict[str, object]]:
    return [
        {
            "model_family": family.value,
            "retained_fraction": retained_fraction,
            "status": FAIL_CLOSED_VARIANT_STATUS,
            "cutoff": None,
            "retention": None,
            "filtered": None,
            "gate": None,
        }
        for family in ModelFamily
        for retained_fraction in (0.75, 0.50, 0.25)
    ]


def _build_failure_result(
    *,
    dataset_root: Path,
    processed_manifest_path: Path,
    feature_root: Path,
    feature_manifest_path: Path,
    strategy_id: str,
    code_commit: str,
    failure: PreprocessingFitFailure,
) -> dict[str, object]:
    fit = _load_split_dataset(
        dataset_root=Path(dataset_root),
        processed_manifest_path=Path(processed_manifest_path),
        feature_root=Path(feature_root),
        feature_manifest_path=Path(feature_manifest_path),
        strategy_id=strategy_id,
        split=FIT_SPLIT,
    )
    selection = _load_split_dataset(
        dataset_root=Path(dataset_root),
        processed_manifest_path=Path(processed_manifest_path),
        feature_root=Path(feature_root),
        feature_manifest_path=Path(feature_manifest_path),
        strategy_id=strategy_id,
        split=SELECTION_SPLIT,
    )
    fit_features, fit_ids, _ = _labeled_model_rows(fit)
    null_counts = _input_null_counts(fit_features)
    failure_index = list(MODEL_INPUT_COLUMNS).index(failure.column)
    if null_counts[failure_index] != len(fit_ids):
        raise ValueError(
            "Phase 6 fail-closed evidence no longer reproduces the all-null fit condition"
        )

    selection_candidates = selection["candidates"]
    selection_bars = selection["bars"]
    if not isinstance(selection_candidates, tuple) or not isinstance(selection_bars, tuple):
        raise TypeError("invalid Phase 6 selection dataset while recording model failure")
    baseline = run_candidate_backtest(
        bars=selection_bars,
        candidates=selection_candidates,
        strategy_id=strategy_id,
        split=SELECTION_SPLIT,
        code_commit=code_commit,
        slippage_pips=0.2,
    )

    label_by_id = fit["label_by_id"]
    if not isinstance(label_by_id, Mapping):
        raise TypeError("invalid Phase 6 fit label mapping while recording model failure")

    models = {
        family.value: _failure_model_evidence(
            family,
            failure=failure,
            fit_row_count=len(fit_ids),
            null_counts=null_counts,
        )
        for family in ModelFamily
    }
    selection_artifact: dict[str, object] = {
        "experiment_id": EXPERIMENT_ID,
        "evidence_contract_version": EVIDENCE_CONTRACT_VERSION,
        "strategy_id": strategy_id,
        "strategy": _strategy_evidence(strategy_id),
        "code_commit": code_commit,
        "feature_set_version": FEATURE_SET_VERSION,
        "phase5_checkpoint_sha": PHASE5_CHECKPOINT_SHA,
        "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
        "fit_split": {
            "start": FIT_SPLIT.start.isoformat(),
            "end_exclusive": FIT_SPLIT.end_exclusive.isoformat(),
        },
        "selection_split": {
            "start": SELECTION_SPLIT.start.isoformat(),
            "end_exclusive": SELECTION_SPLIT.end_exclusive.isoformat(),
        },
        "datasets": {
            "fit": _split_evidence(fit),
            "selection": _split_evidence(selection),
        },
        "fit_dataset_digest": _dataset_digest(fit["model_frame"], label_by_id),
        "fit_feature_manifest_sha256": fit["feature_manifest_sha256"],
        "selection_feature_manifest_sha256": selection["feature_manifest_sha256"],
        "models": models,
        "baseline_02": _serialize_financial(baseline),
        "variants": _failure_variants(),
        "tie_break_order": [
            "net_return_improvement",
            "expectancy_improvement",
            "profit_factor_improvement",
            "lower_max_drawdown",
            "higher_trade_count",
            "logistic_before_histogram",
            "retained_0.75_before_0.50_before_0.25",
        ],
        "selected_variant": "NO_ML_CHALLENGER",
        "failure": {
            "status": "PREPROCESSING_FAILED",
            "reason_code": failure.reason_code,
            "column": failure.column,
            "scope": "ALL_FROZEN_MODELS",
        },
    }
    result = {
        "experiment_id": EXPERIMENT_ID,
        "strategy_id": strategy_id,
        "code_commit": code_commit,
        "execution_status": FAIL_CLOSED_EXECUTION_STATUS,
        "selection": selection_artifact,
        "validation": {
            "status": "NO_ML_CHALLENGER",
            "validation_loaded": False,
            "reason": "ALL_FROZEN_MODELS_FAILED_PREPROCESSING",
        },
    }
    _scan_final_test_lock(result)
    return result


def run_phase6_strategy_cell_or_failure(
    *,
    dataset_root: Path,
    processed_manifest_path: Path,
    feature_root: Path,
    feature_manifest_path: Path,
    strategy_id: str,
    out_dir: Path,
    code_commit: str,
) -> dict[str, object]:
    try:
        return run_phase6_strategy_cell(
            dataset_root=dataset_root,
            processed_manifest_path=processed_manifest_path,
            feature_root=feature_root,
            feature_manifest_path=feature_manifest_path,
            strategy_id=strategy_id,
            out_dir=out_dir,
            code_commit=code_commit,
        )
    except PreprocessingFitFailure as failure:
        result = _build_failure_result(
            dataset_root=dataset_root,
            processed_manifest_path=processed_manifest_path,
            feature_root=feature_root,
            feature_manifest_path=feature_manifest_path,
            strategy_id=strategy_id,
            code_commit=code_commit,
            failure=failure,
        )
        selection_path = Path(out_dir) / "selection.json"
        _atomic_write(selection_path, _stable_json_bytes(result["selection"]))
        return result


def _validate_failure_result(result: Mapping[str, object]) -> dict[str, object]:
    if result.get("execution_status") != FAIL_CLOSED_EXECUTION_STATUS:
        raise ValueError("not a Phase 6 fail-closed model result")
    if result.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("Phase 6 fail-closed experiment identity mismatch")
    strategy_id = result.get("strategy_id")
    if strategy_id not in FROZEN_STRATEGIES:
        raise ValueError("Phase 6 fail-closed strategy identity mismatch")
    code_commit = result.get("code_commit")
    if not isinstance(code_commit, str) or not code_commit:
        raise ValueError("Phase 6 fail-closed code commit is missing")
    selection = result.get("selection")
    if not isinstance(selection, Mapping):
        raise ValueError("Phase 6 fail-closed selection evidence is missing")
    if selection.get("selected_variant") != "NO_ML_CHALLENGER":
        raise ValueError("Phase 6 fail-closed result cannot select a challenger")
    if selection.get("feature_set_version") != FEATURE_SET_VERSION:
        raise ValueError("Phase 6 fail-closed feature identity mismatch")
    if selection.get("phase5_checkpoint_sha") != PHASE5_CHECKPOINT_SHA:
        raise ValueError("Phase 6 fail-closed Phase 5 checkpoint mismatch")
    if selection.get("processed_manifest_sha256") != USDJPY_PROCESSED_MANIFEST_SHA256:
        raise ValueError("Phase 6 fail-closed processed identity mismatch")
    models = selection.get("models")
    if not isinstance(models, Mapping) or set(models) != {family.value for family in ModelFamily}:
        raise ValueError("Phase 6 fail-closed evidence must bind both frozen models")
    for family in ModelFamily:
        model = models[family.value]
        if not isinstance(model, Mapping):
            raise ValueError("Phase 6 fail-closed model evidence must be a mapping")
        status = model.get("fit_status")
        if not isinstance(status, Mapping):
            raise ValueError("Phase 6 fail-closed fit status is missing")
        if status.get("status") != "PREPROCESSING_FAILED":
            raise ValueError("Phase 6 fail-closed model status mismatch")
        if status.get("reason_code") != "ALL_NULL_FIT_COLUMN":
            raise ValueError("Phase 6 fail-closed reason mismatch")
        if status.get("fit_count") != 0 or status.get("refit_after_selection") is not False:
            raise ValueError("Phase 6 fail-closed fit accounting mismatch")
    variants = selection.get("variants")
    if not isinstance(variants, list) or len(variants) != 6:
        raise ValueError("Phase 6 fail-closed evidence must bind six frozen variants")
    expected = {
        (family.value, fraction)
        for family in ModelFamily
        for fraction in (0.75, 0.50, 0.25)
    }
    actual = {
        (row.get("model_family"), row.get("retained_fraction"))
        for row in variants
        if isinstance(row, Mapping)
        and row.get("status") == FAIL_CLOSED_VARIANT_STATUS
    }
    if actual != expected:
        raise ValueError("Phase 6 fail-closed variant evidence mismatch")
    validation = result.get("validation")
    if not isinstance(validation, Mapping):
        raise ValueError("Phase 6 fail-closed validation evidence is missing")
    if validation.get("status") != "NO_ML_CHALLENGER" or validation.get("validation_loaded") is not False:
        raise ValueError("Phase 6 fail-closed validation must remain unopened")
    _scan_final_test_lock(result)
    return dict(result)


def write_phase6_fail_closed_artifacts(
    result: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    normalized = _validate_failure_result(result)
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    selection_path = root / "selection.json"
    result_path = root / "result.json"
    _atomic_write(selection_path, _stable_json_bytes(normalized["selection"]))
    _atomic_write(result_path, _stable_json_bytes(normalized))
    manifest: dict[str, object] = {
        "protocol": PHASE6_ARTIFACT_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "strategy_id": normalized["strategy_id"],
        "code_commit": normalized["code_commit"],
        "feature_set_version": FEATURE_SET_VERSION,
        "phase5_checkpoint_sha": PHASE5_CHECKPOINT_SHA,
        "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
        "execution_status": FAIL_CLOSED_EXECUTION_STATUS,
        "runtime_versions": _runtime_versions(),
        "artifacts": [
            _artifact_record(selection_path),
            _artifact_record(result_path),
        ],
    }
    _scan_final_test_lock(manifest)
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest
