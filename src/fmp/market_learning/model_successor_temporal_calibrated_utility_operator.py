from __future__ import annotations

import re
from typing import Mapping, Sequence


REPOSITORY = "Dtwosam/FMP"
DEC155_MERGED_COMMIT = "a8b6204faccf411fd489ca5a1d004d90ed75be33"
TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_FILE = (
    "phase8a-exp051-temporal-calibrated-utility-model-training.yml"
)
TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_PATH = (
    ".github/workflows/"
    "phase8a-exp051-temporal-calibrated-utility-model-training.yml"
)
TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_NAME = (
    "phase8a-exp051-temporal-calibrated-utility-model-training"
)

_SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")


def _validate_sha(value: object, *, field: str) -> str:
    if not isinstance(value, str) or _SHA40.fullmatch(value) is None:
        raise ValueError(
            f"{field} must be a 40-character Git SHA"
        )
    return value.lower()


def _remote_matches_repository(remote_url: str) -> bool:
    normalized = remote_url.strip().removesuffix("/")
    accepted = {
        f"https://github.com/{REPOSITORY}",
        f"https://github.com/{REPOSITORY}.git",
        f"git@github.com:{REPOSITORY}",
        f"git@github.com:{REPOSITORY}.git",
        f"ssh://git@github.com/{REPOSITORY}",
        f"ssh://git@github.com/{REPOSITORY}.git",
    }
    return normalized in accepted


def validate_temporal_calibrated_utility_operator_checkout(
    *,
    branch: str,
    head_sha: str,
    origin_main_sha: str,
    porcelain_status: str,
    origin_url: str,
) -> dict[str, object]:
    if branch != "main":
        raise ValueError(
            "EXP-051 dispatch requires the local main branch"
        )
    head = _validate_sha(
        head_sha,
        field="local HEAD",
    )
    origin = _validate_sha(
        origin_main_sha,
        field="origin/main",
    )
    if head != origin:
        raise ValueError(
            "local HEAD must exactly match fetched origin/main"
        )
    if porcelain_status.strip():
        raise ValueError(
            "EXP-051 dispatch requires a clean working tree"
        )
    if not _remote_matches_repository(origin_url):
        raise ValueError(
            "origin remote does not match Dtwosam/FMP"
        )
    return {
        "repository": REPOSITORY,
        "dec155_merged_commit": DEC155_MERGED_COMMIT,
        "branch": "main",
        "head_sha": head,
        "clean_worktree": True,
        "origin_verified": True,
    }


def temporal_calibrated_utility_model_runs_endpoint() -> str:
    return (
        f"repos/{REPOSITORY}/actions/workflows/"
        f"{TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_FILE}/runs"
        "?branch=main&event=workflow_dispatch&per_page=100"
    )


def _positive_run_id(value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value <= 0
    ):
        raise ValueError(
            "EXP-051 model run id must be a positive integer"
        )
    return value


def temporal_calibrated_utility_model_run_endpoint(
    run_id: int,
) -> str:
    value = _positive_run_id(run_id)
    return f"repos/{REPOSITORY}/actions/runs/{value}"


def temporal_calibrated_utility_model_run_jobs_endpoint(
    run_id: int,
) -> str:
    value = _positive_run_id(run_id)
    return (
        f"repos/{REPOSITORY}/actions/runs/{value}/"
        "jobs?per_page=100"
    )


def temporal_calibrated_utility_model_run_artifacts_endpoint(
    run_id: int,
) -> str:
    value = _positive_run_id(run_id)
    return (
        f"repos/{REPOSITORY}/actions/runs/{value}/"
        "artifacts?per_page=100"
    )


def temporal_calibrated_utility_artifact_download_endpoint(
    artifact_id: int,
) -> str:
    if (
        not isinstance(artifact_id, int)
        or isinstance(artifact_id, bool)
        or artifact_id <= 0
    ):
        raise ValueError(
            "EXP-051 artifact id must be a positive integer"
        )
    return (
        f"repos/{REPOSITORY}/actions/artifacts/"
        f"{artifact_id}/zip"
    )


def select_temporal_calibrated_utility_manual_main_run(
    payload: Mapping[str, object],
) -> Mapping[str, object] | None:
    runs = payload.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError(
            "EXP-051 workflow-run listing is malformed"
        )

    relevant: list[Mapping[str, object]] = []
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-051 workflow-run listing contains a malformed row"
            )
        if raw.get("event") != "workflow_dispatch":
            continue
        if raw.get("head_branch") != "main":
            continue
        relevant.append(raw)

    if len(relevant) > 1:
        ids = ", ".join(
            str(raw.get("id"))
            for raw in relevant
        )
        raise ValueError(
            "EXP-051 workflow has multiple manual main runs: "
            f"{ids}; DEC-155 authorizes only one"
        )
    if not relevant:
        return None

    run = relevant[0]
    _positive_run_id(run.get("id"))
    if (
        run.get("name")
        != TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_NAME
    ):
        raise ValueError(
            "EXP-051 manual main run name mismatch"
        )
    if (
        run.get("path")
        != TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_PATH
    ):
        raise ValueError(
            "EXP-051 manual main run path mismatch"
        )
    status = run.get("status")
    conclusion = run.get("conclusion")
    if not isinstance(status, str) or not status:
        raise ValueError(
            "EXP-051 manual main run status is invalid"
        )
    if (
        conclusion is not None
        and not isinstance(conclusion, str)
    ):
        raise ValueError(
            "EXP-051 manual main run conclusion is invalid"
        )
    return run


