from __future__ import annotations

from typing import Mapping

from .model_successor_result_review import (
    validate_successor_model_terminal_review,
)


SUCCESSOR_MODEL_RESULT_RECORD_DECISION = "DEC-102"
REVIEWED_SUCCESSOR_MODEL_RUN_ID = 35911916239
REVIEWED_SUCCESSOR_MODEL_HEAD_SHA = (
    "6d42a5053c5f2f696071715640dab24973a40517"
)
REVIEWED_SUCCESSOR_MODEL_RUN_ATTEMPT = 1

AUTHORIZATION_PREFLIGHT_JOB_ID = 107353620434
AGGREGATE_MODEL_EVIDENCE_JOB_ID = 107365635911
MATRIX_JOB_IDS = frozenset(
    {
        107353779152,
        107353779161,
        107353779183,
        107353779188,
        107353779202,
        107353779209,
        107353779245,
        107353779255,
        107353779328,
    }
)

AGGREGATE_ARTIFACT_ID = 10774927034
AGGREGATE_EVIDENCE_FINGERPRINT = (
    "3e0ebac02dbba690b4c03dd10c3fdd30c5eb0d6356b881e38f9a3527f0135c55"
)

EXPECTED_ARTIFACTS: Mapping[str, tuple[int, str]] = {
    (
        "exp045-model-cell-results-EURUSD-5m-"
        "6d42a5053c5f2f696071715640dab24973a40517"
    ): (
        10773444973,
        "sha256:236cdb91af7ebdcd3e5fd98bfd8dfabcbcbfb25221fd16aa903f764d24ce6c37",
    ),
    (
        "exp045-model-cell-results-EURUSD-15m-"
        "6d42a5053c5f2f696071715640dab24973a40517"
    ): (
        10773198666,
        "sha256:3e9b351dec386ed7a9a415a8cd5f070f2baa5adf6c2c6819f9e7cda3b2192774",
    ),
    (
        "exp045-model-cell-results-EURUSD-1h-"
        "6d42a5053c5f2f696071715640dab24973a40517"
    ): (
        10773811698,
        "sha256:b3567613ec8f8d94dd8d989de99663591679c12dd1a1f2a382b1dbdd44aed33f",
    ),
    (
        "exp045-model-cell-results-GBPUSD-5m-"
        "6d42a5053c5f2f696071715640dab24973a40517"
    ): (
        10773709400,
        "sha256:f680a3f0acdef2c4f1e58c8b1c4d850bbe30753d916b9893c967860358517c28",
    ),
    (
        "exp045-model-cell-results-GBPUSD-15m-"
        "6d42a5053c5f2f696071715640dab24973a40517"
    ): (
        10773553841,
        "sha256:108915955a4a300667151614bd95e8020bc24bd73f5f201135d5fd54d4feffea",
    ),
    (
        "exp045-model-cell-results-GBPUSD-1h-"
        "6d42a5053c5f2f696071715640dab24973a40517"
    ): (
        10774685531,
        "sha256:95f862158e7421a7e57edb0a71d98c7c9434a6331d532db083f1be366bd199fe",
    ),
    (
        "exp045-model-cell-results-USDJPY-5m-"
        "6d42a5053c5f2f696071715640dab24973a40517"
    ): (
        10775341008,
        "sha256:b41c922ea830bb71638455f00058b422d45fa3c30d82c3e6074d349f6627ddd0",
    ),
    (
        "exp045-model-cell-results-USDJPY-15m-"
        "6d42a5053c5f2f696071715640dab24973a40517"
    ): (
        10774751957,
        "sha256:b829a00d2a67281c8d3234882a925cb737e5ab5dc9f3cf027fc06a4615b2ac78",
    ),
    (
        "exp045-model-cell-results-USDJPY-1h-"
        "6d42a5053c5f2f696071715640dab24973a40517"
    ): (
        10774845741,
        "sha256:a6b1d87f77d4993588bdb9c5ed0696dd1c576dd070751f78462ca96d5622d52b",
    ),
    (
        "exp045-model-result-evidence-"
        "6d42a5053c5f2f696071715640dab24973a40517-"
        "from-feature-35867307338-outcome-35876715434"
    ): (
        AGGREGATE_ARTIFACT_ID,
        "sha256:8602d0b5e9bb6ad746f5cd5c96e878e631d6ed090dcd7a236c0ee00c6fadd5a5",
    ),
}

SELECTED_CELL = ("GBPUSD", "5m", 240)
SELECTED_CELL_RESULT_FINGERPRINT = (
    "d6c2ce934be43e1e76852bb7d6c6ca46d33160bff372719bf083cb7923b352ff"
)
SELECTED_MODEL_FAMILY = "hist_gradient_boosting"
SELECTED_CONFIDENCE_THRESHOLD = 0.6
SELECTION_DIRECTIONAL_CANDIDATE_COUNT = 460
SELECTION_TOTAL_NET_PIPS_AT_0P5 = 2353.6999999999875
VALIDATION_DIRECTIONAL_CANDIDATE_COUNT = 83
VALIDATION_TOTAL_NET_PIPS_AT_0P5 = -1397.5000000000007

