from __future__ import annotations

from copy import deepcopy
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
    HOLDOUT_GATE_SCENARIOS,
    MODEL_CELLS,
    VALIDATION_GATE_SCENARIOS,
)
from .model_successor_density_protocol import CANDIDATE_BUDGET_ANCHORS
from .model_successor_fit_temporal_feature_support_utility_protocol import (
    FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION,
    PRIOR_RESULT_INFORMED,
    UNTOUCHED_OOS,
    fit_temporal_feature_support_utility_protocol_fingerprint,
)
from .model_successor_fit_temporal_feature_support_utility_training import (
    DEC174_MERGED_COMMIT,
    DEC174_PROTOCOL_BLOB_SHA,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_VERSION,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    run_fit_temporal_feature_support_utility_model_cell_core,
    validate_fit_temporal_feature_support_utility_training_sources,
)
from .model_successor_fit_temporal_support_utility_artifacts import (
    _validate_consensus_block as _predecessor_validate_consensus_block,
    _validate_fit_block as _predecessor_validate_fit_block,
    _validate_forward_block as _predecessor_validate_forward_block,
    _validate_variant as _predecessor_validate_variant,
)
from .model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_WINDOWS,
)
from .model_successor_regime_utility_artifacts import (
    _canonical_json,
    _git_blob_sha,
    _sha256,
    _validate_commit,
    _validate_sha256,
)
from .model_successor_temporal_jackknife_utility_protocol import (
    FIT_JACKKNIFE_VIEWS,
)


FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION = (
    "fmp-exp053-fit-temporal-feature-support-utility-artifact-runner-v1"
)
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION = (
    "DEC-176"
)
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EVIDENCE_VERSION = 1

DEC175_MERGED_COMMIT = (
    "60abce7c2674f9c25e4132037c9eb24cab1baf22"
)
DEC175_TRAINING_CORE_BLOB_SHA = (
    "4fd0e48302f97e188a8124e1543bde0ffdb43b6f"
)
LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)
PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA = (
    "ae06184b9a84405119b6ed434a8973139d8ae006"
)

AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = (
    False
)
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED = False
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


def _feature_windows_by_parent(
) -> dict[str, dict[str, dict[str, object]]]:
    grouped: dict[str, dict[str, dict[str, object]]] = {}
    for raw in FIT_TEMPORAL_SUPPORT_WINDOWS:
        window = dict(raw)
        parent = str(window["parent_regime"])
        grouped.setdefault(parent, {})[
            str(window["name"])
        ] = window
    return grouped


def validate_fit_temporal_feature_support_utility_artifact_runner_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "legacy_data_loader": (
            root / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "dec174_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_feature_support_utility_protocol.py",
            DEC174_PROTOCOL_BLOB_SHA,
        ),
        "dec175_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_feature_support_utility_training.py",
            DEC175_TRAINING_CORE_BLOB_SHA,
        ),
        "predecessor_artifact_helper": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_support_utility_artifacts.py",
            PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-053 artifact dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-053 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    training = (
        validate_fit_temporal_feature_support_utility_training_sources(
            repository_root=root,
        )
    )
    if training[
        "fit_temporal_feature_support_utility_training_core_decision"
    ] != FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION:
        raise ValueError("EXP-053 training-core decision drift")
    if training["model_fit_authorized"] is not False:
        raise ValueError("EXP-053 training-core fit authorization drift")
    if training[
        "fit_temporal_feature_support_utility_result_execution_authorized"
    ] is not False:
        raise ValueError(
            "EXP-053 training-core result authorization drift"
        )

    fingerprint = (
        fit_temporal_feature_support_utility_protocol_fingerprint()
    )
    if len(fingerprint) != 64:
        raise ValueError("EXP-053 protocol fingerprint is invalid")

    return {
        "fit_temporal_feature_support_utility_model_artifact_runner_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "fit_temporal_feature_support_utility_model_artifact_runner_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "dec174_merged_commit": DEC174_MERGED_COMMIT,
        "dec175_merged_commit": DEC175_MERGED_COMMIT,
        "dec174_protocol_blob_sha": actual["dec174_protocol"],
        "dec175_training_core_blob_sha": actual[
            "dec175_training_core"
        ],
        "predecessor_training_core_blob_sha": (
            PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_artifact_helper_blob_sha": actual[
            "predecessor_artifact_helper"
        ],
        "legacy_data_loader_blob_sha": actual[
            "legacy_data_loader"
        ],
        "fit_temporal_feature_support_utility_protocol_fingerprint": (
            fingerprint
        ),
        "authoritative_fit_temporal_feature_support_utility_model_result_execution_authorized": (
            False
        ),
        "fit_temporal_feature_support_utility_model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _finite_number(
    value: object,
    *,
    field: str,
) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise ValueError(f"{field} must be finite")
    return float(value)


