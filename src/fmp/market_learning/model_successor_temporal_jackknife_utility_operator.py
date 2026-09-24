from __future__ import annotations

import re
from typing import Mapping, Sequence


REPOSITORY = "Dtwosam/FMP"
DEC146_MERGED_COMMIT = "dd40df2522cf3ae9cfa5802d3d2a95a995570981"
TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_FILE = "phase8a-exp050-temporal-jackknife-utility-model-training.yml"
TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp050-temporal-jackknife-utility-model-training.yml"
)
TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_NAME = "phase8a-exp050-temporal-jackknife-utility-model-training"

_SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")


def _validate_sha(value: object, *, field: str) -> str:
    if not isinstance(value, str) or _SHA40.fullmatch(value) is None:
        raise ValueError(f"{field} must be a 40-character Git SHA")
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


def validate_temporal_jackknife_utility_operator_checkout(
    *,
    branch: str,
    head_sha: str,
    origin_main_sha: str,
    porcelain_status: str,
    origin_url: str,
) -> dict[str, object]:
    if branch != "main":
        raise ValueError(
            "EXP-050 dispatch requires the local main branch"
        )
    head = _validate_sha(head_sha, field="local HEAD")
    origin = _validate_sha(origin_main_sha, field="origin/main")
    if head != origin:
        raise ValueError(
            "local HEAD must exactly match fetched origin/main"
        )
    if porcelain_status.strip():
        raise ValueError(
            "EXP-050 dispatch requires a clean working tree"
        )
    if not _remote_matches_repository(origin_url):
        raise ValueError(
            "origin remote does not match Dtwosam/FMP"
        )
    return {
        "repository": REPOSITORY,
        "dec137_merged_commit": DEC146_MERGED_COMMIT,
        "branch": "main",
        "head_sha": head,
        "clean_worktree": True,
        "origin_verified": True,
    }


def temporal_jackknife_utility_model_runs_endpoint() -> str:
    return (
        f"repos/{REPOSITORY}/actions/workflows/"
        f"{TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_FILE}/runs"
        "?branch=main&event=workflow_dispatch&per_page=100"
    )


def _positive_run_id(value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value <= 0
    ):
        raise ValueError(
            "EXP-050 model run id must be a positive integer"
        )
    return value


def temporal_jackknife_utility_model_run_endpoint(run_id: int) -> str:
    value = _positive_run_id(run_id)
    return f"repos/{REPOSITORY}/actions/runs/{value}"


def temporal_jackknife_utility_model_run_jobs_endpoint(run_id: int) -> str:
    value = _positive_run_id(run_id)
    return (
        f"repos/{REPOSITORY}/actions/runs/{value}/jobs?per_page=100"
    )


def temporal_jackknife_utility_model_run_artifacts_endpoint(run_id: int) -> str:
    value = _positive_run_id(run_id)
    return (
        f"repos/{REPOSITORY}/actions/runs/{value}/"
        "artifacts?per_page=100"
    )


def temporal_jackknife_utility_artifact_download_endpoint(
    artifact_id: int,
) -> str:
    if (
        not isinstance(artifact_id, int)
        or isinstance(artifact_id, bool)
        or artifact_id <= 0
    ):
        raise ValueError(
            "EXP-050 artifact id must be a positive integer"
        )
    return (
        f"repos/{REPOSITORY}/actions/artifacts/"
        f"{artifact_id}/zip"
    )


