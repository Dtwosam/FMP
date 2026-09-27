from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Mapping, Sequence
import zipfile

from fmp.discovery.historical_execution_operator import (
    build_historical_execution_plan,
)
from fmp.discovery.historical_execution_plan_result_decision import (
    DEC287_PLAN_RAW_SHA256,
    DEC287_PROOF_ARTIFACT_ID,
    DEC287_PROOF_ARTIFACT_NAME,
    DEC287_PROOF_RUN_ID,
    freeze_reviewed_historical_execution_plan_proof,
)
from fmp.discovery.historical_executor import (
    EXP061_HISTORICAL_EXECUTOR_DECISION,
    historical_execution_evidence,
    validate_fresh_historical_execution_plan,
)


ROOT = Path(__file__).resolve().parents[1]
_SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
_REPO = "Dtwosam/FMP"


def _run(command: Sequence[str], *, capture: bool = True) -> str:
    completed = subprocess.run(
        list(command),
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )
    return completed.stdout.strip() if capture else ""


def _run_bytes(command: Sequence[str]) -> bytes:
    completed = subprocess.run(
        list(command),
        cwd=ROOT,
        check=True,
        text=False,
        capture_output=True,
    )
    return bytes(completed.stdout)


def _executor_head_sha() -> str:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("DEC-289 executor requires GitHub Actions")
    if os.environ.get("GITHUB_REPOSITORY") != _REPO:
        raise SystemExit("DEC-289 executor requires Dtwosam/FMP")
    if os.environ.get("GITHUB_EVENT_NAME") != "push":
        raise SystemExit("DEC-289 executor requires a push event")
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise SystemExit("DEC-289 executor requires refs/heads/main")
    if os.environ.get("GITHUB_RUN_ATTEMPT") != "1":
        raise SystemExit("DEC-289 executor refuses workflow reruns")

    head = os.environ.get("GITHUB_SHA", "")
    if _SHA40.fullmatch(head) is None:
        raise SystemExit("DEC-289 executor requires a valid GITHUB_SHA")
    return head.lower()


def _read_gh_json(endpoint: str) -> dict[str, object]:
    raw = _run(("gh", "api", endpoint))
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"gh api returned invalid JSON for {endpoint}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"gh api returned non-object JSON for {endpoint}")
    return value


def _load_reviewed_predecessor() -> dict[str, object]:
    proof_run = _read_gh_json(
        f"repos/{_REPO}/actions/runs/{DEC287_PROOF_RUN_ID}"
    )
    artifacts = _read_gh_json(
        f"repos/{_REPO}/actions/runs/{DEC287_PROOF_RUN_ID}/artifacts"
    )
    archive = _run_bytes(
        (
            "gh",
            "api",
            f"repos/{_REPO}/actions/artifacts/{DEC287_PROOF_ARTIFACT_ID}/zip",
        )
    )
    archive_sha256 = hashlib.sha256(archive).hexdigest()

    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            names = bundle.namelist()
            if names != ["historical-execution-plan.json"]:
                raise SystemExit(
                    "DEC-289 requires exactly historical-execution-plan.json "
                    "in the reviewed proof artifact"
                )
            plan_bytes = bundle.read(names[0])
    except zipfile.BadZipFile as exc:
        raise SystemExit("DEC-289 reviewed proof artifact is not a ZIP") from exc

    plan_raw_sha256 = hashlib.sha256(plan_bytes).hexdigest()
    if plan_raw_sha256 != DEC287_PLAN_RAW_SHA256:
        raise SystemExit("DEC-289 reviewed plan raw SHA-256 mismatch")

    try:
        plan = json.loads(plan_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit("DEC-289 reviewed plan JSON is invalid") from exc
    if not isinstance(plan, dict):
        raise SystemExit("DEC-289 reviewed plan root must be an object")

    reviewed = freeze_reviewed_historical_execution_plan_proof(
        repository_root=ROOT,
        proof_run=proof_run,
        proof_artifacts_payload=artifacts,
        plan=plan,
        artifact_zip_sha256=archive_sha256,
        plan_raw_sha256=plan_raw_sha256,
    )
    if reviewed.get("proof_artifact_name") != DEC287_PROOF_ARTIFACT_NAME:
        raise SystemExit("DEC-289 reviewed artifact name mismatch")
    return reviewed


def _fresh_plan(*, expected_head_sha: str) -> dict[str, object]:
    main_branch = _read_gh_json(f"repos/{_REPO}/branches/main")
    runs = _read_gh_json(
        f"repos/{_REPO}/actions/workflows/"
        "phase8a-exp061-discovery.yml/runs"
        "?branch=main&event=workflow_dispatch&per_page=100"
    )
    value = build_historical_execution_plan(
        repository_root=ROOT,
        main_branch=main_branch,
        workflow_runs=runs,
        expected_head_sha=expected_head_sha,
    )
    if not isinstance(value, dict):
        raise SystemExit("DEC-286 operator returned a non-object plan")
    return value


def _print_evidence(evidence: Mapping[str, object]) -> None:
    print(
        json.dumps(
            dict(evidence),
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
    )


def main() -> int:
    head_sha = _executor_head_sha()
    reviewed = _load_reviewed_predecessor()

    first = _fresh_plan(expected_head_sha=head_sha)
    first_command = validate_fresh_historical_execution_plan(
        first,
        expected_head_sha=head_sha,
    )

    second = _fresh_plan(expected_head_sha=head_sha)
    if first != second:
        raise SystemExit("DEC-289 historical execution plans changed before dispatch")
    second_command = validate_fresh_historical_execution_plan(
        second,
        expected_head_sha=head_sha,
    )
    if first_command != second_command:
        raise SystemExit("DEC-289 dispatch command changed before dispatch")

    _run(second_command, capture=False)

    evidence = historical_execution_evidence(
        plan=second,
        reviewed_predecessor=reviewed,
        executor_head_sha=head_sha,
    )
    if evidence.get("executor_decision") != EXP061_HISTORICAL_EXECUTOR_DECISION:
        raise SystemExit("DEC-289 executor evidence decision mismatch")
    _print_evidence(evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
