from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Mapping, Sequence

from .contracts import EVIDENCE_LABEL
from .model_artifacts import (
    AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID,
    AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT,
    AUTHORITATIVE_FEATURE_RUN_ID,
    AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID,
    AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT,
    AUTHORITATIVE_OUTCOME_RUN_ID,
    AUTHORITATIVE_READINESS_ARTIFACT_ID,
    AUTHORITATIVE_READINESS_FINGERPRINT,
    VerifiedCellArtifacts,
    load_authoritative_cell_artifacts,
    validate_authoritative_readiness,
)
from .model_protocol import (
    DIAGNOSTIC_SCENARIOS,
    HOLDOUT_GATE_SCENARIOS,
    MODEL_CELLS,
    VALIDATION_GATE_SCENARIOS,
)
from .model_successor_density_protocol import CANDIDATE_BUDGET_ANCHORS
from .model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL,
    FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION,
    FIT_TEMPORAL_SUPPORT_WINDOWS,
    PRIOR_RESULT_INFORMED,
    UNTOUCHED_OOS,
    fit_temporal_support_utility_protocol_fingerprint,
)
from .model_successor_fit_temporal_support_utility_training import (
    DEC163_MERGED_COMMIT,
    DEC163_PROTOCOL_BLOB_SHA,
    FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_VERSION,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    run_fit_temporal_support_utility_model_cell_core,
    validate_fit_temporal_support_utility_training_sources,
)
from .model_successor_regime_utility_artifacts import (
    _canonical_json,
    _git_blob_sha,
    _sha256,
    _validate_commit,
    _validate_financial_gate,
    _validate_sha256,
    _validate_target_summary,
    _validate_window,
)
from .model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    TEMPORAL_STABILITY_WINDOWS,
)
from .model_successor_temporal_calibrated_utility_protocol import (
    FINANCIAL_TARGET_COLUMNS,
)
from .model_successor_temporal_jackknife_utility_protocol import (
    FIT_JACKKNIFE_VIEWS,
)


FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION = (
    "fmp-exp052-fit-temporal-support-utility-artifact-runner-v1"
)
FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION = "DEC-165"
FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EVIDENCE_VERSION = 1

DEC164_MERGED_COMMIT = "d9f893504b2d790eb73bc49edf4c0919ef2ff914"
DEC164_TRAINING_CORE_BLOB_SHA = (
    "fe5664438752a161134bbed6f55d9985f1c1470a"
)
LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)
PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA = (
    "6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13"
)

AUTHORITATIVE_FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = (
    False
)
FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _view_definitions() -> dict[str, dict[str, object]]:
    return {
        str(raw["name"]): {
            "included_regimes": tuple(
                str(value) for value in raw["included_regimes"]
            ),
            "excluded_regime": str(raw["excluded_regime"]),
        }
        for raw in FIT_JACKKNIFE_VIEWS
    }


def _support_windows_by_parent() -> dict[str, dict[str, dict[str, object]]]:
    grouped: dict[str, dict[str, dict[str, object]]] = {}
    for raw in FIT_TEMPORAL_SUPPORT_WINDOWS:
        window = dict(raw)
        parent = str(window["parent_regime"])
        grouped.setdefault(parent, {})[str(window["name"])] = window
    return grouped


