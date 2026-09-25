from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .model_successor_fit_temporal_residual_bound_utility_result_review import (
    validate_fit_temporal_residual_bound_utility_model_terminal_review,
)


FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_DECISION = "DEC-196"

REVIEWED_MODEL_RUN_ID = 36152351767
REVIEWED_MODEL_HEAD_SHA = "5ca369a87f8a761c3232b75f95a701043721fd36"
REVIEWED_MODEL_RUN_ATTEMPT = 1
REVIEWED_MODEL_RUN_CONCLUSION = "success"

REVIEWED_AGGREGATE_ARTIFACT_ID = 10873466808
REVIEWED_AGGREGATE_ARTIFACT_NAME = (
    "exp054-fit-temporal-residual-bound-utility-model-result-evidence-"
    "5ca369a87f8a761c3232b75f95a701043721fd36-"
    "from-feature-35867307338-outcome-35876715434"
)
REVIEWED_AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:"
    "d9adb29cb1bc4d9c6b2bbc65e80c168d90a7d0df909d0c1fb1377347b2ee223b"
)
REVIEWED_EVIDENCE_FINGERPRINT = (
    "307b576f06c6aa2fb01a267232a0de55"
    "3bfa79c1bdbe6bf5d55b2bfc3b40787c"
)

REVIEWED_VERIFIED_CELL_COUNT = 18
REVIEWED_VERIFIED_REGRESSOR_COUNT = 108
REVIEWED_VERIFIED_POOLED_REFERENCE_COUNT = 108
REVIEWED_VERIFIED_UTILITY_SUPPORT_REFERENCE_COUNT = 432
REVIEWED_VERIFIED_FEATURE_SUPPORT_REFERENCE_COUNT = 216
REVIEWED_VERIFIED_RESIDUAL_REFERENCE_COUNT = 432
REVIEWED_TOTAL_VARIANT_COUNT = 54
REVIEWED_AVAILABLE_BUDGET_VARIANT_COUNT = 28
REVIEWED_UNAVAILABLE_BUDGET_VARIANT_COUNT = 26
REVIEWED_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT = 26392
REVIEWED_SELECTED_CELL_COUNT = 0
REVIEWED_NO_STABLE_MODEL_CHALLENGER_COUNT = 18
REVIEWED_VALIDATION_PASS_CELL_COUNT = 0
REVIEWED_HOLDOUT_PASS_CELL_COUNT = 0
REVIEWED_AGGREGATE_SELECTION_PASS_VARIANT_COUNT = 2
REVIEWED_STABLE_SELECTION_PASS_VARIANT_COUNT = 0
REVIEWED_ACCEPTED_MODEL_CANDIDATE_COUNT = 0

REVIEWED_AGGREGATE_PASS_VARIANTS = (
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 60, 1000),
)

