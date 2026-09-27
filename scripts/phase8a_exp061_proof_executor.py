from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.proof_executor import (
    EXP061_PROOF_EXECUTOR_DECISION,
    proof_execution_evidence,
    validate_fresh_proof_execution_plan,
)
from fmp.discovery.proof_operator import build_proof_plan


ROOT = Path(__file__).resolve().parents[1]
_SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")


def _run(command: Sequence[str], *, capture: bool = True) -> str:
    completed = subprocess.run(
        list(command),
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )
    return completed.stdout.strip() if capture else ""


def _executor_head_sha() -> str:
    if os.environ.get("GITHUB_EVENT_NAME") != "push":
        raise SystemExit("EXP-061 proof executor requires a push event")
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise SystemExit("EXP-061 proof executor requires refs/heads/main")
    if os.environ.get("GITHUB_RUN_ATTEMPT") != "1":
        raise SystemExit("EXP-061 proof executor refuses workflow reruns")

    head = os.environ.get("GITHUB_SHA", "")
    if _SHA40.fullmatch(head) is None:
        raise SystemExit("EXP-061 proof executor requires a valid GITHUB_SHA")
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


def _fresh_plan(*, expected_head_sha: str) -> dict[str, object]:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if repo != "Dtwosam/FMP":
        raise SystemExit("EXP-061 proof executor requires Dtwosam/FMP repository")

    main_branch = _read_gh_json(f"repos/{repo}/branches/main")
    runs = _read_gh_json(
        f"repos/{repo}/actions/workflows/"
        "phase8a-exp061-discovery.yml/runs"
        "?branch=main&event=workflow_dispatch&per_page=100"
    )
    value = build_proof_plan(
        main_branch=main_branch,
        workflow_runs=runs,
        expected_head_sha=expected_head_sha,
    )
    if not isinstance(value, dict):
        raise SystemExit("DEC-278 operator returned a non-object plan")
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

    first = _fresh_plan(expected_head_sha=head_sha)
    first_command = validate_fresh_proof_execution_plan(
        first,
        expected_head_sha=head_sha,
    )

    second = _fresh_plan(expected_head_sha=head_sha)
    if first != second:
        raise SystemExit("EXP-061 proof plans changed before dispatch")
    second_command = validate_fresh_proof_execution_plan(
        second,
        expected_head_sha=head_sha,
    )
    if first_command != second_command:
        raise SystemExit("EXP-061 proof dispatch command changed before dispatch")

    _run(second_command, capture=False)

    evidence = proof_execution_evidence(
        plan=second,
        executor_head_sha=head_sha,
    )
    if evidence.get("executor_decision") != EXP061_PROOF_EXECUTOR_DECISION:
        raise SystemExit("EXP-061 proof executor evidence decision mismatch")
    _print_evidence(evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
