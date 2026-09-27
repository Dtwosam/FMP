from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from fmp.discovery.historical_result_review import (
    review_historical_result_terminal_shape,
)


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only EXP-061 historical terminal-shape reviewer"
    )
    parser.add_argument("--run-json", type=Path, required=True)
    parser.add_argument("--jobs-json", type=Path, required=True)
    parser.add_argument("--artifacts-json", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = review_historical_result_terminal_shape(
            run=_read_json(args.run_json),
            jobs_payload=_read_json(args.jobs_json),
            artifacts_payload=_read_json(args.artifacts_json),
            expected_head_sha=args.expected_head,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