def _normalize_predecessor_fit(
    fit: Mapping[str, object],
) -> dict[str, object]:
    normalized = deepcopy(dict(fit))
    replacements = {
        "FORBIDDEN_BY_DEC150_DEC163_DEC174": (
            "FORBIDDEN_BY_DEC150_DEC163"
        ),
        "EXCLUDED_BY_DEC150_DEC163_DEC174": (
            "EXCLUDED_BY_DEC150_DEC163"
        ),
        "EXCLUDED_BY_DEC112_DEC150_DEC163_DEC174": (
            "EXCLUDED_BY_DEC112_DEC150_DEC163"
        ),
    }
    for field in (
        "full_fit_single_model",
        "view_weight_search",
        "view_fallback",
        "selection_window_calibration",
        "hist_gradient_boosting_classifier",
        "logistic_regression",
    ):
        raw = normalized.get(field)
        if isinstance(raw, dict):
            status = raw.get("status")
            if status in replacements:
                raw["status"] = replacements[status]
    return normalized


def _validate_feature_references(
    fit: Mapping[str, object],
) -> int:
    expected_views = _view_definitions()
    windows_by_parent = _feature_windows_by_parent()
    refs = fit.get(
        "fit_temporal_feature_support_references"
    )
    if (
        not isinstance(refs, Mapping)
        or set(refs) != set(expected_views)
    ):
        raise ValueError(
            "EXP-053 feature-support reference inventory mismatch"
        )

    verified = 0
    for view_name in sorted(expected_views):
        record = refs.get(view_name)
        if not isinstance(record, Mapping):
            raise ValueError(
                "EXP-053 feature-support view record malformed"
            )
        expected = expected_views[view_name]
        excluded = str(expected["excluded_regime"])
        if record.get("status") != "FROZEN":
            raise ValueError(
                "EXP-053 feature-support view status mismatch"
            )
        included = record.get("included_regimes")
        if (
            not isinstance(included, list)
            or tuple(str(value) for value in included)
            != expected["included_regimes"]
        ):
            raise ValueError(
                "EXP-053 feature-support included-regime mismatch"
            )
        if record.get("excluded_regime") != excluded:
            raise ValueError(
                "EXP-053 feature-support excluded-regime mismatch"
            )
        if record.get("reference_count") != 4:
            raise ValueError(
                "EXP-053 feature-support view count mismatch"
            )
        windows = record.get("windows")
        expected_windows = windows_by_parent.get(excluded)
        if (
            not isinstance(windows, Mapping)
            or not expected_windows
            or set(windows) != set(expected_windows)
        ):
            raise ValueError(
                "EXP-053 feature-support window inventory mismatch"
            )

        for window_name in sorted(expected_windows):
            supplied = windows.get(window_name)
            expected_window = expected_windows[window_name]
            if not isinstance(supplied, Mapping):
                raise ValueError(
                    "EXP-053 feature-support window malformed"
                )
            for field in (
                "name",
                "parent_regime",
                "start",
                "end_exclusive",
            ):
                if supplied.get(field) != expected_window[field]:
                    raise ValueError(
                        f"EXP-053 feature-support window {field} mismatch"
                    )
            if supplied.get("status") != "FROZEN":
                raise ValueError(
                    "EXP-053 feature-support window status mismatch"
                )
            row_count = supplied.get("row_count")
            dimensions = supplied.get(
                "transformed_dimension_count"
            )
            active = supplied.get(
                "active_dimension_count"
            )
            for field, value in (
                ("row count", row_count),
                ("dimension count", dimensions),
                ("active dimension count", active),
            ):
                if (
                    not isinstance(value, int)
                    or isinstance(value, bool)
                    or value <= 0
                ):
                    raise ValueError(
                        f"EXP-053 feature-support {field} invalid"
                    )
            if int(active) > int(dimensions):
                raise ValueError(
                    "EXP-053 active feature dimensions exceed total"
                )
            for field in (
                "preprocessor_fingerprint",
                "center_digest",
                "scale_digest",
                "active_dimension_mask_digest",
                "sorted_reference_distance_digest",
            ):
                _validate_sha256(
                    supplied.get(field),
                    field=f"EXP-053 feature-support {field}",
                )
            minimum = _finite_number(
                supplied.get("minimum_reference_distance"),
                field="EXP-053 feature-support minimum distance",
            )
            maximum = _finite_number(
                supplied.get("maximum_reference_distance"),
                field="EXP-053 feature-support maximum distance",
            )
            mean = _finite_number(
                supplied.get("mean_reference_distance"),
                field="EXP-053 feature-support mean distance",
            )
            if (
                minimum < 0.0
                or maximum < 0.0
                or minimum > maximum
                or not minimum <= mean <= maximum
            ):
                raise ValueError(
                    "EXP-053 feature-support distance bounds invalid"
                )
            verified += 1

    if (
        fit.get(
            "fit_temporal_feature_support_reference_count"
        )
        != FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL
        or verified
        != FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL
    ):
        raise ValueError(
            "EXP-053 feature-support reference count mismatch"
        )
    return verified


