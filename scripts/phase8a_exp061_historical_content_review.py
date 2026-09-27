from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from fmp.discovery.historical_result_content_review import (
    review_historical_result_content,
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
        description="Read-only EXP-061 historical content reviewer"
    )
    parser.add_argument(
        "--cell-json",
        type=Path,
        action="append",
        required=True,
        help="Repeat exactly 18 times.",
    )
    parser.add_argument("--aggregate-json", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cells = [_read_json(path) for path in args.cell_json]
        aggregate = _read_json(args.aggregate_json)
        report = review_historical_result_content(
            cells,
            aggregate,
            expected_head_sha=args.expected_head,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
