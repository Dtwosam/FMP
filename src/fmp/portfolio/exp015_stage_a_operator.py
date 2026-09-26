from __future__ import annotations

import re
from typing import Mapping, Sequence

from .exp015_stage_a_terminal_review import DEC264_GUARDED_WORKFLOW_BLOB_SHA


REPOSITORY = "Dtwosam/FMP"
DEC264_MERGED_COMMIT = "92ef2668b1a0cb416e7f772a8a061d2f280005a1"
DEC264_TERMINAL_REVIEW_BLOB_SHA = "751c886f2d00e46d3c0a20fabbe0db4231db0d5d"
EXP015_STAGE_A_WORKFLOW_FILE = "phase8a-exp015-stage-a.yml"
EXP015_STAGE_A_WORKFLOW_PATH = ".github/workflows/phase8a-exp015-stage-a.yml"
EXP015_STAGE_A_WORKFLOW_NAME = "phase8a-exp015-stage-a"

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


def validate_exp015_stage_a_operator_checkout(
    *,
    branch: str,
    head_sha: str,
    origin_main_sha: str,
    porcelain_status: str,
    origin_url: str,
) -> dict[str, object]:
    if branch != "main":
        raise ValueError("EXP-015 Stage A operator requires the local main branch")
    head = _validate_sha(head_sha, field="local HEAD")
    origin = _validate_sha(origin_main_sha, field="origin/main")
    if head != origin:
        raise ValueError("local HEAD must exactly match fetched origin/main")
    if porcelain_status.strip():
        raise ValueError("EXP-015 Stage A operator requires a clean working tree")
    if not _remote_matches_repository(origin_url):
        raise ValueError("origin remote does not match Dtwosam/FMP")
    return {
        "repository": REPOSITORY,
        "dec264_merged_commit": DEC264_MERGED_COMMIT,
        "dec264_guarded_workflow_blob_sha": DEC264_GUARDED_WORKFLOW_BLOB_SHA,
        "dec264_terminal_review_blob_sha": DEC264_TERMINAL_REVIEW_BLOB_SHA,
        "branch": "main",
        "head_sha": head,
        "clean_worktree": True,
        "origin_verified": True,
    }


def exp015_stage_a_runs_endpoint() -> str:
    return (
        f"repos/{REPOSITORY}/actions/workflows/"
        f"{EXP015_STAGE_A_WORKFLOW_FILE}/runs"
        "?branch=main&event=workflow_dispatch&per_page=100"
    )


def _positive_run_id(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError("EXP-015 Stage A run id must be a positive integer")
    return value


def select_exp015_stage_a_manual_main_run(
    payload: Mapping[str, object],
) -> Mapping[str, object] | None:
    runs = payload.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("EXP-015 Stage A workflow-run listing is malformed")

    relevant: list[Mapping[str, object]] = []
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-015 Stage A workflow-run listing contains a malformed row"
            )
        if raw.get("event") != "workflow_dispatch":
            continue
        if raw.get("head_branch") != "main":
            continue
        relevant.append(raw)

    if len(relevant) > 1:
        ids = ", ".join(str(item.get("id")) for item in relevant)
        raise ValueError(
            "EXP-015 Stage A has multiple authoritative manual-main runs: "
            f"{ids}; DEC-264 permits only one"
        )
    if not relevant:
        return None

    run = relevant[0]
    _positive_run_id(run.get("id"))
    if run.get("name") != EXP015_STAGE_A_WORKFLOW_NAME:
        raise ValueError("EXP-015 Stage A manual-main run name mismatch")
    if run.get("path") != EXP015_STAGE_A_WORKFLOW_PATH:
        raise ValueError("EXP-015 Stage A manual-main run path mismatch")
    if run.get("run_attempt") != 1:
        raise ValueError("EXP-015 Stage A manual-main run must be attempt 1")
    _validate_sha(run.get("head_sha"), field="EXP-015 Stage A run head SHA")
    status = run.get("status")
    conclusion = run.get("conclusion")
    if not isinstance(status, str) or not status:
        raise ValueError("EXP-015 Stage A manual-main run status is invalid")
    if conclusion is not None and not isinstance(conclusion, str):
        raise ValueError("EXP-015 Stage A manual-main run conclusion is invalid")
    return run