def _validate_fit_block(
    fit: Mapping[str, object],
) -> tuple[int, int, int, int]:
    normalized = _normalize_predecessor_fit(fit)
    regressors, pooled, utility_support = (
        _predecessor_validate_fit_block(normalized)
    )
    feature_support = _validate_feature_references(fit)
    return (
        regressors,
        pooled,
        utility_support,
        feature_support,
    )


def _validate_consensus_block(
    block: Mapping[str, object],
    *,
    expected_row_count: int,
    field: str,
) -> int:
    eligible = _predecessor_validate_consensus_block(
        block,
        expected_row_count=expected_row_count,
        field=field,
    )
    if block.get(
        "fit_temporal_feature_support_reference_count"
    ) != FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL:
        raise ValueError(
            f"{field} feature-support reference count mismatch"
        )
    minimum = block.get(
        "minimum_robust_fit_temporal_feature_support"
    )
    maximum = block.get(
        "maximum_robust_fit_temporal_feature_support"
    )
    if eligible == 0:
        if minimum is not None or maximum is not None:
            raise ValueError(
                f"{field} empty feature-support bounds mismatch"
            )
    else:
        low = _finite_number(
            minimum,
            field=f"{field} feature-support minimum",
        )
        high = _finite_number(
            maximum,
            field=f"{field} feature-support maximum",
        )
        if low < 0.0 or high > 1.0 or low > high:
            raise ValueError(
                f"{field} feature-support bounds invalid"
            )
    return eligible


def _validate_quadruple_cutoff(
    raw: Mapping[str, object],
    *,
    field: str,
) -> tuple[float, float, float, float]:
    feature = _finite_number(
        raw.get(
            "selection_derived_feature_support_cutoff"
        ),
        field=f"{field} feature-support cutoff",
    )
    utility = _finite_number(
        raw.get("selection_derived_support_cutoff"),
        field=f"{field} utility-support cutoff",
    )
    pooled = _finite_number(
        raw.get(
            "selection_derived_pooled_calibrated_cutoff"
        ),
        field=f"{field} pooled cutoff",
    )
    raw_cutoff = _finite_number(
        raw.get("selection_derived_raw_cutoff"),
        field=f"{field} raw cutoff",
    )
    for label, value in (
        ("feature-support", feature),
        ("utility-support", utility),
        ("pooled", pooled),
    ):
        if value < 0.0 or value > 1.0:
            raise ValueError(
                f"{field} {label} cutoff out of range"
            )
    if raw_cutoff <= 0.0:
        raise ValueError(
            f"{field} raw cutoff must be positive"
        )
    return feature, utility, pooled, raw_cutoff


def _validate_variant(
    raw: Mapping[str, object],
    *,
    expected_eligible_count: int,
) -> tuple[bool, bool, bool]:
    evaluation = raw.get("evaluation_status")
    if evaluation == "BUDGET_UNAVAILABLE":
        if raw.get(
            "selection_derived_feature_support_cutoff"
        ) is not None:
            raise ValueError(
                "EXP-053 unavailable feature cutoff must be null"
            )
    elif evaluation == "EVALUATED":
        _validate_quadruple_cutoff(
            raw,
            field="EXP-053 selection",
        )
    else:
        raise ValueError(
            "EXP-053 variant evaluation status mismatch"
        )

    normalized = deepcopy(dict(raw))
    normalized.pop(
        "selection_derived_feature_support_cutoff",
        None,
    )
    return _predecessor_validate_variant(
        normalized,
        expected_eligible_count=expected_eligible_count,
    )


