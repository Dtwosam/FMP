from __future__ import annotations

from typing import Mapping


EXP015_STAGE_A_FAILURE_RESULT_DECISION = "DEC-269"

DEC268_MERGED_COMMIT = "ccd5972a18afff05419ce7084b6ce7cc03c683ce"
DEC264_TERMINAL_REVIEWER_BLOB_SHA = "751c886f2d00e46d3c0a20fabbe0db4231db0d5d"
DEC264_GUARDED_WORKFLOW_BLOB_SHA = "ae8bdfbdb1bcfd62204a1bd0ec32dddfd9938930"

REVIEWED_STAGE_A_RUN_ID = 36279397331
REVIEWED_STAGE_A_HEAD_SHA = "500f12ca5cb6e611f93b5d3a9eb52fb678e7774f"
REVIEWED_STAGE_A_RUN_ATTEMPT = 1
REVIEWED_STAGE_A_RUN_CONCLUSION = "failure"

REVIEWED_CATALOG_JOB_ID = 108508225193
REVIEWED_FAILED_CELL_JOB_ID = 108508311714
REVIEWED_AUTHORIZATION_JOB_ID = 108538985395
REVIEWED_SUCCESSFUL_CELL_JOB_IDS = (
    108508311689,
    108508311695,
    108508311700,
    108508311733,
    108508311748,
    108508311751,
    108508311765,
    108508311794,
)

REVIEWED_FAILED_CELL = ("USDJPY", "1h")
EXPECTED_FAILURE_SIGNATURE = "ValueError: daily start equity must be finite and positive"
FAILURE_CLASSIFICATION = (
    "USDJPY_1H_NON_POSITIVE_OR_NON_FINITE_DAILY_START_EQUITY_FAIL_CLOSED"
)
DEC264_REVIEW_COMPATIBILITY_NOTE = (
    "DEC-264 expected short matrix job names, but GitHub persisted expanded/truncated "
    "matrix job names; DEC-269 therefore binds the exact completed run by immutable "
    "run/job/artifact identities without changing or rerunning Stage A."
)

CATALOG_ARTIFACT = {
    "id": 10918282455,
    "name": (
        "phase8a-exp015-catalog-"
        "500f12ca5cb6e611f93b5d3a9eb52fb678e7774f"
    ),
    "digest": (
        "sha256:78b7f008d5a0035d9acdb2a7169c206890c1b92ffd3a96575abc226adc212a89"
    ),
}

CELL_ARTIFACTS = {
    ("EURUSD", "1h"): {
        "id": 10917993679,
        "digest": "sha256:83c4109728f612743bed2efc0bb2da5b760a868d5498c57d9c39760de1874661",
    },
    ("EURUSD", "15m"): {
        "id": 10918849922,
        "digest": "sha256:c795e88b8bf0b08e39c155f279db546e93733a257d7a2cd9d12dfe46beed7091",
    },
    ("EURUSD", "5m"): {
        "id": 10919892108,
        "digest": "sha256:34eb6eb25c299c6230bc43d7ac00c476bb511c01b379468042712a46c153ddbc",
    },
    ("GBPUSD", "1h"): {
        "id": 10919359533,
        "digest": "sha256:83e3b02c93a74c4ebdd2bd9884fe6d59b89f07f114b75868e464848fb7ad49be",
    },
    ("GBPUSD", "15m"): {
        "id": 10919473025,
        "digest": "sha256:48081e99fa340f33309954e190ad3d16895cae92d76555484b11ec701bd591cb",
    },
    ("GBPUSD", "5m"): {
        "id": 10921711075,
        "digest": "sha256:3bf9f51ce7e6805efa8aee1911270f63c8c7a59d76326e2105b9d7bf33d909a6",
    },
    ("USDJPY", "15m"): {
        "id": 10920831214,
        "digest": "sha256:c93ed5f71ef0744f568c37c4b8c5cedd04c599e57c01dcec1d5bd629ee76510f",
    },
    ("USDJPY", "5m"): {
        "id": 10921963807,
        "digest": "sha256:00c9714813d24dfa02420b9a2c0f24120fc3e97b800c0243ed7b20d69c22c7df",
    },
}

