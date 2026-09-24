from __future__ import annotations

import hashlib
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
    GATE_REQUIREMENTS,
    MIN_DIRECTIONAL_CANDIDATES,
    MODEL_CELLS,
)
from .model_successor_regime_utility_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
    FINANCIAL_TARGET_COLUMNS,
    FIT_REGIME_WINDOWS,
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    PRIOR_RESULT_INFORMED,
    REGIME_UTILITY_EXPERIMENT_ID,
    REGIME_UTILITY_PROTOCOL_DECISION,
    REGIME_UTILITY_PROTOCOL_VERSION,
    TEMPORAL_STABILITY_WINDOWS,
    UNTOUCHED_OOS,
    regime_utility_protocol_fingerprint,
)
from .model_successor_regime_utility_training import (
    BASE_TRAINING_CORE_BLOB_SHA,
    DEC132_MERGED_COMMIT,
    DEC132_PROTOCOL_BLOB_SHA,
    DENSITY_HELPER_CORE_BLOB_SHA,
    REGIME_UTILITY_TRAINING_CORE_DECISION,
    REGIME_UTILITY_TRAINING_CORE_VERSION,
    run_regime_utility_model_cell_core,
)


REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION = (
    "fmp-exp049-regime-utility-artifact-runner-v1"
)
REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION = "DEC-134"
REGIME_UTILITY_MODEL_RESULT_EVIDENCE_VERSION = 1

DEC133_MERGED_COMMIT = (
    "a6420e35a9219c81e65c5179843488f94b6668d3"
)
DEC133_TRAINING_CORE_BLOB_SHA = (
    "e1018b20210b7bb8d666071d8eb878aba5899111"
)
LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)

AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = False
REGIME_UTILITY_MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False

