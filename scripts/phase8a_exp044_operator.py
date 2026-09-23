from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Sequence

from fmp.market_learning.operator import (
    FEATURE_WORKFLOW_NAME,
    OUTCOME_WORKFLOW_NAME,
    feature_dispatch_command,
    feature_run_endpoint,
    feature_runs_endpoint,
    outcome_dispatch_command,
    outcome_runs_endpoint,
    shell_join,
    validate_feature_run_for_outcomes,
    validate_no_existing_manual_runs,
    validate_operator_checkout,
)


def _run(command: Sequence[str], *, capture: bool = True) -> str:
    completed = subprocess.run(
        list(command),
        check=True,
        text=True,
        capture_output=capture,
    )
    return completed.stdout.strip() if capture else ""


def _gh_json(endpoint: str) -> dict[str, object]:
    raw = _run(("gh", "api", endpoint))
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"GitHub API returned invalid JSON for {endpoint}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"GitHub API returned a non-object for {endpoint}")
    return value


def _checkout_preflight() -> dict[str, object]:
    _run(("git", "fetch", "--quiet", "origin", "main"), capture=False)
    return validate_operator_checkout(
        branch=_run(("git", "branch", "--show-current")),
        head_sha=_run(("git", "rev-parse", "HEAD")),
        origin_main_sha=_run(("git", "rev-parse", "origin/main")),
        porcelain_status=_run(("git", "status", "--porcelain")),
        origin_url=_run(("git", "remote", "get-url", "origin")),
    )


def _require_gh_auth() -> None:
    try:
        _run(("gh", "auth", "status"), capture=False)
    except subprocess.CalledProcessError as exc:
        raise SystemExit("GitHub CLI authentication is required before EXP-044 dispatch") from exc


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Safely prepare or perform the manual EXP-044 GitHub workflow dispatch"
    )
    sub = out.add_subparsers(dest="command", required=True)

    features = sub.add_parser("features", help="prepare or dispatch EXP-044 feature generation")
    features.add_argument("--execute", action="store_true")

    outcomes = sub.add_parser("outcomes", help="prepare or dispatch EXP-044 outcome materialization")
    outcomes.add_argument("--feature-run-id", type=int, required=True)
    outcomes.add_argument("--execute", action="store_true")
    return out


def _print_report(report: dict[str, object]) -> None:
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    _require_gh_auth()
    checkout = _checkout_preflight()

    if args.command == "features":
        listing = _gh_json(feature_runs_endpoint())
        validate_no_existing_manual_runs(
            listing,
            workflow_name=FEATURE_WORKFLOW_NAME,
        )
        command = feature_dispatch_command()
        report: dict[str, object] = {
            **checkout,
            "stage": "features",
            "existing_manual_main_runs": 0,
            "ready_to_dispatch": True,
            "execute_requested": bool(args.execute),
            "dispatch_command": shell_join(command),
            "model_fit_authorized": False,
            "promotion_authorized": False,
            "trading_authorized": False,
        }
        if not args.execute:
            _print_report(report)
            return 0
        _run(command, capture=False)
        report["dispatch_submitted"] = True
        report["result_claimed"] = False
        _print_report(report)
        return 0

    feature_run_id = args.feature_run_id
    run = _gh_json(feature_run_endpoint(feature_run_id))
    feature = validate_feature_run_for_outcomes(
        run,
        expected_run_id=feature_run_id,
    )
    listing = _gh_json(outcome_runs_endpoint())
    validate_no_existing_manual_runs(
        listing,
        workflow_name=OUTCOME_WORKFLOW_NAME,
    )
    command = outcome_dispatch_command(feature_run_id)
    report = {
        **checkout,
        **feature,
        "stage": "outcomes",
        "existing_manual_main_runs": 0,
        "ready_to_dispatch": True,
        "execute_requested": bool(args.execute),
        "dispatch_command": shell_join(command),
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "trading_authorized": False,
    }
    if not args.execute:
        _print_report(report)
        return 0
    _run(command, capture=False)
    report["dispatch_submitted"] = True
    report["result_claimed"] = False
    _print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