MODEL_RUN_DISPATCH_AUTHORIZED = False
REPLACEMENT_MODEL_RUN_AUTHORIZED = False
AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED = False
MODEL_PROTOCOL_RESULT_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _canonical_hash(value: object) -> str:
    payload = (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_aggregate_artifact_identity(
    artifacts_payload: Mapping[str, object],
) -> None:
    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("DEC-196 artifact listing is malformed")

    matches: list[Mapping[str, object]] = []
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-196 artifact row is malformed")
        if raw.get("name") == REVIEWED_AGGREGATE_ARTIFACT_NAME:
            matches.append(raw)

    if len(matches) != 1:
        raise ValueError(
            "DEC-196 requires exactly one reviewed aggregate artifact"
        )

    artifact = matches[0]
    if artifact.get("id") != REVIEWED_AGGREGATE_ARTIFACT_ID:
        raise ValueError("DEC-196 aggregate artifact id mismatch")
    if artifact.get("expired") is not False:
        raise ValueError(
            "DEC-196 aggregate artifact must remain non-expired"
        )
    if artifact.get("digest") != REVIEWED_AGGREGATE_ARTIFACT_DIGEST:
        raise ValueError("DEC-196 aggregate artifact digest mismatch")


def _aggregate_pass_variants(
    aggregate_evidence: Mapping[str, object],
) -> tuple[tuple[str, str, int, int], ...]:
    cells = aggregate_evidence.get("cells")
    if not isinstance(cells, list):
        raise ValueError("DEC-196 aggregate evidence cells malformed")

    passed: list[tuple[str, str, int, int]] = []
    for raw_cell in cells:
        if not isinstance(raw_cell, Mapping):
            raise ValueError("DEC-196 aggregate cell malformed")
        identity = raw_cell.get("cell")
        selection = raw_cell.get("selection")
        if not isinstance(identity, Mapping) or not isinstance(selection, Mapping):
            raise ValueError("DEC-196 aggregate cell identity malformed")
        variants = selection.get("variants")
        if not isinstance(variants, list):
            raise ValueError("DEC-196 aggregate variants malformed")
        for variant in variants:
            if not isinstance(variant, Mapping):
                raise ValueError("DEC-196 aggregate variant malformed")
            if variant.get("aggregate_selection_gate_passed") is not True:
                continue
            passed.append(
                (
                    str(identity.get("symbol")),
                    str(identity.get("timeframe")),
                    int(identity.get("horizon_minutes")),
                    int(variant.get("candidate_budget_anchor")),
                )
            )
    return tuple(sorted(passed))


def _summary(
    aggregate_evidence: Mapping[str, object],
) -> dict[str, int]:
    cells = aggregate_evidence.get("cells")
    if not isinstance(cells, list):
        raise ValueError("DEC-196 aggregate evidence cells malformed")

    regressor_count = 0
    pooled_count = 0
    support_count = 0
    feature_count = 0
    residual_count = 0
    total_variants = 0
    available_variants = 0
    unavailable_variants = 0
    aggregate_passes = 0
    stable_passes = 0
    selected_cells = 0
    no_stable_cells = 0
    validation_passes = 0
    holdout_passes = 0
    eligible_rows = 0

    for raw_cell in cells:
        if not isinstance(raw_cell, Mapping):
            raise ValueError("DEC-196 aggregate cell malformed")

        supplied = dict(raw_cell)
        fingerprint = supplied.pop("result_fingerprint", None)
        if not isinstance(fingerprint, str) or _canonical_hash(supplied) != fingerprint:
            raise ValueError("DEC-196 cell result fingerprint mismatch")

        fit = raw_cell.get("fit")
        selection = raw_cell.get("selection")
        validation = raw_cell.get("validation")
        holdout = raw_cell.get("retrospective_holdout")
        if (
            not isinstance(fit, Mapping)
            or not isinstance(selection, Mapping)
            or not isinstance(validation, Mapping)
            or not isinstance(holdout, Mapping)
        ):
            raise ValueError("DEC-196 aggregate cell blocks malformed")

        regressor_count += int(fit.get("regressor_count", -1))
        pooled_count += int(fit.get("calibration_reference_count", -1))
        support_count += int(
            fit.get("fit_temporal_support_reference_count", -1)
        )
        feature_count += int(
            fit.get("fit_temporal_feature_support_reference_count", -1)
        )
        residual_count += int(
            fit.get("fit_temporal_residual_reference_count", -1)
        )

        variants = selection.get("variants")
        if not isinstance(variants, list):
            raise ValueError("DEC-196 aggregate variants malformed")
        total_variants += len(variants)

        cell_eligible_counts: set[int] = set()
        for variant in variants:
            if not isinstance(variant, Mapping):
                raise ValueError("DEC-196 aggregate variant malformed")
            count = variant.get("eligible_selection_row_count")
            if (
                not isinstance(count, int)
                or isinstance(count, bool)
                or count < 0
            ):
                raise ValueError(
                    "DEC-196 eligible selection row count malformed"
                )
            cell_eligible_counts.add(count)

            status = variant.get("status")
            if status == "AVAILABLE":
                available_variants += 1
            else:
                unavailable_variants += 1

            if variant.get("aggregate_selection_gate_passed") is True:
                aggregate_passes += 1
            if variant.get("selection_gate_passed") is True:
                stable_passes += 1

        if len(cell_eligible_counts) > 1:
            raise ValueError(
                "DEC-196 eligible selection row count drift within cell"
            )
        if cell_eligible_counts:
            eligible_rows += next(iter(cell_eligible_counts))

        if selection.get("selected_variant") is not None:
            selected_cells += 1
        if selection.get("status") == (
            "NO_FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_STABLE_MODEL_CHALLENGER"
        ):
            no_stable_cells += 1
        if validation.get("status") == "PASS":
            validation_passes += 1
        if holdout.get("status") == "PASS":
            holdout_passes += 1

    return {
        "verified_regressor_count": regressor_count,
        "verified_pooled_calibration_reference_count": pooled_count,
        "verified_fit_temporal_support_reference_count": support_count,
        "verified_fit_temporal_feature_support_reference_count": feature_count,
        "verified_fit_temporal_residual_reference_count": residual_count,
        "total_variant_count": total_variants,
        "available_budget_variant_count": available_variants,
        "unavailable_budget_variant_count": unavailable_variants,
        "utility_eligible_selection_row_count": eligible_rows,
        "selected_cell_count": selected_cells,
        "no_fit_temporal_residual_bound_utility_stable_model_challenger_count": (
            no_stable_cells
        ),
        "validation_pass_cell_count": validation_passes,
        "holdout_pass_cell_count": holdout_passes,
        "aggregate_selection_pass_variant_count": aggregate_passes,
        "stable_selection_pass_variant_count": stable_passes,
    }


def validate_reviewed_fit_temporal_residual_bound_utility_model_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    aggregate_evidence: Mapping[str, object],
) -> dict[str, object]:
    if run.get("id") != REVIEWED_MODEL_RUN_ID:
        raise ValueError("DEC-196 reviewed model run id mismatch")
    if run.get("head_sha") != REVIEWED_MODEL_HEAD_SHA:
        raise ValueError("DEC-196 reviewed model head SHA mismatch")
    if run.get("run_attempt") != REVIEWED_MODEL_RUN_ATTEMPT:
        raise ValueError("DEC-196 reviewed model run attempt mismatch")
    if run.get("conclusion") != REVIEWED_MODEL_RUN_CONCLUSION:
        raise ValueError("DEC-196 reviewed model run conclusion mismatch")

    _validate_aggregate_artifact_identity(artifacts_payload)

    review = (
        validate_fit_temporal_residual_bound_utility_model_terminal_review(
            run=run,
            jobs_payload=jobs_payload,
            artifacts_payload=artifacts_payload,
            aggregate_evidence=aggregate_evidence,
        )
    )

    exact_review = {
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_"
            "RESULT_REVIEW_REQUIRED"
        ),
        "fit_temporal_residual_bound_utility_model_terminal_reviewed": True,
        "fit_temporal_residual_bound_utility_model_result_review_decision": (
            "DEC-190"
        ),
        "reviewed_model_run_id": REVIEWED_MODEL_RUN_ID,
        "reviewed_model_head_sha": REVIEWED_MODEL_HEAD_SHA,
        "reviewed_model_run_attempt": REVIEWED_MODEL_RUN_ATTEMPT,
        "reviewed_model_run_conclusion": REVIEWED_MODEL_RUN_CONCLUSION,
        "persisted_cell_artifact_count": 9,
        "aggregate_artifact_present": True,
        "fit_temporal_residual_bound_utility_model_result_evidence_verified": (
            True
        ),
        "verified_cell_count": REVIEWED_VERIFIED_CELL_COUNT,
        "verified_fit_temporal_residual_reference_count": (
            REVIEWED_VERIFIED_RESIDUAL_REFERENCE_COUNT
        ),
        "evidence_fingerprint": REVIEWED_EVIDENCE_FINGERPRINT,
        "prior_result_informed": True,
        "untouched_oos": False,
        "replacement_model_run_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    for field, expected in exact_review.items():
        if review.get(field) != expected:
            raise ValueError(
                f"DEC-196 terminal review {field} mismatch"
            )

    summary = _summary(aggregate_evidence)
    exact_summary = {
        "verified_regressor_count": REVIEWED_VERIFIED_REGRESSOR_COUNT,
        "verified_pooled_calibration_reference_count": (
            REVIEWED_VERIFIED_POOLED_REFERENCE_COUNT
        ),
        "verified_fit_temporal_support_reference_count": (
            REVIEWED_VERIFIED_UTILITY_SUPPORT_REFERENCE_COUNT
        ),
        "verified_fit_temporal_feature_support_reference_count": (
            REVIEWED_VERIFIED_FEATURE_SUPPORT_REFERENCE_COUNT
        ),
        "verified_fit_temporal_residual_reference_count": (
            REVIEWED_VERIFIED_RESIDUAL_REFERENCE_COUNT
        ),
        "total_variant_count": REVIEWED_TOTAL_VARIANT_COUNT,
        "available_budget_variant_count": (
            REVIEWED_AVAILABLE_BUDGET_VARIANT_COUNT
        ),
        "unavailable_budget_variant_count": (
            REVIEWED_UNAVAILABLE_BUDGET_VARIANT_COUNT
        ),
        "utility_eligible_selection_row_count": (
            REVIEWED_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
        ),
        "selected_cell_count": REVIEWED_SELECTED_CELL_COUNT,
        "no_fit_temporal_residual_bound_utility_stable_model_challenger_count": (
            REVIEWED_NO_STABLE_MODEL_CHALLENGER_COUNT
        ),
        "validation_pass_cell_count": REVIEWED_VALIDATION_PASS_CELL_COUNT,
        "holdout_pass_cell_count": REVIEWED_HOLDOUT_PASS_CELL_COUNT,
        "aggregate_selection_pass_variant_count": (
            REVIEWED_AGGREGATE_SELECTION_PASS_VARIANT_COUNT
        ),
        "stable_selection_pass_variant_count": (
            REVIEWED_STABLE_SELECTION_PASS_VARIANT_COUNT
        ),
    }
    for field, expected in exact_summary.items():
        if summary.get(field) != expected:
            raise ValueError(f"DEC-196 reviewed {field} mismatch")

    passes = _aggregate_pass_variants(aggregate_evidence)
    if passes != tuple(sorted(REVIEWED_AGGREGATE_PASS_VARIANTS)):
        raise ValueError("DEC-196 aggregate pass inventory mismatch")

    return {
        **review,
        **summary,
        "fit_temporal_residual_bound_utility_model_result_decision": (
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_DECISION
        ),
        "stage": (
            "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_"
            "REVIEWED_NO_STABLE_CHALLENGER"
        ),
        "accepted_model_candidate_count": (
            REVIEWED_ACCEPTED_MODEL_CANDIDATE_COUNT
        ),
        "reviewed_aggregate_pass_variants": [
            list(value) for value in REVIEWED_AGGREGATE_PASS_VARIANTS
        ],
        "model_run_dispatch_authorized": MODEL_RUN_DISPATCH_AUTHORIZED,
        "replacement_model_run_authorized": REPLACEMENT_MODEL_RUN_AUTHORIZED,
        "authoritative_model_result_execution_authorized": (
            AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED
        ),
        "model_protocol_result_authorized": MODEL_PROTOCOL_RESULT_AUTHORIZED,
        "model_fit_authorized": MODEL_FIT_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "shadow_authorized": SHADOW_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


__all__ = [
    "AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEMO_ORDER_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_DECISION",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "MODEL_RUN_DISPATCH_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REPLACEMENT_MODEL_RUN_AUTHORIZED",
    "REVIEWED_AGGREGATE_ARTIFACT_DIGEST",
    "REVIEWED_AGGREGATE_ARTIFACT_ID",
    "REVIEWED_AGGREGATE_ARTIFACT_NAME",
    "REVIEWED_AGGREGATE_PASS_VARIANTS",
    "REVIEWED_EVIDENCE_FINGERPRINT",
    "REVIEWED_MODEL_HEAD_SHA",
    "REVIEWED_MODEL_RUN_ID",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "validate_reviewed_fit_temporal_residual_bound_utility_model_result",
]