def classify_temporal_calibrated_utility_model_run(
    run: Mapping[str, object] | None,
) -> dict[str, object]:
    if run is None:
        return {
            "run_present": False,
            "run_state": "MISSING",
            "run_id": None,
        }

    run_id = _positive_run_id(run.get("id"))
    status = run.get("status")
    conclusion = run.get("conclusion")
    state = (
        "TERMINAL"
        if status == "completed"
        else "IN_PROGRESS"
    )
    return {
        "run_present": True,
        "run_state": state,
        "run_id": run_id,
        "status": status,
        "conclusion": conclusion,
    }


def temporal_calibrated_utility_model_dispatch_command(
) -> tuple[str, ...]:
    return (
        "gh",
        "workflow",
        "run",
        TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_FILE,
        "--ref",
        "main",
        "-R",
        REPOSITORY,
    )


def shell_join(command: Sequence[str]) -> str:
    safe: list[str] = []
    for part in command:
        if (
            not part
            or re.search(r"[^A-Za-z0-9_./:=@+-]", part)
        ):
            safe.append(
                "'" + part.replace("'", "'\\''") + "'"
            )
        else:
            safe.append(part)
    return " ".join(safe)


def build_temporal_calibrated_utility_operator_report(
    *,
    checkout: Mapping[str, object],
    run: Mapping[str, object] | None,
) -> dict[str, object]:
    state = classify_temporal_calibrated_utility_model_run(
        run
    )
    common: dict[str, object] = {
        **dict(checkout),
        **state,
        "read_only": True,
        "prior_result_informed": True,
        "untouched_oos": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }

    if state["run_state"] == "MISSING":
        command = (
            temporal_calibrated_utility_model_dispatch_command()
        )
        return {
            **common,
            "stage": (
                "TEMPORAL_CALIBRATED_UTILITY_MODEL_"
                "RUN_DISPATCH_REQUIRED"
            ),
            "next_action": (
                "Dispatch exactly one guarded historical EXP-051 "
                "model workflow from clean current main."
            ),
            "dispatch_command": shell_join(command),
            "temporal_calibrated_utility_model_run_dispatch_authorized": (
                True
            ),
            "authoritative_temporal_calibrated_utility_model_result_execution_authorized": (
                True
            ),
            "model_protocol_result_authorized": True,
            "model_fit_authorized": True,
            "replacement_model_run_authorized": False,
        }

    if state["run_state"] == "IN_PROGRESS":
        return {
            **common,
            "stage": (
                "TEMPORAL_CALIBRATED_UTILITY_MODEL_"
                "RUN_IN_PROGRESS"
            ),
            "next_action": (
                "Inspect the existing EXP-051 model run; "
                "do not dispatch another run."
            ),
            "temporal_calibrated_utility_model_run_dispatch_authorized": (
                False
            ),
            "authoritative_temporal_calibrated_utility_model_result_execution_authorized": (
                False
            ),
            "model_protocol_result_authorized": False,
            "model_fit_authorized": False,
            "replacement_model_run_authorized": False,
        }

    return {
        **common,
        "stage": (
            "TEMPORAL_CALIBRATED_UTILITY_MODEL_"
            "TERMINAL_REVIEW_REQUIRED"
        ),
        "next_action": (
            "Validate the terminal run through the frozen DEC-154 "
            "review contract; do not dispatch another run."
        ),
        "temporal_calibrated_utility_model_run_dispatch_authorized": (
            False
        ),
        "authoritative_temporal_calibrated_utility_model_result_execution_authorized": (
            False
        ),
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "replacement_model_run_authorized": False,
    }