LOGISTIC_NONCONVERGENCE_CELLS = frozenset(
    {
        ("EURUSD", "15m", 240),
        ("EURUSD", "5m", 60),
        ("EURUSD", "5m", 240),
        ("GBPUSD", "5m", 60),
        ("USDJPY", "5m", 60),
        ("USDJPY", "5m", 240),
    }
)

REPLACEMENT_MODEL_RUN_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _validate_exact_artifact_inventory(
    artifacts_payload: Mapping[str, object],
) -> None:
    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError(
            "reviewed EXP-045 artifact listing is malformed"
        )
    if len(artifacts) != len(EXPECTED_ARTIFACTS):
        raise ValueError(
            "reviewed EXP-045 artifact count mismatch"
        )

    indexed: dict[str, Mapping[str, object]] = {}
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "reviewed EXP-045 artifact row is malformed"
            )
        name = raw.get("name")
        if not isinstance(name, str) or name in indexed:
            raise ValueError(
                "reviewed EXP-045 artifact name is malformed or duplicated"
            )
        indexed[name] = raw

    if set(indexed) != set(EXPECTED_ARTIFACTS):
        raise ValueError(
            "reviewed EXP-045 artifact inventory mismatch"
        )

    for name, (artifact_id, digest) in EXPECTED_ARTIFACTS.items():
        raw = indexed[name]
        if raw.get("id") != artifact_id:
            raise ValueError(
                f"reviewed EXP-045 artifact id mismatch: {name}"
            )
        if raw.get("digest") != digest:
            raise ValueError(
                f"reviewed EXP-045 artifact digest mismatch: {name}"
            )
        if raw.get("expired") is not False:
            raise ValueError(
                f"reviewed EXP-045 artifact unexpectedly expired: {name}"
            )


