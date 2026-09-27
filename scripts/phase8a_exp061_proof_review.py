from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from fmp.discovery.proof_review import review_proof_terminal


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _review(args: argparse.Namespace) -> int:
    result = review_proof_terminal(
        executor_evidence=_read_json(args.executor_json),
        run=_read_json(args.run_json),
        jobs_payload=_read_json(args.jobs_json),
        artifacts_payload=_read_json(args.artifacts_json),
        preflight_evidence=_read_json(args.preflight_json),
        expected_head_sha=args.expected_head,
    )
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only EXP-061 proof terminal reviewer"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    review = sub.add_parser("review")
    review.add_argument("--executor-json", type=Path, required=True)
    review.add_argument("--run-json", type=Path, required=True)
    review.add_argument("--jobs-json", type=Path, required=True)
    review.add_argument("--artifacts-json", type=Path, required=True)
    review.add_argument("--preflight-json", type=Path, required=True)
    review.add_argument("--expected-head", required=True)
    review.set_defaults(func=_review)
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
