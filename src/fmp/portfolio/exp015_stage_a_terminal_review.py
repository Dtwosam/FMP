from __future__ import annotations

from typing import Mapping

from .challenger_discovery import (
    EXP015_ID,
    build_exp015_challengers,
    exp015_catalog_identity_sha256,
)
from .challenger_discovery_stage_a import (
    EXP015_STAGE_A_AUTHORIZATION_PROTOCOL,
    exp015_strategy_source_sha256,
)


EXP015_STAGE_A_TERMINAL_REVIEW_DECISION = "DEC-264"
EXP015_STAGE_A_WORKFLOW_NAME = "phase8a-exp015-stage-a"
EXP015_STAGE_A_WORKFLOW_PATH = ".github/workflows/phase8a-exp015-stage-a.yml"

DEC263_MERGED_COMMIT = "46512e56abb097bd8e7f1a9503f762e3d18b3715"
DEC264_GUARDED_WORKFLOW_BLOB_SHA = "ae8bdfbdb1bcfd62204a1bd0ec32dddfd9938930"
EXP015_CATALOG_SOURCE_BLOB_SHA = "8b2a047668b6f607fee48dc09d7efb5fbdd153d7"
EXP015_STAGE_A_SOURCE_BLOB_SHA = "6f8be2a6d873b872ed8c47d5f3705a36c21958a5"
EXP015_CLI_BLOB_SHA = "6d676dbc35bb0244d83dc3134893849022814a4a"
EXP015_SCRIPT_BLOB_SHA = "803ef9569880a6b22353e33b91ce63c9c9151424"

EXPECTED_CELLS = (
    ("EURUSD", "5m"),
    ("EURUSD", "15m"),
    ("EURUSD", "1h"),
    ("GBPUSD", "5m"),
    ("GBPUSD", "15m"),
    ("GBPUSD", "1h"),
    ("USDJPY", "5m"),
    ("USDJPY", "15m"),
    ("USDJPY", "1h"),
)
EXPECTED_FAMILIES = {
    "mean_reversion",
    "previous_day_rejection",
    "session_breakout",
    "session_sweep_rejection",
    "trend_continuation",
    "volatility_breakout",
}
TERMINAL_NON_SUCCESS_CONCLUSIONS = {"failure", "cancelled", "timed_out"}

STAGE_A_RETRY_AUTHORIZED = False
STAGE_A_REPLACEMENT_AUTHORIZED = False
STAGE_B_EXECUTION_AUTHORIZED = False
STAGE_C_EXECUTION_AUTHORIZED = False
PORTFOLIO_SELECTION_AUTHORIZED = False
PHASE8A_ACCEPTANCE_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _validate_head_sha(value: object) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError("EXP-015 Stage A terminal review head SHA is malformed")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(
            "EXP-015 Stage A terminal review head SHA must be hexadecimal"
        ) from exc
    return value.lower()


