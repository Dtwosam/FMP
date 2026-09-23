from __future__ import annotations

import re
from typing import Mapping, Sequence


REPOSITORY = "Dtwosam/FMP"
FEATURE_WORKFLOW_FILE = "phase8a-exp044-market-features.yml"
FEATURE_WORKFLOW_PATH = ".github/workflows/phase8a-exp044-market-features.yml"
FEATURE_WORKFLOW_NAME = "phase8a-exp044-market-features"
OUTCOME_WORKFLOW_FILE = "phase8a-exp044-market-outcomes.yml"
OUTCOME_WORKFLOW_PATH = ".github/workflows/phase8a-exp044-market-outcomes.yml"
OUTCOME_WORKFLOW_NAME = "phase8a-exp044-market-outcomes"

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


def validate_operator_checkout(
    *,
    branch: str,
    head_sha: str,
    origin_main_sha: str,
    porcelain_status: str,
    origin_url: str,
) -> dict[str, object]:
    if branch != "main":
        raise ValueError("EXP-044 dispatch requires the local main branch")
    head = _validate_sha(head_sha, field="local HEAD")
    origin = _validate_sha(origin_main_sha, field="origin/main")
    if head != origin:
        raise ValueError("local HEAD must exactly match fetched origin/main")
    if porcelain_status.strip():
        raise ValueError("EXP-044 dispatch requires a clean working tree")
    if not _remote_matches_repository(origin_url):
        raise ValueError("origin remote does not match Dtwosam/FMP")
    return {
        "repository": REPOSITORY,
        "branch": "main",
        "head_sha": head,
        "clean_worktree": True,
        "origin_verified": True,
    }


def validate_no_existing_manual_runs(
    payload: Mapping[str, object],
    *,
    workflow_name: str,
) -> None:
    runs = payload.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("workflow-run listing is malformed")
    relevant = []
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError("workflow-run listing contains a malformed row")
        if raw.get("event") != "workflow_dispatch":
            continue
        if raw.get("head_branch") != "main":
            continue
        relevant.append(raw)
    if relevant:
        ids = []
        for raw in relevant:
            run_id = raw.get("id")
            ids.append(str(run_id) if isinstance(run_id, int) else "unknown")
        raise ValueError(
            f"{workflow_name} already has manual main run(s): {', '.join(ids)}; "
            "inspect existing evidence instead of creating a duplicate"
        )


def validate_feature_run_for_outcomes(
    run: Mapping[str, object],
    *,
    expected_run_id: int,
) -> dict[str, object]:
    if not isinstance(expected_run_id, int) or isinstance(expected_run_id, bool) or expected_run_id <= 0:
        raise ValueError("feature run id must be a positive integer")
    if run.get("id") != expected_run_id:
        raise ValueError("feature workflow run id mismatch")
    if run.get("name") != FEATURE_WORKFLOW_NAME:
        raise ValueError("feature workflow run name mismatch")
    if run.get("path") != FEATURE_WORKFLOW_PATH:
        raise ValueError("feature workflow run path mismatch")
    if run.get("event") != "workflow_dispatch":
        raise ValueError("feature workflow run must be workflow_dispatch")
    if run.get("head_branch") != "main":
        raise ValueError("feature workflow run must originate from main")
    if run.get("status") != "completed":
        raise ValueError("feature workflow run is not completed")
    if run.get("conclusion") != "success":
        raise ValueError("feature workflow run did not succeed")
    head_sha = _validate_sha(run.get("head_sha"), field="feature workflow head_sha")
    return {
        "feature_run_id": expected_run_id,
        "feature_head_sha": head_sha,
        "feature_run_verified": True,
    }


def select_feature_evidence_artifact(
    payload: Mapping[str, object],
    *,
    feature_head_sha: str,
) -> dict[str, object]:
    sha = _validate_sha(feature_head_sha, field="feature evidence head SHA")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("feature artifact listing is malformed")
    expected = f"exp044-market-feature-evidence-{sha}"
    matches: list[Mapping[str, object]] = []
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError("feature artifact listing contains a malformed row")
        if raw.get("name") != expected:
            continue
        if raw.get("expired") is not False:
            continue
        matches.append(raw)
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one non-expired aggregate feature evidence artifact: {expected}"
        )
    artifact_id = matches[0].get("id")
    if not isinstance(artifact_id, int) or isinstance(artifact_id, bool) or artifact_id <= 0:
        raise ValueError("aggregate feature evidence artifact id is invalid")
    return {
        "artifact_id": artifact_id,
        "artifact_name": expected,
        "feature_head_sha": sha,
    }