def validate_selected_successor_challenger(
    result: Mapping[str, object],
) -> dict[str, object]:
    if result.get("result_fingerprint") != (
        SELECTED_CELL_RESULT_FINGERPRINT
    ):
        raise ValueError(
            "reviewed EXP-045 selected-cell fingerprint mismatch"
        )

    cell = result.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError(
            "reviewed EXP-045 selected-cell identity is malformed"
        )
    identity = (
        cell.get("symbol"),
        cell.get("timeframe"),
        cell.get("horizon_minutes"),
    )
    if identity != SELECTED_CELL:
        raise ValueError(
            "reviewed EXP-045 selected-cell identity mismatch"
        )

    selection = result.get("selection")
    if not isinstance(selection, Mapping):
        raise ValueError(
            "reviewed EXP-045 selection block is malformed"
        )
    if selection.get("status") != "SELECTED":
        raise ValueError(
            "reviewed EXP-045 selected cell must remain selected"
        )
    variant = selection.get("selected_variant")
    if not isinstance(variant, Mapping):
        raise ValueError(
            "reviewed EXP-045 selected variant is malformed"
        )
    if (
        variant.get("model_family") != SELECTED_MODEL_FAMILY
        or variant.get("confidence_threshold")
        != SELECTED_CONFIDENCE_THRESHOLD
    ):
        raise ValueError(
            "reviewed EXP-045 selected variant mismatch"
        )

    variants = selection.get("variants")
    if not isinstance(variants, list):
        raise ValueError(
            "reviewed EXP-045 selection variants are malformed"
        )
    selected_rows = [
        raw
        for raw in variants
        if isinstance(raw, Mapping)
        and raw.get("model_family") == SELECTED_MODEL_FAMILY
        and raw.get("confidence_threshold")
        == SELECTED_CONFIDENCE_THRESHOLD
    ]
    if len(selected_rows) != 1:
        raise ValueError(
            "reviewed EXP-045 selected-variant row mismatch"
        )
    selected_row = selected_rows[0]
    scenarios = selected_row.get("scenarios")
    if not isinstance(scenarios, Mapping):
        raise ValueError(
            "reviewed EXP-045 selection scenarios are malformed"
        )
    selection_scenario = scenarios.get("0.5")
    if not isinstance(selection_scenario, Mapping):
        raise ValueError(
            "reviewed EXP-045 selection 0.5 scenario is missing"
        )
    gate = selection_scenario.get("gate")
    metrics = selection_scenario.get("metrics")
    if not isinstance(gate, Mapping) or not isinstance(metrics, Mapping):
        raise ValueError(
            "reviewed EXP-045 selection scenario is malformed"
        )
    if gate.get("passed") is not True:
        raise ValueError(
            "reviewed EXP-045 selected variant must pass selection"
        )
    if (
        metrics.get("directional_candidate_count")
        != SELECTION_DIRECTIONAL_CANDIDATE_COUNT
        or metrics.get("total_net_pips")
        != SELECTION_TOTAL_NET_PIPS_AT_0P5
    ):
        raise ValueError(
            "reviewed EXP-045 selection metrics mismatch"
        )

    validation = result.get("validation")
    if not isinstance(validation, Mapping):
        raise ValueError(
            "reviewed EXP-045 validation block is malformed"
        )
    if validation.get("status") != "REJECT":
        raise ValueError(
            "reviewed EXP-045 selected cell must remain validation-rejected"
        )
    validation_scenarios = validation.get("scenarios")
    if not isinstance(validation_scenarios, Mapping):
        raise ValueError(
            "reviewed EXP-045 validation scenarios are malformed"
        )
    validation_scenario = validation_scenarios.get("0.5")
    if not isinstance(validation_scenario, Mapping):
        raise ValueError(
            "reviewed EXP-045 validation 0.5 scenario is missing"
        )
    validation_gate = validation_scenario.get("gate")
    validation_metrics = validation_scenario.get("metrics")
    if (
        not isinstance(validation_gate, Mapping)
        or not isinstance(validation_metrics, Mapping)
    ):
        raise ValueError(
            "reviewed EXP-045 validation scenario is malformed"
        )
    if validation_gate.get("passed") is not False:
        raise ValueError(
            "reviewed EXP-045 validation gate must remain failed"
        )
    if (
        validation_metrics.get("directional_candidate_count")
        != VALIDATION_DIRECTIONAL_CANDIDATE_COUNT
        or validation_metrics.get("total_net_pips")
        != VALIDATION_TOTAL_NET_PIPS_AT_0P5
    ):
        raise ValueError(
            "reviewed EXP-045 validation metrics mismatch"
        )

    holdout = result.get("retrospective_holdout")
    if (
        not isinstance(holdout, Mapping)
        or holdout.get("status") != "LOCKED_VALIDATION_REJECT"
    ):
        raise ValueError(
            "reviewed EXP-045 holdout must remain locked after validation reject"
        )

    return {
        "selected_cell_verified": True,
        "selected_cell": SELECTED_CELL,
        "selected_model_family": SELECTED_MODEL_FAMILY,
        "selected_confidence_threshold": (
            SELECTED_CONFIDENCE_THRESHOLD
        ),
        "selection_directional_candidate_count": (
            SELECTION_DIRECTIONAL_CANDIDATE_COUNT
        ),
        "selection_total_net_pips_at_0p5": (
            SELECTION_TOTAL_NET_PIPS_AT_0P5
        ),
        "validation_directional_candidate_count": (
            VALIDATION_DIRECTIONAL_CANDIDATE_COUNT
        ),
        "validation_total_net_pips_at_0p5": (
            VALIDATION_TOTAL_NET_PIPS_AT_0P5
        ),
        "validation_status": "REJECT",
        "retrospective_holdout_status": (
            "LOCKED_VALIDATION_REJECT"
        ),
    }