def _index_jobs(
    jobs_payload: Mapping[str, object],
) -> tuple[Mapping[str, object], list[Mapping[str, object]], Mapping[str, object]]:
    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 11:
        raise ValueError(
            "EXP-015 Stage A terminal review requires exactly 11 workflow jobs"
        )

    catalog: list[Mapping[str, object]] = []
    matrix: list[Mapping[str, object]] = []
    authorize: list[Mapping[str, object]] = []
    seen_ids: set[int] = set()

    for raw in jobs:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-015 Stage A terminal review job row is malformed")
        job_id = raw.get("id")
        if (
            not isinstance(job_id, int)
            or isinstance(job_id, bool)
            or job_id in seen_ids
        ):
            raise ValueError("EXP-015 Stage A terminal review job id is malformed")
        seen_ids.add(job_id)
        if raw.get("status") != "completed":
            raise ValueError("EXP-015 Stage A terminal review requires completed jobs")
        name = raw.get("name")
        if not isinstance(name, str):
            raise ValueError("EXP-015 Stage A terminal review job name is malformed")
        if name == "catalog-freeze":
            catalog.append(raw)
        elif name.startswith("stage-a-cell ("):
            matrix.append(raw)
        elif name == "stage-a-authorize":
            authorize.append(raw)
        else:
            raise ValueError(
                f"unexpected EXP-015 Stage A terminal review job name: {name!r}"
            )

    if len(catalog) != 1:
        raise ValueError("EXP-015 Stage A terminal review requires one catalog job")
    if len(matrix) != 9:
        raise ValueError("EXP-015 Stage A terminal review requires nine matrix jobs")
    expected_matrix_names = {
        f"stage-a-cell ({symbol}, {timeframe})"
        for symbol, timeframe in EXPECTED_CELLS
    }
    matrix_names = {str(job["name"]) for job in matrix}
    if len(matrix_names) != 9 or matrix_names != expected_matrix_names:
        raise ValueError(
            "EXP-015 Stage A terminal review matrix job coverage mismatch"
        )
    if len(authorize) != 1:
        raise ValueError(
            "EXP-015 Stage A terminal review requires one authorization job"
        )
    return catalog[0], matrix, authorize[0]


def _expected_artifact_names(head_sha: str) -> tuple[set[str], str, str]:
    cell_names = {
        f"phase8a-exp015-stage-a-{symbol}-{timeframe}-{head_sha}"
        for symbol, timeframe in EXPECTED_CELLS
    }
    catalog = f"phase8a-exp015-catalog-{head_sha}"
    authorization = f"phase8a-exp015-stage-a-authorization-{head_sha}"
    return cell_names, catalog, authorization


def _validate_artifacts(
    artifacts_payload: Mapping[str, object],
    *,
    head_sha: str,
) -> tuple[set[str], bool, bool]:
    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("EXP-015 Stage A artifact listing is malformed")

    expected_cells, expected_catalog, expected_authorization = (
        _expected_artifact_names(head_sha)
    )
    seen: set[str] = set()
    allowed = expected_cells | {expected_catalog, expected_authorization}
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-015 Stage A artifact row is malformed")
        name = raw.get("name")
        if not isinstance(name, str) or name in seen:
            raise ValueError("EXP-015 Stage A artifact name is malformed or duplicated")
        if raw.get("expired") is not False:
            raise ValueError("EXP-015 Stage A terminal review requires live artifacts")
        if name not in allowed:
            raise ValueError(f"unexpected EXP-015 Stage A artifact: {name!r}")
        seen.add(name)

    total_count = artifacts_payload.get("total_count")
    if total_count is not None and total_count != len(artifacts):
        raise ValueError("EXP-015 Stage A artifact count mismatch")

    return (
        seen & expected_cells,
        expected_catalog in seen,
        expected_authorization in seen,
    )


