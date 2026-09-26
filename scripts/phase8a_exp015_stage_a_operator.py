from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Mapping, Sequence

from fmp.portfolio.exp015_stage_a_operator import (
    build_exp015_stage_a_operator_report,
    exp015_stage_a_runs_endpoint,
    select_exp015_stage_a_manual_main_run,
    validate_exp015_stage_a_operator_checkout,
    validate_exp015_stage_a_operator_report,
)


ROOT = Path(__file__).resolve().parents[1]
OPERATOR_DECISION = "DEC-265"


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
        raise SystemExit(
            f"GitHub API returned invalid JSON for {endpoint}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            f"GitHub API returned a non-object for {endpoint}"
        )
    return value


def _require_gh_auth() -> None:
    try:
        _run(("gh", "auth", "status"))
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            "GitHub CLI authentication is required before "
            "EXP-015 Stage A operator use"
        ) from exc


def _checkout_preflight() -> dict[str, object]:
    _run(("git", "fetch", "--quiet", "origin", "main"), capture=False)
    return validate_exp015_stage_a_operator_checkout(
        branch=_run(("git", "branch", "--show-current")),
        head_sha=_run(("git", "rev-parse", "HEAD")),
        origin_main_sha=_run(("git", "rev-parse", "origin/main")),
        porcelain_status=_run(("git", "status", "--porcelain")),
        origin_url=_run(("git", "remote", "get-url", "origin")),
    )


def _next_report() -> dict[str, object]:
    checkout = _checkout_preflight()
    listing = _gh_json(exp015_stage_a_runs_endpoint())
    run = select_exp015_stage_a_manual_main_run(listing)
    report = build_exp015_stage_a_operator_report(
        checkout=checkout,
        run=run,
    )
    report["operator_decision"] = OPERATOR_DECISION
    return validate_exp015_stage_a_operator_report(report)


def _print_report(report: Mapping[str, object]) -> None:
    print(
        json.dumps(
            dict(report),
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
    )


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description=(
            "Read-only EXP-015 Stage A authoritative-slot operator"
        )
    )
    sub = out.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "next",
        help=(
            "inspect live EXP-015 Stage A state and return "
            "the one next authoritative action"
        ),
    )
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    _require_gh_auth()

    if args.command != "next":
        raise SystemExit(
            f"unsupported EXP-015 Stage A operator command: {args.command}"
        )

    _print_report(_next_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
