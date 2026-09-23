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
    CONFIDENCE_THRESHOLDS,
    MODEL_CELLS,
    MODEL_FAMILIES,
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
from .model_successor_stability_training import (
    DEC104_MERGED_COMMIT,
    DEC104_PROTOCOL_BLOB_SHA,
    STABILITY_TRAINING_CORE_DECISION,
    STABILITY_TRAINING_CORE_VERSION,
    run_stability_model_cell_core,
)


STABILITY_MODEL_ARTIFACT_RUNNER_VERSION = (
    "fmp-exp046-stability-artifact-runner-v1"
)
STABILITY_MODEL_ARTIFACT_RUNNER_DECISION = "DEC-106"
STABILITY_MODEL_RESULT_EVIDENCE_VERSION = 1

DEC105_MERGED_COMMIT = (
    "7aa3d86f6c1fce61dd7e35d9ba9830b1fa7355b5"
)
DEC105_TRAINING_CORE_BLOB_SHA = (
    "6733d3c530fba944b9ea0c62783ed2110552e532"
)
LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)

AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = False
STABILITY_MODEL_FIT_AUTHORIZED = False
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


def validate_stability_artifact_runner_sources(
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
        "dec104_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_stability_protocol.py",
            DEC104_PROTOCOL_BLOB_SHA,
        ),
        "dec105_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_stability_training.py",
            DEC105_TRAINING_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-046 artifact dependency: {path}"
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
        "stability_model_artifact_runner_version": (
            STABILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "stability_model_artifact_runner_decision": (
            STABILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "dec104_merged_commit": DEC104_MERGED_COMMIT,
        "dec105_merged_commit": DEC105_MERGED_COMMIT,
        "legacy_data_loader_blob_sha": actual[
            "legacy_data_loader"
        ],
        "dec104_protocol_blob_sha": actual[
            "dec104_protocol"
        ],
        "dec105_training_core_blob_sha": actual[
            "dec105_training_core"
        ],
        "stability_protocol_fingerprint": (
            protocol_fingerprint
        ),
        "authoritative_stability_model_result_execution_authorized": False,
        "stability_model_fit_authorized": False,
        "promotion_authorized": False,
        "trading_authorized": False,
    }


def _validate_status_chain(
    *,
    selection: object,
    validation: object,
    holdout: object,
) -> None:
    if selection == "NO_MODEL_FAMILY_AVAILABLE":
        if validation != "LOCKED_NO_MODEL_FAMILY":
            raise ValueError(
                "EXP-046 no-family cell must keep validation locked"
            )
        if holdout != "LOCKED_NO_MODEL_FAMILY":
            raise ValueError(
                "EXP-046 no-family cell must keep holdout locked"
            )
        return

    if selection == "NO_STABLE_MODEL_CHALLENGER":
        if validation != "LOCKED_NO_SELECTION":
            raise ValueError(
                "EXP-046 no-stable-challenger validation must be locked"
            )
        if holdout != "LOCKED_NO_SELECTION":
            raise ValueError(
                "EXP-046 no-stable-challenger holdout must be locked"
            )
        return

    if selection != "SELECTED":
        raise ValueError(
            f"unexpected EXP-046 selection status: {selection!r}"
        )

    if validation == "REJECT":
        if holdout != "LOCKED_VALIDATION_REJECT":
            raise ValueError(
                "EXP-046 rejected validation must keep holdout locked"
            )
        return

    if validation == "PASS":
        if holdout not in {"PASS", "REJECT"}:
            raise ValueError(
                "EXP-046 passed validation must produce holdout result"
            )
        return

    raise ValueError(
        f"unexpected EXP-046 validation status: {validation!r}"
    )


def _validate_window(
    window: Mapping[str, object],
    *,
    expected: Mapping[str, object],
    full_selection_candidate_count: int,
) -> bool:
    for field in ("name", "start", "end_exclusive"):
        if window.get(field) != expected[field]:
            raise ValueError(
                f"EXP-046 stability window {field} mismatch"
            )

    row_count = window.get("row_count")
    if (
        not isinstance(row_count, int)
        or isinstance(row_count, bool)
        or row_count <= 0
    ):
        raise ValueError(
            "EXP-046 stability window row count is invalid"
        )

    metrics = window.get("metrics")
    gate = window.get("gate")
    if not isinstance(metrics, Mapping):
        raise ValueError(
            "EXP-046 stability window metrics are malformed"
        )
    if not isinstance(gate, Mapping):
        raise ValueError(
            "EXP-046 stability window gate is malformed"
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
            "EXP-046 stability candidate count is invalid"
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
            "EXP-046 stability candidate-share mismatch"
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
        ("absolute_gross_negative_pips", gross_negative),
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise ValueError(
                f"EXP-046 stability {field} is invalid"
            )
    if mean is not None and (
        not isinstance(mean, (int, float))
        or isinstance(mean, bool)
        or not math.isfinite(float(mean))
    ):
        raise ValueError(
            "EXP-046 stability mean_net_pips is invalid"
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
    criteria = gate.get("criteria")
    if criteria != expected_criteria:
        raise ValueError(
            "EXP-046 stability window criteria mismatch"
        )
    expected_passed = all(expected_criteria.values())
    if gate.get("passed") is not expected_passed:
        raise ValueError(
            "EXP-046 stability window pass mismatch"
        )
    return expected_passed


def _validate_fitted_variant(
    raw: Mapping[str, object],
) -> tuple[bool, bool]:
    if raw.get("evaluation_status") != "EVALUATED":
        raise ValueError(
            "EXP-046 fitted-family variant must be evaluated"
        )
    aggregate = raw.get(
        "aggregate_selection_gate_passed"
    )
    final = raw.get("selection_gate_passed")
    if not isinstance(aggregate, bool):
        raise ValueError(
            "EXP-046 aggregate gate status is malformed"
        )
    if not isinstance(final, bool):
        raise ValueError(
            "EXP-046 final gate status is malformed"
        )

    scenarios = raw.get("scenarios")
    if not isinstance(scenarios, Mapping):
        raise ValueError(
            "EXP-046 variant scenarios are malformed"
        )
    scenario = scenarios.get("0.5")
    if not isinstance(scenario, Mapping):
        raise ValueError(
            "EXP-046 variant is missing 0.5 scenario"
        )
    scenario_gate = scenario.get("gate")
    scenario_metrics = scenario.get("metrics")
    if (
        not isinstance(scenario_gate, Mapping)
        or not isinstance(scenario_metrics, Mapping)
    ):
        raise ValueError(
            "EXP-046 aggregate scenario evidence is malformed"
        )
    if scenario_gate.get("passed") is not aggregate:
        raise ValueError(
            "EXP-046 aggregate gate evidence mismatch"
        )

    full_count = scenario_metrics.get(
        "directional_candidate_count"
    )
    if (
        not isinstance(full_count, int)
        or isinstance(full_count, bool)
        or full_count < 0
    ):
        raise ValueError(
            "EXP-046 aggregate candidate count is invalid"
        )

    stability = raw.get("temporal_stability")
    if not isinstance(stability, Mapping):
        raise ValueError(
            "EXP-046 temporal-stability block is malformed"
        )
    if stability.get(
        "minimum_directional_candidate_share_per_window"
    ) != MIN_STABILITY_WINDOW_CANDIDATE_SHARE:
        raise ValueError(
            "EXP-046 stability share threshold mismatch"
        )

    if not aggregate:
        if stability.get("status") != "LOCKED_AGGREGATE_REJECT":
            raise ValueError(
                "EXP-046 aggregate reject must lock stability"
            )
        if stability.get("windows") != []:
            raise ValueError(
                "EXP-046 aggregate reject cannot contain windows"
            )
        if final is not False:
            raise ValueError(
                "EXP-046 aggregate reject cannot pass final gate"
            )
        return False, False

    if full_count <= 0:
        raise ValueError(
            "EXP-046 aggregate pass requires candidates"
        )

    windows = stability.get("windows")
    if not isinstance(windows, list) or len(windows) != 4:
        raise ValueError(
            "EXP-046 aggregate pass requires four stability windows"
        )

    expected_windows = [
        dict(window)
        for window in TEMPORAL_STABILITY_WINDOWS
    ]
    window_passes: list[bool] = []
    for window, expected in zip(
        windows,
        expected_windows,
        strict=True,
    ):
        if not isinstance(window, Mapping):
            raise ValueError(
                "EXP-046 stability window row is malformed"
            )
        window_passes.append(
            _validate_window(
                window,
                expected=expected,
                full_selection_candidate_count=full_count,
            )
        )

    expected_status = (
        "PASS" if all(window_passes) else "REJECT"
    )
    if stability.get("status") != expected_status:
        raise ValueError(
            "EXP-046 stability status mismatch"
        )
    expected_final = expected_status == "PASS"
    if final is not expected_final:
        raise ValueError(
            "EXP-046 final selection-gate mismatch"
        )
    return True, expected_final


def _validate_stability_cell_result(
    result: Mapping[str, object],
) -> dict[str, object]:
    cell = result.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError(
            "EXP-046 model result is missing cell identity"
        )
    horizon = cell.get("horizon_minutes")
    if (
        not isinstance(horizon, int)
        or isinstance(horizon, bool)
    ):
        raise ValueError(
            "EXP-046 model result horizon is malformed"
        )
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
        raise ValueError(
            f"unexpected EXP-046 model result cell: {identity}"
        )

    exact = {
        "experiment_id": STABILITY_SUCCESSOR_EXPERIMENT_ID,
        "training_core_version": (
            STABILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            STABILITY_TRAINING_CORE_DECISION
        ),
        "dec104_merged_commit": DEC104_MERGED_COMMIT,
        "dec104_protocol_blob_sha": DEC104_PROTOCOL_BLOB_SHA,
        "protocol_decision": STABILITY_PROTOCOL_DECISION,
        "protocol_version": STABILITY_PROTOCOL_VERSION,
        "protocol_fingerprint": (
            stability_protocol_fingerprint()
        ),
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
            raise ValueError(
                f"EXP-046 model result {field} mismatch"
            )

    fit = result.get("fit")
    if not isinstance(fit, Mapping):
        raise ValueError(
            "EXP-046 model result fit block is malformed"
        )
    families = fit.get("families")
    if (
        not isinstance(families, Mapping)
        or set(families) != set(MODEL_FAMILIES)
    ):
        raise ValueError(
            "EXP-046 model result family set mismatch"
        )

    for family in MODEL_FAMILIES:
        raw = families[family]
        if not isinstance(raw, Mapping):
            raise ValueError(
                f"EXP-046 {family} fit record is malformed"
            )
        status = raw.get("status")
        if status == "FITTED":
            _validate_sha256(
                raw.get("preprocessor_fingerprint"),
                field=(
                    f"EXP-046 {family} preprocessor fingerprint"
                ),
            )
            _validate_sha256(
                raw.get("model_fingerprint"),
                field=f"EXP-046 {family} model fingerprint",
            )
            if raw.get("fit_attempt_count") != 1:
                raise ValueError(
                    f"EXP-046 {family} fit-attempt mismatch"
                )
            continue
        if (
            family == "logistic_regression"
            and status == "FAILED_NON_CONVERGENCE"
        ):
            if raw.get(
                "failure_reason"
            ) != "LBFGS_MAX_ITER_REACHED":
                raise ValueError(
                    "EXP-046 logistic failure reason mismatch"
                )
            if raw.get("fit_attempt_count") != 1:
                raise ValueError(
                    "EXP-046 logistic fit-attempt mismatch"
                )
            if raw.get("retry_authorized") is not False:
                raise ValueError(
                    "EXP-046 logistic retry must remain false"
                )
            continue
        raise ValueError(
            f"unexpected EXP-046 {family} fit status: {status!r}"
        )

    selection = result.get("selection")
    validation = result.get("validation")
    holdout = result.get("retrospective_holdout")
    if (
        not isinstance(selection, Mapping)
        or not isinstance(validation, Mapping)
        or not isinstance(holdout, Mapping)
    ):
        raise ValueError(
            "EXP-046 chronology blocks are malformed"
        )

    variants = selection.get("variants")
    if not isinstance(variants, list) or len(variants) != 6:
        raise ValueError(
            "EXP-046 must preserve six selection variants"
        )

    expected_slots = {
        (family, float(threshold))
        for family in MODEL_FAMILIES
        for threshold in CONFIDENCE_THRESHOLDS
    }
    indexed: dict[
        tuple[str, float],
        Mapping[str, object],
    ] = {}
    aggregate_pass_count = 0
    stable_pass_count = 0
    stability_reject_count = 0

    for raw in variants:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-046 model variant is malformed"
            )
        family = raw.get("model_family")
        threshold = raw.get("confidence_threshold")
        if (
            not isinstance(family, str)
            or not isinstance(threshold, (int, float))
            or isinstance(threshold, bool)
        ):
            raise ValueError(
                "EXP-046 variant identity is malformed"
            )
        slot = (family, float(threshold))
        if slot not in expected_slots:
            raise ValueError(
                f"unexpected EXP-046 variant slot: {slot}"
            )
        if slot in indexed:
            raise ValueError(
                "duplicate EXP-046 variant slot"
            )

        family_record = families[family]
        assert isinstance(family_record, Mapping)
        family_status = family_record.get("status")
        if raw.get("family_fit_status") != family_status:
            raise ValueError(
                "EXP-046 variant family-fit mismatch"
            )

        if family_status == "FITTED":
            aggregate_passed, final_passed = (
                _validate_fitted_variant(raw)
            )
            aggregate_pass_count += int(
                aggregate_passed
            )
            stable_pass_count += int(final_passed)
            stability_reject_count += int(
                aggregate_passed and not final_passed
            )
        else:
            if family != "logistic_regression":
                raise ValueError(
                    "EXP-046 unavailable family must be logistic"
                )
            if raw.get(
                "evaluation_status"
            ) != "FAMILY_UNAVAILABLE":
                raise ValueError(
                    "EXP-046 unavailable logistic variant mismatch"
                )
            if raw.get(
                "failure_reason"
            ) != "LBFGS_MAX_ITER_REACHED":
                raise ValueError(
                    "EXP-046 unavailable logistic reason mismatch"
                )
            if raw.get(
                "aggregate_selection_gate_passed"
            ) is not False:
                raise ValueError(
                    "EXP-046 unavailable variant cannot aggregate-pass"
                )
            stability = raw.get("temporal_stability")
            if (
                not isinstance(stability, Mapping)
                or stability.get("status")
                != "FAMILY_UNAVAILABLE"
                or stability.get("windows") != []
            ):
                raise ValueError(
                    "EXP-046 unavailable variant stability mismatch"
                )
            if raw.get("selection_gate_passed") is not False:
                raise ValueError(
                    "EXP-046 unavailable variant cannot final-pass"
                )
        indexed[slot] = raw

    if set(indexed) != expected_slots:
        raise ValueError(
            "EXP-046 variant-slot inventory mismatch"
        )

    selected_variant = selection.get("selected_variant")
    selection_status = selection.get("status")
    if selection_status == "SELECTED":
        if not isinstance(selected_variant, Mapping):
            raise ValueError(
                "EXP-046 selected cell lacks variant identity"
            )
        selected_family = selected_variant.get("model_family")
        selected_threshold = selected_variant.get(
            "confidence_threshold"
        )
        if (
            not isinstance(selected_family, str)
            or not isinstance(
                selected_threshold,
                (int, float),
            )
            or isinstance(selected_threshold, bool)
        ):
            raise ValueError(
                "EXP-046 selected variant is malformed"
            )
        chosen = indexed.get(
            (
                selected_family,
                float(selected_threshold),
            )
        )
        if (
            chosen is None
            or chosen.get("selection_gate_passed") is not True
            or chosen.get("family_fit_status") != "FITTED"
        ):
            raise ValueError(
                "EXP-046 selected variant is not stable-eligible"
            )
    elif selected_variant is not None:
        raise ValueError(
            "EXP-046 unselected cell cannot name a variant"
        )

    _validate_status_chain(
        selection=selection_status,
        validation=validation.get("status"),
        holdout=holdout.get("status"),
    )

    result_fingerprint = _validate_sha256(
        result.get("result_fingerprint"),
        field="EXP-046 cell result fingerprint",
    )
    unsigned = dict(result)
    unsigned.pop("result_fingerprint", None)
    if _sha256(_canonical_json(unsigned)) != result_fingerprint:
        raise ValueError(
            "EXP-046 cell result fingerprint mismatch"
        )

    return {
        "symbol": identity[0],
        "timeframe": identity[1],
        "horizon_minutes": identity[2],
        "result_fingerprint": result_fingerprint,
        "selection_status": selection_status,
        "validation_status": validation.get("status"),
        "retrospective_holdout_status": holdout.get("status"),
        "logistic_fit_status": families[
            "logistic_regression"
        ].get("status"),
        "hgb_fit_status": families[
            "hist_gradient_boosting"
        ].get("status"),
        "aggregate_selection_pass_variant_count": (
            aggregate_pass_count
        ),
        "stable_selection_pass_variant_count": (
            stable_pass_count
        ),
        "stability_reject_variant_count": (
            stability_reject_count
        ),
    }


def compile_stability_model_result_evidence(
    cell_results: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    commit = _validate_commit(
        code_commit,
        field="EXP-046 model-result code commit",
    )
    expected_cells = {
        (cell.symbol, cell.timeframe, cell.horizon_minutes)
        for cell in MODEL_CELLS
    }
    indexed: dict[
        tuple[str, str, int],
        dict[str, object],
    ] = {}
    for result in cell_results:
        if not isinstance(result, Mapping):
            raise ValueError(
                "EXP-046 model result row must be an object"
            )
        summary = _validate_stability_cell_result(result)
        identity = (
            str(summary["symbol"]),
            str(summary["timeframe"]),
            int(summary["horizon_minutes"]),
        )
        if identity in indexed:
            raise ValueError(
                "duplicate EXP-046 model result cell"
            )
        indexed[identity] = summary

    if set(indexed) != expected_cells:
        missing = sorted(
            expected_cells - set(indexed)
        )
        raise ValueError(
            f"EXP-046 result evidence is incomplete: {missing}"
        )

    cells = [indexed[key] for key in sorted(indexed)]
    evidence: dict[str, object] = {
        "evidence_version": (
            STABILITY_MODEL_RESULT_EVIDENCE_VERSION
        ),
        "runner_version": (
            STABILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "runner_decision": (
            STABILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "experiment_id": STABILITY_SUCCESSOR_EXPERIMENT_ID,
        "training_core_version": (
            STABILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            STABILITY_TRAINING_CORE_DECISION
        ),
        "training_core_commit": DEC105_MERGED_COMMIT,
        "training_core_blob_sha": (
            DEC105_TRAINING_CORE_BLOB_SHA
        ),
        "protocol_decision": STABILITY_PROTOCOL_DECISION,
        "protocol_version": STABILITY_PROTOCOL_VERSION,
        "protocol_commit": DEC104_MERGED_COMMIT,
        "protocol_blob_sha": DEC104_PROTOCOL_BLOB_SHA,
        "protocol_fingerprint": (
            stability_protocol_fingerprint()
        ),
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
        "readiness_artifact_id": (
            AUTHORITATIVE_READINESS_ARTIFACT_ID
        ),
        "readiness_fingerprint": (
            AUTHORITATIVE_READINESS_FINGERPRINT
        ),
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
        raise ValueError(
            "EXP-046 aggregate cell identity is malformed"
        )
    identity = (symbol, timeframe, horizon)
    if identity not in expected_cells:
        raise ValueError(
            f"unexpected EXP-046 aggregate cell: {identity}"
        )
    _validate_sha256(
        raw.get("result_fingerprint"),
        field="EXP-046 aggregate cell result fingerprint",
    )

    selection = raw.get("selection_status")
    validation = raw.get("validation_status")
    holdout = raw.get("retrospective_holdout_status")
    _validate_status_chain(
        selection=selection,
        validation=validation,
        holdout=holdout,
    )

    for field in (
        "aggregate_selection_pass_variant_count",
        "stable_selection_pass_variant_count",
        "stability_reject_variant_count",
    ):
        value = raw.get(field)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
            or value > 6
        ):
            raise ValueError(
                f"EXP-046 aggregate cell {field} is invalid"
            )
    if (
        int(raw["stable_selection_pass_variant_count"])
        + int(raw["stability_reject_variant_count"])
        != int(raw["aggregate_selection_pass_variant_count"])
    ):
        raise ValueError(
            "EXP-046 aggregate/stability variant accounting mismatch"
        )

    if raw.get("logistic_fit_status") not in {
        "FITTED",
        "FAILED_NON_CONVERGENCE",
    }:
        raise ValueError(
            "EXP-046 logistic fit summary is invalid"
        )
    if raw.get("hgb_fit_status") != "FITTED":
        raise ValueError(
            "EXP-046 HGB fit summary must be FITTED"
        )
    return identity


def validate_stability_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    if not isinstance(evidence, Mapping):
        raise ValueError(
            "EXP-046 model-result evidence must be an object"
        )
    commit = _validate_commit(
        expected_code_commit,
        field="EXP-046 expected code commit",
    )
    unsigned = dict(evidence)
    supplied = _validate_sha256(
        unsigned.pop("evidence_fingerprint", None),
        field="EXP-046 aggregate evidence fingerprint",
    )
    if _sha256(_canonical_json(unsigned)) != supplied:
        raise ValueError(
            "EXP-046 aggregate evidence fingerprint mismatch"
        )

    exact = {
        "evidence_version": (
            STABILITY_MODEL_RESULT_EVIDENCE_VERSION
        ),
        "runner_version": (
            STABILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "runner_decision": (
            STABILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "experiment_id": STABILITY_SUCCESSOR_EXPERIMENT_ID,
        "training_core_version": (
            STABILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            STABILITY_TRAINING_CORE_DECISION
        ),
        "training_core_commit": DEC105_MERGED_COMMIT,
        "training_core_blob_sha": (
            DEC105_TRAINING_CORE_BLOB_SHA
        ),
        "protocol_decision": STABILITY_PROTOCOL_DECISION,
        "protocol_version": STABILITY_PROTOCOL_VERSION,
        "protocol_commit": DEC104_MERGED_COMMIT,
        "protocol_blob_sha": DEC104_PROTOCOL_BLOB_SHA,
        "protocol_fingerprint": (
            stability_protocol_fingerprint()
        ),
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
        "readiness_artifact_id": (
            AUTHORITATIVE_READINESS_ARTIFACT_ID
        ),
        "readiness_fingerprint": (
            AUTHORITATIVE_READINESS_FINGERPRINT
        ),
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
                f"EXP-046 aggregate evidence {field} mismatch"
            )

    cells = evidence.get("cells")
    if (
        not isinstance(cells, list)
        or len(cells) != len(MODEL_CELLS)
    ):
        raise ValueError(
            "EXP-046 aggregate evidence must contain 18 cells"
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
    no_stable_count = 0
    no_family_count = 0
    validation_pass_count = 0
    holdout_pass_count = 0
    logistic_nonconvergence_count = 0
    aggregate_pass_variant_count = 0
    stable_pass_variant_count = 0
    stability_reject_variant_count = 0

    for raw in cells:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-046 aggregate cell summary is malformed"
            )
        identity = _validate_summary_cell(
            raw,
            expected_cells=expected_cells,
        )
        if identity in indexed:
            raise ValueError(
                "duplicate EXP-046 aggregate cell"
            )
        indexed[identity] = raw

        selection = raw["selection_status"]
        validation = raw["validation_status"]
        holdout = raw["retrospective_holdout_status"]
        selected_count += int(selection == "SELECTED")
        no_stable_count += int(
            selection == "NO_STABLE_MODEL_CHALLENGER"
        )
        no_family_count += int(
            selection == "NO_MODEL_FAMILY_AVAILABLE"
        )
        validation_pass_count += int(validation == "PASS")
        holdout_pass_count += int(holdout == "PASS")
        logistic_nonconvergence_count += int(
            raw["logistic_fit_status"]
            == "FAILED_NON_CONVERGENCE"
        )
        aggregate_pass_variant_count += int(
            raw[
                "aggregate_selection_pass_variant_count"
            ]
        )
        stable_pass_variant_count += int(
            raw[
                "stable_selection_pass_variant_count"
            ]
        )
        stability_reject_variant_count += int(
            raw["stability_reject_variant_count"]
        )

    if set(indexed) != expected_cells:
        raise ValueError(
            "EXP-046 aggregate cell set mismatch"
        )

    return {
        "stability_model_result_evidence_verified": True,
        "stability_model_result_evidence_fingerprint": (
            supplied
        ),
        "stability_model_result_code_commit": commit,
        "verified_cell_count": len(cells),
        "selected_cell_count": selected_count,
        "no_stable_model_challenger_count": (
            no_stable_count
        ),
        "no_model_family_available_count": (
            no_family_count
        ),
        "validation_pass_count": validation_pass_count,
        "retrospective_holdout_pass_count": (
            holdout_pass_count
        ),
        "logistic_nonconvergence_cell_count": (
            logistic_nonconvergence_count
        ),
        "aggregate_selection_pass_variant_count": (
            aggregate_pass_variant_count
        ),
        "stable_selection_pass_variant_count": (
            stable_pass_variant_count
        ),
        "stability_reject_variant_count": (
            stability_reject_variant_count
        ),
        "prior_result_informed": True,
        "untouched_oos": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def run_authoritative_stability_model_bundle(
    *,
    repository_root: Path,
    readiness: Mapping[str, object],
    feature_roots: Mapping[tuple[str, str], Path],
    outcome_roots: Mapping[tuple[str, str], Path],
    code_commit: str,
) -> dict[str, object]:
    if (
        AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "DEC-106 source is non-executable for authoritative "
            "EXP-046 model fitting"
        )

    # Intentionally unreachable under DEC-106. A later separate
    # execution decision must open this gate.
    validate_stability_artifact_runner_sources(
        repository_root=repository_root,
    )
    indexed = validate_authoritative_readiness(readiness)
    cell_results: list[dict[str, object]] = []
    for cell in MODEL_CELLS:
        identity = (cell.symbol, cell.timeframe)
        if identity not in indexed:
            raise ValueError(
                f"missing authoritative EXP-046 source cell: {identity}"
            )
        if (
            identity not in feature_roots
            or identity not in outcome_roots
        ):
            raise ValueError(
                f"missing extracted EXP-046 artifact root: {identity}"
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
            run_stability_model_cell_core(
                features=loaded.feature_frame,
                outcomes=loaded.outcome_frame,
                cell=cell,
            )
        )

    return compile_stability_model_result_evidence(
        cell_results,
        code_commit=code_commit,
    )


def write_stability_model_result_evidence(
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
            "conflicting existing EXP-046 model-result evidence"
        )
    destination.write_text(
        payload,
        encoding="utf-8",
    )


def load_stability_model_result_evidence(
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
            f"cannot read EXP-046 model-result evidence: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError(
            "EXP-046 model-result evidence root must be an object"
        )
    validate_stability_model_result_evidence(
        value,
        expected_code_commit=expected_code_commit,
    )
    return value


__all__ = [
    "AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC105_MERGED_COMMIT",
    "DEC105_TRAINING_CORE_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "LEGACY_DATA_LOADER_BLOB_SHA",
    "LIVE_ORDER_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "STABILITY_MODEL_ARTIFACT_RUNNER_DECISION",
    "STABILITY_MODEL_ARTIFACT_RUNNER_VERSION",
    "STABILITY_MODEL_FIT_AUTHORIZED",
    "STABILITY_MODEL_RESULT_EVIDENCE_VERSION",
    "TRADING_AUTHORIZED",
    "compile_stability_model_result_evidence",
    "load_stability_model_result_evidence",
    "run_authoritative_stability_model_bundle",
    "validate_stability_artifact_runner_sources",
    "validate_stability_model_result_evidence",
    "write_stability_model_result_evidence",
]