def _validate_authorization_evidence(
    evidence: Mapping[str, object],
    *,
    head_sha: str,
) -> dict[str, object]:
    if evidence.get("protocol") != EXP015_STAGE_A_AUTHORIZATION_PROTOCOL:
        raise ValueError("EXP-015 Stage A authorization protocol mismatch")
    if evidence.get("experiment_id") != EXP015_ID:
        raise ValueError("EXP-015 Stage A authorization experiment mismatch")
    if evidence.get("evidence_label") != "RETROSPECTIVE_ALREADY_SEEN":
        raise ValueError("EXP-015 Stage A authorization must be retrospective")
    if evidence.get("untouched_oos") is not False:
        raise ValueError("EXP-015 Stage A authorization cannot be untouched OOS")
    if evidence.get("promotion_authorized") is not False:
        raise ValueError("EXP-015 Stage A authorization cannot authorize promotion")
    if evidence.get("historical_status_mutation_authorized") is not False:
        raise ValueError("EXP-015 Stage A authorization cannot mutate lifecycle")
    if evidence.get("runner_code_commit") != head_sha:
        raise ValueError("EXP-015 Stage A authorization runner commit mismatch")

    expected_catalog_sha = exp015_catalog_identity_sha256(code_commit=head_sha)
    if evidence.get("catalog_identity_sha256") != expected_catalog_sha:
        raise ValueError("EXP-015 Stage A authorization catalog identity mismatch")
    expected_source_sha = exp015_strategy_source_sha256()
    if evidence.get("strategy_source_sha256") != expected_source_sha:
        raise ValueError("EXP-015 Stage A authorization strategy source mismatch")

    exact_ints = {
        "cell_count": 9,
        "ranking_cell_count": 54,
        "strategy_identity_count": 567,
        "maximum_stage_a_survivors": 108,
    }
    for field, expected in exact_ints.items():
        if evidence.get(field) != expected:
            raise ValueError(f"EXP-015 Stage A authorization {field} mismatch")

    survivors_raw = evidence.get("survivor_fingerprints")
    survivor_count = evidence.get("survivor_count")
    if not isinstance(survivors_raw, list):
        raise ValueError("EXP-015 Stage A survivor list is malformed")
    survivors = tuple(str(item) for item in survivors_raw)
    if (
        not isinstance(survivor_count, int)
        or isinstance(survivor_count, bool)
        or survivor_count != len(survivors)
        or survivor_count > 108
        or len(set(survivors)) != len(survivors)
        or list(survivors) != sorted(survivors)
    ):
        raise ValueError("EXP-015 Stage A survivor accounting mismatch")

    catalog = build_exp015_challengers(code_commit=head_sha)
    catalog_by_fingerprint = {
        item.strategy.fingerprint: item.strategy
        for item in catalog
    }
    catalog_fingerprints = set(catalog_by_fingerprint)
    if len(catalog_fingerprints) != 567:
        raise ValueError("EXP-015 Stage A terminal review catalog size drift")
    if not set(survivors).issubset(catalog_fingerprints):
        raise ValueError("EXP-015 Stage A survivor is outside frozen catalog")
    if evidence.get("stage_b_source_open_authorized") is not bool(survivors):
        raise ValueError("EXP-015 Stage A source-open flag mismatches survivors")

    expected_fingerprints_by_cell: dict[tuple[str, str], list[str]] = {
        cell: sorted(
            fingerprint
            for fingerprint, strategy in catalog_by_fingerprint.items()
            if (strategy.symbol, strategy.timeframe) == cell
        )
        for cell in EXPECTED_CELLS
    }

    cells_raw = evidence.get("cells")
    if not isinstance(cells_raw, list) or len(cells_raw) != 9:
        raise ValueError("EXP-015 Stage A authorization cell evidence is malformed")

    expected_cells = set(EXPECTED_CELLS)
    seen_cells: set[tuple[str, str]] = set()
    covered_fingerprints: set[str] = set()
    covered_survivors: set[str] = set()
    for raw in cells_raw:
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-015 Stage A authorization cell row is malformed")
        symbol = raw.get("symbol")
        timeframe = raw.get("timeframe")
        if not isinstance(symbol, str) or not isinstance(timeframe, str):
            raise ValueError("EXP-015 Stage A authorization cell identity is malformed")
        cell = (symbol, timeframe)
        if cell not in expected_cells or cell in seen_cells:
            raise ValueError("EXP-015 Stage A authorization cell coverage mismatch")
        seen_cells.add(cell)

        fingerprints = raw.get("strategy_fingerprints")
        if (
            not isinstance(fingerprints, list)
            or len(fingerprints) != 63
            or any(not isinstance(item, str) for item in fingerprints)
        ):
            raise ValueError(
                "EXP-015 Stage A authorization cell must bind 63 strategies"
            )
        expected_fingerprints = expected_fingerprints_by_cell[cell]
        if fingerprints != expected_fingerprints:
            raise ValueError(
                "EXP-015 Stage A authorization cell strategy membership mismatch"
            )
        normalized = set(fingerprints)
        if covered_fingerprints.intersection(normalized):
            raise ValueError(
                "EXP-015 Stage A authorization strategy coverage is duplicated"
            )
        covered_fingerprints.update(normalized)

        rankings = raw.get("family_rankings")
        gates = raw.get("strategy_gates")
        if not isinstance(rankings, Mapping) or set(rankings) != EXPECTED_FAMILIES:
            raise ValueError("EXP-015 Stage A family-ranking coverage mismatch")
        if not isinstance(gates, Mapping) or set(gates) != normalized:
            raise ValueError("EXP-015 Stage A strategy-gate coverage mismatch")

        mandatory_by_family: dict[str, set[str]] = {
            family: set() for family in EXPECTED_FAMILIES
        }
        for fingerprint in expected_fingerprints:
            gate = gates[fingerprint]
            if not isinstance(gate, Mapping):
                raise ValueError("EXP-015 Stage A strategy gate row is malformed")
            strategy = catalog_by_fingerprint[fingerprint]
            if gate.get("family") != strategy.family:
                raise ValueError("EXP-015 Stage A strategy gate family mismatch")
            if gate.get("parameters_json") != strategy.parameters_json:
                raise ValueError("EXP-015 Stage A strategy gate parameters mismatch")
            mandatory = gate.get("mandatory_gate_pass")
            if not isinstance(mandatory, bool):
                raise ValueError(
                    "EXP-015 Stage A strategy gate mandatory flag is malformed"
                )
            if mandatory:
                mandatory_by_family[strategy.family].add(fingerprint)

        cell_survivors = raw.get("survivor_fingerprints")
        if (
            not isinstance(cell_survivors, list)
            or len(cell_survivors) > 12
            or any(not isinstance(item, str) for item in cell_survivors)
            or cell_survivors != sorted(cell_survivors)
            or len(set(cell_survivors)) != len(cell_survivors)
        ):
            raise ValueError("EXP-015 Stage A cell survivor list is malformed")
        if not set(cell_survivors).issubset(normalized):
            raise ValueError("EXP-015 Stage A cell survivor outside cell catalog")

        selected_by_rankings: set[str] = set()
        for family in EXPECTED_FAMILIES:
            ranking = rankings[family]
            if not isinstance(ranking, Mapping):
                raise ValueError("EXP-015 Stage A family-ranking row is malformed")
            passing = ranking.get("passing_fingerprints")
            selected = ranking.get("selected_fingerprints")
            if (
                not isinstance(passing, list)
                or not isinstance(selected, list)
                or any(not isinstance(item, str) for item in passing)
                or any(not isinstance(item, str) for item in selected)
                or len(set(passing)) != len(passing)
                or len(set(selected)) != len(selected)
                or len(selected) > 2
            ):
                raise ValueError("EXP-015 Stage A family-ranking list is malformed")
            if set(passing) != mandatory_by_family[family]:
                raise ValueError(
                    "EXP-015 Stage A family-ranking passers mismatch strategy gates"
                )
            if selected != passing[:2]:
                raise ValueError(
                    "EXP-015 Stage A family-ranking selection mismatch"
                )
            if any(
                catalog_by_fingerprint[fingerprint].family != family
                for fingerprint in passing
            ):
                raise ValueError(
                    "EXP-015 Stage A family-ranking contains wrong-family strategy"
                )
            selected_by_rankings.update(selected)

        if selected_by_rankings != set(cell_survivors):
            raise ValueError(
                "EXP-015 Stage A cell survivors mismatch family selections"
            )
        if covered_survivors.intersection(cell_survivors):
            raise ValueError("EXP-015 Stage A survivor appears in multiple cells")
        covered_survivors.update(cell_survivors)

    if seen_cells != expected_cells:
        raise ValueError("EXP-015 Stage A authorization missing a required cell")
    if covered_fingerprints != catalog_fingerprints:
        raise ValueError("EXP-015 Stage A authorization does not cover 567 strategies")
    if covered_survivors != set(survivors):
        raise ValueError(
            "EXP-015 Stage A aggregate survivors mismatch cell selections"
        )

    return {
        "exp015_stage_a_authorization_evidence_verified": True,
        "verified_cell_count": 9,
        "verified_ranking_cell_count": 54,
        "verified_strategy_identity_count": 567,
        "verified_maximum_stage_a_survivors": 108,
        "verified_survivor_count": survivor_count,
        "verified_stage_b_source_open": bool(survivors),
        "verified_catalog_identity_sha256": expected_catalog_sha,
        "verified_strategy_source_sha256": expected_source_sha,
    }