def validate_fit_temporal_support_utility_artifact_runner_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "legacy_data_loader": (
            root / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "dec163_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_support_utility_protocol.py",
            DEC163_PROTOCOL_BLOB_SHA,
        ),
        "dec164_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_support_utility_training.py",
            DEC164_TRAINING_CORE_BLOB_SHA,
        ),
        "predecessor_artifact_helper": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_utility_artifacts.py",
            PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-052 artifact dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-052 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    training = validate_fit_temporal_support_utility_training_sources(
        repository_root=root,
    )
    if training[
        "fit_temporal_support_utility_training_core_decision"
    ] != FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION:
        raise ValueError("EXP-052 training-core decision drift")
    if training["model_fit_authorized"] is not False:
        raise ValueError("EXP-052 training-core fit authorization drift")
    if training[
        "fit_temporal_support_utility_result_execution_authorized"
    ] is not False:
        raise ValueError(
            "EXP-052 training-core result authorization drift"
        )

    fingerprint = fit_temporal_support_utility_protocol_fingerprint()
    if len(fingerprint) != 64:
        raise ValueError("EXP-052 protocol fingerprint is invalid")

    return {
        "fit_temporal_support_utility_model_artifact_runner_version": (
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "fit_temporal_support_utility_model_artifact_runner_decision": (
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "dec163_merged_commit": DEC163_MERGED_COMMIT,
        "dec164_merged_commit": DEC164_MERGED_COMMIT,
        "dec163_protocol_blob_sha": actual["dec163_protocol"],
        "dec164_training_core_blob_sha": actual["dec164_training_core"],
        "predecessor_training_core_blob_sha": (
            PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "legacy_data_loader_blob_sha": actual["legacy_data_loader"],
        "predecessor_artifact_helper_blob_sha": actual[
            "predecessor_artifact_helper"
        ],
        "fit_temporal_support_utility_protocol_fingerprint": fingerprint,
        "authoritative_fit_temporal_support_utility_model_result_execution_authorized": (
            False
        ),
        "fit_temporal_support_utility_model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _finite_number(value: object, *, field: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise ValueError(f"{field} must be finite")
    return float(value)


def _validate_fit_block(
    fit: Mapping[str, object],
) -> tuple[int, int, int]:
    expected_views = _view_definitions()
    models = fit.get("jackknife_models")
    if not isinstance(models, Mapping) or set(models) != set(expected_views):
        raise ValueError("EXP-052 jackknife fit inventory mismatch")
    if fit.get("jackknife_view_count") != 3:
        raise ValueError("EXP-052 jackknife view count mismatch")
    if fit.get("regressor_count") != 6:
        raise ValueError("EXP-052 total regressor count mismatch")

    verified_regressors = 0
    for view_name in sorted(expected_views):
        record = models.get(view_name)
        if not isinstance(record, Mapping):
            raise ValueError("EXP-052 jackknife fit record malformed")
        expected = expected_views[view_name]
        if record.get("status") != "FITTED":
            raise ValueError("EXP-052 jackknife fit status mismatch")
        included = record.get("included_regimes")
        if (
            not isinstance(included, list)
            or tuple(str(v) for v in included)
            != expected["included_regimes"]
        ):
            raise ValueError(
                "EXP-052 jackknife included-regime identity mismatch"
            )
        if record.get("excluded_regime") != expected["excluded_regime"]:
            raise ValueError(
                "EXP-052 jackknife excluded-regime identity mismatch"
            )
        row_count = record.get("row_count")
        if (
            not isinstance(row_count, int)
            or isinstance(row_count, bool)
            or row_count <= 0
        ):
            raise ValueError("EXP-052 jackknife row count invalid")
        if record.get("regressor_count") != 2:
            raise ValueError("EXP-052 jackknife regressor count mismatch")
        regressors = record.get("regressors")
        if (
            not isinstance(regressors, Mapping)
            or set(regressors) != set(FINANCIAL_TARGET_COLUMNS)
        ):
            raise ValueError("EXP-052 regressor inventory mismatch")
        for target in FINANCIAL_TARGET_COLUMNS:
            target_record = regressors.get(target)
            if not isinstance(target_record, Mapping):
                raise ValueError("EXP-052 regressor record malformed")
            if (
                target_record.get("status") != "FITTED"
                or target_record.get("fit_attempt_count") != 1
            ):
                raise ValueError("EXP-052 regressor fit record mismatch")
            summary = target_record.get("target_summary")
            if not isinstance(summary, Mapping):
                raise ValueError("EXP-052 target summary missing")
            _validate_target_summary(
                summary,
                expected_row_count=row_count,
                field=f"EXP-052 {view_name} {target}",
            )
            _validate_sha256(
                target_record.get("preprocessor_fingerprint"),
                field=(
                    f"EXP-052 {view_name} {target} "
                    "preprocessor fingerprint"
                ),
            )
            _validate_sha256(
                target_record.get("model_fingerprint"),
                field=f"EXP-052 {view_name} {target} model fingerprint",
            )
            verified_regressors += 1

    pooled = fit.get("out_of_fit_calibration_references")
    if not isinstance(pooled, Mapping) or set(pooled) != set(expected_views):
        raise ValueError("EXP-052 pooled reference inventory mismatch")
    verified_pooled = 0
    for view_name in sorted(expected_views):
        record = pooled.get(view_name)
        if not isinstance(record, Mapping):
            raise ValueError("EXP-052 pooled reference record malformed")
        expected = expected_views[view_name]
        if record.get("status") != "FROZEN":
            raise ValueError("EXP-052 pooled reference status mismatch")
        if record.get("excluded_regime") != expected["excluded_regime"]:
            raise ValueError("EXP-052 pooled excluded-regime mismatch")
        included = record.get("included_regimes")
        if (
            not isinstance(included, list)
            or tuple(str(v) for v in included)
            != expected["included_regimes"]
        ):
            raise ValueError("EXP-052 pooled included-regime mismatch")
        row_count = record.get("row_count")
        if (
            not isinstance(row_count, int)
            or isinstance(row_count, bool)
            or row_count <= 0
        ):
            raise ValueError("EXP-052 pooled row count invalid")
        if record.get("target_count") != 2:
            raise ValueError("EXP-052 pooled target count mismatch")
        targets = record.get("targets")
        if (
            not isinstance(targets, Mapping)
            or set(targets) != set(FINANCIAL_TARGET_COLUMNS)
        ):
            raise ValueError("EXP-052 pooled target inventory mismatch")
        for target in FINANCIAL_TARGET_COLUMNS:
            target_record = targets.get(target)
            if not isinstance(target_record, Mapping):
                raise ValueError("EXP-052 pooled target malformed")
            if (
                target_record.get("status") != "FROZEN"
                or target_record.get("excluded_regime")
                != expected["excluded_regime"]
                or target_record.get("row_count") != row_count
            ):
                raise ValueError("EXP-052 pooled target identity mismatch")
            minimum = _finite_number(
                target_record.get("minimum_prediction"),
                field="EXP-052 pooled minimum",
            )
            maximum = _finite_number(
                target_record.get("maximum_prediction"),
                field="EXP-052 pooled maximum",
            )
            mean = _finite_number(
                target_record.get("mean_prediction"),
                field="EXP-052 pooled mean",
            )
            if minimum > maximum or not minimum <= mean <= maximum:
                raise ValueError("EXP-052 pooled prediction bounds invalid")
            _validate_sha256(
                target_record.get("row_bound_prediction_digest"),
                field=f"EXP-052 {view_name} {target} pooled prediction digest",
            )
            _validate_sha256(
                target_record.get("sorted_reference_digest"),
                field=f"EXP-052 {view_name} {target} pooled reference digest",
            )
            verified_pooled += 1
    if fit.get("calibration_reference_count") != 6 or verified_pooled != 6:
        raise ValueError("EXP-052 pooled reference count mismatch")

    support = fit.get("fit_temporal_support_references")
    if not isinstance(support, Mapping) or set(support) != set(expected_views):
        raise ValueError("EXP-052 support reference inventory mismatch")
    windows_by_parent = _support_windows_by_parent()
    verified_support = 0
    for view_name in sorted(expected_views):
        record = support.get(view_name)
        if not isinstance(record, Mapping):
            raise ValueError("EXP-052 support view record malformed")
        expected = expected_views[view_name]
        excluded = str(expected["excluded_regime"])
        if record.get("status") != "FROZEN":
            raise ValueError("EXP-052 support view status mismatch")
        if record.get("excluded_regime") != excluded:
            raise ValueError("EXP-052 support excluded-regime mismatch")
        included = record.get("included_regimes")
        if (
            not isinstance(included, list)
            or tuple(str(v) for v in included)
            != expected["included_regimes"]
        ):
            raise ValueError("EXP-052 support included-regime mismatch")
        if record.get("target_count") != 2:
            raise ValueError("EXP-052 support target count mismatch")
        if record.get("support_reference_count") != 8:
            raise ValueError("EXP-052 support view reference count mismatch")
        targets = record.get("targets")
        if (
            not isinstance(targets, Mapping)
            or set(targets) != set(FINANCIAL_TARGET_COLUMNS)
        ):
            raise ValueError("EXP-052 support target inventory mismatch")
        expected_windows = windows_by_parent.get(excluded)
        if not expected_windows or len(expected_windows) != 4:
            raise ValueError("EXP-052 expected support windows missing")
        for target in FINANCIAL_TARGET_COLUMNS:
            target_record = targets.get(target)
            if not isinstance(target_record, Mapping):
                raise ValueError("EXP-052 support target malformed")
            if (
                target_record.get("status") != "FROZEN"
                or target_record.get("excluded_regime") != excluded
                or target_record.get("window_count") != 4
            ):
                raise ValueError("EXP-052 support target identity mismatch")
            windows = target_record.get("windows")
            if (
                not isinstance(windows, Mapping)
                or set(windows) != set(expected_windows)
            ):
                raise ValueError("EXP-052 support window inventory mismatch")
            for window_name in sorted(expected_windows):
                supplied = windows.get(window_name)
                expected_window = expected_windows[window_name]
                if not isinstance(supplied, Mapping):
                    raise ValueError("EXP-052 support window malformed")
                for field in (
                    "name",
                    "parent_regime",
                    "start",
                    "end_exclusive",
                ):
                    if supplied.get(field) != expected_window[field]:
                        raise ValueError(
                            f"EXP-052 support window {field} mismatch"
                        )
                if supplied.get("status") != "FROZEN":
                    raise ValueError("EXP-052 support window status mismatch")
                row_count = supplied.get("row_count")
                if (
                    not isinstance(row_count, int)
                    or isinstance(row_count, bool)
                    or row_count <= 0
                ):
                    raise ValueError("EXP-052 support window row count invalid")
                minimum = _finite_number(
                    supplied.get("minimum_prediction"),
                    field="EXP-052 support minimum",
                )
                maximum = _finite_number(
                    supplied.get("maximum_prediction"),
                    field="EXP-052 support maximum",
                )
                mean = _finite_number(
                    supplied.get("mean_prediction"),
                    field="EXP-052 support mean",
                )
                if minimum > maximum or not minimum <= mean <= maximum:
                    raise ValueError(
                        "EXP-052 support prediction bounds invalid"
                    )
                _validate_sha256(
                    supplied.get("row_bound_prediction_digest"),
                    field=(
                        f"EXP-052 {view_name} {target} "
                        f"{window_name} prediction digest"
                    ),
                )
                _validate_sha256(
                    supplied.get("sorted_reference_digest"),
                    field=(
                        f"EXP-052 {view_name} {target} "
                        f"{window_name} reference digest"
                    ),
                )
                verified_support += 1

    if (
        fit.get("fit_temporal_support_reference_count")
        != FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL
        or verified_support != FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL
    ):
        raise ValueError("EXP-052 support reference count mismatch")

    forbidden = {
        "full_fit_single_model": "FORBIDDEN_BY_DEC150_DEC163",
        "view_weight_search": "FORBIDDEN_BY_DEC150_DEC163",
        "view_fallback": "FORBIDDEN_BY_DEC150_DEC163",
        "selection_window_calibration": "FORBIDDEN_BY_DEC150_DEC163",
        "hist_gradient_boosting_classifier": "EXCLUDED_BY_DEC150_DEC163",
        "logistic_regression": "EXCLUDED_BY_DEC112_DEC150_DEC163",
    }
    for field, status in forbidden.items():
        if fit.get(field) != {"status": status, "fit_attempt_count": 0}:
            raise ValueError(f"EXP-052 {field} record mismatch")

    return verified_regressors, verified_pooled, verified_support


def _validate_consensus_block(
    block: Mapping[str, object],
    *,
    expected_row_count: int,
    field: str,
) -> int:
    if block.get("row_count") != expected_row_count:
        raise ValueError(f"{field} consensus row count mismatch")
    counts = block.get("consensus_direction_counts")
    names = {"LONG", "SHORT", "NO_TRADE"}
    if not isinstance(counts, Mapping) or set(counts) != names:
        raise ValueError(f"{field} consensus direction counts malformed")
    normalized: dict[str, int] = {}
    for name in sorted(names):
        value = counts.get(name)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            raise ValueError(f"{field} consensus count invalid")
        normalized[name] = value
    if sum(normalized.values()) != expected_row_count:
        raise ValueError(f"{field} consensus count total mismatch")
    eligible = normalized["LONG"] + normalized["SHORT"]
    if block.get("consensus_eligible_row_count") != eligible:
        raise ValueError(f"{field} eligible count mismatch")
    expected_rate = (
        float(eligible / expected_row_count) if expected_row_count else 0.0
    )
    rate = _finite_number(
        block.get("consensus_eligible_rate"),
        field=f"{field} eligible rate",
    )
    if not math.isclose(rate, expected_rate, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError(f"{field} eligible rate mismatch")

    keys = (
        ("minimum_robust_raw_utility", "maximum_robust_raw_utility", "raw"),
        (
            "minimum_robust_pooled_calibrated_utility",
            "maximum_robust_pooled_calibrated_utility",
            "pooled",
        ),
        (
            "minimum_robust_fit_temporal_support",
            "maximum_robust_fit_temporal_support",
            "support",
        ),
    )
    if eligible == 0:
        for low, high, _ in keys:
            if block.get(low) is not None or block.get(high) is not None:
                raise ValueError(f"{field} empty bounds mismatch")
    else:
        for low, high, label in keys:
            minimum = _finite_number(
                block.get(low),
                field=f"{field} {label} minimum",
            )
            maximum = _finite_number(
                block.get(high),
                field=f"{field} {label} maximum",
            )
            if minimum > maximum:
                raise ValueError(f"{field} {label} bounds mismatch")
            if label == "raw":
                if minimum <= 0.0:
                    raise ValueError(f"{field} raw utility must be positive")
            else:
                if minimum < 0.0 or maximum > 1.0:
                    raise ValueError(f"{field} {label} bounds out of range")

    digests = block.get("view_prediction_digests")
    expected_views = set(_view_definitions())
    if not isinstance(digests, Mapping) or set(digests) != expected_views:
        raise ValueError(f"{field} prediction digest view set mismatch")
    for view in sorted(expected_views):
        target_digests = digests.get(view)
        if (
            not isinstance(target_digests, Mapping)
            or set(target_digests) != set(FINANCIAL_TARGET_COLUMNS)
        ):
            raise ValueError(f"{field} prediction digest target set mismatch")
        for target in FINANCIAL_TARGET_COLUMNS:
            _validate_sha256(
                target_digests.get(target),
                field=f"{field} {view} {target} prediction digest",
            )
    return eligible


def _validate_triple_cutoff(
    raw: Mapping[str, object],
    *,
    field: str,
) -> tuple[float, float, float]:
    support = _finite_number(
        raw.get("selection_derived_support_cutoff"),
        field=f"{field} support cutoff",
    )
    pooled = _finite_number(
        raw.get("selection_derived_pooled_calibrated_cutoff"),
        field=f"{field} pooled cutoff",
    )
    raw_cutoff = _finite_number(
        raw.get("selection_derived_raw_cutoff"),
        field=f"{field} raw cutoff",
    )
    if not 0.0 <= support <= 1.0:
        raise ValueError(f"{field} support cutoff out of range")
    if not 0.0 <= pooled <= 1.0:
        raise ValueError(f"{field} pooled cutoff out of range")
    if raw_cutoff <= 0.0:
        raise ValueError(f"{field} raw cutoff must be positive")
    return support, pooled, raw_cutoff


def _validate_variant(
    raw: Mapping[str, object],
    *,
    expected_eligible_count: int,
) -> tuple[bool, bool, bool]:
    budget = raw.get("candidate_budget_anchor")
    if budget not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError("EXP-052 candidate budget mismatch")
    if raw.get("model_family") != "hist_gradient_boosting_regression":
        raise ValueError("EXP-052 model family mismatch")
    eligible = raw.get("eligible_utility_row_count")
    if eligible != expected_eligible_count:
        raise ValueError("EXP-052 eligible count mismatch")

    evaluation = raw.get("evaluation_status")
    if evaluation == "BUDGET_UNAVAILABLE":
        if raw.get("status") != "UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS":
            raise ValueError("EXP-052 unavailable status mismatch")
        if (
            not isinstance(eligible, int)
            or isinstance(eligible, bool)
            or eligible < 0
            or eligible >= int(budget)
        ):
            raise ValueError("EXP-052 unavailable eligible count invalid")
        for field in (
            "selection_derived_support_cutoff",
            "selection_derived_pooled_calibrated_cutoff",
            "selection_derived_raw_cutoff",
        ):
            if raw.get(field) is not None:
                raise ValueError("EXP-052 unavailable cutoff must be null")
        if raw.get("aggregate_selection_gate_passed") is not False:
            raise ValueError("EXP-052 unavailable aggregate flag mismatch")
        if raw.get("selection_gate_passed") is not False:
            raise ValueError("EXP-052 unavailable final flag mismatch")
        stability = raw.get("temporal_stability")
        if (
            not isinstance(stability, Mapping)
            or stability.get("status") != "BUDGET_UNAVAILABLE"
            or stability.get("windows") != []
            or stability.get(
                "minimum_directional_candidate_share_per_window"
            )
            != MIN_STABILITY_WINDOW_CANDIDATE_SHARE
        ):
            raise ValueError("EXP-052 unavailable stability mismatch")
        return False, False, True

    if evaluation != "EVALUATED" or raw.get("status") != "AVAILABLE":
        raise ValueError("EXP-052 evaluated variant status mismatch")
    if (
        not isinstance(eligible, int)
        or isinstance(eligible, bool)
        or eligible < int(budget)
    ):
        raise ValueError("EXP-052 available eligible count invalid")
    selected_count = raw.get("selection_candidate_count_at_cutoff")
    if (
        not isinstance(selected_count, int)
        or isinstance(selected_count, bool)
        or selected_count < int(budget)
        or selected_count > eligible
    ):
        raise ValueError("EXP-052 selected-at-cutoff count invalid")
    _validate_triple_cutoff(raw, field="EXP-052 selection")

    scenarios = raw.get("scenarios")
    if not isinstance(scenarios, Mapping) or set(scenarios) != {"0.5"}:
        raise ValueError("EXP-052 selection scenario inventory mismatch")
    scenario = scenarios["0.5"]
    if not isinstance(scenario, Mapping):
        raise ValueError("EXP-052 selection scenario malformed")
    metrics = scenario.get("metrics")
    gate = scenario.get("gate")
    if not isinstance(metrics, Mapping) or not isinstance(gate, Mapping):
        raise ValueError("EXP-052 financial evidence malformed")
    aggregate_passed = _validate_financial_gate(
        metrics=metrics,
        gate=gate,
        field="EXP-052 selection 0.5",
    )
    if raw.get("aggregate_selection_gate_passed") is not aggregate_passed:
        raise ValueError("EXP-052 aggregate flag mismatch")

    stability = raw.get("temporal_stability")
    if not isinstance(stability, Mapping):
        raise ValueError("EXP-052 stability evidence malformed")
    if (
        stability.get("minimum_directional_candidate_share_per_window")
        != MIN_STABILITY_WINDOW_CANDIDATE_SHARE
    ):
        raise ValueError("EXP-052 stability share floor mismatch")

    stability_passed = False
    if aggregate_passed:
        windows = stability.get("windows")
        if (
            not isinstance(windows, list)
            or len(windows) != len(TEMPORAL_STABILITY_WINDOWS)
        ):
            raise ValueError("EXP-052 stability window inventory mismatch")
        full_count = metrics.get("directional_candidate_count")
        if not isinstance(full_count, int):
            raise ValueError("EXP-052 aggregate candidate count invalid")
        passes = [
            _validate_window(
                supplied,
                expected=dict(expected),
                full_selection_candidate_count=full_count,
            )
            for supplied, expected in zip(
                windows, TEMPORAL_STABILITY_WINDOWS, strict=True
            )
        ]
        stability_passed = all(passes)
        if stability.get("status") != (
            "PASS" if stability_passed else "REJECT"
        ):
            raise ValueError("EXP-052 stability status mismatch")
    else:
        if (
            stability.get("status") != "LOCKED_AGGREGATE_REJECT"
            or stability.get("windows") != []
        ):
            raise ValueError("EXP-052 aggregate reject stability mismatch")

    final_pass = aggregate_passed and stability_passed
    if raw.get("selection_gate_passed") is not final_pass:
        raise ValueError("EXP-052 final selection flag mismatch")
    return aggregate_passed, final_pass, False


def _validate_status_chain(
    *,
    selection: object,
    validation: object,
    holdout: object,
) -> None:
    if selection == "NO_FIT_TEMPORAL_SUPPORT_UTILITY_STABLE_MODEL_CHALLENGER":
        if validation != "LOCKED_NO_SELECTION" or holdout != "LOCKED_NO_SELECTION":
            raise ValueError("EXP-052 no-selection forward lock mismatch")
        return
    if selection != "SELECTED":
        raise ValueError(f"unexpected EXP-052 selection status: {selection!r}")
    if validation == "REJECT":
        if holdout != "LOCKED_VALIDATION_REJECT":
            raise ValueError("EXP-052 validation reject holdout mismatch")
        return
    if validation == "PASS":
        if holdout not in {"PASS", "REJECT"}:
            raise ValueError("EXP-052 validation pass holdout mismatch")
        return
    raise ValueError(f"unexpected EXP-052 validation status: {validation!r}")


def _validate_forward_block(
    block: Mapping[str, object],
    *,
    expected_row_count: int,
    field: str,
    gate_scenarios: Sequence[float],
) -> None:
    if block.get("status") not in {"PASS", "REJECT"}:
        raise ValueError(f"{field} status invalid")
    if block.get("row_count") != expected_row_count:
        raise ValueError(f"{field} row count mismatch")
    consensus = block.get("fit_temporal_support_consensus")
    if not isinstance(consensus, Mapping):
        raise ValueError(f"{field} consensus malformed")
    _validate_consensus_block(
        consensus,
        expected_row_count=expected_row_count,
        field=field,
    )
    _validate_sha256(
        block.get("fit_temporal_support_consensus_digest"),
        field=f"{field} consensus digest",
    )
    if block.get("candidate_budget_anchor") not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError(f"{field} budget mismatch")
    _validate_triple_cutoff(block, field=field)

    expected_scenarios = {
        str(float(v))
        for v in (*DIAGNOSTIC_SCENARIOS, *gate_scenarios)
    }
    scenarios = block.get("scenarios")
    if (
        not isinstance(scenarios, Mapping)
        or set(scenarios) != expected_scenarios
    ):
        raise ValueError(f"{field} scenario inventory mismatch")
    gate_results: dict[str, bool] = {}
    for name, scenario in scenarios.items():
        if not isinstance(scenario, Mapping):
            raise ValueError(f"{field} scenario malformed")
        metrics = scenario.get("metrics")
        gate = scenario.get("gate")
        if not isinstance(metrics, Mapping) or not isinstance(gate, Mapping):
            raise ValueError(f"{field} financial evidence malformed")
        gate_results[str(name)] = _validate_financial_gate(
            metrics=metrics,
            gate=gate,
            field=f"{field} {name}",
        )
    expected_pass = all(
        gate_results[str(float(v))] for v in gate_scenarios
    )
    if block.get("status") != ("PASS" if expected_pass else "REJECT"):
        raise ValueError(f"{field} status/gate mismatch")


def _validate_cell_result(raw: Mapping[str, object]) -> dict[str, object]:
    exact = {
        "experiment_id": FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID,
        "training_core_version": FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_VERSION,
        "training_core_decision": FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
        "dec163_merged_commit": DEC163_MERGED_COMMIT,
        "dec163_protocol_blob_sha": DEC163_PROTOCOL_BLOB_SHA,
        "predecessor_training_core_blob_sha": PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        "predecessor_training_core_decision": "DEC-151",
        "protocol_decision": FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION,
        "protocol_version": FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION,
        "protocol_fingerprint": fit_temporal_support_utility_protocol_fingerprint(),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": UNTOUCHED_OOS,
    }
    for field, expected in exact.items():
        if raw.get(field) != expected:
            raise ValueError(f"EXP-052 cell {field} mismatch")

    cell = raw.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError("EXP-052 cell identity malformed")
    identity = (
        cell.get("symbol"),
        cell.get("timeframe"),
        cell.get("horizon_minutes"),
    )
    expected_identities = {
        (c.symbol, c.timeframe, c.horizon_minutes) for c in MODEL_CELLS
    }
    if identity not in expected_identities:
        raise ValueError("EXP-052 cell identity unsupported")

    _validate_sha256(
        raw.get("processed_manifest_sha256"),
        field="EXP-052 processed manifest sha256",
    )
    joined = raw.get("joined_row_count")
    if (
        not isinstance(joined, int)
        or isinstance(joined, bool)
        or joined <= 0
    ):
        raise ValueError("EXP-052 joined row count invalid")
    splits = raw.get("split_row_counts")
    required = {
        "fit",
        "selection",
        "validation",
        "retrospective_holdout",
    }
    if not isinstance(splits, Mapping) or set(splits) != required:
        raise ValueError("EXP-052 split inventory mismatch")
    for name in sorted(required):
        value = splits.get(name)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value <= 0
        ):
            raise ValueError("EXP-052 split row count invalid")

    fit = raw.get("fit")
    if not isinstance(fit, Mapping):
        raise ValueError("EXP-052 fit evidence malformed")
    regressors, pooled_refs, support_refs = _validate_fit_block(fit)

    selection = raw.get("selection")
    validation = raw.get("validation")
    holdout = raw.get("retrospective_holdout")
    if (
        not isinstance(selection, Mapping)
        or not isinstance(validation, Mapping)
        or not isinstance(holdout, Mapping)
    ):
        raise ValueError("EXP-052 result-stage evidence malformed")
    if selection.get("row_count") != splits["selection"]:
        raise ValueError("EXP-052 selection row count mismatch")
    consensus = selection.get("fit_temporal_support_consensus")
    if not isinstance(consensus, Mapping):
        raise ValueError("EXP-052 selection consensus malformed")
    eligible_count = _validate_consensus_block(
        consensus,
        expected_row_count=int(splits["selection"]),
        field="EXP-052 selection",
    )
    _validate_sha256(
        selection.get("fit_temporal_support_consensus_digest"),
        field="EXP-052 selection consensus digest",
    )

    variants = selection.get("variants")
    if (
        not isinstance(variants, list)
        or len(variants) != len(CANDIDATE_BUDGET_ANCHORS)
    ):
        raise ValueError("EXP-052 variant inventory mismatch")
    if {
        item.get("candidate_budget_anchor")
        for item in variants
        if isinstance(item, Mapping)
    } != set(CANDIDATE_BUDGET_ANCHORS):
        raise ValueError("EXP-052 budget coverage mismatch")

    aggregate_pass_count = 0
    stable_pass_count = 0
    unavailable_count = 0
    stable_variants: list[Mapping[str, object]] = []
    for item in variants:
        if not isinstance(item, Mapping):
            raise ValueError("EXP-052 variant malformed")
        aggregate_passed, stable_passed, unavailable = _validate_variant(
            item,
            expected_eligible_count=eligible_count,
        )
        aggregate_pass_count += int(aggregate_passed)
        stable_pass_count += int(stable_passed)
        unavailable_count += int(unavailable)
        if stable_passed:
            stable_variants.append(item)

    selection_status = selection.get("status")
    selected = selection.get("selected_variant")
    no_challenger = "NO_FIT_TEMPORAL_SUPPORT_UTILITY_STABLE_MODEL_CHALLENGER"
    if selection_status == no_challenger:
        if stable_variants or selected is not None:
            raise ValueError("EXP-052 no-challenger selection mismatch")
    elif selection_status == "SELECTED":
        if not stable_variants or not isinstance(selected, Mapping):
            raise ValueError("EXP-052 selected variant missing")
        if (
            selected.get("model_family")
            != "hist_gradient_boosting_regression"
            or selected.get("candidate_budget_anchor")
            not in CANDIDATE_BUDGET_ANCHORS
        ):
            raise ValueError("EXP-052 selected variant identity mismatch")
        triple = _validate_triple_cutoff(
            selected,
            field="EXP-052 selected variant",
        )
        matches = []
        for item in stable_variants:
            if (
                item.get("candidate_budget_anchor")
                == selected.get("candidate_budget_anchor")
                and _validate_triple_cutoff(
                    item, field="EXP-052 stable variant"
                )
                == triple
            ):
                matches.append(item)
        if len(matches) != 1:
            raise ValueError("EXP-052 selected stable variant not unique")
    else:
        raise ValueError("EXP-052 selection status invalid")

    validation_status = validation.get("status")
    holdout_status = holdout.get("status")
    _validate_status_chain(
        selection=selection_status,
        validation=validation_status,
        holdout=holdout_status,
    )
    if validation_status in {"PASS", "REJECT"}:
        _validate_forward_block(
            validation,
            expected_row_count=int(splits["validation"]),
            field="EXP-052 validation",
            gate_scenarios=VALIDATION_GATE_SCENARIOS,
        )
    if holdout_status in {"PASS", "REJECT"}:
        _validate_forward_block(
            holdout,
            expected_row_count=int(splits["retrospective_holdout"]),
            field="EXP-052 holdout",
            gate_scenarios=HOLDOUT_GATE_SCENARIOS,
        )

    for field in (
        "model_fit_authorized",
        "promotion_authorized",
        "shadow_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if raw.get(field) is not False:
            raise ValueError(f"EXP-052 cell {field} must remain false")

    supplied = _validate_sha256(
        raw.get("result_fingerprint"),
        field="EXP-052 cell result fingerprint",
    )
    expected = _sha256(
        _canonical_json(
            {k: v for k, v in raw.items() if k != "result_fingerprint"}
        )
    )
    if supplied != expected:
        raise ValueError("EXP-052 cell result fingerprint mismatch")

    return {
        "selection_status": selection_status,
        "validation_status": validation_status,
        "holdout_status": holdout_status,
        "aggregate_selection_pass_variant_count": aggregate_pass_count,
        "stable_selection_pass_variant_count": stable_pass_count,
        "unavailable_budget_variant_count": unavailable_count,
        "utility_eligible_selection_row_count": eligible_count,
        "verified_regressor_count": regressors,
        "verified_pooled_calibration_reference_count": pooled_refs,
        "verified_fit_temporal_support_reference_count": support_refs,
    }


def _compile_summary(
    cell_results: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validated = [_validate_cell_result(item) for item in cell_results]
    return {
        "verified_cell_count": len(validated),
        "selected_cell_count": sum(
            item["selection_status"] == "SELECTED" for item in validated
        ),
        "no_fit_temporal_support_utility_stable_model_challenger_count": sum(
            item["selection_status"]
            == "NO_FIT_TEMPORAL_SUPPORT_UTILITY_STABLE_MODEL_CHALLENGER"
            for item in validated
        ),
        "aggregate_selection_pass_variant_count": sum(
            int(item["aggregate_selection_pass_variant_count"])
            for item in validated
        ),
        "stable_selection_pass_variant_count": sum(
            int(item["stable_selection_pass_variant_count"])
            for item in validated
        ),
        "unavailable_budget_variant_count": sum(
            int(item["unavailable_budget_variant_count"])
            for item in validated
        ),
        "utility_eligible_selection_row_count": sum(
            int(item["utility_eligible_selection_row_count"])
            for item in validated
        ),
        "verified_regressor_count": sum(
            int(item["verified_regressor_count"]) for item in validated
        ),
        "verified_pooled_calibration_reference_count": sum(
            int(item["verified_pooled_calibration_reference_count"])
            for item in validated
        ),
        "verified_fit_temporal_support_reference_count": sum(
            int(item["verified_fit_temporal_support_reference_count"])
            for item in validated
        ),
        "validation_pass_cell_count": sum(
            item["validation_status"] == "PASS" for item in validated
        ),
        "holdout_pass_cell_count": sum(
            item["holdout_status"] == "PASS" for item in validated
        ),
    }


def compile_fit_temporal_support_utility_model_result_evidence(
    cell_results: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    commit = _validate_commit(code_commit, field="EXP-052 code commit")
    expected_identities = {
        (c.symbol, c.timeframe, c.horizon_minutes) for c in MODEL_CELLS
    }
    supplied: list[tuple[object, object, object]] = []
    for row in cell_results:
        cell = row.get("cell")
        if not isinstance(cell, Mapping):
            raise ValueError("EXP-052 cell result identity malformed")
        supplied.append(
            (
                cell.get("symbol"),
                cell.get("timeframe"),
                cell.get("horizon_minutes"),
            )
        )
    if (
        len(cell_results) != len(MODEL_CELLS)
        or len(set(supplied)) != len(supplied)
        or set(supplied) != expected_identities
    ):
        raise ValueError("EXP-052 model-result cell evidence incomplete")

    ordered = sorted(
        (dict(item) for item in cell_results),
        key=lambda item: (
            str(item["cell"]["symbol"]),
            str(item["cell"]["timeframe"]),
            int(item["cell"]["horizon_minutes"]),
        ),
    )
    summary = _compile_summary(ordered)
    evidence: dict[str, object] = {
        "evidence_version": FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EVIDENCE_VERSION,
        "artifact_runner_version": (
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "artifact_runner_decision": (
            FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "experiment_id": FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID,
        "code_commit": commit,
        "dec163_merged_commit": DEC163_MERGED_COMMIT,
        "dec164_merged_commit": DEC164_MERGED_COMMIT,
        "dec163_protocol_blob_sha": DEC163_PROTOCOL_BLOB_SHA,
        "dec164_training_core_blob_sha": DEC164_TRAINING_CORE_BLOB_SHA,
        "predecessor_training_core_blob_sha": PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        "predecessor_artifact_helper_blob_sha": PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA,
        "legacy_data_loader_blob_sha": LEGACY_DATA_LOADER_BLOB_SHA,
        "protocol_decision": FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION,
        "protocol_version": FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION,
        "protocol_fingerprint": fit_temporal_support_utility_protocol_fingerprint(),
        "training_core_version": FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_VERSION,
        "training_core_decision": FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
        "authoritative_sources": {
            "feature_run_id": AUTHORITATIVE_FEATURE_RUN_ID,
            "feature_evidence_artifact_id": AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID,
            "feature_evidence_fingerprint": AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT,
            "outcome_run_id": AUTHORITATIVE_OUTCOME_RUN_ID,
            "outcome_evidence_artifact_id": AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID,
            "outcome_evidence_fingerprint": AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT,
            "readiness_artifact_id": AUTHORITATIVE_READINESS_ARTIFACT_ID,
            "readiness_fingerprint": AUTHORITATIVE_READINESS_FINGERPRINT,
        },
        "evidence_label": EVIDENCE_LABEL,
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "untouched_oos": UNTOUCHED_OOS,
        "cell_count": len(ordered),
        "cells": ordered,
        "summary": summary,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    evidence["evidence_fingerprint"] = _sha256(_canonical_json(evidence))
    return evidence


def validate_fit_temporal_support_utility_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    expected_commit = _validate_commit(
        expected_code_commit,
        field="EXP-052 expected code commit",
    )
    exact = {
        "evidence_version": FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EVIDENCE_VERSION,
        "artifact_runner_version": FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION,
        "artifact_runner_decision": FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
        "experiment_id": FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID,
        "code_commit": expected_commit,
        "dec163_merged_commit": DEC163_MERGED_COMMIT,
        "dec164_merged_commit": DEC164_MERGED_COMMIT,
        "dec163_protocol_blob_sha": DEC163_PROTOCOL_BLOB_SHA,
        "dec164_training_core_blob_sha": DEC164_TRAINING_CORE_BLOB_SHA,
        "predecessor_training_core_blob_sha": PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        "predecessor_artifact_helper_blob_sha": PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA,
        "legacy_data_loader_blob_sha": LEGACY_DATA_LOADER_BLOB_SHA,
        "protocol_decision": FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION,
        "protocol_version": FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION,
        "protocol_fingerprint": fit_temporal_support_utility_protocol_fingerprint(),
        "training_core_version": FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_VERSION,
        "training_core_decision": FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
        "evidence_label": EVIDENCE_LABEL,
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "untouched_oos": UNTOUCHED_OOS,
    }
    for field, expected in exact.items():
        if evidence.get(field) != expected:
            raise ValueError(f"EXP-052 evidence {field} mismatch")

    expected_sources = {
        "feature_run_id": AUTHORITATIVE_FEATURE_RUN_ID,
        "feature_evidence_artifact_id": AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID,
        "feature_evidence_fingerprint": AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT,
        "outcome_run_id": AUTHORITATIVE_OUTCOME_RUN_ID,
        "outcome_evidence_artifact_id": AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID,
        "outcome_evidence_fingerprint": AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT,
        "readiness_artifact_id": AUTHORITATIVE_READINESS_ARTIFACT_ID,
        "readiness_fingerprint": AUTHORITATIVE_READINESS_FINGERPRINT,
    }
    if evidence.get("authoritative_sources") != expected_sources:
        raise ValueError("EXP-052 authoritative source identity mismatch")

    cells = evidence.get("cells")
    if not isinstance(cells, list):
        raise ValueError("EXP-052 evidence cells must be a list")
    if evidence.get("cell_count") != len(MODEL_CELLS):
        raise ValueError("EXP-052 evidence cell count mismatch")
    identities = []
    for row in cells:
        if not isinstance(row, Mapping):
            raise ValueError("EXP-052 evidence cell malformed")
        cell = row.get("cell")
        if not isinstance(cell, Mapping):
            raise ValueError("EXP-052 evidence cell identity malformed")
        identities.append(
            (
                cell.get("symbol"),
                cell.get("timeframe"),
                cell.get("horizon_minutes"),
            )
        )
    expected_identities = {
        (c.symbol, c.timeframe, c.horizon_minutes) for c in MODEL_CELLS
    }
    if (
        len(cells) != len(MODEL_CELLS)
        or len(set(identities)) != len(identities)
        or set(identities) != expected_identities
    ):
        raise ValueError("EXP-052 model-result cell evidence incomplete")

    summary = _compile_summary(cells)
    if evidence.get("summary") != summary:
        raise ValueError("EXP-052 evidence summary mismatch")
    if summary["verified_regressor_count"] != 108:
        raise ValueError("EXP-052 aggregate regressor count mismatch")
    if summary["verified_pooled_calibration_reference_count"] != 108:
        raise ValueError("EXP-052 pooled reference aggregate count mismatch")
    if summary["verified_fit_temporal_support_reference_count"] != 432:
        raise ValueError("EXP-052 support reference aggregate count mismatch")

    for field in (
        "model_fit_authorized",
        "promotion_authorized",
        "shadow_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if evidence.get(field) is not False:
            raise ValueError(f"EXP-052 evidence {field} must remain false")

    supplied_fingerprint = _validate_sha256(
        evidence.get("evidence_fingerprint"),
        field="EXP-052 evidence fingerprint",
    )
    expected_fingerprint = _sha256(
        _canonical_json(
            {
                key: value
                for key, value in evidence.items()
                if key != "evidence_fingerprint"
            }
        )
    )
    if supplied_fingerprint != expected_fingerprint:
        raise ValueError("EXP-052 evidence fingerprint mismatch")

    return {
        "fit_temporal_support_utility_model_result_evidence_verified": True,
        **summary,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
        "evidence_fingerprint": supplied_fingerprint,
    }


def write_fit_temporal_support_utility_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    path: Path,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(
            dict(evidence),
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )
    if (
        destination.exists()
        and destination.read_text(encoding="utf-8") != payload
    ):
        raise ValueError("conflicting existing EXP-052 model-result evidence")
    destination.write_text(payload, encoding="utf-8")


def load_fit_temporal_support_utility_model_result_evidence(
    path: Path,
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"cannot read EXP-052 model-result evidence: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("EXP-052 model-result evidence root must be object")
    validate_fit_temporal_support_utility_model_result_evidence(
        value,
        expected_code_commit=expected_code_commit,
    )
    return value


def run_authoritative_fit_temporal_support_utility_model_bundle(
    *,
    repository_root: Path,
    readiness: Mapping[str, object],
    feature_roots: Mapping[tuple[str, str], Path],
    outcome_roots: Mapping[tuple[str, str], Path],
    code_commit: str,
) -> dict[str, object]:
    if (
        AUTHORITATIVE_FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "DEC-165 source is non-executable for authoritative "
            "EXP-052 model fitting"
        )

    validate_fit_temporal_support_utility_artifact_runner_sources(
        repository_root=repository_root,
    )
    indexed = validate_authoritative_readiness(readiness)
    cell_results: list[dict[str, object]] = []
    for cell in MODEL_CELLS:
        identity = (cell.symbol, cell.timeframe)
        if identity not in indexed:
            raise ValueError(
                f"missing authoritative EXP-052 source cell: {identity}"
            )
        if identity not in feature_roots or identity not in outcome_roots:
            raise ValueError(
                f"missing extracted EXP-052 artifact root: {identity}"
            )
        loaded: VerifiedCellArtifacts = load_authoritative_cell_artifacts(
            readiness=readiness,
            feature_root=feature_roots[identity],
            outcome_root=outcome_roots[identity],
            symbol=cell.symbol,
            timeframe=cell.timeframe,
        )
        cell_results.append(
            run_fit_temporal_support_utility_model_cell_core(
                features=loaded.feature_frame,
                outcomes=loaded.outcome_frame,
                cell=cell,
            )
        )
    return compile_fit_temporal_support_utility_model_result_evidence(
        cell_results,
        code_commit=code_commit,
    )


__all__ = [
    "AUTHORITATIVE_FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC164_MERGED_COMMIT",
    "DEC164_TRAINING_CORE_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION",
    "FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION",
    "FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED",
    "FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EVIDENCE_VERSION",
    "LEGACY_DATA_LOADER_BLOB_SHA",
    "LIVE_ORDER_AUTHORIZED",
    "PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "_compile_summary",
    "_validate_consensus_block",
    "_validate_fit_block",
    "_validate_variant",
    "compile_fit_temporal_support_utility_model_result_evidence",
    "load_fit_temporal_support_utility_model_result_evidence",
    "run_authoritative_fit_temporal_support_utility_model_bundle",
    "validate_fit_temporal_support_utility_artifact_runner_sources",
    "validate_fit_temporal_support_utility_model_result_evidence",
    "write_fit_temporal_support_utility_model_result_evidence",
]
