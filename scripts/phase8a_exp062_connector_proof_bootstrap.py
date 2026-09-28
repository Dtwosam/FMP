from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Sequence

from fmp.discovery.exp062_connector_proof_bootstrap import (
    EXPECTED_MAIN_SHA,
    build_connector_proof_bootstrap_evidence,
)
from fmp.discovery.exp062_proof_operator import (
    build_proof_plan,
    proof_dispatch_command,
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


def _read_gh_json(endpoint: str) -> dict[str, object]:
    raw = _run(("gh", "api", endpoint))
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"gh api returned invalid JSON for {endpoint}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"gh api returned non-object JSON for {endpoint}")
    return value


def _require_context() -> tuple[str, str, str, str, int]:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("DEC-306 bootstrap requires GitHub Actions")
    if os.environ.get("GITHUB_REPOSITORY") != _REPO:
        raise SystemExit("DEC-306 bootstrap requires Dtwosam/FMP")
    if not os.environ.get("GH_TOKEN"):
        raise SystemExit("DEC-306 bootstrap requires GH_TOKEN")

    expected = os.environ.get("EXP062_BOOTSTRAP_EXPECTED_MAIN_SHA", "")
    if _SHA40.fullmatch(expected) is None:
        raise SystemExit("DEC-306 expected main SHA is malformed")
    expected = expected.lower()
    if expected != EXPECTED_MAIN_SHA:
        raise SystemExit("DEC-306 expected main SHA source mismatch")

    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    base_ref = os.environ.get("GITHUB_BASE_REF", "")
    head_ref = os.environ.get("GITHUB_HEAD_REF", "")
    try:
        run_attempt = int(os.environ.get("GITHUB_RUN_ATTEMPT", "0"))
    except ValueError as exc:
        raise SystemExit("DEC-306 run attempt is malformed") from exc

    checkout_head = _run(("git", "rev-parse", "HEAD")).lower()
    if checkout_head != expected:
        raise SystemExit("DEC-306 checkout is not the exact pinned main head")
    if _run(("git", "status", "--porcelain")):
        raise SystemExit("DEC-306 requires a clean exact-main checkout")

    return expected, event_name, base_ref, head_ref, run_attempt


def _fresh_plan(*, expected_head_sha: str) -> dict[str, object]:
    main_branch = _read_gh_json(f"repos/{_REPO}/branches/main")
    runs = _read_gh_json(
        f"repos/{_REPO}/actions/workflows/"
        "phase8a-exp062-discovery.yml/runs"
        "?branch=main&event=workflow_dispatch&per_page=100"
    )
    value = build_proof_plan(
        main_branch=main_branch,
        workflow_runs=runs,
        expected_head_sha=expected_head_sha,
    )
    if not isinstance(value, dict):
        raise SystemExit("DEC-302 operator returned a non-object plan")
    return value


def main() -> int:
    expected, event_name, base_ref, head_ref, run_attempt = _require_context()

    first = _fresh_plan(expected_head_sha=expected)
    second = _fresh_plan(expected_head_sha=expected)
    evidence = build_connector_proof_bootstrap_evidence(
        first,
        second,
        main_head_sha=expected,
        event_name=event_name,
        base_ref=base_ref,
        head_ref=head_ref,
        run_attempt=run_attempt,
    )

    _run(proof_dispatch_command(), capture=False)

    print(
        json.dumps(
            evidence,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
