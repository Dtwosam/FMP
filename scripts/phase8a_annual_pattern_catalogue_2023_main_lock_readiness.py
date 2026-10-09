from __future__ import annotations

import argparse
import json
import sys
# The audit CLI is read-only even when environment bytecode suppression is off.
# Set this before importing the project package, not after argument parsing.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2023_main_lock_readiness import (
    build_2023_main_lock_readiness,
    validate_2023_main_lock_readiness,
)


def _read(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"DEC-612 cannot read JSON: {path}") from exc


def _object(path: Path) -> Mapping[str, object]:
    value = _read(path)
    if not isinstance(value, dict):
        raise ValueError(f"DEC-612 requires JSON object: {path}")
    return value


def _list_or_null(path: Path) -> object:
    value = _read(path)
    if value is not None and not isinstance(value, list):
        raise ValueError(f"DEC-612 requires list or null: {path}")
    return value


def _optional_object(path: Path) -> Mapping[str, object] | None:
    value = _read(path)
    if value is not None and not isinstance(value, dict):
        raise ValueError(f"DEC-612 requires object or null: {path}")
    return value


def _cmd_assess(args: argparse.Namespace) -> int:
    # Anchor containment to the actual source checkout, not the caller's cwd.
    # Invoking this CLI from scripts/ must not permit writing into repo root.
    checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    # Reject output targets inside the checkout before reading any input JSON.
    if target.is_relative_to(checkout):
        raise ValueError("DEC-612 refuses audit output inside checkout")
    value = build_2023_main_lock_readiness(
        dec611_audit=_object(args.dec611_audit_json),
        repository_root=Path("."),
        main_branch=_object(args.main_branch_json),
        annual_workflow_runs=_object(args.annual_workflow_runs_json),
        branch_protection=_optional_object(args.branch_protection_json),
        effective_branch_rules=_list_or_null(args.effective_branch_rules_json),
        inherited_rulesets=_list_or_null(args.inherited_rulesets_json),
        expected_head_sha=args.expected_head_sha,
    )
    validate_2023_main_lock_readiness(value)
    payload = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") != payload:
        raise ValueError(f"DEC-612 conflicting existing output: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only DEC-612 main lock readiness assessment; never dispatches"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess")
    for flag in (
        "dec611-audit-json", "main-branch-json", "annual-workflow-runs-json",
        "branch-protection-json", "effective-branch-rules-json",
        "inherited-rulesets-json",
    ):
        assess.add_argument("--" + flag, required=True, type=Path)
    assess.add_argument("--expected-head-sha", required=True)
    assess.add_argument("--out", required=True, type=Path)
    assess.set_defaults(func=_cmd_assess)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
