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
from .model_successor_density_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
)
from .model_successor_regime_utility_artifacts import (
    _canonical_json,
    _git_blob_sha,
    _sha256,
    _validate_commit,
    _validate_financial_gate,
    _validate_sha256,
    _validate_target_summary,
    _validate_variant,
)
from .model_successor_temporal_jackknife_utility_protocol import (
    FINANCIAL_TARGET_COLUMNS,
    FIT_JACKKNIFE_VIEWS,
    PRIOR_RESULT_INFORMED,
    TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID,
    TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION,
    TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION,
    UNTOUCHED_OOS,
    temporal_jackknife_utility_protocol_fingerprint,
)
from .model_successor_temporal_jackknife_utility_training import (
    DEC141_MERGED_COMMIT,
    DEC141_PROTOCOL_BLOB_SHA,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION,
    TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION,
    run_temporal_jackknife_utility_model_cell_core,
)


TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION = (
    "fmp-exp050-temporal-jackknife-utility-artifact-runner-v1"
)
TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION = "DEC-143"
TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EVIDENCE_VERSION = 1

DEC142_MERGED_COMMIT = (
    "fa6fd14a880a84a44795efe4099679ed0f642497"
)
DEC142_TRAINING_CORE_BLOB_SHA = (
    "ec97a9941af052d6e223e4bafab9a9989ec57ff0"
)
LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)
PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA = (
    "6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13"
)

AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = False
TEMPORAL_JACKKNIFE_UTILITY_MODEL_FIT_AUTHORIZED = False
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
                str(value)
                for value in raw["included_regimes"]
            ),
            "excluded_regime": str(raw["excluded_regime"]),
        }
        for raw in FIT_JACKKNIFE_VIEWS
    }