_DIRECTION_CLASSES = ("LONG", "SHORT", "NO_TRADE")


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


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_regime_utility_artifact_runner_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "legacy_data_loader": (
            root / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "dec132_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_utility_protocol.py",
            DEC132_PROTOCOL_BLOB_SHA,
        ),
        "dec133_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_utility_training.py",
            DEC133_TRAINING_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-049 artifact dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-049 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    protocol_fingerprint = regime_utility_protocol_fingerprint()
    if len(protocol_fingerprint) != 64:
        raise ValueError(
            "EXP-049 regime-utility protocol fingerprint is invalid"
        )

    return {
        "regime_utility_model_artifact_runner_version": (
            REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "regime_utility_model_artifact_runner_decision": (
            REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "dec132_merged_commit": DEC132_MERGED_COMMIT,
        "dec133_merged_commit": DEC133_MERGED_COMMIT,
        "legacy_data_loader_blob_sha": actual["legacy_data_loader"],
        "dec132_protocol_blob_sha": actual["dec132_protocol"],
        "dec133_training_core_blob_sha": actual[
            "dec133_training_core"
        ],
        "base_training_core_blob_sha": BASE_TRAINING_CORE_BLOB_SHA,
        "density_helper_core_blob_sha": DENSITY_HELPER_CORE_BLOB_SHA,
        "regime_utility_protocol_fingerprint": protocol_fingerprint,
        "authoritative_regime_utility_model_result_execution_authorized": False,
        "regime_utility_model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _validate_financial_gate(
    *,
    metrics: Mapping[str, object],
    gate: Mapping[str, object],
    field: str,
) -> bool:
    count = metrics.get("directional_candidate_count")
    total = metrics.get("total_net_pips")
    mean = metrics.get("mean_net_pips")
    gross_positive = metrics.get("gross_positive_pips")
    gross_negative = metrics.get("absolute_gross_negative_pips")
    if (
        not isinstance(count, int)
        or isinstance(count, bool)
        or count < 0
    ):
        raise ValueError(f"{field} directional candidate count is invalid")
    for name, value in (
        ("total_net_pips", total),
        ("gross_positive_pips", gross_positive),
        ("absolute_gross_negative_pips", gross_negative),
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise ValueError(f"{field} {name} is invalid")
    if mean is not None and (
        not isinstance(mean, (int, float))
        or isinstance(mean, bool)
        or not math.isfinite(float(mean))
    ):
        raise ValueError(f"{field} mean_net_pips is invalid")

    criteria = {
        GATE_REQUIREMENTS[0]: count >= MIN_DIRECTIONAL_CANDIDATES,
        GATE_REQUIREMENTS[1]: float(total) > 0.0,
        GATE_REQUIREMENTS[2]: mean is not None and float(mean) > 0.0,
        GATE_REQUIREMENTS[3]: (
            float(gross_positive) > float(gross_negative)
        ),
    }
    if gate.get("criteria") != criteria:
        raise ValueError(f"{field} financial gate criteria mismatch")
    passed = all(criteria.values())
    if gate.get("passed") is not passed:
        raise ValueError(f"{field} financial gate pass mismatch")
    return passed


def _validate_status_chain(
    *,
    selection: object,
    validation: object,
    holdout: object,
) -> None:
    if selection == "NO_REGIME_UTILITY_STABLE_MODEL_CHALLENGER":
        if validation != "LOCKED_NO_SELECTION":
            raise ValueError(
                "EXP-049 no-challenger validation must be locked"
            )
        if holdout != "LOCKED_NO_SELECTION":
            raise ValueError(
                "EXP-049 no-challenger holdout must be locked"
            )
        return
    if selection != "SELECTED":
        raise ValueError(
            f"unexpected EXP-049 selection status: {selection!r}"
        )
    if validation == "REJECT":
        if holdout != "LOCKED_VALIDATION_REJECT":
            raise ValueError(
                "EXP-049 rejected validation must keep holdout locked"
            )
        return
    if validation == "PASS":
        if holdout not in {"PASS", "REJECT"}:
            raise ValueError(
                "EXP-049 passed validation must produce holdout result"
            )
        return
    raise ValueError(
        f"unexpected EXP-049 validation status: {validation!r}"
    )


def _validate_target_summary(
    summary: Mapping[str, object],
    *,
    expected_row_count: int,
    field: str,
) -> None:
    if summary.get("row_count") != expected_row_count:
        raise ValueError(f"{field} target summary row count mismatch")
    for name in (
        "minimum_net_pips",
        "maximum_net_pips",
        "mean_net_pips",
    ):
        value = summary.get(name)
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise ValueError(f"{field} {name} is invalid")
    minimum = float(summary["minimum_net_pips"])
    maximum = float(summary["maximum_net_pips"])
    mean = float(summary["mean_net_pips"])
    if minimum > maximum or mean < minimum or mean > maximum:
        raise ValueError(f"{field} target summary order mismatch")
    counts = []
    for name in ("positive_count", "negative_count", "zero_count"):
        value = summary.get(name)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            raise ValueError(f"{field} {name} is invalid")
        counts.append(value)
    if sum(counts) != expected_row_count:
        raise ValueError(f"{field} target summary count mismatch")


def _validate_utility_consensus_block(
    block: Mapping[str, object],
    *,
    expected_row_count: int,
    field: str,
) -> int:
    if block.get("row_count") != expected_row_count:
        raise ValueError(f"{field} consensus row count mismatch")
    counts = block.get("consensus_direction_counts")
    if (
        not isinstance(counts, Mapping)
        or set(counts) != set(_DIRECTION_CLASSES)
    ):
        raise ValueError(
            f"{field} consensus direction counts are malformed"
        )
    normalized: dict[str, int] = {}
    for name in _DIRECTION_CLASSES:
        value = counts.get(name)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            raise ValueError(f"{field} consensus count is invalid")
        normalized[name] = value
    if sum(normalized.values()) != expected_row_count:
        raise ValueError(f"{field} consensus count total mismatch")

    eligible = normalized["LONG"] + normalized["SHORT"]
    if block.get("consensus_eligible_row_count") != eligible:
        raise ValueError(f"{field} consensus eligible count mismatch")
    rate = block.get("consensus_eligible_rate")
    expected_rate = (
        float(eligible / expected_row_count)
        if expected_row_count
        else 0.0
    )
    if (
        not isinstance(rate, (int, float))
        or isinstance(rate, bool)
        or not math.isfinite(float(rate))
        or not math.isclose(
            float(rate),
            expected_rate,
            rel_tol=0.0,
            abs_tol=1e-15,
        )
    ):
        raise ValueError(f"{field} consensus eligible rate mismatch")

    minimum = block.get("minimum_robust_utility")
    maximum = block.get("maximum_robust_utility")
    if eligible == 0:
        if minimum is not None or maximum is not None:
            raise ValueError(
                f"{field} empty robust utility evidence mismatch"
            )
    else:
        for name, value in (("minimum", minimum), ("maximum", maximum)):
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(float(value))
                or float(value) <= 0.0
            ):
                raise ValueError(
                    f"{field} robust utility {name} is invalid"
                )
        if float(minimum) > float(maximum):
            raise ValueError(
                f"{field} robust utility order mismatch"
            )

    digests = block.get("regime_prediction_digests")
    regime_names = {
        str(window["name"]) for window in FIT_REGIME_WINDOWS
    }
    if (
        not isinstance(digests, Mapping)
        or set(digests) != regime_names
    ):
        raise ValueError(
            f"{field} regime prediction digest set mismatch"
        )
    for regime_name in sorted(regime_names):
        target_digests = digests.get(regime_name)
        if (
            not isinstance(target_digests, Mapping)
            or set(target_digests) != set(FINANCIAL_TARGET_COLUMNS)
        ):
            raise ValueError(
                f"{field} {regime_name} prediction digest inventory mismatch"
            )
        for target in FINANCIAL_TARGET_COLUMNS:
            _validate_sha256(
                target_digests.get(target),
                field=(
                    f"{field} {regime_name} {target} prediction digest"
                ),
            )
    return eligible


def _validate_window(
    window: Mapping[str, object],
    *,
    expected: Mapping[str, object],
    full_selection_candidate_count: int,
) -> bool:
    for field in ("name", "start", "end_exclusive"):
        if window.get(field) != expected[field]:
            raise ValueError(
                f"EXP-049 stability window {field} mismatch"
            )
    row_count = window.get("row_count")
    if (
        not isinstance(row_count, int)
        or isinstance(row_count, bool)
        or row_count <= 0
    ):
        raise ValueError("EXP-049 stability window row count is invalid")
    metrics = window.get("metrics")
    gate = window.get("gate")
    if not isinstance(metrics, Mapping) or not isinstance(gate, Mapping):
        raise ValueError("EXP-049 stability window evidence is malformed")
    candidate_count = metrics.get("directional_candidate_count")
    if (
        not isinstance(candidate_count, int)
        or isinstance(candidate_count, bool)
        or candidate_count < 0
        or full_selection_candidate_count <= 0
    ):
        raise ValueError("EXP-049 stability candidate count is invalid")
    expected_share = candidate_count / full_selection_candidate_count
    supplied_share = gate.get("directional_candidate_share")
    if (
        not isinstance(supplied_share, (int, float))
        or isinstance(supplied_share, bool)
        or not math.isfinite(float(supplied_share))
        or not math.isclose(
            float(supplied_share),
            expected_share,
            rel_tol=0.0,
            abs_tol=1e-15,
        )
    ):
        raise ValueError("EXP-049 stability candidate-share mismatch")

    total = metrics.get("total_net_pips")
    mean = metrics.get("mean_net_pips")
    gross_positive = metrics.get("gross_positive_pips")
    gross_negative = metrics.get("absolute_gross_negative_pips")
    for name, value in (
        ("total_net_pips", total),
        ("gross_positive_pips", gross_positive),
        ("absolute_gross_negative_pips", gross_negative),
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise ValueError(f"EXP-049 stability {name} is invalid")
    if mean is not None and (
        not isinstance(mean, (int, float))
        or isinstance(mean, bool)
        or not math.isfinite(float(mean))
    ):
        raise ValueError("EXP-049 stability mean_net_pips is invalid")

    expected_criteria = {
        "directional_candidate_share>=0.10": (
            expected_share >= MIN_STABILITY_WINDOW_CANDIDATE_SHARE
        ),
        "total_net_pips>0": float(total) > 0.0,
        "mean_net_pips>0": mean is not None and float(mean) > 0.0,
        "gross_positive_pips>absolute_gross_negative_pips": (
            float(gross_positive) > float(gross_negative)
        ),
    }
    if gate.get("criteria") != expected_criteria:
        raise ValueError(
            "EXP-049 stability window criteria mismatch"
        )
    passed = all(expected_criteria.values())
    if gate.get("passed") is not passed:
        raise ValueError("EXP-049 stability window pass mismatch")
    return passed


def _validate_variant(
    raw: Mapping[str, object],
) -> tuple[bool, bool, bool]:
    budget = raw.get("candidate_budget_anchor")
    if budget not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError("EXP-049 utility budget identity mismatch")
    if raw.get("model_family") != "hist_gradient_boosting_regression":
        raise ValueError("EXP-049 variant model family mismatch")

    evaluation = raw.get("evaluation_status")
    if evaluation == "BUDGET_UNAVAILABLE":
        if raw.get("status") != "UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS":
            raise ValueError("EXP-049 unavailable utility status mismatch")
        eligible = raw.get("eligible_utility_row_count")
        if (
            not isinstance(eligible, int)
            or isinstance(eligible, bool)
            or eligible < 0
            or eligible >= int(budget)
        ):
            raise ValueError(
                "EXP-049 unavailable utility row count mismatch"
            )
        if raw.get("selection_derived_cutoff") is not None:
            raise ValueError(
                "EXP-049 unavailable budget cannot have cutoff"
            )
        if raw.get("aggregate_selection_gate_passed") is not False:
            raise ValueError(
                "EXP-049 unavailable budget cannot aggregate-pass"
            )
        if raw.get("selection_gate_passed") is not False:
            raise ValueError(
                "EXP-049 unavailable budget cannot final-pass"
            )
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
            raise ValueError(
                "EXP-049 unavailable stability evidence mismatch"
            )
        return False, False, True

    if evaluation != "EVALUATED" or raw.get("status") != "AVAILABLE":
        raise ValueError("EXP-049 utility variant status mismatch")
    eligible = raw.get("eligible_utility_row_count")
    selected_at_cutoff = raw.get("selection_candidate_count_at_cutoff")
    cutoff = raw.get("selection_derived_cutoff")
    if (
        not isinstance(eligible, int)
        or isinstance(eligible, bool)
        or eligible < int(budget)
    ):
        raise ValueError(
            "EXP-049 eligible utility row count is invalid"
        )
    if (
        not isinstance(selected_at_cutoff, int)
        or isinstance(selected_at_cutoff, bool)
        or selected_at_cutoff < int(budget)
        or selected_at_cutoff > eligible
    ):
        raise ValueError(
            "EXP-049 selected-at-cutoff count is invalid"
        )
    if (
        not isinstance(cutoff, (int, float))
        or isinstance(cutoff, bool)
        or not math.isfinite(float(cutoff))
        or float(cutoff) <= 0.0
    ):
        raise ValueError("EXP-049 robust-utility cutoff is invalid")

    scenarios = raw.get("scenarios")
    if (
        not isinstance(scenarios, Mapping)
        or set(scenarios) != {"0.5"}
    ):
        raise ValueError(
            "EXP-049 selection scenario inventory mismatch"
        )
    scenario = scenarios["0.5"]
    if not isinstance(scenario, Mapping):
        raise ValueError("EXP-049 selection scenario is malformed")
    metrics = scenario.get("metrics")
    gate = scenario.get("gate")
    if not isinstance(metrics, Mapping) or not isinstance(gate, Mapping):
        raise ValueError("EXP-049 aggregate scenario is malformed")
    if metrics.get("directional_candidate_count") != selected_at_cutoff:
        raise ValueError("EXP-049 cutoff candidate count mismatch")
    aggregate = _validate_financial_gate(
        metrics=metrics,
        gate=gate,
        field="EXP-049 aggregate selection",
    )
    if raw.get("aggregate_selection_gate_passed") is not aggregate:
        raise ValueError("EXP-049 aggregate gate evidence mismatch")
    final = raw.get("selection_gate_passed")
    if not isinstance(final, bool):
        raise ValueError("EXP-049 final gate status is malformed")

    stability = raw.get("temporal_stability")
    if not isinstance(stability, Mapping):
        raise ValueError("EXP-049 temporal-stability block malformed")
    if stability.get(
        "minimum_directional_candidate_share_per_window"
    ) != MIN_STABILITY_WINDOW_CANDIDATE_SHARE:
        raise ValueError("EXP-049 stability share threshold mismatch")

    if not aggregate:
        if stability.get("status") != "LOCKED_AGGREGATE_REJECT":
            raise ValueError(
                "EXP-049 aggregate reject must lock stability"
            )
        if stability.get("windows") != [] or final is not False:
            raise ValueError(
                "EXP-049 aggregate reject stability mismatch"
            )
        return False, False, False

    windows = stability.get("windows")
    if not isinstance(windows, list) or len(windows) != 4:
        raise ValueError(
            "EXP-049 aggregate pass requires four stability windows"
        )
    passes: list[bool] = []
    expected_windows = [dict(window) for window in TEMPORAL_STABILITY_WINDOWS]
    for window, expected in zip(
        windows,
        expected_windows,
        strict=True,
    ):
        if not isinstance(window, Mapping):
            raise ValueError("EXP-049 stability window is malformed")
        passes.append(
            _validate_window(
                window,
                expected=expected,
                full_selection_candidate_count=int(selected_at_cutoff),
            )
        )
    expected_status = "PASS" if all(passes) else "REJECT"
    if stability.get("status") != expected_status:
        raise ValueError("EXP-049 stability status mismatch")
    expected_final = expected_status == "PASS"
    if final is not expected_final:
        raise ValueError("EXP-049 final selection-gate mismatch")
    return True, expected_final, False


def _validate_fit_block(
    fit: Mapping[str, object],
) -> dict[str, dict[str, str]]:
    regime_models = fit.get("regime_models")
    expected_names = tuple(
        str(window["name"]) for window in FIT_REGIME_WINDOWS
    )
    if (
        not isinstance(regime_models, Mapping)
        or set(regime_models) != set(expected_names)
        or fit.get("regime_model_count") != len(expected_names)
        or fit.get("regressor_count") != 6
    ):
        raise ValueError("EXP-049 regime fit inventory mismatch")

    fingerprints: dict[str, dict[str, str]] = {}
    for regime_name in expected_names:
        record = regime_models.get(regime_name)
        if not isinstance(record, Mapping):
            raise ValueError("EXP-049 regime fit record is malformed")
        row_count = record.get("row_count")
        if (
            record.get("status") != "FITTED"
            or not isinstance(row_count, int)
            or isinstance(row_count, bool)
            or row_count <= 0
            or record.get("regressor_count") != 2
        ):
            raise ValueError("EXP-049 regime fit record mismatch")
        regressors = record.get("regressors")
        if (
            not isinstance(regressors, Mapping)
            or set(regressors) != set(FINANCIAL_TARGET_COLUMNS)
        ):
            raise ValueError(
                "EXP-049 regressor inventory mismatch"
            )
        target_fps: dict[str, str] = {}
        for target in FINANCIAL_TARGET_COLUMNS:
            regressor = regressors.get(target)
            if not isinstance(regressor, Mapping):
                raise ValueError(
                    "EXP-049 regressor record is malformed"
                )
            if (
                regressor.get("status") != "FITTED"
                or regressor.get("fit_attempt_count") != 1
            ):
                raise ValueError(
                    "EXP-049 regressor fit status mismatch"
                )
            summary = regressor.get("target_summary")
            if not isinstance(summary, Mapping):
                raise ValueError(
                    "EXP-049 regressor target summary is malformed"
                )
            _validate_target_summary(
                summary,
                expected_row_count=row_count,
                field=f"EXP-049 {regime_name} {target}",
            )
            _validate_sha256(
                regressor.get("preprocessor_fingerprint"),
                field=(
                    f"EXP-049 {regime_name} {target} "
                    "preprocessor fingerprint"
                ),
            )
            target_fps[target] = _validate_sha256(
                regressor.get("model_fingerprint"),
                field=(
                    f"EXP-049 {regime_name} {target} model fingerprint"
                ),
            )
        fingerprints[regime_name] = target_fps

    if fit.get("full_fit_single_model") != {
        "status": "FORBIDDEN_BY_DEC132",
        "fit_attempt_count": 0,
    }:
        raise ValueError("EXP-049 full-fit fallback record mismatch")
    if fit.get("hist_gradient_boosting_classifier") != {
        "status": "EXCLUDED_BY_DEC132",
        "fit_attempt_count": 0,
    }:
        raise ValueError("EXP-049 classifier exclusion record mismatch")
    if fit.get("logistic_regression") != {
        "status": "EXCLUDED_BY_DEC112_DEC132",
        "fit_attempt_count": 0,
    }:
        raise ValueError("EXP-049 logistic exclusion record mismatch")
    return fingerprints


def _validate_forward_block(
    block: Mapping[str, object],
    *,
    expected_budget: int,
    expected_cutoff: float,
    field: str,
) -> str:
    status = block.get("status")
    if status not in {"PASS", "REJECT"}:
        raise ValueError(f"{field} status is invalid")
    row_count = block.get("row_count")
    if (
        not isinstance(row_count, int)
        or isinstance(row_count, bool)
        or row_count <= 0
    ):
        raise ValueError(f"{field} row count is invalid")
    consensus = block.get("regime_utility_consensus")
    if not isinstance(consensus, Mapping):
        raise ValueError(f"{field} consensus block is malformed")
    _validate_utility_consensus_block(
        consensus,
        expected_row_count=row_count,
        field=field,
    )
    _validate_sha256(
        block.get("regime_utility_consensus_digest"),
        field=f"{field} consensus digest",
    )
    if block.get("candidate_budget_anchor") != expected_budget:
        raise ValueError(f"{field} budget does not match selection")
    cutoff = block.get("selection_derived_cutoff")
    if (
        not isinstance(cutoff, (int, float))
        or isinstance(cutoff, bool)
        or float(cutoff) != expected_cutoff
    ):
        raise ValueError(f"{field} cutoff does not match selection")

    scenarios = block.get("scenarios")
    if (
        not isinstance(scenarios, Mapping)
        or set(scenarios) != {"0.2", "0.5", "1.0"}
    ):
        raise ValueError(f"{field} scenario inventory mismatch")
    passes: dict[str, bool] = {}
    for scenario_name in ("0.2", "0.5", "1.0"):
        raw = scenarios.get(scenario_name)
        if not isinstance(raw, Mapping):
            raise ValueError(f"{field} scenario row is malformed")
        metrics = raw.get("metrics")
        gate = raw.get("gate")
        if not isinstance(metrics, Mapping) or not isinstance(gate, Mapping):
            raise ValueError(f"{field} financial evidence is malformed")
        passes[scenario_name] = _validate_financial_gate(
            metrics=metrics,
            gate=gate,
            field=f"{field} scenario {scenario_name}",
        )
    expected_status = (
        "PASS" if passes["0.5"] and passes["1.0"] else "REJECT"
    )
    if status != expected_status:
        raise ValueError(f"{field} gate status mismatch")
    return status


def _validate_regime_utility_cell_result(
    result: Mapping[str, object],
) -> dict[str, object]:
    cell = result.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError("EXP-049 result is missing cell identity")
    horizon = cell.get("horizon_minutes")
    if not isinstance(horizon, int) or isinstance(horizon, bool):
        raise ValueError("EXP-049 result horizon is malformed")
    identity = (
        str(cell.get("symbol")),
        str(cell.get("timeframe")),
        horizon,
    )
    expected_cells = {
        (item.symbol, item.timeframe, item.horizon_minutes)
        for item in MODEL_CELLS
    }
    if identity not in expected_cells:
        raise ValueError(f"unexpected EXP-049 result cell: {identity}")

    exact = {
        "experiment_id": REGIME_UTILITY_EXPERIMENT_ID,
        "training_core_version": REGIME_UTILITY_TRAINING_CORE_VERSION,
        "training_core_decision": REGIME_UTILITY_TRAINING_CORE_DECISION,
        "dec132_merged_commit": DEC132_MERGED_COMMIT,
        "dec132_protocol_blob_sha": DEC132_PROTOCOL_BLOB_SHA,
        "base_training_core_blob_sha": BASE_TRAINING_CORE_BLOB_SHA,
        "density_helper_core_blob_sha": DENSITY_HELPER_CORE_BLOB_SHA,
        "protocol_decision": REGIME_UTILITY_PROTOCOL_DECISION,
        "protocol_version": REGIME_UTILITY_PROTOCOL_VERSION,
        "protocol_fingerprint": regime_utility_protocol_fingerprint(),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": UNTOUCHED_OOS,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    for field, expected in exact.items():
        if result.get(field) != expected:
            raise ValueError(f"EXP-049 result {field} mismatch")

    _validate_sha256(
        result.get("processed_manifest_sha256"),
        field="EXP-049 processed manifest fingerprint",
    )
    joined_row_count = result.get("joined_row_count")
    if (
        not isinstance(joined_row_count, int)
        or isinstance(joined_row_count, bool)
        or joined_row_count <= 0
    ):
        raise ValueError("EXP-049 joined row count is invalid")
    split_counts = result.get("split_row_counts")
    if (
        not isinstance(split_counts, Mapping)
        or set(split_counts)
        != {"fit", "selection", "validation", "retrospective_holdout"}
    ):
        raise ValueError("EXP-049 split row counts are malformed")
    for value in split_counts.values():
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value <= 0
        ):
            raise ValueError("EXP-049 split row count is invalid")

    fit = result.get("fit")
    if not isinstance(fit, Mapping):
        raise ValueError("EXP-049 fit block is malformed")
    regressor_fingerprints = _validate_fit_block(fit)

    selection = result.get("selection")
    validation = result.get("validation")
    holdout = result.get("retrospective_holdout")
    if (
        not isinstance(selection, Mapping)
        or not isinstance(validation, Mapping)
        or not isinstance(holdout, Mapping)
    ):
        raise ValueError("EXP-049 chronology blocks are malformed")
    selection_rows = selection.get("row_count")
    if (
        not isinstance(selection_rows, int)
        or isinstance(selection_rows, bool)
        or selection_rows <= 0
        or selection_rows != split_counts["selection"]
    ):
        raise ValueError("EXP-049 selection row count mismatch")

    consensus = selection.get("regime_utility_consensus")
    if not isinstance(consensus, Mapping):
        raise ValueError("EXP-049 selection consensus is malformed")
    eligible_rows = _validate_utility_consensus_block(
        consensus,
        expected_row_count=selection_rows,
        field="EXP-049 selection",
    )
    _validate_sha256(
        selection.get("regime_utility_consensus_digest"),
        field="EXP-049 selection consensus digest",
    )

    variants = selection.get("variants")
    if not isinstance(variants, list) or len(variants) != 3:
        raise ValueError("EXP-049 must contain exactly three variants")
    indexed: dict[int, Mapping[str, object]] = {}
    aggregate_pass_count = 0
    stable_pass_count = 0
    stability_reject_count = 0
    unavailable_budget_count = 0
    for raw in variants:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-049 utility variant is malformed")
        budget = raw.get("candidate_budget_anchor")
        if (
            not isinstance(budget, int)
            or isinstance(budget, bool)
            or budget not in CANDIDATE_BUDGET_ANCHORS
            or budget in indexed
        ):
            raise ValueError("EXP-049 utility budget inventory mismatch")
        aggregate, final, unavailable = _validate_variant(raw)
        if raw.get("eligible_utility_row_count") != eligible_rows:
            raise ValueError(
                "EXP-049 variant utility eligible count mismatch"
            )
        aggregate_pass_count += int(aggregate)
        stable_pass_count += int(final)
        stability_reject_count += int(aggregate and not final)
        unavailable_budget_count += int(unavailable)
        indexed[budget] = raw
    if set(indexed) != set(CANDIDATE_BUDGET_ANCHORS):
        raise ValueError("EXP-049 utility budget inventory mismatch")

    passing = [
        raw
        for raw in indexed.values()
        if raw.get("selection_gate_passed") is True
    ]
    expected_selected = (
        max(
            passing,
            key=lambda raw: (
                float(
                    raw["scenarios"]["0.5"]["metrics"]["total_net_pips"]
                ),
                int(
                    raw["scenarios"]["0.5"]["metrics"][
                        "directional_candidate_count"
                    ]
                ),
                -int(raw["candidate_budget_anchor"]),
            ),
        )
        if passing
        else None
    )

    selected_variant = selection.get("selected_variant")
    selection_status = selection.get("status")
    selected_budget: int | None = None
    selected_cutoff: float | None = None
    if selection_status == "SELECTED":
        if not isinstance(selected_variant, Mapping):
            raise ValueError("EXP-049 selected cell lacks variant identity")
        if selected_variant.get(
            "model_family"
        ) != "hist_gradient_boosting_regression":
            raise ValueError("EXP-049 selected model family mismatch")
        budget = selected_variant.get("candidate_budget_anchor")
        cutoff = selected_variant.get("selection_derived_cutoff")
        if (
            not isinstance(budget, int)
            or isinstance(budget, bool)
            or budget not in indexed
            or not isinstance(cutoff, (int, float))
            or isinstance(cutoff, bool)
        ):
            raise ValueError("EXP-049 selected variant is malformed")
        chosen = indexed[budget]
        if (
            chosen.get("selection_gate_passed") is not True
            or float(chosen["selection_derived_cutoff"])
            != float(cutoff)
        ):
            raise ValueError(
                "EXP-049 selected variant is not utility-stable eligible"
            )
        if (
            expected_selected is None
            or int(expected_selected["candidate_budget_anchor"]) != budget
            or float(expected_selected["selection_derived_cutoff"])
            != float(cutoff)
        ):
            raise ValueError(
                "EXP-049 selected variant is not deterministic winner"
            )
        selected_budget = budget
        selected_cutoff = float(cutoff)
    elif selection_status == "NO_REGIME_UTILITY_STABLE_MODEL_CHALLENGER":
        if selected_variant is not None:
            raise ValueError(
                "EXP-049 unselected cell cannot name a variant"
            )
        if expected_selected is not None:
            raise ValueError(
                "EXP-049 no-challenger status hides stable variant"
            )
    else:
        raise ValueError(
            f"unexpected EXP-049 selection status: {selection_status!r}"
        )

    _validate_status_chain(
        selection=selection_status,
        validation=validation.get("status"),
        holdout=holdout.get("status"),
    )
    if selection_status == "SELECTED":
        assert selected_budget is not None
        assert selected_cutoff is not None
        validation_status = _validate_forward_block(
            validation,
            expected_budget=selected_budget,
            expected_cutoff=selected_cutoff,
            field="EXP-049 validation",
        )
        if validation_status == "PASS":
            _validate_forward_block(
                holdout,
                expected_budget=selected_budget,
                expected_cutoff=selected_cutoff,
                field="EXP-049 retrospective holdout",
            )
        elif holdout != {"status": "LOCKED_VALIDATION_REJECT"}:
            raise ValueError(
                "EXP-049 rejected validation holdout lock mismatch"
            )
    else:
        if validation != {"status": "LOCKED_NO_SELECTION"}:
            raise ValueError(
                "EXP-049 no-selection validation lock mismatch"
            )
        if holdout != {"status": "LOCKED_NO_SELECTION"}:
            raise ValueError(
                "EXP-049 no-selection holdout lock mismatch"
            )

    result_fingerprint = _validate_sha256(
        result.get("result_fingerprint"),
        field="EXP-049 cell result fingerprint",
    )
    unsigned = dict(result)
    unsigned.pop("result_fingerprint", None)
    if _sha256(_canonical_json(unsigned)) != result_fingerprint:
        raise ValueError("EXP-049 cell result fingerprint mismatch")

    return {
        "symbol": identity[0],
        "timeframe": identity[1],
        "horizon_minutes": identity[2],
        "result_fingerprint": result_fingerprint,
        "selection_status": selection_status,
        "validation_status": validation.get("status"),
        "retrospective_holdout_status": holdout.get("status"),
        "regime_model_count": 3,
        "regressor_count": 6,
        "regime_regressor_fingerprints": regressor_fingerprints,
        "classifier_fit_status": (
            fit["hist_gradient_boosting_classifier"]["status"]
        ),
        "logistic_fit_status": fit["logistic_regression"]["status"],
        "utility_eligible_selection_row_count": eligible_rows,
        "aggregate_selection_pass_variant_count": aggregate_pass_count,
        "stable_selection_pass_variant_count": stable_pass_count,
        "stability_reject_variant_count": stability_reject_count,
        "unavailable_budget_variant_count": unavailable_budget_count,
    }


def compile_regime_utility_model_result_evidence(
    cell_results: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    commit = _validate_commit(
        code_commit,
        field="EXP-049 model-result code commit",
    )
    expected_cells = {
        (cell.symbol, cell.timeframe, cell.horizon_minutes)
        for cell in MODEL_CELLS
    }
    indexed: dict[tuple[str, str, int], dict[str, object]] = {}
    for result in cell_results:
        if not isinstance(result, Mapping):
            raise ValueError(
                "EXP-049 model result row must be an object"
            )
        summary = _validate_regime_utility_cell_result(result)
        identity = (
            str(summary["symbol"]),
            str(summary["timeframe"]),
            int(summary["horizon_minutes"]),
        )
        if identity in indexed:
            raise ValueError("duplicate EXP-049 model result cell")
        indexed[identity] = summary
    if set(indexed) != expected_cells:
        missing = sorted(expected_cells - set(indexed))
        raise ValueError(
            f"EXP-049 result evidence is incomplete: {missing}"
        )

    cells = [indexed[key] for key in sorted(indexed)]
    evidence: dict[str, object] = {
        "evidence_version": REGIME_UTILITY_MODEL_RESULT_EVIDENCE_VERSION,
        "runner_version": REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION,
        "runner_decision": REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
        "experiment_id": REGIME_UTILITY_EXPERIMENT_ID,
        "training_core_version": REGIME_UTILITY_TRAINING_CORE_VERSION,
        "training_core_decision": REGIME_UTILITY_TRAINING_CORE_DECISION,
        "training_core_commit": DEC133_MERGED_COMMIT,
        "training_core_blob_sha": DEC133_TRAINING_CORE_BLOB_SHA,
        "protocol_decision": REGIME_UTILITY_PROTOCOL_DECISION,
        "protocol_version": REGIME_UTILITY_PROTOCOL_VERSION,
        "protocol_commit": DEC132_MERGED_COMMIT,
        "protocol_blob_sha": DEC132_PROTOCOL_BLOB_SHA,
        "protocol_fingerprint": regime_utility_protocol_fingerprint(),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": UNTOUCHED_OOS,
        "code_commit": commit,
        "source_data_experiment_id": "EXP-20260923-044",
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
        "readiness_artifact_id": AUTHORITATIVE_READINESS_ARTIFACT_ID,
        "readiness_fingerprint": AUTHORITATIVE_READINESS_FINGERPRINT,
        "verified_cell_count": len(cells),
        "cells": cells,
        "model_protocol_result_authorized": False,
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


def _validate_summary_cell(
    raw: Mapping[str, object],
    *,
    expected_cells: set[tuple[str, str, int]],
) -> tuple[str, str, int]:
    symbol = raw.get("symbol")
    timeframe = raw.get("timeframe")
    horizon = raw.get("horizon_minutes")
    if (
        not isinstance(symbol, str)
        or not isinstance(timeframe, str)
        or not isinstance(horizon, int)
        or isinstance(horizon, bool)
    ):
        raise ValueError("EXP-049 aggregate cell identity is malformed")
    identity = (symbol, timeframe, horizon)
    if identity not in expected_cells:
        raise ValueError(f"unexpected EXP-049 aggregate cell: {identity}")
    _validate_sha256(
        raw.get("result_fingerprint"),
        field="EXP-049 aggregate cell result fingerprint",
    )
    _validate_status_chain(
        selection=raw.get("selection_status"),
        validation=raw.get("validation_status"),
        holdout=raw.get("retrospective_holdout_status"),
    )
    if (
        raw.get("regime_model_count") != 3
        or raw.get("regressor_count") != 6
    ):
        raise ValueError("EXP-049 aggregate regressor count mismatch")
    fingerprints = raw.get("regime_regressor_fingerprints")
    expected_regimes = {
        str(window["name"]) for window in FIT_REGIME_WINDOWS
    }
    if (
        not isinstance(fingerprints, Mapping)
        or set(fingerprints) != expected_regimes
    ):
        raise ValueError(
            "EXP-049 aggregate regime fingerprint set mismatch"
        )
    for regime in expected_regimes:
        target_fps = fingerprints.get(regime)
        if (
            not isinstance(target_fps, Mapping)
            or set(target_fps) != set(FINANCIAL_TARGET_COLUMNS)
        ):
            raise ValueError(
                "EXP-049 aggregate regressor fingerprint inventory mismatch"
            )
        for target in FINANCIAL_TARGET_COLUMNS:
            _validate_sha256(
                target_fps.get(target),
                field=(
                    f"EXP-049 aggregate {regime} {target} "
                    "model fingerprint"
                ),
            )
    if raw.get("classifier_fit_status") != "EXCLUDED_BY_DEC132":
        raise ValueError(
            "EXP-049 classifier exclusion summary mismatch"
        )
    if raw.get("logistic_fit_status") != "EXCLUDED_BY_DEC112_DEC132":
        raise ValueError(
            "EXP-049 logistic exclusion summary mismatch"
        )
    eligible = raw.get("utility_eligible_selection_row_count")
    if (
        not isinstance(eligible, int)
        or isinstance(eligible, bool)
        or eligible < 0
    ):
        raise ValueError(
            "EXP-049 aggregate utility eligible count is invalid"
        )
    for field in (
        "aggregate_selection_pass_variant_count",
        "stable_selection_pass_variant_count",
        "stability_reject_variant_count",
        "unavailable_budget_variant_count",
    ):
        value = raw.get(field)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
            or value > 3
        ):
            raise ValueError(
                f"EXP-049 aggregate cell {field} is invalid"
            )
    if (
        int(raw["stable_selection_pass_variant_count"])
        + int(raw["stability_reject_variant_count"])
        != int(raw["aggregate_selection_pass_variant_count"])
    ):
        raise ValueError(
            "EXP-049 aggregate/stability accounting mismatch"
        )
    return identity


def validate_regime_utility_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    if not isinstance(evidence, Mapping):
        raise ValueError(
            "EXP-049 model-result evidence must be an object"
        )
    commit = _validate_commit(
        expected_code_commit,
        field="EXP-049 expected code commit",
    )
    unsigned = dict(evidence)
    supplied = _validate_sha256(
        unsigned.pop("evidence_fingerprint", None),
        field="EXP-049 aggregate evidence fingerprint",
    )
    if _sha256(_canonical_json(unsigned)) != supplied:
        raise ValueError(
            "EXP-049 aggregate evidence fingerprint mismatch"
        )

    exact = {
        "evidence_version": REGIME_UTILITY_MODEL_RESULT_EVIDENCE_VERSION,
        "runner_version": REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION,
        "runner_decision": REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
        "experiment_id": REGIME_UTILITY_EXPERIMENT_ID,
        "training_core_version": REGIME_UTILITY_TRAINING_CORE_VERSION,
        "training_core_decision": REGIME_UTILITY_TRAINING_CORE_DECISION,
        "training_core_commit": DEC133_MERGED_COMMIT,
        "training_core_blob_sha": DEC133_TRAINING_CORE_BLOB_SHA,
        "protocol_decision": REGIME_UTILITY_PROTOCOL_DECISION,
        "protocol_version": REGIME_UTILITY_PROTOCOL_VERSION,
        "protocol_commit": DEC132_MERGED_COMMIT,
        "protocol_blob_sha": DEC132_PROTOCOL_BLOB_SHA,
        "protocol_fingerprint": regime_utility_protocol_fingerprint(),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": UNTOUCHED_OOS,
        "code_commit": commit,
        "source_data_experiment_id": "EXP-20260923-044",
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
        "readiness_artifact_id": AUTHORITATIVE_READINESS_ARTIFACT_ID,
        "readiness_fingerprint": AUTHORITATIVE_READINESS_FINGERPRINT,
        "verified_cell_count": len(MODEL_CELLS),
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    for field, expected in exact.items():
        if evidence.get(field) != expected:
            raise ValueError(
                f"EXP-049 aggregate evidence {field} mismatch"
            )

    cells = evidence.get("cells")
    if (
        not isinstance(cells, list)
        or len(cells) != len(MODEL_CELLS)
    ):
        raise ValueError(
            "EXP-049 aggregate evidence must contain 18 cells"
        )
    expected_cells = {
        (cell.symbol, cell.timeframe, cell.horizon_minutes)
        for cell in MODEL_CELLS
    }
    indexed: dict[
        tuple[str, str, int],
        Mapping[str, object],
    ] = {}
    selected_count = 0
    no_challenger_count = 0
    validation_pass_count = 0
    holdout_pass_count = 0
    aggregate_pass_variant_count = 0
    stable_pass_variant_count = 0
    stability_reject_variant_count = 0
    unavailable_budget_variant_count = 0
    utility_eligible_selection_row_count = 0

    for raw in cells:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-049 aggregate cell summary is malformed"
            )
        identity = _validate_summary_cell(
            raw,
            expected_cells=expected_cells,
        )
        if identity in indexed:
            raise ValueError("duplicate EXP-049 aggregate cell")
        indexed[identity] = raw
        selection = raw["selection_status"]
        selected_count += int(selection == "SELECTED")
        no_challenger_count += int(
            selection == "NO_REGIME_UTILITY_STABLE_MODEL_CHALLENGER"
        )
        validation_pass_count += int(
            raw["validation_status"] == "PASS"
        )
        holdout_pass_count += int(
            raw["retrospective_holdout_status"] == "PASS"
        )
        aggregate_pass_variant_count += int(
            raw["aggregate_selection_pass_variant_count"]
        )
        stable_pass_variant_count += int(
            raw["stable_selection_pass_variant_count"]
        )
        stability_reject_variant_count += int(
            raw["stability_reject_variant_count"]
        )
        unavailable_budget_variant_count += int(
            raw["unavailable_budget_variant_count"]
        )
        utility_eligible_selection_row_count += int(
            raw["utility_eligible_selection_row_count"]
        )
    if set(indexed) != expected_cells:
        raise ValueError("EXP-049 aggregate cell set mismatch")

    return {
        "regime_utility_model_result_evidence_verified": True,
        "regime_utility_model_result_evidence_fingerprint": supplied,
        "regime_utility_model_result_code_commit": commit,
        "verified_cell_count": len(cells),
        "selected_cell_count": selected_count,
        "no_regime_utility_stable_model_challenger_count": (
            no_challenger_count
        ),
        "validation_pass_count": validation_pass_count,
        "retrospective_holdout_pass_count": holdout_pass_count,
        "aggregate_selection_pass_variant_count": (
            aggregate_pass_variant_count
        ),
        "stable_selection_pass_variant_count": stable_pass_variant_count,
        "stability_reject_variant_count": stability_reject_variant_count,
        "unavailable_budget_variant_count": (
            unavailable_budget_variant_count
        ),
        "utility_eligible_selection_row_count": (
            utility_eligible_selection_row_count
        ),
        "prior_result_informed": True,
        "untouched_oos": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def run_authoritative_regime_utility_model_bundle(
    *,
    repository_root: Path,
    readiness: Mapping[str, object],
    feature_roots: Mapping[tuple[str, str], Path],
    outcome_roots: Mapping[tuple[str, str], Path],
    code_commit: str,
) -> dict[str, object]:
    if (
        AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "DEC-134 source is non-executable for authoritative "
            "EXP-049 model fitting"
        )

    validate_regime_utility_artifact_runner_sources(
        repository_root=repository_root
    )
    indexed = validate_authoritative_readiness(readiness)
    cell_results: list[dict[str, object]] = []
    for cell in MODEL_CELLS:
        identity = (cell.symbol, cell.timeframe)
        if identity not in indexed:
            raise ValueError(
                f"missing authoritative EXP-049 source cell: {identity}"
            )
        if identity not in feature_roots or identity not in outcome_roots:
            raise ValueError(
                f"missing extracted EXP-049 artifact root: {identity}"
            )
        loaded: VerifiedCellArtifacts = load_authoritative_cell_artifacts(
            readiness=readiness,
            feature_root=feature_roots[identity],
            outcome_root=outcome_roots[identity],
            symbol=cell.symbol,
            timeframe=cell.timeframe,
        )
        cell_results.append(
            run_regime_utility_model_cell_core(
                features=loaded.feature_frame,
                outcomes=loaded.outcome_frame,
                cell=cell,
            )
        )
    return compile_regime_utility_model_result_evidence(
        cell_results,
        code_commit=code_commit,
    )


def write_regime_utility_model_result_evidence(
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
        raise ValueError(
            "conflicting existing EXP-049 model-result evidence"
        )
    destination.write_text(payload, encoding="utf-8")


def load_regime_utility_model_result_evidence(
    path: Path,
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise ValueError(
            f"cannot read EXP-049 model-result evidence: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError(
            "EXP-049 model-result evidence root must be an object"
        )
    validate_regime_utility_model_result_evidence(
        value,
        expected_code_commit=expected_code_commit,
    )
    return value


__all__ = [
    "AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC133_MERGED_COMMIT",
    "DEC133_TRAINING_CORE_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "LEGACY_DATA_LOADER_BLOB_SHA",
    "LIVE_ORDER_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION",
    "REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION",
    "REGIME_UTILITY_MODEL_FIT_AUTHORIZED",
    "REGIME_UTILITY_MODEL_RESULT_EVIDENCE_VERSION",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "_canonical_json",
    "_sha256",
    "compile_regime_utility_model_result_evidence",
    "load_regime_utility_model_result_evidence",
    "run_authoritative_regime_utility_model_bundle",
    "validate_regime_utility_artifact_runner_sources",
    "validate_regime_utility_model_result_evidence",
    "write_regime_utility_model_result_evidence",
]