def select_temporal_jackknife_utility_manual_main_run(
    payload: Mapping[str, object],
) -> Mapping[str, object] | None:
    runs = payload.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError(
            "EXP-050 workflow-run listing is malformed"
        )

    relevant: list[Mapping[str, object]] = []
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-050 workflow-run listing contains a malformed row"
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
            "EXP-050 workflow has multiple manual main runs: "
            f"{ids}; DEC-146 authorizes only one"
        )
    if not relevant:
        return None

    run = relevant[0]
    _positive_run_id(run.get("id"))
    if run.get("name") != TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_NAME:
        raise ValueError(
            "EXP-050 manual main run name mismatch"
        )
    if run.get("path") != TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_PATH:
        raise ValueError(
            "EXP-050 manual main run path mismatch"
        )
    status = run.get("status")
    conclusion = run.get("conclusion")
    if not isinstance(status, str) or not status:
        raise ValueError(
            "EXP-050 manual main run status is invalid"
        )
    if (
        conclusion is not None
        and not isinstance(conclusion, str)
    ):
        raise ValueError(
            "EXP-050 manual main run conclusion is invalid"
        )
    return run


def classify_temporal_jackknife_utility_model_run(
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
    if status != "completed":
        state = "IN_PROGRESS"
    else:
        state = "TERMINAL"
    return {
        "run_present": True,
        "run_state": state,
        "run_id": run_id,
        "status": status,
        "conclusion": conclusion,
    }


def temporal_jackknife_utility_model_dispatch_command() -> tuple[str, ...]:
    return (
        "gh",
        "workflow",
        "run",
        TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_FILE,
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


def build_temporal_jackknife_utility_operator_report(
    *,
    checkout: Mapping[str, object],
    run: Mapping[str, object] | None,
) -> dict[str, object]:
    state = classify_temporal_jackknife_utility_model_run(run)
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
        command = temporal_jackknife_utility_model_dispatch_command()
        return {
            **common,
            "stage": "TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_REQUIRED",
            "next_action": (
                "Dispatch exactly one guarded historical EXP-050 "
                "model workflow from clean current main."
            ),
            "dispatch_command": shell_join(command),
            "temporal_jackknife_utility_model_run_dispatch_authorized": True,
            "authoritative_temporal_jackknife_utility_model_result_execution_authorized": True,
            "model_protocol_result_authorized": True,
            "model_fit_authorized": True,
            "replacement_model_run_authorized": False,
        }

    if state["run_state"] == "IN_PROGRESS":
        return {
            **common,
            "stage": "TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_IN_PROGRESS",
            "next_action": (
                "Inspect the existing EXP-050 model run; "
                "do not dispatch another run."
            ),
            "temporal_jackknife_utility_model_run_dispatch_authorized": False,
            "authoritative_temporal_jackknife_utility_model_result_execution_authorized": False,
            "model_protocol_result_authorized": False,
            "model_fit_authorized": False,
            "replacement_model_run_authorized": False,
        }

    return {
        **common,
        "stage": "TEMPORAL_JACKKNIFE_UTILITY_MODEL_TERMINAL_REVIEW_REQUIRED",
        "next_action": (
            "Validate the terminal run through the frozen DEC-145 "
            "review contract; do not dispatch another run."
        ),
        "temporal_jackknife_utility_model_run_dispatch_authorized": False,
        "authoritative_temporal_jackknife_utility_model_result_execution_authorized": False,
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "replacement_model_run_authorized": False,
    }


def temporal_jackknife_utility_operator_gate_metadata(
    gate: Mapping[str, object],
) -> dict[str, object]:
    decisions = {
        "temporal_jackknife_utility_model_execution_gate_decision": "DEC-144",
        "temporal_jackknife_utility_model_execution_authorization_decision": "DEC-146",
    }
    for field, expected in decisions.items():
        if gate.get(field) != expected:
            raise ValueError(
                f"EXP-050 operator gate {field} mismatch"
            )

    sha_fields = (
        "dec141_merged_commit",
        "dec142_merged_commit",
        "dec143_merged_commit",
        "dec144_merged_commit",
        "dec145_merged_commit",
        "dec144_workflow_blob_sha",
        "dec144_cli_blob_sha",
        "dec144_gate_blob_sha",
        "dec145_review_blob_sha",
        "temporal_jackknife_utility_workflow_blob_sha",
        "temporal_jackknife_utility_cli_blob_sha",
    )
    metadata: dict[str, object] = dict(decisions)
    for field in sha_fields:
        metadata[field] = _validate_sha(
            gate.get(field),
            field=f"EXP-050 operator gate {field}",
        )
    return metadata


def dispatch_command_for_temporal_jackknife_utility_report(
    report: Mapping[str, object],
) -> tuple[str, ...] | None:
    if report.get("read_only") is not True:
        raise ValueError(
            "EXP-050 next report must be explicitly read-only"
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
                f"EXP-050 next report {field} must remain false"
            )

    stage = report.get("stage")
    if stage != "TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_DISPATCH_REQUIRED":
        for field in (
            "temporal_jackknife_utility_model_run_dispatch_authorized",
            "authoritative_temporal_jackknife_utility_model_result_execution_authorized",
            "model_protocol_result_authorized",
            "model_fit_authorized",
        ):
            if report.get(field) is not False:
                raise ValueError(
                    f"EXP-050 non-dispatch report {field} "
                    "must be false"
                )
        if "dispatch_command" in report:
            raise ValueError(
                "EXP-050 non-dispatch report must not contain "
                "a dispatch command"
            )
        return None

    for field in (
        "temporal_jackknife_utility_model_run_dispatch_authorized",
        "authoritative_temporal_jackknife_utility_model_result_execution_authorized",
        "model_protocol_result_authorized",
        "model_fit_authorized",
    ):
        if report.get(field) is not True:
            raise ValueError(
                f"EXP-050 dispatch report {field} must be true"
            )

    command = temporal_jackknife_utility_model_dispatch_command()
    if report.get("dispatch_command") != shell_join(command):
        raise ValueError(
            "EXP-050 dispatch command does not match frozen workflow"
        )
    return command


def select_temporal_jackknife_utility_aggregate_artifact(
    payload: Mapping[str, object],
    *,
    head_sha: str,
) -> dict[str, object]:
    sha = _validate_sha(
        head_sha,
        field="EXP-050 model-result head SHA",
    )
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError(
            "EXP-050 artifact listing is malformed"
        )
    expected = (
        f"exp050-temporal-jackknife-utility-model-result-evidence-{sha}-"
        "from-feature-35867307338-outcome-35876715434"
    )
    matches: list[Mapping[str, object]] = []
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-050 artifact listing contains a malformed row"
            )
        if raw.get("name") != expected:
            continue
        if raw.get("expired") is not False:
            continue
        matches.append(raw)

    if len(matches) != 1:
        raise ValueError(
            "expected exactly one non-expired EXP-050 aggregate "
            f"artifact: {expected}"
        )
    artifact_id = matches[0].get("id")
    if (
        not isinstance(artifact_id, int)
        or isinstance(artifact_id, bool)
        or artifact_id <= 0
    ):
        raise ValueError(
            "EXP-050 aggregate artifact id is invalid"
        )
    return {
        "artifact_id": artifact_id,
        "artifact_name": expected,
        "head_sha": sha,
    }


__all__ = [
    "DEC146_MERGED_COMMIT",
    "REPOSITORY",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_FILE",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_NAME",
    "TEMPORAL_JACKKNIFE_UTILITY_MODEL_WORKFLOW_PATH",
    "build_temporal_jackknife_utility_operator_report",
    "classify_temporal_jackknife_utility_model_run",
    "temporal_jackknife_utility_operator_gate_metadata",
    "dispatch_command_for_temporal_jackknife_utility_report",
    "select_temporal_jackknife_utility_aggregate_artifact",
    "select_temporal_jackknife_utility_manual_main_run",
    "shell_join",
    "temporal_jackknife_utility_artifact_download_endpoint",
    "temporal_jackknife_utility_model_dispatch_command",
    "temporal_jackknife_utility_model_run_artifacts_endpoint",
    "temporal_jackknife_utility_model_run_endpoint",
    "temporal_jackknife_utility_model_run_jobs_endpoint",
    "temporal_jackknife_utility_model_runs_endpoint",
    "validate_temporal_jackknife_utility_operator_checkout",
]