STAGE_A_RETRY_AUTHORIZED = False
STAGE_A_REPLACEMENT_AUTHORIZED = False
STAGE_B_SOURCE_OPEN_AUTHORIZED = False
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


def _expected_cell_artifact_name(symbol: str, timeframe: str) -> str:
    return (
        f"phase8a-exp015-stage-a-{symbol}-{timeframe}-"
        f"{REVIEWED_STAGE_A_HEAD_SHA}"
    )


def _validate_run(run: Mapping[str, object]) -> None:
    exact = {
        "id": REVIEWED_STAGE_A_RUN_ID,
        "name": "phase8a-exp015-stage-a",
        "path": ".github/workflows/phase8a-exp015-stage-a.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": REVIEWED_STAGE_A_HEAD_SHA,
        "run_attempt": REVIEWED_STAGE_A_RUN_ATTEMPT,
        "status": "completed",
        "conclusion": REVIEWED_STAGE_A_RUN_CONCLUSION,
    }
    for field, expected in exact.items():
        if run.get(field) != expected:
            raise ValueError(f"DEC-269 reviewed Stage A run {field} mismatch")


def _validate_jobs(jobs_payload: Mapping[str, object]) -> None:
    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 11:
        raise ValueError("DEC-269 requires exactly 11 Stage A jobs")
    by_id: dict[int, Mapping[str, object]] = {}
    for raw in jobs:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-269 Stage A job row is malformed")
        job_id = raw.get("id")
        if not isinstance(job_id, int) or isinstance(job_id, bool) or job_id in by_id:
            raise ValueError("DEC-269 Stage A job id is malformed or duplicated")
        if raw.get("status") != "completed":
            raise ValueError("DEC-269 requires terminal Stage A jobs")
        by_id[job_id] = raw

    expected_ids = {
        REVIEWED_CATALOG_JOB_ID,
        REVIEWED_FAILED_CELL_JOB_ID,
        REVIEWED_AUTHORIZATION_JOB_ID,
        *REVIEWED_SUCCESSFUL_CELL_JOB_IDS,
    }
    if set(by_id) != expected_ids:
        raise ValueError("DEC-269 Stage A job inventory mismatch")
    if by_id[REVIEWED_CATALOG_JOB_ID].get("conclusion") != "success":
        raise ValueError("DEC-269 catalog job conclusion mismatch")
    if by_id[REVIEWED_FAILED_CELL_JOB_ID].get("conclusion") != "failure":
        raise ValueError("DEC-269 failed cell job conclusion mismatch")
    if by_id[REVIEWED_AUTHORIZATION_JOB_ID].get("conclusion") != "skipped":
        raise ValueError("DEC-269 authorization job must be skipped")
    for job_id in REVIEWED_SUCCESSFUL_CELL_JOB_IDS:
        if by_id[job_id].get("conclusion") != "success":
            raise ValueError(
                f"DEC-269 successful cell job conclusion mismatch for {job_id}"
            )


def _validate_artifacts(artifacts_payload: Mapping[str, object]) -> None:
    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 9:
        raise ValueError(
            "DEC-269 requires exactly the catalog plus eight successful cell artifacts"
        )
    by_name: dict[str, Mapping[str, object]] = {}
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-269 artifact row is malformed")
        name = raw.get("name")
        if not isinstance(name, str) or name in by_name:
            raise ValueError("DEC-269 artifact name is malformed or duplicated")
        if raw.get("expired") is not False:
            raise ValueError("DEC-269 requires non-expired Stage A artifacts")
        by_name[name] = raw

    expected_names = {str(CATALOG_ARTIFACT["name"])}
    expected_names.update(
        _expected_cell_artifact_name(symbol, timeframe)
        for symbol, timeframe in CELL_ARTIFACTS
    )
    if set(by_name) != expected_names:
        raise ValueError("DEC-269 persisted artifact inventory mismatch")

    catalog = by_name[str(CATALOG_ARTIFACT["name"])]
    if catalog.get("id") != CATALOG_ARTIFACT["id"]:
        raise ValueError("DEC-269 catalog artifact id mismatch")
    if catalog.get("digest") != CATALOG_ARTIFACT["digest"]:
        raise ValueError("DEC-269 catalog artifact digest mismatch")

    for cell, expected in CELL_ARTIFACTS.items():
        row = by_name[_expected_cell_artifact_name(*cell)]
        if row.get("id") != expected["id"]:
            raise ValueError(f"DEC-269 artifact id mismatch for {cell}")
        if row.get("digest") != expected["digest"]:
            raise ValueError(f"DEC-269 artifact digest mismatch for {cell}")

    missing_name = _expected_cell_artifact_name(*REVIEWED_FAILED_CELL)
    if missing_name in by_name:
        raise ValueError("DEC-269 failed USDJPY 1h cell cannot have a result artifact")
    authorization_name = (
        "phase8a-exp015-stage-a-authorization-"
        f"{REVIEWED_STAGE_A_HEAD_SHA}"
    )
    if authorization_name in by_name:
        raise ValueError("DEC-269 failed Stage A cannot have authorization evidence")