def validate_feature_evidence_for_outcomes(
    evidence: Mapping[str, object],
    *,
    expected_code_commit: str,
) -> dict[str, object]:
    sha = _validate_sha(expected_code_commit, field="expected feature evidence commit")
    if evidence.get("code_commit") != sha:
        raise ValueError("aggregate feature evidence code commit mismatch")
    if evidence.get("feature_evidence_complete") is not True:
        raise ValueError("aggregate feature evidence is not complete")
    if evidence.get("verified_cell_count") != 9:
        raise ValueError("aggregate feature evidence must contain exactly nine cells")
    fingerprint = evidence.get("evidence_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("aggregate feature evidence fingerprint is invalid")
    try:
        int(fingerprint, 16)
    except ValueError as exc:
        raise ValueError("aggregate feature evidence fingerprint must be hexadecimal") from exc
    for field in (
        "model_fit_authorized",
        "shadow_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
    ):
        if evidence.get(field) is not False:
            raise ValueError(f"aggregate feature evidence {field} must remain false")
    return {
        "feature_evidence_verified": True,
        "feature_evidence_fingerprint": fingerprint,
        "feature_evidence_code_commit": sha,
    }


def feature_runs_endpoint() -> str:
    return (
        f"repos/{REPOSITORY}/actions/workflows/{FEATURE_WORKFLOW_FILE}/runs"
        "?branch=main&event=workflow_dispatch&per_page=100"
    )


def outcome_runs_endpoint() -> str:
    return (
        f"repos/{REPOSITORY}/actions/workflows/{OUTCOME_WORKFLOW_FILE}/runs"
        "?branch=main&event=workflow_dispatch&per_page=100"
    )


def feature_run_artifacts_endpoint(run_id: int) -> str:
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        raise ValueError("feature run id must be a positive integer")
    return f"repos/{REPOSITORY}/actions/runs/{run_id}/artifacts?per_page=100"


def artifact_download_endpoint(artifact_id: int) -> str:
    if not isinstance(artifact_id, int) or isinstance(artifact_id, bool) or artifact_id <= 0:
        raise ValueError("artifact id must be a positive integer")
    return f"repos/{REPOSITORY}/actions/artifacts/{artifact_id}/zip"


def feature_run_endpoint(run_id: int) -> str:
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        raise ValueError("feature run id must be a positive integer")
    return f"repos/{REPOSITORY}/actions/runs/{run_id}"


def feature_dispatch_command() -> tuple[str, ...]:
    return (
        "gh",
        "workflow",
        "run",
        FEATURE_WORKFLOW_FILE,
        "--ref",
        "main",
        "-R",
        REPOSITORY,
    )


def outcome_dispatch_command(feature_run_id: int) -> tuple[str, ...]:
    if not isinstance(feature_run_id, int) or isinstance(feature_run_id, bool) or feature_run_id <= 0:
        raise ValueError("feature run id must be a positive integer")
    return (
        "gh",
        "workflow",
        "run",
        OUTCOME_WORKFLOW_FILE,
        "--ref",
        "main",
        "-R",
        REPOSITORY,
        "-f",
        f"feature_run_id={feature_run_id}",
    )


def shell_join(command: Sequence[str]) -> str:
    safe = []
    for part in command:
        if not part or re.search(r"[^A-Za-z0-9_./:=@+-]", part):
            safe.append("'" + part.replace("'", "'\\''") + "'")
        else:
            safe.append(part)
    return " ".join(safe)


__all__ = [
    "FEATURE_WORKFLOW_FILE",
    "FEATURE_WORKFLOW_NAME",
    "FEATURE_WORKFLOW_PATH",
    "OUTCOME_WORKFLOW_FILE",
    "OUTCOME_WORKFLOW_NAME",
    "OUTCOME_WORKFLOW_PATH",
    "REPOSITORY",
    "artifact_download_endpoint",
    "feature_dispatch_command",
    "feature_run_artifacts_endpoint",
    "feature_run_endpoint",
    "feature_runs_endpoint",
    "outcome_dispatch_command",
    "outcome_runs_endpoint",
    "select_feature_evidence_artifact",
    "shell_join",
    "validate_feature_evidence_for_outcomes",
    "validate_feature_run_for_outcomes",
    "validate_no_existing_manual_runs",
    "validate_operator_checkout",
]