def validate_temporal_jackknife_utility_artifact_runner_sources(
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
        "dec141_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_jackknife_utility_protocol.py",
            DEC141_PROTOCOL_BLOB_SHA,
        ),
        "dec142_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_jackknife_utility_training.py",
            DEC142_TRAINING_CORE_BLOB_SHA,
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
                f"missing EXP-050 artifact dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-050 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    protocol_fingerprint = (
        temporal_jackknife_utility_protocol_fingerprint()
    )
    if len(protocol_fingerprint) != 64:
        raise ValueError(
            "EXP-050 temporal-jackknife protocol fingerprint is invalid"
        )

    return {
        "temporal_jackknife_utility_model_artifact_runner_version": (
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "temporal_jackknife_utility_model_artifact_runner_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "dec141_merged_commit": DEC141_MERGED_COMMIT,
        "dec142_merged_commit": DEC142_MERGED_COMMIT,
        "legacy_data_loader_blob_sha": actual[
            "legacy_data_loader"
        ],
        "dec141_protocol_blob_sha": actual[
            "dec141_protocol"
        ],
        "dec142_training_core_blob_sha": actual[
            "dec142_training_core"
        ],
        "predecessor_training_core_blob_sha": (
            PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_artifact_helper_blob_sha": actual[
            "predecessor_artifact_helper"
        ],
        "temporal_jackknife_utility_protocol_fingerprint": (
            protocol_fingerprint
        ),
        "authoritative_temporal_jackknife_utility_model_result_execution_authorized": (
            False
        ),
        "temporal_jackknife_utility_model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _validate_fit_block(
    fit: Mapping[str, object],
) -> int:
    expected_views = _view_definitions()
    models = fit.get("jackknife_models")
    if (
        not isinstance(models, Mapping)
        or set(models) != set(expected_views)
    ):
        raise ValueError(
            "EXP-050 jackknife fit inventory mismatch"
        )
    if fit.get("jackknife_view_count") != 3:
        raise ValueError(
            "EXP-050 jackknife view count mismatch"
        )
    if fit.get("regressor_count") != 6:
        raise ValueError(
            "EXP-050 total regressor count mismatch"
        )

    verified_regressors = 0
    for view_name in sorted(expected_views):
        record = models.get(view_name)
        if not isinstance(record, Mapping):
            raise ValueError(
                "EXP-050 jackknife fit record is malformed"
            )
        if record.get("status") != "FITTED":
            raise ValueError(
                "EXP-050 jackknife fit status mismatch"
            )
        expected = expected_views[view_name]
        included = record.get("included_regimes")
        if (
            not isinstance(included, list)
            or tuple(str(value) for value in included)
            != expected["included_regimes"]
        ):
            raise ValueError(
                "EXP-050 jackknife included-regime identity mismatch"
            )
        if (
            record.get("excluded_regime")
            != expected["excluded_regime"]
        ):
            raise ValueError(
                "EXP-050 jackknife excluded-regime identity mismatch"
            )

        row_count = record.get("row_count")
        if (
            not isinstance(row_count, int)
            or isinstance(row_count, bool)
            or row_count <= 0
        ):
            raise ValueError(
                "EXP-050 jackknife fit row count is invalid"
            )
        if record.get("regressor_count") != 2:
            raise ValueError(
                "EXP-050 jackknife regressor count mismatch"
            )

        regressors = record.get("regressors")
        if (
            not isinstance(regressors, Mapping)
            or set(regressors)
            != set(FINANCIAL_TARGET_COLUMNS)
        ):
            raise ValueError(
                "EXP-050 regressor inventory mismatch"
            )
        for target in FINANCIAL_TARGET_COLUMNS:
            target_record = regressors.get(target)
            if not isinstance(target_record, Mapping):
                raise ValueError(
                    "EXP-050 regressor record is malformed"
                )
            if (
                target_record.get("status") != "FITTED"
                or target_record.get("fit_attempt_count") != 1
            ):
                raise ValueError(
                    "EXP-050 regressor fit record mismatch"
                )
            summary = target_record.get("target_summary")
            if not isinstance(summary, Mapping):
                raise ValueError(
                    "EXP-050 regressor target summary missing"
                )
            _validate_target_summary(
                summary,
                expected_row_count=row_count,
                field=f"EXP-050 {view_name} {target}",
            )
            _validate_sha256(
                target_record.get("preprocessor_fingerprint"),
                field=(
                    f"EXP-050 {view_name} {target} "
                    "preprocessor fingerprint"
                ),
            )
            _validate_sha256(
                target_record.get("model_fingerprint"),
                field=(
                    f"EXP-050 {view_name} {target} "
                    "model fingerprint"
                ),
            )
            verified_regressors += 1

    for field in (
        "full_fit_single_model",
        "view_weight_search",
        "view_fallback",
    ):
        if fit.get(field) != {
            "status": "FORBIDDEN_BY_DEC141",
            "fit_attempt_count": 0,
        }:
            raise ValueError(
                f"EXP-050 {field} record mismatch"
            )
    if fit.get("hist_gradient_boosting_classifier") != {
        "status": "EXCLUDED_BY_DEC141",
        "fit_attempt_count": 0,
    }:
        raise ValueError(
            "EXP-050 classifier fallback record mismatch"
        )
    if fit.get("logistic_regression") != {
        "status": "EXCLUDED_BY_DEC112_DEC141",
        "fit_attempt_count": 0,
    }:
        raise ValueError(
            "EXP-050 logistic fallback record mismatch"
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

    digests = block.get("view_prediction_digests")
    expected_views = set(_view_definitions())
    if (
        not isinstance(digests, Mapping)
        or set(digests) != expected_views
    ):
        raise ValueError(
            f"{field} view prediction digest set mismatch"
        )
    for view_name in sorted(expected_views):
        target_digests = digests.get(view_name)
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
                    f"{field} {view_name} {target} "
                    "prediction digest"
                ),
            )
    return eligible