def _validate_status_chain(
    *,
    selection: object,
    validation: object,
    holdout: object,
) -> None:
    if selection == (
        "NO_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_"
        "STABLE_MODEL_CHALLENGER"
    ):
        if (
            validation != "LOCKED_NO_SELECTION"
            or holdout != "LOCKED_NO_SELECTION"
        ):
            raise ValueError(
                "EXP-053 no-selection forward lock mismatch"
            )
        return
    if selection != "SELECTED":
        raise ValueError(
            f"unexpected EXP-053 selection status: {selection!r}"
        )
    if validation == "REJECT":
        if holdout != "LOCKED_VALIDATION_REJECT":
            raise ValueError(
                "EXP-053 validation reject holdout mismatch"
            )
        return
    if validation == "PASS":
        if holdout not in {"PASS", "REJECT"}:
            raise ValueError(
                "EXP-053 validation pass holdout mismatch"
            )
        return
    raise ValueError(
        f"unexpected EXP-053 validation status: {validation!r}"
    )


def _validate_forward_block(
    block: Mapping[str, object],
    *,
    expected_row_count: int,
    field: str,
    gate_scenarios: Sequence[float],
) -> None:
    consensus = block.get(
        "fit_temporal_feature_support_consensus"
    )
    if not isinstance(consensus, Mapping):
        raise ValueError(
            f"{field} feature-support consensus malformed"
        )
    _validate_consensus_block(
        consensus,
        expected_row_count=expected_row_count,
        field=field,
    )
    _validate_sha256(
        block.get(
            "fit_temporal_feature_support_consensus_digest"
        ),
        field=f"{field} feature-support consensus digest",
    )
    _validate_quadruple_cutoff(
        block,
        field=field,
    )

    normalized = deepcopy(dict(block))
    normalized["fit_temporal_support_consensus"] = (
        normalized.pop(
            "fit_temporal_feature_support_consensus"
        )
    )
    normalized["fit_temporal_support_consensus_digest"] = (
        normalized.pop(
            "fit_temporal_feature_support_consensus_digest"
        )
    )
    normalized.pop(
        "selection_derived_feature_support_cutoff",
        None,
    )
    _predecessor_validate_forward_block(
        normalized,
        expected_row_count=expected_row_count,
        field=field,
        gate_scenarios=gate_scenarios,
    )


