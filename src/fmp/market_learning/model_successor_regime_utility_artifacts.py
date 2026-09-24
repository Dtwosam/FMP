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
    DIAGNOSTIC_SCENARIOS,
    GATE_REQUIREMENTS,
    HOLDOUT_GATE_SCENARIOS,
    MIN_DIRECTIONAL_CANDIDATES,
    MODEL_CELLS,
    VALIDATION_GATE_SCENARIOS,
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
        raise ValueError(
            f"{field} must be a 64-character sha256"
        )
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(
            f"{field} must be hexadecimal"
        ) from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(
            f"{field} must be a 40-character Git commit"
        )
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(
            f"{field} must be hexadecimal"
        ) from exc
    return value.lower()


def validate_regime_utility_artifact_runner_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "legacy_data_loader": (
            root
            / "src/fmp/market_learning/model_artifacts.py",
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
        "legacy_data_loader_blob_sha": actual[
            "legacy_data_loader"
        ],
        "dec132_protocol_blob_sha": actual[
            "dec132_protocol"
        ],
        "dec133_training_core_blob_sha": actual[
            "dec133_training_core"
        ],
        "base_training_core_blob_sha": (
            BASE_TRAINING_CORE_BLOB_SHA
        ),
        "density_helper_core_blob_sha": (
            DENSITY_HELPER_CORE_BLOB_SHA
        ),
        "regime_utility_protocol_fingerprint": (
            protocol_fingerprint
        ),
        "authoritative_regime_utility_model_result_execution_authorized": (
            False
        ),
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
    gross_negative = metrics.get(
        "absolute_gross_negative_pips"
    )

    if (
        not isinstance(count, int)
        or isinstance(count, bool)
        or count < 0
    ):
        raise ValueError(
            f"{field} directional candidate count is invalid"
        )
    for name, value in (
        ("total_net_pips", total),
        ("gross_positive_pips", gross_positive),
        (
            "absolute_gross_negative_pips",
            gross_negative,
        ),
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise ValueError(
                f"{field} {name} is invalid"
            )
    if mean is not None and (
        not isinstance(mean, (int, float))
        or isinstance(mean, bool)
        or not math.isfinite(float(mean))
    ):
        raise ValueError(
            f"{field} mean_net_pips is invalid"
        )

    criteria = {
        GATE_REQUIREMENTS[0]: (
            count >= MIN_DIRECTIONAL_CANDIDATES
        ),
        GATE_REQUIREMENTS[1]: float(total) > 0.0,
        GATE_REQUIREMENTS[2]: (
            mean is not None and float(mean) > 0.0
        ),
        GATE_REQUIREMENTS[3]: (
            float(gross_positive)
            > float(gross_negative)
        ),
    }
    if gate.get("criteria") != criteria:
        raise ValueError(
            f"{field} financial gate criteria mismatch"
        )
    passed = all(criteria.values())
    if gate.get("passed") is not passed:
        raise ValueError(
            f"{field} financial gate pass mismatch"
        )
    return passed


def _validate_status_chain(
    *,
    selection: object,
    validation: object,
    holdout: object,
) -> None:
    if (
        selection
        == "NO_REGIME_UTILITY_STABLE_MODEL_CHALLENGER"
    ):
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
        raise ValueError(
            f"{field} target summary row count mismatch"
        )

    minimum = summary.get("minimum_net_pips")
    maximum = summary.get("maximum_net_pips")
    mean = summary.get("mean_net_pips")
    for name, value in (
        ("minimum_net_pips", minimum),
        ("maximum_net_pips", maximum),
        ("mean_net_pips", mean),
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise ValueError(
                f"{field} {name} is invalid"
            )
    if float(minimum) > float(maximum):
        raise ValueError(
            f"{field} target summary bounds are invalid"
        )
    if not (
        float(minimum)
        <= float(mean)
        <= float(maximum)
    ):
        raise ValueError(
            f"{field} target summary mean is outside bounds"
        )

    counts: list[int] = []
    for name in (
        "positive_count",
        "negative_count",
        "zero_count",
    ):
        value = summary.get(name)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            raise ValueError(
                f"{field} {name} is invalid"
            )
        counts.append(value)
    if sum(counts) != expected_row_count:
        raise ValueError(
            f"{field} target summary count mismatch"
        )


def _validate_fit_block(
    fit: Mapping[str, object],
) -> int:
    regime_names = {
        str(window["name"])
        for window in FIT_REGIME_WINDOWS
    }
    regimes = fit.get("regime_models")
    if (
        not isinstance(regimes, Mapping)
        or set(regimes) != regime_names
    ):
        raise ValueError(
            "EXP-049 regime fit inventory mismatch"
        )
    if fit.get("regime_model_count") != 3:
        raise ValueError(
            "EXP-049 regime model count mismatch"
        )
    if fit.get("regressor_count") != 6:
        raise ValueError(
            "EXP-049 total regressor count mismatch"
        )

    verified_regressors = 0
    for regime_name in sorted(regime_names):
        regime = regimes.get(regime_name)
        if not isinstance(regime, Mapping):
            raise ValueError(
                "EXP-049 regime fit record is malformed"
            )
        if regime.get("status") != "FITTED":
            raise ValueError(
                "EXP-049 regime fit status mismatch"
            )
        row_count = regime.get("row_count")
        if (
            not isinstance(row_count, int)
            or isinstance(row_count, bool)
            or row_count <= 0
        ):
            raise ValueError(
                "EXP-049 regime fit row count is invalid"
            )
        if regime.get("regressor_count") != 2:
            raise ValueError(
                "EXP-049 regime regressor count mismatch"
            )

        regressors = regime.get("regressors")
        if (
            not isinstance(regressors, Mapping)
            or set(regressors)
            != set(FINANCIAL_TARGET_COLUMNS)
        ):
            raise ValueError(
                "EXP-049 regressor inventory mismatch"
            )
        for target in FINANCIAL_TARGET_COLUMNS:
            record = regressors.get(target)
            if not isinstance(record, Mapping):
                raise ValueError(
                    "EXP-049 regressor record is malformed"
                )
            if (
                record.get("status") != "FITTED"
                or record.get("fit_attempt_count") != 1
            ):
                raise ValueError(
                    "EXP-049 regressor fit record mismatch"
                )
            summary = record.get("target_summary")
            if not isinstance(summary, Mapping):
                raise ValueError(
                    "EXP-049 regressor target summary missing"
                )
            _validate_target_summary(
                summary,
                expected_row_count=row_count,
                field=(
                    f"EXP-049 {regime_name} {target}"
                ),
            )
            _validate_sha256(
                record.get("preprocessor_fingerprint"),
                field=(
                    f"EXP-049 {regime_name} {target} "
                    "preprocessor fingerprint"
                ),
            )
            _validate_sha256(
                record.get("model_fingerprint"),
                field=(
                    f"EXP-049 {regime_name} {target} "
                    "model fingerprint"
                ),
            )
            verified_regressors += 1

    if fit.get("full_fit_single_model") != {
        "status": "FORBIDDEN_BY_DEC132",
        "fit_attempt_count": 0,
    }:
        raise ValueError(
            "EXP-049 full-fit fallback record mismatch"
        )
    if fit.get("hist_gradient_boosting_classifier") != {
        "status": "EXCLUDED_BY_DEC132",
        "fit_attempt_count": 0,
    }:
        raise ValueError(
            "EXP-049 classifier fallback record mismatch"
        )
    if fit.get("logistic_regression") != {
        "status": "EXCLUDED_BY_DEC112_DEC132",
        "fit_attempt_count": 0,
    }:
        raise ValueError(
            "EXP-049 logistic fallback record mismatch"
        )

    return verified_regressors


def _validate_consensus_block(
    block: Mapping[str, object],
    *,
    expected_row_count: int,
    field: str,
) -> int:
    if block.get("row_count") != expected_row_count:
        raise ValueError(
            f"{field} consensus row count mismatch"
        )

    counts = block.get("consensus_direction_counts")
    expected_names = {"LONG", "SHORT", "NO_TRADE"}
    if (
        not isinstance(counts, Mapping)
        or set(counts) != expected_names
    ):
        raise ValueError(
            f"{field} consensus direction counts are malformed"
        )
    normalized: dict[str, int] = {}
    for name in sorted(expected_names):
        value = counts.get(name)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            raise ValueError(
                f"{field} consensus count is invalid"
            )
        normalized[name] = value
    if sum(normalized.values()) != expected_row_count:
        raise ValueError(
            f"{field} consensus count total mismatch"
        )

    eligible = normalized["LONG"] + normalized["SHORT"]
    if block.get("consensus_eligible_row_count") != eligible:
        raise ValueError(
            f"{field} consensus eligible count mismatch"
        )
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
        raise ValueError(
            f"{field} consensus eligible rate mismatch"
        )

    minimum = block.get("minimum_robust_utility")
    maximum = block.get("maximum_robust_utility")
    if eligible == 0:
        if minimum is not None or maximum is not None:
            raise ValueError(
                f"{field} empty utility bounds mismatch"
            )
    else:
        for name, value in (
            ("minimum", minimum),
            ("maximum", maximum),
        ):
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
        str(window["name"])
        for window in FIT_REGIME_WINDOWS
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
            or set(target_digests)
            != set(FINANCIAL_TARGET_COLUMNS)
        ):
            raise ValueError(
                f"{field} target prediction digest set mismatch"
            )
        for target in FINANCIAL_TARGET_COLUMNS:
            _validate_sha256(
                target_digests.get(target),
                field=(
                    f"{field} {regime_name} {target} "
                    "prediction digest"
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
        raise ValueError(
            "EXP-049 stability window row count is invalid"
        )

    metrics = window.get("metrics")
    gate = window.get("gate")
    if not isinstance(metrics, Mapping):
        raise ValueError(
            "EXP-049 stability window metrics are malformed"
        )
    if not isinstance(gate, Mapping):
        raise ValueError(
            "EXP-049 stability window gate is malformed"
        )

    candidate_count = metrics.get(
        "directional_candidate_count"
    )
    if (
        not isinstance(candidate_count, int)
        or isinstance(candidate_count, bool)
        or candidate_count < 0
    ):
        raise ValueError(
            "EXP-049 stability candidate count is invalid"
        )
    if full_selection_candidate_count <= 0:
        raise ValueError(
            "EXP-049 stability denominator must be positive"
        )

    expected_share = (
        candidate_count / full_selection_candidate_count
    )
    supplied_share = gate.get(
        "directional_candidate_share"
    )
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
        raise ValueError(
            "EXP-049 stability candidate-share mismatch"
        )

    total = metrics.get("total_net_pips")
    mean = metrics.get("mean_net_pips")
    gross_positive = metrics.get("gross_positive_pips")
    gross_negative = metrics.get(
        "absolute_gross_negative_pips"
    )
    for field, value in (
        ("total_net_pips", total),
        ("gross_positive_pips", gross_positive),
        (
            "absolute_gross_negative_pips",
            gross_negative,
        ),
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise ValueError(
                f"EXP-049 stability {field} is invalid"
            )
    if mean is not None and (
        not isinstance(mean, (int, float))
        or isinstance(mean, bool)
        or not math.isfinite(float(mean))
    ):
        raise ValueError(
            "EXP-049 stability mean_net_pips is invalid"
        )

    expected_criteria = {
        "directional_candidate_share>=0.10": (
            expected_share
            >= MIN_STABILITY_WINDOW_CANDIDATE_SHARE
        ),
        "total_net_pips>0": float(total) > 0.0,
        "mean_net_pips>0": (
            mean is not None and float(mean) > 0.0
        ),
        "gross_positive_pips>absolute_gross_negative_pips": (
            float(gross_positive)
            > float(gross_negative)
        ),
    }
    if gate.get("criteria") != expected_criteria:
        raise ValueError(
            "EXP-049 stability window criteria mismatch"
        )
    passed = all(expected_criteria.values())
    if gate.get("passed") is not passed:
        raise ValueError(
            "EXP-049 stability window pass mismatch"
        )
    return passed


def _validate_variant(
    raw: Mapping[str, object],
    *,
    expected_eligible_count: int,
) -> tuple[bool, bool, bool]:
    budget = raw.get("candidate_budget_anchor")
    if budget not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError(
            "EXP-049 utility budget identity mismatch"
        )
    if (
        raw.get("model_family")
        != "hist_gradient_boosting_regression"
    ):
        raise ValueError(
            "EXP-049 utility variant must be HGB regression"
        )

    eligible = raw.get("eligible_utility_row_count")
    if eligible != expected_eligible_count:
        raise ValueError(
            "EXP-049 variant utility eligible count mismatch"
        )

    evaluation = raw.get("evaluation_status")
    if evaluation == "BUDGET_UNAVAILABLE":
        if raw.get("status") != (
            "UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS"
        ):
            raise ValueError(
                "EXP-049 unavailable utility status mismatch"
            )
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
        if raw.get(
            "aggregate_selection_gate_passed"
        ) is not False:
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

    if evaluation != "EVALUATED":
        raise ValueError(
            "EXP-049 utility variant evaluation status mismatch"
        )
    if raw.get("status") != "AVAILABLE":
        raise ValueError(
            "EXP-049 available utility status mismatch"
        )
    if (
        not isinstance(eligible, int)
        or isinstance(eligible, bool)
        or eligible < int(budget)
    ):
        raise ValueError(
            "EXP-049 eligible utility row count is invalid"
        )

    selected_at_cutoff = raw.get(
        "selection_candidate_count_at_cutoff"
    )
    cutoff = raw.get("selection_derived_cutoff")
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
        raise ValueError(
            "EXP-049 utility cutoff is invalid"
        )

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
        raise ValueError(
            "EXP-049 selection scenario is malformed"
        )
    metrics = scenario.get("metrics")
    gate = scenario.get("gate")
    if not isinstance(metrics, Mapping) or not isinstance(
        gate,
        Mapping,
    ):
        raise ValueError(
            "EXP-049 selection financial evidence malformed"
        )
    aggregate_passed = _validate_financial_gate(
        metrics=metrics,
        gate=gate,
        field="EXP-049 selection 0.5",
    )
    if (
        raw.get("aggregate_selection_gate_passed")
        is not aggregate_passed
    ):
        raise ValueError(
            "EXP-049 aggregate selection flag mismatch"
        )

    stability = raw.get("temporal_stability")
    if not isinstance(stability, Mapping):
        raise ValueError(
            "EXP-049 temporal stability evidence malformed"
        )
    if (
        stability.get(
            "minimum_directional_candidate_share_per_window"
        )
        != MIN_STABILITY_WINDOW_CANDIDATE_SHARE
    ):
        raise ValueError(
            "EXP-049 stability share floor mismatch"
        )

    stability_passed = False
    if aggregate_passed:
        windows = stability.get("windows")
        if (
            not isinstance(windows, list)
            or len(windows)
            != len(TEMPORAL_STABILITY_WINDOWS)
        ):
            raise ValueError(
                "EXP-049 stability window inventory mismatch"
            )
        full_count = metrics.get(
            "directional_candidate_count"
        )
        if not isinstance(full_count, int):
            raise ValueError(
                "EXP-049 aggregate candidate count invalid"
            )
        window_passes = [
            _validate_window(
                supplied,
                expected=dict(expected),
                full_selection_candidate_count=full_count,
            )
            for supplied, expected in zip(
                windows,
                TEMPORAL_STABILITY_WINDOWS,
                strict=True,
            )
        ]
        stability_passed = all(window_passes)
        expected_status = (
            "PASS" if stability_passed else "REJECT"
        )
        if stability.get("status") != expected_status:
            raise ValueError(
                "EXP-049 stability status mismatch"
            )
    else:
        if (
            stability.get("status")
            != "LOCKED_AGGREGATE_REJECT"
            or stability.get("windows") != []
        ):
            raise ValueError(
                "EXP-049 aggregate reject stability lock mismatch"
            )

    final_pass = aggregate_passed and stability_passed
    if raw.get("selection_gate_passed") is not final_pass:
        raise ValueError(
            "EXP-049 final selection flag mismatch"
        )
    return aggregate_passed, final_pass, False


def _validate_forward_block(
    block: Mapping[str, object],
    *,
    expected_row_count: int,
    field: str,
    gate_scenarios: Sequence[float],
) -> None:
    if block.get("status") not in {"PASS", "REJECT"}:
        raise ValueError(
            f"{field} status is invalid"
        )
    if block.get("row_count") != expected_row_count:
        raise ValueError(
            f"{field} row count mismatch"
        )
    consensus = block.get("regime_utility_consensus")
    if not isinstance(consensus, Mapping):
        raise ValueError(
            f"{field} utility consensus is malformed"
        )
    _validate_consensus_block(
        consensus,
        expected_row_count=expected_row_count,
        field=field,
    )
    _validate_sha256(
        block.get("regime_utility_consensus_digest"),
        field=f"{field} utility consensus digest",
    )

    budget = block.get("candidate_budget_anchor")
    if budget not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError(
            f"{field} candidate budget mismatch"
        )
    cutoff = block.get("selection_derived_cutoff")
    if (
        not isinstance(cutoff, (int, float))
        or isinstance(cutoff, bool)
        or not math.isfinite(float(cutoff))
        or float(cutoff) <= 0.0
    ):
        raise ValueError(
            f"{field} utility cutoff is invalid"
        )

    expected_scenarios = {
        str(float(value))
        for value in (
            *DIAGNOSTIC_SCENARIOS,
            *gate_scenarios,
        )
    }
    scenarios = block.get("scenarios")
    if (
        not isinstance(scenarios, Mapping)
        or set(scenarios) != expected_scenarios
    ):
        raise ValueError(
            f"{field} scenario inventory mismatch"
        )

    gate_results: dict[str, bool] = {}
    for name, scenario in scenarios.items():
        if not isinstance(scenario, Mapping):
            raise ValueError(
                f"{field} scenario record malformed"
            )
        metrics = scenario.get("metrics")
        gate = scenario.get("gate")
        if (
            not isinstance(metrics, Mapping)
            or not isinstance(gate, Mapping)
        ):
            raise ValueError(
                f"{field} financial evidence malformed"
            )
        gate_results[str(name)] = _validate_financial_gate(
            metrics=metrics,
            gate=gate,
            field=f"{field} {name}",
        )

    expected_pass = all(
        gate_results[str(float(value))]
        for value in gate_scenarios
    )
    if block.get("status") != (
        "PASS" if expected_pass else "REJECT"
    ):
        raise ValueError(
            f"{field} status/gate mismatch"
        )


def _validate_cell_result(
    raw: Mapping[str, object],
) -> dict[str, object]:
    if raw.get("experiment_id") != REGIME_UTILITY_EXPERIMENT_ID:
        raise ValueError(
            "EXP-049 cell experiment identity mismatch"
        )
    if raw.get(
        "training_core_version"
    ) != REGIME_UTILITY_TRAINING_CORE_VERSION:
        raise ValueError(
            "EXP-049 training core version mismatch"
        )
    if raw.get(
        "training_core_decision"
    ) != REGIME_UTILITY_TRAINING_CORE_DECISION:
        raise ValueError(
            "EXP-049 training core decision mismatch"
        )
    if raw.get("dec132_merged_commit") != DEC132_MERGED_COMMIT:
        raise ValueError(
            "EXP-049 DEC-132 merge identity mismatch"
        )
    if (
        raw.get("dec132_protocol_blob_sha")
        != DEC132_PROTOCOL_BLOB_SHA
    ):
        raise ValueError(
            "EXP-049 protocol blob identity mismatch"
        )
    if (
        raw.get("base_training_core_blob_sha")
        != BASE_TRAINING_CORE_BLOB_SHA
    ):
        raise ValueError(
            "EXP-049 base training blob mismatch"
        )
    if (
        raw.get("density_helper_core_blob_sha")
        != DENSITY_HELPER_CORE_BLOB_SHA
    ):
        raise ValueError(
            "EXP-049 density helper blob mismatch"
        )
    if raw.get(
        "protocol_decision"
    ) != REGIME_UTILITY_PROTOCOL_DECISION:
        raise ValueError(
            "EXP-049 protocol decision mismatch"
        )
    if raw.get(
        "protocol_version"
    ) != REGIME_UTILITY_PROTOCOL_VERSION:
        raise ValueError(
            "EXP-049 protocol version mismatch"
        )
    if raw.get(
        "protocol_fingerprint"
    ) != regime_utility_protocol_fingerprint():
        raise ValueError(
            "EXP-049 protocol fingerprint mismatch"
        )
    if raw.get("prior_result_informed") is not PRIOR_RESULT_INFORMED:
        raise ValueError(
            "EXP-049 prior-result flag mismatch"
        )
    if raw.get("evidence_label") != EVIDENCE_LABEL:
        raise ValueError(
            "EXP-049 evidence label mismatch"
        )
    if raw.get("untouched_oos") is not UNTOUCHED_OOS:
        raise ValueError(
            "EXP-049 untouched-OOS flag mismatch"
        )

    cell = raw.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError(
            "EXP-049 cell identity is malformed"
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
            "EXP-049 cell identity is unsupported"
        )

    _validate_sha256(
        raw.get("processed_manifest_sha256"),
        field="EXP-049 processed manifest sha256",
    )

    joined_row_count = raw.get("joined_row_count")
    if (
        not isinstance(joined_row_count, int)
        or isinstance(joined_row_count, bool)
        or joined_row_count <= 0
    ):
        raise ValueError(
            "EXP-049 joined row count is invalid"
        )
    split_counts = raw.get("split_row_counts")
    required_splits = {
        "fit",
        "selection",
        "validation",
        "retrospective_holdout",
    }
    if (
        not isinstance(split_counts, Mapping)
        or set(split_counts) != required_splits
    ):
        raise ValueError(
            "EXP-049 split row inventory mismatch"
        )
    for name in sorted(required_splits):
        value = split_counts.get(name)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value <= 0
        ):
            raise ValueError(
                "EXP-049 split row count is invalid"
            )

    fit = raw.get("fit")
    if not isinstance(fit, Mapping):
        raise ValueError(
            "EXP-049 fit evidence is malformed"
        )
    verified_regressors = _validate_fit_block(fit)

    selection = raw.get("selection")
    validation = raw.get("validation")
    holdout = raw.get("retrospective_holdout")
    if (
        not isinstance(selection, Mapping)
        or not isinstance(validation, Mapping)
        or not isinstance(holdout, Mapping)
    ):
        raise ValueError(
            "EXP-049 result stage evidence is malformed"
        )

    selection_row_count = selection.get("row_count")
    if selection_row_count != split_counts["selection"]:
        raise ValueError(
            "EXP-049 selection row count mismatch"
        )
    consensus = selection.get(
        "regime_utility_consensus"
    )
    if not isinstance(consensus, Mapping):
        raise ValueError(
            "EXP-049 selection utility consensus malformed"
        )
    eligible_count = _validate_consensus_block(
        consensus,
        expected_row_count=int(selection_row_count),
        field="EXP-049 selection",
    )
    _validate_sha256(
        selection.get("regime_utility_consensus_digest"),
        field="EXP-049 selection consensus digest",
    )

    variants = selection.get("variants")
    if (
        not isinstance(variants, list)
        or len(variants) != len(CANDIDATE_BUDGET_ANCHORS)
    ):
        raise ValueError(
            "EXP-049 selection variant inventory mismatch"
        )
    if {
        item.get("candidate_budget_anchor")
        for item in variants
        if isinstance(item, Mapping)
    } != set(CANDIDATE_BUDGET_ANCHORS):
        raise ValueError(
            "EXP-049 selection budget coverage mismatch"
        )

    aggregate_pass_count = 0
    stable_pass_count = 0
    unavailable_count = 0
    stable_variants: list[Mapping[str, object]] = []
    for item in variants:
        if not isinstance(item, Mapping):
            raise ValueError(
                "EXP-049 selection variant is malformed"
            )
        aggregate_passed, stable_passed, unavailable = (
            _validate_variant(
                item,
                expected_eligible_count=eligible_count,
            )
        )
        aggregate_pass_count += int(aggregate_passed)
        stable_pass_count += int(stable_passed)
        unavailable_count += int(unavailable)
        if stable_passed:
            stable_variants.append(item)

    selection_status = selection.get("status")
    selected_variant = selection.get("selected_variant")
    if (
        selection_status
        == "NO_REGIME_UTILITY_STABLE_MODEL_CHALLENGER"
    ):
        if stable_variants:
            raise ValueError(
                "EXP-049 no-challenger status hides stable variant"
            )
        if selected_variant is not None:
            raise ValueError(
                "EXP-049 no-challenger cannot select variant"
            )
    elif selection_status == "SELECTED":
        if not stable_variants:
            raise ValueError(
                "EXP-049 selected status has no stable variant"
            )
        if not isinstance(selected_variant, Mapping):
            raise ValueError(
                "EXP-049 selected variant record missing"
            )
        family = selected_variant.get("model_family")
        budget = selected_variant.get(
            "candidate_budget_anchor"
        )
        cutoff = selected_variant.get(
            "selection_derived_cutoff"
        )
        if (
            family != "hist_gradient_boosting_regression"
            or budget not in CANDIDATE_BUDGET_ANCHORS
            or not isinstance(cutoff, (int, float))
            or isinstance(cutoff, bool)
            or not math.isfinite(float(cutoff))
            or float(cutoff) <= 0.0
        ):
            raise ValueError(
                "EXP-049 selected variant identity mismatch"
            )
        matches = [
            item
            for item in stable_variants
            if item.get("candidate_budget_anchor") == budget
            and math.isclose(
                float(item.get("selection_derived_cutoff")),
                float(cutoff),
                rel_tol=0.0,
                abs_tol=0.0,
            )
        ]
        if len(matches) != 1:
            raise ValueError(
                "EXP-049 selected variant is not a unique stable variant"
            )
    else:
        raise ValueError(
            "EXP-049 selection status is invalid"
        )

    validation_status = validation.get("status")
    holdout_status = holdout.get("status")
    _validate_status_chain(
        selection=selection_status,
        validation=validation_status,
        holdout=holdout_status,
    )

    if selection_status == "SELECTED":
        if validation_status in {"PASS", "REJECT"}:
            _validate_forward_block(
                validation,
                expected_row_count=int(
                    split_counts["validation"]
                ),
                field="EXP-049 validation",
                gate_scenarios=VALIDATION_GATE_SCENARIOS,
            )
        if holdout_status in {"PASS", "REJECT"}:
            _validate_forward_block(
                holdout,
                expected_row_count=int(
                    split_counts["retrospective_holdout"]
                ),
                field="EXP-049 retrospective holdout",
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
                f"EXP-049 {field} must remain false"
            )

    supplied_fingerprint = _validate_sha256(
        raw.get("result_fingerprint"),
        field="EXP-049 cell result fingerprint",
    )
    expected_fingerprint = _sha256(
        _canonical_json(
            {
                key: value
                for key, value in raw.items()
                if key != "result_fingerprint"
            }
        )
    )
    if supplied_fingerprint != expected_fingerprint:
        raise ValueError(
            "EXP-049 cell result fingerprint mismatch"
        )

    return {
        "identity": identity,
        "selection_status": selection_status,
        "validation_status": validation_status,
        "holdout_status": holdout_status,
        "aggregate_selection_pass_variant_count": (
            aggregate_pass_count
        ),
        "stable_selection_pass_variant_count": (
            stable_pass_count
        ),
        "unavailable_budget_variant_count": unavailable_count,
        "utility_eligible_selection_row_count": eligible_count,
        "verified_regressor_count": verified_regressors,
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
        "no_regime_utility_stable_model_challenger_count": sum(
            item["selection_status"]
            == "NO_REGIME_UTILITY_STABLE_MODEL_CHALLENGER"
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
            int(item["unavailable_budget_variant_count"])
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
        "validation_pass_cell_count": sum(
            item["validation_status"] == "PASS"
            for item in validated
        ),
        "holdout_pass_cell_count": sum(
            item["holdout_status"] == "PASS"
            for item in validated
        ),
    }


def compile_regime_utility_model_result_evidence(
    cell_results: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    commit = _validate_commit(
        code_commit,
        field="EXP-049 code commit",
    )
    expected_identities = {
        (
            cell.symbol,
            cell.timeframe,
            cell.horizon_minutes,
        )
        for cell in MODEL_CELLS
    }
    supplied_identities: list[
        tuple[object, object, object]
    ] = []
    for row in cell_results:
        cell = row.get("cell")
        if not isinstance(cell, Mapping):
            raise ValueError(
                "EXP-049 cell result identity is malformed"
            )
        supplied_identities.append(
            (
                cell.get("symbol"),
                cell.get("timeframe"),
                cell.get("horizon_minutes"),
            )
        )
    if (
        len(cell_results) != len(MODEL_CELLS)
        or len(set(supplied_identities))
        != len(supplied_identities)
        or set(supplied_identities)
        != expected_identities
    ):
        raise ValueError(
            "EXP-049 model-result cell evidence is incomplete"
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
            REGIME_UTILITY_MODEL_RESULT_EVIDENCE_VERSION
        ),
        "artifact_runner_version": (
            REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "artifact_runner_decision": (
            REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "experiment_id": REGIME_UTILITY_EXPERIMENT_ID,
        "code_commit": commit,
        "dec132_merged_commit": DEC132_MERGED_COMMIT,
        "dec133_merged_commit": DEC133_MERGED_COMMIT,
        "dec132_protocol_blob_sha": (
            DEC132_PROTOCOL_BLOB_SHA
        ),
        "dec133_training_core_blob_sha": (
            DEC133_TRAINING_CORE_BLOB_SHA
        ),
        "legacy_data_loader_blob_sha": (
            LEGACY_DATA_LOADER_BLOB_SHA
        ),
        "base_training_core_blob_sha": (
            BASE_TRAINING_CORE_BLOB_SHA
        ),
        "density_helper_core_blob_sha": (
            DENSITY_HELPER_CORE_BLOB_SHA
        ),
        "protocol_decision": (
            REGIME_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            REGIME_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            regime_utility_protocol_fingerprint()
        ),
        "training_core_version": (
            REGIME_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            REGIME_UTILITY_TRAINING_CORE_DECISION
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


def validate_regime_utility_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    expected_commit = _validate_commit(
        expected_code_commit,
        field="EXP-049 expected code commit",
    )
    if evidence.get("evidence_version") != (
        REGIME_UTILITY_MODEL_RESULT_EVIDENCE_VERSION
    ):
        raise ValueError(
            "EXP-049 model-result evidence version mismatch"
        )
    if evidence.get("artifact_runner_version") != (
        REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
    ):
        raise ValueError(
            "EXP-049 artifact runner version mismatch"
        )
    if evidence.get("artifact_runner_decision") != (
        REGIME_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
    ):
        raise ValueError(
            "EXP-049 artifact runner decision mismatch"
        )
    if evidence.get("experiment_id") != (
        REGIME_UTILITY_EXPERIMENT_ID
    ):
        raise ValueError(
            "EXP-049 evidence experiment identity mismatch"
        )
    if evidence.get("code_commit") != expected_commit:
        raise ValueError(
            "EXP-049 evidence code commit mismatch"
        )
    for field, expected in (
        ("dec132_merged_commit", DEC132_MERGED_COMMIT),
        ("dec133_merged_commit", DEC133_MERGED_COMMIT),
        (
            "dec132_protocol_blob_sha",
            DEC132_PROTOCOL_BLOB_SHA,
        ),
        (
            "dec133_training_core_blob_sha",
            DEC133_TRAINING_CORE_BLOB_SHA,
        ),
        (
            "legacy_data_loader_blob_sha",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        (
            "base_training_core_blob_sha",
            BASE_TRAINING_CORE_BLOB_SHA,
        ),
        (
            "density_helper_core_blob_sha",
            DENSITY_HELPER_CORE_BLOB_SHA,
        ),
        (
            "protocol_decision",
            REGIME_UTILITY_PROTOCOL_DECISION,
        ),
        (
            "protocol_version",
            REGIME_UTILITY_PROTOCOL_VERSION,
        ),
        (
            "protocol_fingerprint",
            regime_utility_protocol_fingerprint(),
        ),
        (
            "training_core_version",
            REGIME_UTILITY_TRAINING_CORE_VERSION,
        ),
        (
            "training_core_decision",
            REGIME_UTILITY_TRAINING_CORE_DECISION,
        ),
        ("evidence_label", EVIDENCE_LABEL),
        ("prior_result_informed", PRIOR_RESULT_INFORMED),
        ("untouched_oos", UNTOUCHED_OOS),
    ):
        if evidence.get(field) != expected:
            raise ValueError(
                f"EXP-049 evidence {field} mismatch"
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
            "EXP-049 authoritative source identity mismatch"
        )

    cells = evidence.get("cells")
    if not isinstance(cells, list):
        raise ValueError(
            "EXP-049 evidence cells must be a list"
        )
    if evidence.get("cell_count") != len(MODEL_CELLS):
        raise ValueError(
            "EXP-049 evidence cell count mismatch"
        )
    expected_identities = {
        (
            cell.symbol,
            cell.timeframe,
            cell.horizon_minutes,
        )
        for cell in MODEL_CELLS
    }
    supplied_identities: list[
        tuple[object, object, object]
    ] = []
    for row in cells:
        if not isinstance(row, Mapping):
            raise ValueError(
                "EXP-049 evidence cell is malformed"
            )
        cell = row.get("cell")
        if not isinstance(cell, Mapping):
            raise ValueError(
                "EXP-049 evidence cell identity malformed"
            )
        supplied_identities.append(
            (
                cell.get("symbol"),
                cell.get("timeframe"),
                cell.get("horizon_minutes"),
            )
        )
    if (
        len(cells) != len(MODEL_CELLS)
        or len(set(supplied_identities))
        != len(supplied_identities)
        or set(supplied_identities)
        != expected_identities
    ):
        raise ValueError(
            "EXP-049 model-result cell evidence is incomplete"
        )

    summary = _compile_summary(cells)
    if evidence.get("summary") != summary:
        raise ValueError(
            "EXP-049 evidence summary mismatch"
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
                f"EXP-049 evidence {field} must remain false"
            )

    supplied_fingerprint = _validate_sha256(
        evidence.get("evidence_fingerprint"),
        field="EXP-049 evidence fingerprint",
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
        raise ValueError(
            "EXP-049 evidence fingerprint mismatch"
        )

    return {
        "regime_utility_model_result_evidence_verified": True,
        **summary,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
        "evidence_fingerprint": supplied_fingerprint,
    }


def run_authoritative_regime_utility_model_bundle(
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
        AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "DEC-134 source is non-executable for authoritative "
            "EXP-049 model fitting"
        )

    validate_regime_utility_artifact_runner_sources(
        repository_root=repository_root,
    )
    indexed = validate_authoritative_readiness(readiness)
    cell_results: list[dict[str, object]] = []
    for cell in MODEL_CELLS:
        identity = (cell.symbol, cell.timeframe)
        if identity not in indexed:
            raise ValueError(
                f"missing authoritative EXP-049 source cell: {identity}"
            )
        if (
            identity not in feature_roots
            or identity not in outcome_roots
        ):
            raise ValueError(
                f"missing extracted EXP-049 artifact root: {identity}"
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
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    payload = json.dumps(
        dict(evidence),
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"
    if (
        destination.exists()
        and destination.read_text(encoding="utf-8")
        != payload
    ):
        raise ValueError(
            "conflicting existing EXP-049 model-result evidence"
        )
    destination.write_text(
        payload,
        encoding="utf-8",
    )


def load_regime_utility_model_result_evidence(
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