def temporal_calibrated_utility_operator_gate_metadata(
    gate: Mapping[str, object],
) -> dict[str, object]:
    decisions = {
        "temporal_calibrated_utility_model_execution_gate_decision": (
            "DEC-153"
        ),
        "temporal_calibrated_utility_model_execution_authorization_decision": (
            "DEC-155"
        ),
    }
    for field, expected in decisions.items():
        if gate.get(field) != expected:
            raise ValueError(
                f"EXP-051 operator gate {field} mismatch"
            )

    sha_fields = (
        "dec150_merged_commit",
        "dec151_merged_commit",
        "dec152_merged_commit",
        "dec153_merged_commit",
        "dec154_merged_commit",
        "dec153_workflow_blob_sha",
        "dec153_cli_blob_sha",
        "dec153_gate_blob_sha",
        "dec154_review_blob_sha",
        "temporal_calibrated_utility_workflow_blob_sha",
        "temporal_calibrated_utility_cli_blob_sha",
    )
    metadata: dict[str, object] = dict(decisions)
    for field in sha_fields:
        metadata[field] = _validate_sha(
            gate.get(field),
            field=f"EXP-051 operator gate {field}",
        )
    return metadata


def dispatch_command_for_temporal_calibrated_utility_report(
    report: Mapping[str, object],
) -> tuple[str, ...] | None:
    if report.get("read_only") is not True:
        raise ValueError(
            "EXP-051 next report must be explicitly read-only"
        )

    for field in (
        "promotion_authorized",
        "shadow_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
        "replacement_model_run_authorized",
    ):
        if report.get(field) is not False:
            raise ValueError(
                f"EXP-051 next report {field} must remain false"
            )

    stage = report.get("stage")
    if stage != (
        "TEMPORAL_CALIBRATED_UTILITY_MODEL_"
        "RUN_DISPATCH_REQUIRED"
    ):
        for field in (
            "temporal_calibrated_utility_model_run_dispatch_authorized",
            "authoritative_temporal_calibrated_utility_model_result_execution_authorized",
            "model_protocol_result_authorized",
            "model_fit_authorized",
        ):
            if report.get(field) is not False:
                raise ValueError(
                    f"EXP-051 non-dispatch report {field} "
                    "must be false"
                )
        if "dispatch_command" in report:
            raise ValueError(
                "EXP-051 non-dispatch report must not contain "
                "a dispatch command"
            )
        return None

    for field in (
        "temporal_calibrated_utility_model_run_dispatch_authorized",
        "authoritative_temporal_calibrated_utility_model_result_execution_authorized",
        "model_protocol_result_authorized",
        "model_fit_authorized",
    ):
        if report.get(field) is not True:
            raise ValueError(
                f"EXP-051 dispatch report {field} must be true"
            )

    command = (
        temporal_calibrated_utility_model_dispatch_command()
    )
    if report.get("dispatch_command") != shell_join(command):
        raise ValueError(
            "EXP-051 dispatch command does not match frozen workflow"
        )
    return command


def select_temporal_calibrated_utility_aggregate_artifact(
    payload: Mapping[str, object],
    *,
    head_sha: str,
) -> dict[str, object]:
    sha = _validate_sha(
        head_sha,
        field="EXP-051 model-result head SHA",
    )
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError(
            "EXP-051 artifact listing is malformed"
        )
    expected = (
        f"exp051-temporal-calibrated-utility-model-result-evidence-{sha}-"
        "from-feature-35867307338-outcome-35876715434"
    )
    matches: list[Mapping[str, object]] = []
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-051 artifact listing contains a malformed row"
            )
        if raw.get("name") != expected:
            continue
        if raw.get("expired") is not False:
            continue
        matches.append(raw)

    if len(matches) != 1:
        raise ValueError(
            "expected exactly one non-expired EXP-051 aggregate "
            f"artifact: {expected}"
        )
    artifact_id = matches[0].get("id")
    if (
        not isinstance(artifact_id, int)
        or isinstance(artifact_id, bool)
        or artifact_id <= 0
    ):
        raise ValueError(
            "EXP-051 aggregate artifact id is invalid"
        )
    return {
        "artifact_id": artifact_id,
        "artifact_name": expected,
        "head_sha": sha,
    }


__all__ = [
    "DEC155_MERGED_COMMIT",
    "REPOSITORY",
    "TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_FILE",
    "TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_NAME",
    "TEMPORAL_CALIBRATED_UTILITY_MODEL_WORKFLOW_PATH",
    "build_temporal_calibrated_utility_operator_report",
    "classify_temporal_calibrated_utility_model_run",
    "dispatch_command_for_temporal_calibrated_utility_report",
    "select_temporal_calibrated_utility_aggregate_artifact",
    "select_temporal_calibrated_utility_manual_main_run",
    "shell_join",
    "temporal_calibrated_utility_artifact_download_endpoint",
    "temporal_calibrated_utility_model_dispatch_command",
    "temporal_calibrated_utility_model_run_artifacts_endpoint",
    "temporal_calibrated_utility_model_run_endpoint",
    "temporal_calibrated_utility_model_run_jobs_endpoint",
    "temporal_calibrated_utility_model_runs_endpoint",
    "temporal_calibrated_utility_operator_gate_metadata",
    "validate_temporal_calibrated_utility_operator_checkout",
]