def validate_exp015_stage_a_reviewed_failure(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    failure_signature: str,
) -> dict[str, object]:
    _validate_run(run)
    _validate_jobs(jobs_payload)
    _validate_artifacts(artifacts_payload)
    if failure_signature != EXPECTED_FAILURE_SIGNATURE:
        raise ValueError("DEC-269 Stage A failure signature mismatch")

    return {
        "exp015_stage_a_failure_result_decision": (
            EXP015_STAGE_A_FAILURE_RESULT_DECISION
        ),
        "stage": "EXP015_STAGE_A_REVIEWED_FAILED_CLOSED",
        "reviewed_stage_a_run_id": REVIEWED_STAGE_A_RUN_ID,
        "reviewed_stage_a_head_sha": REVIEWED_STAGE_A_HEAD_SHA,
        "reviewed_stage_a_run_attempt": REVIEWED_STAGE_A_RUN_ATTEMPT,
        "reviewed_stage_a_run_conclusion": REVIEWED_STAGE_A_RUN_CONCLUSION,
        "failure_classification": FAILURE_CLASSIFICATION,
        "failure_signature": EXPECTED_FAILURE_SIGNATURE,
        "failed_symbol": REVIEWED_FAILED_CELL[0],
        "failed_timeframe": REVIEWED_FAILED_CELL[1],
        "successful_cell_count": 8,
        "failed_cell_count": 1,
        "persisted_cell_artifact_count": 8,
        "catalog_artifact_present": True,
        "authorization_artifact_present": False,
        "authoritative_stage_a_success_result_produced": False,
        "authoritative_survivor_set_produced": False,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "dec264_terminal_reviewer_compatibility_note": (
            DEC264_REVIEW_COMPATIBILITY_NOTE
        ),
        "stage_a_retry_authorized": STAGE_A_RETRY_AUTHORIZED,
        "stage_a_replacement_authorized": STAGE_A_REPLACEMENT_AUTHORIZED,
        "stage_b_source_open_authorized": STAGE_B_SOURCE_OPEN_AUTHORIZED,
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


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "CATALOG_ARTIFACT",
    "CELL_ARTIFACTS",
    "DEC264_GUARDED_WORKFLOW_BLOB_SHA",
    "DEC264_REVIEW_COMPATIBILITY_NOTE",
    "DEC264_TERMINAL_REVIEWER_BLOB_SHA",
    "DEC268_MERGED_COMMIT",
    "DEMO_ORDER_AUTHORIZED",
    "EXPECTED_FAILURE_SIGNATURE",
    "EXP015_STAGE_A_FAILURE_RESULT_DECISION",
    "FAILURE_CLASSIFICATION",
    "LIVE_ORDER_AUTHORIZED",
    "PHASE8A_ACCEPTANCE_AUTHORIZED",
    "PHASE8B_AUTHORIZED",
    "PORTFOLIO_SELECTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REVIEWED_FAILED_CELL",
    "REVIEWED_FAILED_CELL_JOB_ID",
    "REVIEWED_STAGE_A_HEAD_SHA",
    "REVIEWED_STAGE_A_RUN_ID",
    "STAGE_A_REPLACEMENT_AUTHORIZED",
    "STAGE_A_RETRY_AUTHORIZED",
    "STAGE_B_EXECUTION_AUTHORIZED",
    "STAGE_B_SOURCE_OPEN_AUTHORIZED",
    "STAGE_C_EXECUTION_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "validate_exp015_stage_a_reviewed_failure",
]