def validate_exp015_stage_a_terminal_review(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    authorization_evidence: Mapping[str, object] | None = None,
) -> dict[str, object]:
    run_id = run.get("id")
    if not isinstance(run_id, int) or isinstance(run_id, bool):
        raise ValueError("EXP-015 Stage A terminal review run id is malformed")
    if run.get("name") != EXP015_STAGE_A_WORKFLOW_NAME:
        raise ValueError("EXP-015 Stage A terminal review workflow name mismatch")
    if run.get("path") != EXP015_STAGE_A_WORKFLOW_PATH:
        raise ValueError("EXP-015 Stage A terminal review workflow path mismatch")
    if run.get("event") != "workflow_dispatch":
        raise ValueError("EXP-015 Stage A terminal review event mismatch")
    if run.get("head_branch") != "main":
        raise ValueError("EXP-015 Stage A terminal review branch mismatch")
    if run.get("run_attempt") != 1:
        raise ValueError("EXP-015 Stage A terminal review forbids rerun attempts")
    if run.get("status") != "completed":
        raise ValueError("EXP-015 Stage A terminal review run is not completed")

    head_sha = _validate_head_sha(run.get("head_sha"))
    conclusion = run.get("conclusion")
    if conclusion not in {"success", *TERMINAL_NON_SUCCESS_CONCLUSIONS}:
        raise ValueError(
            f"unexpected EXP-015 Stage A terminal conclusion: {conclusion!r}"
        )

    catalog_job, matrix_jobs, authorize_job = _index_jobs(jobs_payload)
    persisted_cells, catalog_present, authorization_present = _validate_artifacts(
        artifacts_payload,
        head_sha=head_sha,
    )

    base: dict[str, object] = {
        "exp015_stage_a_terminal_reviewed": True,
        "exp015_stage_a_terminal_review_decision": (
            EXP015_STAGE_A_TERMINAL_REVIEW_DECISION
        ),
        "dec263_merged_commit": DEC263_MERGED_COMMIT,
        "guarded_workflow_blob_sha": DEC264_GUARDED_WORKFLOW_BLOB_SHA,
        "catalog_source_blob_sha": EXP015_CATALOG_SOURCE_BLOB_SHA,
        "stage_a_source_blob_sha": EXP015_STAGE_A_SOURCE_BLOB_SHA,
        "exp015_cli_blob_sha": EXP015_CLI_BLOB_SHA,
        "exp015_script_blob_sha": EXP015_SCRIPT_BLOB_SHA,
        "reviewed_stage_a_run_id": run_id,
        "reviewed_stage_a_head_sha": head_sha,
        "reviewed_stage_a_run_attempt": 1,
        "reviewed_stage_a_run_conclusion": conclusion,
        "persisted_cell_artifact_count": len(persisted_cells),
        "catalog_artifact_present": catalog_present,
        "authorization_artifact_present": authorization_present,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "stage_a_retry_authorized": STAGE_A_RETRY_AUTHORIZED,
        "stage_a_replacement_authorized": STAGE_A_REPLACEMENT_AUTHORIZED,
        "stage_b_execution_authorized": STAGE_B_EXECUTION_AUTHORIZED,
        "stage_c_execution_authorized": STAGE_C_EXECUTION_AUTHORIZED,
        "portfolio_selection_authorized": PORTFOLIO_SELECTION_AUTHORIZED,
        "phase8a_acceptance_authorized": PHASE8A_ACCEPTANCE_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }

    catalog_conclusion = catalog_job.get("conclusion")
    matrix_conclusions = [job.get("conclusion") for job in matrix_jobs]
    authorization_conclusion = authorize_job.get("conclusion")

    if conclusion == "success":
        if catalog_conclusion != "success":
            raise ValueError("successful EXP-015 Stage A run requires catalog success")
        if any(item != "success" for item in matrix_conclusions):
            raise ValueError(
                "successful EXP-015 Stage A run requires all nine cells to succeed"
            )
        if authorization_conclusion != "success":
            raise ValueError(
                "successful EXP-015 Stage A run requires authorization success"
            )
        if len(persisted_cells) != 9 or not catalog_present or not authorization_present:
            raise ValueError(
                "successful EXP-015 Stage A run requires all 11 expected artifacts"
            )
        if authorization_evidence is None:
            raise ValueError(
                "successful EXP-015 Stage A run requires authorization evidence"
            )
        summary = _validate_authorization_evidence(
            authorization_evidence,
            head_sha=head_sha,
        )
        return {
            **base,
            **summary,
            "stage": "EXP015_STAGE_A_RESULT_REVIEW_REQUIRED",
            "stage_b_execution_authorized": False,
            "portfolio_selection_authorized": False,
            "phase8a_acceptance_authorized": False,
            "phase8b_authorized": False,
        }

    if authorization_evidence is not None:
        raise ValueError(
            "non-success EXP-015 Stage A run cannot claim authorization evidence"
        )
    if authorization_present:
        raise ValueError(
            "non-success EXP-015 Stage A run cannot claim final authorization artifact"
        )

    return {
        **base,
        "stage": "EXP015_STAGE_A_RUN_FAILURE_REVIEW_REQUIRED",
        "catalog_job_conclusion": catalog_conclusion,
        "successful_matrix_job_count": sum(
            item == "success" for item in matrix_conclusions
        ),
        "failed_matrix_job_count": sum(
            item == "failure" for item in matrix_conclusions
        ),
        "cancelled_matrix_job_count": sum(
            item == "cancelled" for item in matrix_conclusions
        ),
        "skipped_matrix_job_count": sum(
            item == "skipped" for item in matrix_conclusions
        ),
        "authorization_job_conclusion": authorization_conclusion,
    }


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "DEC263_MERGED_COMMIT",
    "DEC264_GUARDED_WORKFLOW_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "EXPECTED_CELLS",
    "EXP015_CATALOG_SOURCE_BLOB_SHA",
    "EXP015_CLI_BLOB_SHA",
    "EXP015_SCRIPT_BLOB_SHA",
    "EXP015_STAGE_A_SOURCE_BLOB_SHA",
    "EXP015_STAGE_A_TERMINAL_REVIEW_DECISION",
    "EXP015_STAGE_A_WORKFLOW_NAME",
    "EXP015_STAGE_A_WORKFLOW_PATH",
    "LIVE_ORDER_AUTHORIZED",
    "PHASE8A_ACCEPTANCE_AUTHORIZED",
    "PHASE8B_AUTHORIZED",
    "PORTFOLIO_SELECTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "STAGE_A_REPLACEMENT_AUTHORIZED",
    "STAGE_A_RETRY_AUTHORIZED",
    "STAGE_B_EXECUTION_AUTHORIZED",
    "STAGE_C_EXECUTION_AUTHORIZED",
    "TERMINAL_NON_SUCCESS_CONCLUSIONS",
    "TRADING_AUTHORIZED",
    "validate_exp015_stage_a_terminal_review",
]