def _validate_status_chain(
    *,
    selection: object,
    validation: object,
    holdout: object,
) -> None:
    if (
        selection
        == "NO_TEMPORAL_JACKKNIFE_UTILITY_STABLE_MODEL_CHALLENGER"
    ):
        if validation != "LOCKED_NO_SELECTION":
            raise ValueError(
                "EXP-050 no-challenger validation must be locked"
            )
        if holdout != "LOCKED_NO_SELECTION":
            raise ValueError(
                "EXP-050 no-challenger holdout must be locked"
            )
        return
    if selection != "SELECTED":
        raise ValueError(
            f"unexpected EXP-050 selection status: {selection!r}"
        )
    if validation == "REJECT":
        if holdout != "LOCKED_VALIDATION_REJECT":
            raise ValueError(
                "EXP-050 rejected validation must keep holdout locked"
            )
        return
    if validation == "PASS":
        if holdout not in {"PASS", "REJECT"}:
            raise ValueError(
                "EXP-050 passed validation must produce holdout result"
            )
        return
    raise ValueError(
        f"unexpected EXP-050 validation status: {validation!r}"
    )


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
    consensus = block.get(
        "temporal_jackknife_utility_consensus"
    )
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
        block.get(
            "temporal_jackknife_utility_consensus_digest"
        ),
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
    if raw.get("experiment_id") != (
        TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID
    ):
        raise ValueError(
            "EXP-050 cell experiment identity mismatch"
        )
    if raw.get("training_core_version") != (
        TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION
    ):
        raise ValueError(
            "EXP-050 training core version mismatch"
        )
    if raw.get("training_core_decision") != (
        TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION
    ):
        raise ValueError(
            "EXP-050 training core decision mismatch"
        )
    for field, expected in (
        ("dec141_merged_commit", DEC141_MERGED_COMMIT),
        ("dec141_protocol_blob_sha", DEC141_PROTOCOL_BLOB_SHA),
        (
            "predecessor_training_core_blob_sha",
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        ),
        (
            "predecessor_training_core_decision",
            "DEC-133",
        ),
        (
            "protocol_decision",
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION,
        ),
        (
            "protocol_version",
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION,
        ),
        (
            "protocol_fingerprint",
            temporal_jackknife_utility_protocol_fingerprint(),
        ),
    ):
        if raw.get(field) != expected:
            raise ValueError(
                f"EXP-050 cell {field} mismatch"
            )
    if raw.get("prior_result_informed") is not PRIOR_RESULT_INFORMED:
        raise ValueError(
            "EXP-050 prior-result flag mismatch"
        )
    if raw.get("evidence_label") != EVIDENCE_LABEL:
        raise ValueError(
            "EXP-050 evidence label mismatch"
        )
    if raw.get("untouched_oos") is not UNTOUCHED_OOS:
        raise ValueError(
            "EXP-050 untouched-OOS flag mismatch"
        )

    cell = raw.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError(
            "EXP-050 cell identity is malformed"
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
            "EXP-050 cell identity is unsupported"
        )

    _validate_sha256(
        raw.get("processed_manifest_sha256"),
        field="EXP-050 processed manifest sha256",
    )
    joined_row_count = raw.get("joined_row_count")
    if (
        not isinstance(joined_row_count, int)
        or isinstance(joined_row_count, bool)
        or joined_row_count <= 0
    ):
        raise ValueError(
            "EXP-050 joined row count is invalid"
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
            "EXP-050 split row inventory mismatch"
        )
    for name in sorted(required_splits):
        value = split_counts.get(name)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value <= 0
        ):
            raise ValueError(
                "EXP-050 split row count is invalid"
            )

    fit = raw.get("fit")
    if not isinstance(fit, Mapping):
        raise ValueError(
            "EXP-050 fit evidence is malformed"
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
            "EXP-050 result stage evidence is malformed"
        )
    selection_row_count = selection.get("row_count")
    if selection_row_count != split_counts["selection"]:
        raise ValueError(
            "EXP-050 selection row count mismatch"
        )
    consensus = selection.get(
        "temporal_jackknife_utility_consensus"
    )
    if not isinstance(consensus, Mapping):
        raise ValueError(
            "EXP-050 selection utility consensus malformed"
        )
    eligible_count = _validate_consensus_block(
        consensus,
        expected_row_count=int(selection_row_count),
        field="EXP-050 selection",
    )
    _validate_sha256(
        selection.get(
            "temporal_jackknife_utility_consensus_digest"
        ),
        field="EXP-050 selection consensus digest",
    )

    variants = selection.get("variants")
    if (
        not isinstance(variants, list)
        or len(variants) != len(CANDIDATE_BUDGET_ANCHORS)
    ):
        raise ValueError(
            "EXP-050 selection variant inventory mismatch"
        )
    if {
        item.get("candidate_budget_anchor")
        for item in variants
        if isinstance(item, Mapping)
    } != set(CANDIDATE_BUDGET_ANCHORS):
        raise ValueError(
            "EXP-050 selection budget coverage mismatch"
        )

    aggregate_pass_count = 0
    stable_pass_count = 0
    unavailable_count = 0
    stable_variants: list[Mapping[str, object]] = []
    for item in variants:
        if not isinstance(item, Mapping):
            raise ValueError(
                "EXP-050 selection variant is malformed"
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
    if selection_status == (
        "NO_TEMPORAL_JACKKNIFE_UTILITY_"
        "STABLE_MODEL_CHALLENGER"
    ):
        if stable_variants:
            raise ValueError(
                "EXP-050 no-challenger status hides stable variant"
            )
        if selected_variant is not None:
            raise ValueError(
                "EXP-050 no-challenger cannot select variant"
            )
    elif selection_status == "SELECTED":
        if not stable_variants:
            raise ValueError(
                "EXP-050 selected status has no stable variant"
            )
        if not isinstance(selected_variant, Mapping):
            raise ValueError(
                "EXP-050 selected variant record missing"
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
                "EXP-050 selected variant identity mismatch"
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
                "EXP-050 selected variant is not a unique stable variant"
            )
    else:
        raise ValueError(
            "EXP-050 selection status is invalid"
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
                field="EXP-050 validation",
                gate_scenarios=VALIDATION_GATE_SCENARIOS,
            )
        if holdout_status in {"PASS", "REJECT"}:
            _validate_forward_block(
                holdout,
                expected_row_count=int(
                    split_counts["retrospective_holdout"]
                ),
                field="EXP-050 retrospective holdout",
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
                f"EXP-050 {field} must remain false"
            )

    supplied_fingerprint = _validate_sha256(
        raw.get("result_fingerprint"),
        field="EXP-050 cell result fingerprint",
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
            "EXP-050 cell result fingerprint mismatch"
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
        "no_temporal_jackknife_utility_stable_model_challenger_count": sum(
            item["selection_status"]
            == (
                "NO_TEMPORAL_JACKKNIFE_UTILITY_"
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


def compile_temporal_jackknife_utility_model_result_evidence(
    cell_results: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    commit = _validate_commit(
        code_commit,
        field="EXP-050 code commit",
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
                "EXP-050 cell result identity is malformed"
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
            "EXP-050 model-result cell evidence is incomplete"
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
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EVIDENCE_VERSION
        ),
        "artifact_runner_version": (
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "artifact_runner_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "experiment_id": (
            TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID
        ),
        "code_commit": commit,
        "dec141_merged_commit": DEC141_MERGED_COMMIT,
        "dec142_merged_commit": DEC142_MERGED_COMMIT,
        "dec141_protocol_blob_sha": (
            DEC141_PROTOCOL_BLOB_SHA
        ),
        "dec142_training_core_blob_sha": (
            DEC142_TRAINING_CORE_BLOB_SHA
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
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            temporal_jackknife_utility_protocol_fingerprint()
        ),
        "training_core_version": (
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION
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


def validate_temporal_jackknife_utility_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    expected_commit = _validate_commit(
        expected_code_commit,
        field="EXP-050 expected code commit",
    )
    for field, expected in (
        (
            "evidence_version",
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EVIDENCE_VERSION,
        ),
        (
            "artifact_runner_version",
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION,
        ),
        (
            "artifact_runner_decision",
            TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
        ),
        (
            "experiment_id",
            TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID,
        ),
        ("code_commit", expected_commit),
        ("dec141_merged_commit", DEC141_MERGED_COMMIT),
        ("dec142_merged_commit", DEC142_MERGED_COMMIT),
        (
            "dec141_protocol_blob_sha",
            DEC141_PROTOCOL_BLOB_SHA,
        ),
        (
            "dec142_training_core_blob_sha",
            DEC142_TRAINING_CORE_BLOB_SHA,
        ),
        (
            "predecessor_training_core_blob_sha",
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        ),
        (
            "predecessor_artifact_helper_blob_sha",
            PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA,
        ),
        (
            "legacy_data_loader_blob_sha",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        (
            "protocol_decision",
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION,
        ),
        (
            "protocol_version",
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION,
        ),
        (
            "protocol_fingerprint",
            temporal_jackknife_utility_protocol_fingerprint(),
        ),
        (
            "training_core_version",
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION,
        ),
        (
            "training_core_decision",
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION,
        ),
        ("evidence_label", EVIDENCE_LABEL),
        ("prior_result_informed", PRIOR_RESULT_INFORMED),
        ("untouched_oos", UNTOUCHED_OOS),
    ):
        if evidence.get(field) != expected:
            raise ValueError(
                f"EXP-050 evidence {field} mismatch"
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
            "EXP-050 authoritative source identity mismatch"
        )

    cells = evidence.get("cells")
    if not isinstance(cells, list):
        raise ValueError(
            "EXP-050 evidence cells must be a list"
        )
    if evidence.get("cell_count") != len(MODEL_CELLS):
        raise ValueError(
            "EXP-050 evidence cell count mismatch"
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
                "EXP-050 evidence cell is malformed"
            )
        cell = row.get("cell")
        if not isinstance(cell, Mapping):
            raise ValueError(
                "EXP-050 evidence cell identity malformed"
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
            "EXP-050 model-result cell evidence is incomplete"
        )

    summary = _compile_summary(cells)
    if evidence.get("summary") != summary:
        raise ValueError(
            "EXP-050 evidence summary mismatch"
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
                f"EXP-050 evidence {field} must remain false"
            )

    supplied_fingerprint = _validate_sha256(
        evidence.get("evidence_fingerprint"),
        field="EXP-050 evidence fingerprint",
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
            "EXP-050 evidence fingerprint mismatch"
        )
    return {
        "temporal_jackknife_utility_model_result_evidence_verified": True,
        **summary,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
        "evidence_fingerprint": supplied_fingerprint,
    }


def run_authoritative_temporal_jackknife_utility_model_bundle(
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
        AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "DEC-143 source is non-executable for authoritative "
            "EXP-050 model fitting"
        )

    validate_temporal_jackknife_utility_artifact_runner_sources(
        repository_root=repository_root,
    )
    indexed = validate_authoritative_readiness(readiness)
    cell_results: list[dict[str, object]] = []
    for cell in MODEL_CELLS:
        identity = (cell.symbol, cell.timeframe)
        if identity not in indexed:
            raise ValueError(
                f"missing authoritative EXP-050 source cell: {identity}"
            )
        if (
            identity not in feature_roots
            or identity not in outcome_roots
        ):
            raise ValueError(
                f"missing extracted EXP-050 artifact root: {identity}"
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
            run_temporal_jackknife_utility_model_cell_core(
                features=loaded.feature_frame,
                outcomes=loaded.outcome_frame,
                cell=cell,
            )
        )
    return compile_temporal_jackknife_utility_model_result_evidence(
        cell_results,
        code_commit=code_commit,
    )


def write_temporal_jackknife_utility_model_result_evidence(
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
            "conflicting existing EXP-050 model-result evidence"
        )
    destination.write_text(
        payload,
        encoding="utf-8",
    )


def load_temporal_jackknife_utility_model_result_evidence(
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
            f"cannot read EXP-050 model-result evidence: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError(
            "EXP-050 model-result evidence root must be an object"
        )
    validate_temporal_jackknife_utility_model_result_evidence(
        value,
        expected_code_commit=expected_code_commit,
    )
    return value


__all__ = [
    "AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC142_MERGED_COMMIT",
    "DEC142_TRAINING_CORE_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "LEGACY_DATA_LOADER_BLOB_SHA",
    "LIVE_ORDER_AUTHORIZED",
    "PREDECESSOR_ARTIFACT_HELPER_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_FIT_AUTHORIZED",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EVIDENCE_VERSION",
    "TRADING_AUTHORIZED",
    "_compile_summary",
    "_validate_consensus_block",
    "_validate_fit_block",
    "compile_temporal_jackknife_utility_model_result_evidence",
    "load_temporal_jackknife_utility_model_result_evidence",
    "run_authoritative_temporal_jackknife_utility_model_bundle",
    "validate_temporal_jackknife_utility_artifact_runner_sources",
    "validate_temporal_jackknife_utility_model_result_evidence",
    "write_temporal_jackknife_utility_model_result_evidence",
]
