from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2016_post_install_dispatch_recovery import (
    build_2016_post_install_dispatch_recovery,
    validate_2016_post_install_dispatch_recovery,
)
from fmp.discovery.annual_pattern_catalogue_2016_post_install_runtime_repair import (
    build_2016_post_install_runtime_repair,
    validate_2016_post_install_runtime_repair,
)


def _read_json(path: Path) -> Mapping[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(dict(value), sort_keys=True, indent=2, allow_nan=False)
        + "\n"
    )
    if (
        destination.exists()
        and destination.read_text(encoding="utf-8") != payload
    ):
        raise ValueError(f"conflicting existing output: {destination}")
    destination.write_text(payload, encoding="utf-8")


def _cmd_repair(args: argparse.Namespace) -> int:
    value = build_2016_post_install_runtime_repair(
        repository_root=Path("."),
        installer_run=_read_json(args.installer_run_json),
        installer_jobs=_read_json(args.installer_jobs_json),
        repair_head_sha=args.repair_head_sha,
    )
    validate_2016_post_install_runtime_repair(value)
    _write_json(args.out, value)
    return 0


def _cmd_plan(args: argparse.Namespace) -> int:
    value = build_2016_post_install_dispatch_recovery(
        repository_root=Path("."),
        repair_receipt=_read_json(args.repair_json),
        install_receipt=_read_json(args.install_receipt_json),
        runtime_binding=_read_json(args.runtime_binding_json),
        main_branch=_read_json(args.main_branch_json),
        annual_workflow_runs=_read_json(args.annual_workflow_runs_json),
        expected_head_sha=args.expected_head_sha,
    )
    validate_2016_post_install_dispatch_recovery(value)
    _write_json(args.out, value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Freeze the repaired 2016 runtime state and build the exact "
            "post-install run-378 dispatch recovery plan"
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    repair = subparsers.add_parser("repair")
    repair.add_argument("--installer-run-json", type=Path, required=True)
    repair.add_argument("--installer-jobs-json", type=Path, required=True)
    repair.add_argument("--repair-head-sha", required=True)
    repair.add_argument("--out", type=Path, required=True)
    repair.set_defaults(func=_cmd_repair)

    plan = subparsers.add_parser("plan")
    plan.add_argument("--repair-json", type=Path, required=True)
    plan.add_argument("--install-receipt-json", type=Path, required=True)
    plan.add_argument("--runtime-binding-json", type=Path, required=True)
    plan.add_argument("--main-branch-json", type=Path, required=True)
    plan.add_argument("--annual-workflow-runs-json", type=Path, required=True)
    plan.add_argument("--expected-head-sha", required=True)
    plan.add_argument("--out", type=Path, required=True)
    plan.set_defaults(func=_cmd_plan)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ValueError, PermissionError) as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