def _validate_cell_result(
    raw: Mapping[str, object],
) -> dict[str, object]:
    exact = {
        "experiment_id": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_EXPERIMENT_ID
        ),
        "training_core_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec174_merged_commit": DEC174_MERGED_COMMIT,
        "dec174_protocol_blob_sha": DEC174_PROTOCOL_BLOB_SHA,
        "predecessor_training_core_blob_sha": (
            PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_training_core_decision": "DEC-164",
        "protocol_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            fit_temporal_feature_support_utility_protocol_fingerprint()
        ),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": UNTOUCHED_OOS,
    }
    for field, expected in exact.items():
        if raw.get(field) != expected:
            raise ValueError(
                f"EXP-053 cell {field} mismatch"
            )

    cell = raw.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError(
            "EXP-053 cell identity malformed"
        )
    identity = (
        cell.get("symbol"),
        cell.get("timeframe"),
        cell.get("horizon_minutes"),
    )
    expected_identities = {
        (
            item.symbol,
            item.timeframe,
            item.horizon_minutes,
        )
        for item in MODEL_CELLS
    }
    if identity not in expected_identities:
        raise ValueError(
            "EXP-053 cell identity unsupported"
        )

    _validate_sha256(
        raw.get("processed_manifest_sha256"),
        field="EXP-053 processed manifest sha256",
    )
    joined = raw.get("joined_row_count")
    if (
        not isinstance(joined, int)
        or isinstance(joined, bool)
        or joined <= 0
    ):
        raise ValueError(
            "EXP-053 joined row count invalid"
        )
    splits = raw.get("split_row_counts")
    required = {
        "fit",
        "selection",
        "validation",
        "retrospective_holdout",
    }
    if (
        not isinstance(splits, Mapping)
        or set(splits) != required
    ):
        raise ValueError(
            "EXP-053 split inventory mismatch"
        )
    for name in sorted(required):
        value = splits.get(name)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value <= 0
        ):
            raise ValueError(
                "EXP-053 split row count invalid"
            )

    fit = raw.get("fit")
    if not isinstance(fit, Mapping):
        raise ValueError(
            "EXP-053 fit evidence malformed"
        )
    (
        regressors,
        pooled_refs,
        utility_support_refs,
        feature_support_refs,
    ) = _validate_fit_block(fit)

    selection = raw.get("selection")
    validation = raw.get("validation")
    holdout = raw.get("retrospective_holdout")
    if (
        not isinstance(selection, Mapping)
        or not isinstance(validation, Mapping)
        or not isinstance(holdout, Mapping)
    ):
        raise ValueError(
            "EXP-053 result-stage evidence malformed"
        )
    if selection.get("row_count") != splits["selection"]:
        raise ValueError(
            "EXP-053 selection row count mismatch"
        )
    consensus = selection.get(
        "fit_temporal_feature_support_consensus"
    )
    if not isinstance(consensus, Mapping):
        raise ValueError(
            "EXP-053 selection consensus malformed"
        )
    eligible = _validate_consensus_block(
        consensus,
        expected_row_count=int(splits["selection"]),
        field="EXP-053 selection",
    )
    _validate_sha256(
        selection.get(
            "fit_temporal_feature_support_consensus_digest"
        ),
        field="EXP-053 selection consensus digest",
    )

    variants = selection.get("variants")
    if (
        not isinstance(variants, list)
        or len(variants) != len(CANDIDATE_BUDGET_ANCHORS)
    ):
        raise ValueError(
            "EXP-053 variant inventory mismatch"
        )
    if {
        item.get("candidate_budget_anchor")
        for item in variants
        if isinstance(item, Mapping)
    } != set(CANDIDATE_BUDGET_ANCHORS):
        raise ValueError(
            "EXP-053 budget coverage mismatch"
        )

    aggregate_pass_count = 0
    stable_pass_count = 0
    unavailable_count = 0
    stable_variants: list[Mapping[str, object]] = []
    for item in variants:
        if not isinstance(item, Mapping):
            raise ValueError(
                "EXP-053 variant malformed"
            )
        aggregate_passed, stable_passed, unavailable = (
            _validate_variant(
                item,
                expected_eligible_count=eligible,
            )
        )
        aggregate_pass_count += int(aggregate_passed)
        stable_pass_count += int(stable_passed)
        unavailable_count += int(unavailable)
        if stable_passed:
            stable_variants.append(item)

    selection_status = selection.get("status")
    selected = selection.get("selected_variant")
    no_challenger = (
        "NO_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_"
        "STABLE_MODEL_CHALLENGER"
    )
    if selection_status == no_challenger:
        if stable_variants or selected is not None:
            raise ValueError(
                "EXP-053 no-challenger selection mismatch"
            )
    elif selection_status == "SELECTED":
        if (
            not stable_variants
            or not isinstance(selected, Mapping)
        ):
            raise ValueError(
                "EXP-053 selected variant missing"
            )
        if (
            selected.get("model_family")
            != "hist_gradient_boosting_regression"
            or selected.get("candidate_budget_anchor")
            not in CANDIDATE_BUDGET_ANCHORS
        ):
            raise ValueError(
                "EXP-053 selected variant identity mismatch"
            )
        quadruple = _validate_quadruple_cutoff(
            selected,
            field="EXP-053 selected variant",
        )
        matches = []
        for item in stable_variants:
            if (
                item.get("candidate_budget_anchor")
                == selected.get("candidate_budget_anchor")
                and _validate_quadruple_cutoff(
                    item,
                    field="EXP-053 stable variant",
                )
                == quadruple
            ):
                matches.append(item)
        if len(matches) != 1:
            raise ValueError(
                "EXP-053 selected stable variant not unique"
            )
    else:
        raise ValueError(
            "EXP-053 selection status invalid"
        )

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
            field="EXP-053 validation",
            gate_scenarios=VALIDATION_GATE_SCENARIOS,
        )
    if holdout_status in {"PASS", "REJECT"}:
        _validate_forward_block(
            holdout,
            expected_row_count=int(
                splits["retrospective_holdout"]
            ),
            field="EXP-053 holdout",
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
            raise ValueError(
                f"EXP-053 cell {field} must remain false"
            )

    supplied = _validate_sha256(
        raw.get("result_fingerprint"),
        field="EXP-053 cell result fingerprint",
    )
    expected = _sha256(
        _canonical_json(
            {
                key: value
                for key, value in raw.items()
                if key != "result_fingerprint"
            }
        )
    )
    if supplied != expected:
        raise ValueError(
            "EXP-053 cell result fingerprint mismatch"
        )

    return {
        "selection_status": selection_status,
        "validation_status": validation_status,
        "holdout_status": holdout_status,
        "aggregate_selection_pass_variant_count": (
            aggregate_pass_count
        ),
        "stable_selection_pass_variant_count": (
            stable_pass_count
        ),
        "unavailable_budget_variant_count": (
            unavailable_count
        ),
        "utility_eligible_selection_row_count": eligible,
        "verified_regressor_count": regressors,
        "verified_pooled_calibration_reference_count": (
            pooled_refs
        ),
        "verified_fit_temporal_support_reference_count": (
            utility_support_refs
        ),
        "verified_fit_temporal_feature_support_reference_count": (
            feature_support_refs
        ),
    }


def _compile_summary(
    cell_results: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validated = [
        _validate_cell_result(item)
        for item in cell_results
    ]
    return {
        "verified_cell_count": len(validated),
        "selected_cell_count": sum(
            item["selection_status"] == "SELECTED"
            for item in validated
        ),
        "no_fit_temporal_feature_support_utility_stable_model_challenger_count": sum(
            item["selection_status"]
            == (
                "NO_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_"
                "STABLE_MODEL_CHALLENGER"
            )
            for item in validated
        ),
        "aggregate_selection_pass_variant_count": sum(
            int(
                item[
                    "aggregate_selection_pass_variant_count"
                ]
            )
            for item in validated
        ),
        "stable_selection_pass_variant_count": sum(
            int(
                item[
                    "stable_selection_pass_variant_count"
                ]
            )
            for item in validated
        ),
        "unavailable_budget_variant_count": sum(
            int(
                item[
                    "unavailable_budget_variant_count"
                ]
            )
            for item in validated
        ),
        "utility_eligible_selection_row_count": sum(
            int(
                item[
                    "utility_eligible_selection_row_count"
                ]
            )
            for item in validated
        ),
        "verified_regressor_count": sum(
            int(item["verified_regressor_count"])
            for item in validated
        ),
        "verified_pooled_calibration_reference_count": sum(
            int(
                item[
                    "verified_pooled_calibration_reference_count"
                ]
            )
            for item in validated
        ),
        "verified_fit_temporal_support_reference_count": sum(
            int(
                item[
                    "verified_fit_temporal_support_reference_count"
                ]
            )
            for item in validated
        ),
        "verified_fit_temporal_feature_support_reference_count": sum(
            int(
                item[
                    "verified_fit_temporal_feature_support_reference_count"
                ]
            )
            for item in validated
        ),
        "validation_pass_cell_count": sum(
            item["validation_status"] == "PASS"
            for item in validated
        ),
        "holdout_pass_cell_count": sum(
            item["holdout_status"] == "PASS"
            for item in validated
        ),
    }


def compile_fit_temporal_feature_support_utility_model_result_evidence(
    cell_results: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    commit = _validate_commit(
        code_commit,
        field="EXP-053 code commit",
    )
    expected_identities = {
        (
            cell.symbol,
            cell.timeframe,
            cell.horizon_minutes,
        )
        for cell in MODEL_CELLS
    }
    supplied: list[
        tuple[object, object, object]
    ] = []
    for row in cell_results:
        cell = row.get("cell")
        if not isinstance(cell, Mapping):
            raise ValueError(
                "EXP-053 cell result identity malformed"
            )
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
        raise ValueError(
            "EXP-053 model-result cell evidence incomplete"
        )

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
        "evidence_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EVIDENCE_VERSION
        ),
        "artifact_runner_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "artifact_runner_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "experiment_id": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_EXPERIMENT_ID
        ),
        "code_commit": commit,
        "dec174_merged_commit": DEC174_MERGED_COMMIT,
        "dec175_merged_commit": DEC175_MERGED_COMMIT,
        "dec174_protocol_blob_sha": DEC174_PROTOCOL_BLOB_SHA,
        "dec175_training_core_blob_sha": (
            DEC175_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_training_core_blob_sha": (
            PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_artifact_helper_blob_sha": (
            PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA
        ),
        "legacy_data_loader_blob_sha": (
            LEGACY_DATA_LOADER_BLOB_SHA
        ),
        "protocol_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            fit_temporal_feature_support_utility_protocol_fingerprint()
        ),
        "training_core_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION
        ),
        "authoritative_sources": {
            "feature_run_id": AUTHORITATIVE_FEATURE_RUN_ID,
            "feature_evidence_artifact_id": (
                AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID
            ),
            "feature_evidence_fingerprint": (
                AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT
            ),
            "outcome_run_id": AUTHORITATIVE_OUTCOME_RUN_ID,
            "outcome_evidence_artifact_id": (
                AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID
            ),
            "outcome_evidence_fingerprint": (
                AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT
            ),
            "readiness_artifact_id": (
                AUTHORITATIVE_READINESS_ARTIFACT_ID
            ),
            "readiness_fingerprint": (
                AUTHORITATIVE_READINESS_FINGERPRINT
            ),
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
    evidence["evidence_fingerprint"] = _sha256(
        _canonical_json(evidence)
    )
    return evidence


def validate_fit_temporal_feature_support_utility_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    expected_commit = _validate_commit(
        expected_code_commit,
        field="EXP-053 expected code commit",
    )
    exact = {
        "evidence_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EVIDENCE_VERSION
        ),
        "artifact_runner_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "artifact_runner_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "experiment_id": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_EXPERIMENT_ID
        ),
        "code_commit": expected_commit,
        "dec174_merged_commit": DEC174_MERGED_COMMIT,
        "dec175_merged_commit": DEC175_MERGED_COMMIT,
        "dec174_protocol_blob_sha": DEC174_PROTOCOL_BLOB_SHA,
        "dec175_training_core_blob_sha": (
            DEC175_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_training_core_blob_sha": (
            PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_artifact_helper_blob_sha": (
            PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA
        ),
        "legacy_data_loader_blob_sha": (
            LEGACY_DATA_LOADER_BLOB_SHA
        ),
        "protocol_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            fit_temporal_feature_support_utility_protocol_fingerprint()
        ),
        "training_core_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION
        ),
        "evidence_label": EVIDENCE_LABEL,
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "untouched_oos": UNTOUCHED_OOS,
    }
    for field, expected in exact.items():
        if evidence.get(field) != expected:
            raise ValueError(
                f"EXP-053 evidence {field} mismatch"
            )

    expected_sources = {
        "feature_run_id": AUTHORITATIVE_FEATURE_RUN_ID,
        "feature_evidence_artifact_id": (
            AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID
        ),
        "feature_evidence_fingerprint": (
            AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT
        ),
        "outcome_run_id": AUTHORITATIVE_OUTCOME_RUN_ID,
        "outcome_evidence_artifact_id": (
            AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID
        ),
        "outcome_evidence_fingerprint": (
            AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT
        ),
        "readiness_artifact_id": (
            AUTHORITATIVE_READINESS_ARTIFACT_ID
        ),
        "readiness_fingerprint": (
            AUTHORITATIVE_READINESS_FINGERPRINT
        ),
    }
    if evidence.get("authoritative_sources") != expected_sources:
        raise ValueError(
            "EXP-053 authoritative source identity mismatch"
        )

    cells = evidence.get("cells")
    if not isinstance(cells, list):
        raise ValueError(
            "EXP-053 evidence cells must be a list"
        )
    if evidence.get("cell_count") != len(MODEL_CELLS):
        raise ValueError(
            "EXP-053 evidence cell count mismatch"
        )
    identities = []
    for row in cells:
        if not isinstance(row, Mapping):
            raise ValueError(
                "EXP-053 evidence cell malformed"
            )
        cell = row.get("cell")
        if not isinstance(cell, Mapping):
            raise ValueError(
                "EXP-053 evidence cell identity malformed"
            )
        identities.append(
            (
                cell.get("symbol"),
                cell.get("timeframe"),
                cell.get("horizon_minutes"),
            )
        )
    expected_identities = {
        (
            cell.symbol,
            cell.timeframe,
            cell.horizon_minutes,
        )
        for cell in MODEL_CELLS
    }
    if (
        len(cells) != len(MODEL_CELLS)
        or len(set(identities)) != len(identities)
        or set(identities) != expected_identities
    ):
        raise ValueError(
            "EXP-053 model-result cell evidence incomplete"
        )

    summary = _compile_summary(cells)
    if evidence.get("summary") != summary:
        raise ValueError(
            "EXP-053 evidence summary mismatch"
        )
    expected_counts = {
        "verified_regressor_count": 108,
        "verified_pooled_calibration_reference_count": 108,
        "verified_fit_temporal_support_reference_count": 432,
        "verified_fit_temporal_feature_support_reference_count": 216,
    }
    for field, expected in expected_counts.items():
        if summary[field] != expected:
            raise ValueError(
                f"EXP-053 aggregate {field} mismatch"
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
        if evidence.get(field) is not False:
            raise ValueError(
                f"EXP-053 evidence {field} must remain false"
            )

    supplied = _validate_sha256(
        evidence.get("evidence_fingerprint"),
        field="EXP-053 evidence fingerprint",
    )
    expected = _sha256(
        _canonical_json(
            {
                key: value
                for key, value in evidence.items()
                if key != "evidence_fingerprint"
            }
        )
    )
    if supplied != expected:
        raise ValueError(
            "EXP-053 evidence fingerprint mismatch"
        )

    return {
        "fit_temporal_feature_support_utility_model_result_evidence_verified": (
            True
        ),
        **summary,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
        "evidence_fingerprint": supplied,
    }


def write_fit_temporal_feature_support_utility_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    path: Path,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
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
        and destination.read_text(encoding="utf-8")
        != payload
    ):
        raise ValueError(
            "conflicting existing EXP-053 model-result evidence"
        )
    destination.write_text(
        payload,
        encoding="utf-8",
    )