def classify_exp015_stage_a_run(
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
    state = "TERMINAL" if status == "completed" else "IN_PROGRESS"
    return {
        "run_present": True,
        "run_state": state,
        "run_id": run_id,
        "status": status,
        "conclusion": conclusion,
        "run_head_sha": _validate_sha(
            run.get("head_sha"),
            field="EXP-015 Stage A run head SHA",
        ),
    }


def exp015_stage_a_planned_dispatch_command() -> tuple[str, ...]:
    return (
        "gh",
        "workflow",
        "run",
        EXP015_STAGE_A_WORKFLOW_FILE,
        "--ref",
        "main",
        "-R",
        REPOSITORY,
    )


def shell_join(command: Sequence[str]) -> str:
    safe: list[str] = []
    for part in command:
        if not part or re.search(r"[^A-Za-z0-9_./:=@+-]", part):
            safe.append("'" + part.replace("'", "'\\''") + "'")
        else:
            safe.append(part)
    return " ".join(safe)


def build_exp015_stage_a_operator_report(
    *,
    checkout: Mapping[str, object],
    run: Mapping[str, object] | None,
) -> dict[str, object]:
    state = classify_exp015_stage_a_run(run)
    common: dict[str, object] = {
        **dict(checkout),
        **state,
        "operator_read_only": True,
        "stage_a_dispatch_authorized": False,
        "stage_a_executor_authorized": False,
        "stage_a_retry_authorized": False,
        "stage_a_replacement_authorized": False,
        "stage_b_execution_authorized": False,
        "stage_c_execution_authorized": False,
        "portfolio_selection_authorized": False,
        "phase8a_acceptance_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }

    if state["run_state"] == "MISSING":
        command = exp015_stage_a_planned_dispatch_command()
        return {
            **common,
            "stage": "EXP015_STAGE_A_READ_ONLY_PROOF_REQUIRED",
            "next_action": (
                "Prove the missing authoritative Stage A slot from merged main "
                "with a repository-hosted read-only plan before any executor is considered."
            ),
            "authoritative_slot_available": True,
            "read_only_proof_required": True,
            "planned_dispatch_command": shell_join(command),
        }

    if state["run_state"] == "IN_PROGRESS":
        return {
            **common,
            "stage": "EXP015_STAGE_A_RUN_IN_PROGRESS",
            "next_action": (
                "Inspect the existing authoritative Stage A run; "
                "do not dispatch, retry, rerun, or replace it."
            ),
            "authoritative_slot_available": False,
            "read_only_proof_required": False,
        }

    return {
        **common,
        "stage": "EXP015_STAGE_A_TERMINAL_REVIEW_REQUIRED",
        "next_action": (
            "Validate the terminal Stage A run through the frozen DEC-264 "
            "terminal-review contract; do not retry, rerun, or replace it."
        ),
        "authoritative_slot_available": False,
        "read_only_proof_required": False,
    }


def validate_exp015_stage_a_operator_report(
    report: Mapping[str, object],
) -> dict[str, object]:
    if report.get("operator_read_only") is not True:
        raise ValueError("EXP-015 Stage A operator report must remain read-only")

    locked = (
        "stage_a_dispatch_authorized",
        "stage_a_executor_authorized",
        "stage_a_retry_authorized",
        "stage_a_replacement_authorized",
        "stage_b_execution_authorized",
        "stage_c_execution_authorized",
        "portfolio_selection_authorized",
        "phase8a_acceptance_authorized",
        "phase8b_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    )
    for field in locked:
        if report.get(field) is not False:
            raise ValueError(f"EXP-015 Stage A operator report {field} must remain false")

    stage = report.get("stage")
    if stage == "EXP015_STAGE_A_READ_ONLY_PROOF_REQUIRED":
        expected = shell_join(exp015_stage_a_planned_dispatch_command())
        if report.get("run_state") != "MISSING":
            raise ValueError("EXP-015 Stage A proof-required report must be MISSING")
        if report.get("authoritative_slot_available") is not True:
            raise ValueError("EXP-015 Stage A missing report must preserve the open slot")
        if report.get("read_only_proof_required") is not True:
            raise ValueError("EXP-015 Stage A missing report requires read-only proof")
        if report.get("planned_dispatch_command") != expected:
            raise ValueError("EXP-015 Stage A planned dispatch command mismatch")
    else:
        if report.get("run_state") not in {"IN_PROGRESS", "TERMINAL"}:
            raise ValueError("EXP-015 Stage A non-missing report state mismatch")
        if report.get("authoritative_slot_available") is not False:
            raise ValueError("EXP-015 Stage A used slot cannot remain available")
        if report.get("read_only_proof_required") is not False:
            raise ValueError("EXP-015 Stage A used slot cannot require missing-state proof")
        if "planned_dispatch_command" in report:
            raise ValueError(
                "EXP-015 Stage A non-missing report cannot expose a dispatch plan"
            )

    return dict(report)


__all__ = [
    "DEC264_MERGED_COMMIT",
    "DEC264_TERMINAL_REVIEW_BLOB_SHA",
    "EXP015_STAGE_A_WORKFLOW_FILE",
    "EXP015_STAGE_A_WORKFLOW_NAME",
    "EXP015_STAGE_A_WORKFLOW_PATH",
    "REPOSITORY",
    "build_exp015_stage_a_operator_report",
    "classify_exp015_stage_a_run",
    "exp015_stage_a_planned_dispatch_command",
    "exp015_stage_a_runs_endpoint",
    "select_exp015_stage_a_manual_main_run",
    "shell_join",
    "validate_exp015_stage_a_operator_checkout",
    "validate_exp015_stage_a_operator_report",
]
