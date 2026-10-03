from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2015_replacement_run_review import (
    review_2015_replacement_run,
    validate_2015_replacement_run_review,
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
    payload = json.dumps(dict(value), sort_keys=True, indent=2, allow_nan=False) + "\n"
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing output: {destination}")
    destination.write_text(payload, encoding="utf-8")


def _cmd_review(args: argparse.Namespace) -> int:
    value = review_2015_replacement_run(
        repository_root=Path("."),
        run=_read_json(args.run_json),
        jobs_payload=_read_json(args.jobs_json),
        artifacts_payload=_read_json(args.artifacts_json),
        freeze_evidence=_read_json(args.freeze_evidence),
        freeze_artifact_zip_sha256=args.freeze_artifact_zip_sha256,
        expected_head_sha=args.expected_head_sha,
    )
    validate_2015_replacement_run_review(value)
    _write_json(args.out, value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Review exact successful 2015 replacement annual-catalogue runtime evidence"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    review = subparsers.add_parser("review")
    review.add_argument("--run-json", type=Path, required=True)
    review.add_argument("--jobs-json", type=Path, required=True)
    review.add_argument("--artifacts-json", type=Path, required=True)
    review.add_argument("--freeze-evidence", type=Path, required=True)
    review.add_argument("--freeze-artifact-zip-sha256", required=True)
    review.add_argument("--expected-head-sha", required=True)
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
