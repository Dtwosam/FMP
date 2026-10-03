from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_proof_workflow_run_review import (
    review_proof_workflow_run,
    validate_proof_workflow_run_review,
)


def _read_json(path: Path) -> Mapping[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _read_bytes(path: Path) -> bytes:
    try:
        return Path(path).read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read file: {path}") from exc


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(dict(value), sort_keys=True, indent=2, allow_nan=False) + "\n"
    )
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing output: {destination}")
    destination.write_text(payload, encoding="utf-8")


def _cmd_review(args: argparse.Namespace) -> int:
    value = review_proof_workflow_run(
        repository_root=Path("."),
        main_branch=_read_json(args.main_branch_json),
        proof_run=_read_json(args.proof_run_json),
        proof_job=_read_json(args.proof_job_json),
        artifact=_read_json(args.artifact_json),
        preflight_bytes=_read_bytes(args.preflight_json),
        expected_proof_run_id=args.expected_proof_run_id,
    )
    validate_proof_workflow_run_review(value)
    _write_json(args.out, value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only reviewer for first annual-catalogue proof-workflow run"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    review = subparsers.add_parser("review")
    review.add_argument("--main-branch-json", type=Path, required=True)
    review.add_argument("--proof-run-json", type=Path, required=True)
    review.add_argument("--proof-job-json", type=Path, required=True)
    review.add_argument("--artifact-json", type=Path, required=True)
    review.add_argument("--preflight-json", type=Path, required=True)
    review.add_argument("--expected-proof-run-id", type=int, required=True)
    review.add_argument("--out", type=Path, required=True)
    review.set_defaults(func=_cmd_review)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
