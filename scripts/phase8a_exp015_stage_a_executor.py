from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Mapping, Sequence

from fmp.portfolio.exp015_stage_a_executor import (
    EXECUTOR_DECISION,
    validate_exp015_stage_a_fresh_execution_plan,
)


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
        raise SystemExit("EXP-015 Stage A executor requires a push event")
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise SystemExit("EXP-015 Stage A executor requires refs/heads/main")
    if os.environ.get("GITHUB_RUN_ATTEMPT") != "1":
        raise SystemExit("EXP-015 Stage A executor refuses workflow reruns")

    head = os.environ.get("GITHUB_SHA", "")
    if _SHA40.fullmatch(head) is None:
        raise SystemExit("EXP-015 Stage A executor requires a valid GITHUB_SHA")
    return head.lower()


def _fresh_plan() -> dict[str, object]:
    raw = _run(
        (
            sys.executable,
            "scripts/phase8a_exp015_stage_a_operator.py",
            "next",
        )
    )
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit("DEC-265 operator returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise SystemExit("DEC-265 operator returned a non-object plan")
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

    first = _fresh_plan()
    first_command = validate_exp015_stage_a_fresh_execution_plan(
        first,
        expected_head_sha=head_sha,
    )

    second = _fresh_plan()
    if first != second:
        raise SystemExit("EXP-015 Stage A fresh plans changed before execution")
    second_command = validate_exp015_stage_a_fresh_execution_plan(
        second,
        expected_head_sha=head_sha,
    )
    if first_command != second_command:
        raise SystemExit("EXP-015 Stage A dispatch command changed before execution")

    _run(second_command, capture=False)

    _print_evidence(
        {
            **second,
            "executor_decision": EXECUTOR_DECISION,
            "executor_head_sha": head_sha,
            "fresh_plan_rechecked_twice": True,
            "dispatch_submitted": True,
            "result_claimed": False,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