def load_fit_temporal_feature_support_utility_model_result_evidence(
    path: Path,
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    try:
        value = json.loads(
            Path(path).read_text(encoding="utf-8")
        )
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise ValueError(
            f"cannot read EXP-053 model-result evidence: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError(
            "EXP-053 model-result evidence root must be object"
        )
    validate_fit_temporal_feature_support_utility_model_result_evidence(
        value,
        expected_code_commit=expected_code_commit,
    )
    return value


def run_authoritative_fit_temporal_feature_support_utility_model_bundle(
    *,
    repository_root: Path,
    readiness: Mapping[str, object],
    feature_roots: Mapping[
        tuple[str, str],
        Path,
    ],
    outcome_roots: Mapping[
        tuple[str, str],
        Path,
    ],
    code_commit: str,
) -> dict[str, object]:
    if (
        AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "DEC-176 source is non-executable for authoritative "
            "EXP-053 model fitting"
        )

    validate_fit_temporal_feature_support_utility_artifact_runner_sources(
        repository_root=repository_root,
    )
    indexed = validate_authoritative_readiness(
        readiness
    )
    cell_results: list[dict[str, object]] = []
    for cell in MODEL_CELLS:
        identity = (cell.symbol, cell.timeframe)
        if identity not in indexed:
            raise ValueError(
                f"missing authoritative EXP-053 source cell: {identity}"
            )
        if (
            identity not in feature_roots
            or identity not in outcome_roots
        ):
            raise ValueError(
                f"missing extracted EXP-053 artifact root: {identity}"
            )
        loaded: VerifiedCellArtifacts = (
            load_authoritative_cell_artifacts(
                readiness=readiness,
                feature_root=feature_roots[identity],
                outcome_root=outcome_roots[identity],
                symbol=cell.symbol,
                timeframe=cell.timeframe,
            )
        )
        cell_results.append(
            run_fit_temporal_feature_support_utility_model_cell_core(
                features=loaded.feature_frame,
                outcomes=loaded.outcome_frame,
                cell=cell,
            )
        )
    return (
        compile_fit_temporal_feature_support_utility_model_result_evidence(
            cell_results,
            code_commit=code_commit,
        )
    )


__all__ = [
    "AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC175_MERGED_COMMIT",
    "DEC175_TRAINING_CORE_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EVIDENCE_VERSION",
    "LEGACY_DATA_LOADER_BLOB_SHA",
    "LIVE_ORDER_AUTHORIZED",
    "PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "_compile_summary",
    "_validate_consensus_block",
    "_validate_feature_references",
    "_validate_fit_block",
    "_validate_variant",
    "compile_fit_temporal_feature_support_utility_model_result_evidence",
    "load_fit_temporal_feature_support_utility_model_result_evidence",
    "run_authoritative_fit_temporal_feature_support_utility_model_bundle",
    "validate_fit_temporal_feature_support_utility_artifact_runner_sources",
    "validate_fit_temporal_feature_support_utility_model_result_evidence",
    "write_fit_temporal_feature_support_utility_model_result_evidence",
]