def validate_reviewed_successor_model_result(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    aggregate_evidence: Mapping[str, object],
    selected_cell_evidence: Mapping[str, object],
) -> dict[str, object]:
    if run.get("id") != REVIEWED_SUCCESSOR_MODEL_RUN_ID:
        raise ValueError(
            "reviewed EXP-045 model run id mismatch"
        )
    if run.get("head_sha") != REVIEWED_SUCCESSOR_MODEL_HEAD_SHA:
        raise ValueError(
            "reviewed EXP-045 model run head SHA mismatch"
        )
    if run.get("run_attempt") != REVIEWED_SUCCESSOR_MODEL_RUN_ATTEMPT:
        raise ValueError(
            "reviewed EXP-045 model run attempt mismatch"
        )

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError(
            "reviewed EXP-045 jobs payload is malformed"
        )
    expected_job_ids = {
        AUTHORIZATION_PREFLIGHT_JOB_ID,
        AGGREGATE_MODEL_EVIDENCE_JOB_ID,
        *MATRIX_JOB_IDS,
    }
    actual_job_ids = {
        raw.get("id")
        for raw in jobs
        if isinstance(raw, Mapping)
    }
    if actual_job_ids != expected_job_ids:
        raise ValueError(
            "reviewed EXP-045 job inventory mismatch"
        )
    for raw in jobs:
        if (
            not isinstance(raw, Mapping)
            or raw.get("status") != "completed"
            or raw.get("conclusion") != "success"
        ):
            raise ValueError(
                "reviewed EXP-045 jobs must all remain successful"
            )

    _validate_exact_artifact_inventory(artifacts_payload)

    review = validate_successor_model_terminal_review(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        aggregate_evidence=aggregate_evidence,
    )
    if review.get("stage") != "SUCCESSOR_MODEL_RESULT_REVIEW_REQUIRED":
        raise ValueError(
            "reviewed EXP-045 terminal stage mismatch"
        )
    if review.get("successor_model_result_evidence_fingerprint") != (
        AGGREGATE_EVIDENCE_FINGERPRINT
    ):
        raise ValueError(
            "reviewed EXP-045 aggregate evidence fingerprint mismatch"
        )

    exact_counts = {
        "verified_cell_count": 18,
        "selected_cell_count": 1,
        "no_model_challenger_count": 17,
        "no_model_family_available_count": 0,
        "validation_pass_count": 0,
        "retrospective_holdout_pass_count": 0,
        "logistic_nonconvergence_cell_count": 6,
    }
    for field, expected in exact_counts.items():
        if review.get(field) != expected:
            raise ValueError(
                f"reviewed EXP-045 aggregate count mismatch: {field}"
            )

    cells = aggregate_evidence.get("cells")
    if not isinstance(cells, list):
        raise ValueError(
            "reviewed EXP-045 aggregate cells are malformed"
        )
    selected = [
        raw
        for raw in cells
        if isinstance(raw, Mapping)
        and (
            raw.get("symbol"),
            raw.get("timeframe"),
            raw.get("horizon_minutes"),
        )
        == SELECTED_CELL
    ]
    if len(selected) != 1:
        raise ValueError(
            "reviewed EXP-045 selected aggregate cell mismatch"
        )
    selected_summary = selected[0]
    if (
        selected_summary.get("selection_status") != "SELECTED"
        or selected_summary.get("validation_status") != "REJECT"
        or selected_summary.get("retrospective_holdout_status")
        != "LOCKED_VALIDATION_REJECT"
        or selected_summary.get("result_fingerprint")
        != SELECTED_CELL_RESULT_FINGERPRINT
    ):
        raise ValueError(
            "reviewed EXP-045 selected aggregate summary mismatch"
        )

    nonconverged = {
        (
            raw.get("symbol"),
            raw.get("timeframe"),
            raw.get("horizon_minutes"),
        )
        for raw in cells
        if isinstance(raw, Mapping)
        and raw.get("logistic_fit_status")
        == "FAILED_NON_CONVERGENCE"
    }
    if nonconverged != LOGISTIC_NONCONVERGENCE_CELLS:
        raise ValueError(
            "reviewed EXP-045 non-convergence inventory mismatch"
        )

    selected_detail = validate_selected_successor_challenger(
        selected_cell_evidence
    )

    return {
        **review,
        **selected_detail,
        "successor_model_result_record_decision": (
            SUCCESSOR_MODEL_RESULT_RECORD_DECISION
        ),
        "stage": "SUCCESSOR_MODEL_RESULT_REVIEWED_NO_CANDIDATE",
        "reviewed_successor_model_run_id": (
            REVIEWED_SUCCESSOR_MODEL_RUN_ID
        ),
        "reviewed_successor_model_head_sha": (
            REVIEWED_SUCCESSOR_MODEL_HEAD_SHA
        ),
        "aggregate_artifact_id": AGGREGATE_ARTIFACT_ID,
        "aggregate_evidence_fingerprint": (
            AGGREGATE_EVIDENCE_FINGERPRINT
        ),
        "replacement_model_run_authorized": (
            REPLACEMENT_MODEL_RUN_AUTHORIZED
        ),
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "shadow_authorized": SHADOW_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


__all__ = [
    "AGGREGATE_ARTIFACT_ID",
    "AGGREGATE_EVIDENCE_FINGERPRINT",
    "AGGREGATE_MODEL_EVIDENCE_JOB_ID",
    "AUTHORIZATION_PREFLIGHT_JOB_ID",
    "BROKER_MUTATION_AUTHORIZED",
    "DEMO_ORDER_AUTHORIZED",
    "EXPECTED_ARTIFACTS",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_NONCONVERGENCE_CELLS",
    "MATRIX_JOB_IDS",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REPLACEMENT_MODEL_RUN_AUTHORIZED",
    "REVIEWED_SUCCESSOR_MODEL_HEAD_SHA",
    "REVIEWED_SUCCESSOR_MODEL_RUN_ATTEMPT",
    "REVIEWED_SUCCESSOR_MODEL_RUN_ID",
    "SELECTED_CELL",
    "SELECTED_CELL_RESULT_FINGERPRINT",
    "SELECTED_CONFIDENCE_THRESHOLD",
    "SELECTED_MODEL_FAMILY",
    "SHADOW_AUTHORIZED",
    "SUCCESSOR_MODEL_RESULT_RECORD_DECISION",
    "TRADING_AUTHORIZED",
    "validate_reviewed_successor_model_result",
    "validate_selected_successor_challenger",
]
