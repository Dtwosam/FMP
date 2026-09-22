from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

from .acceptance_review import (
    review_phase8a_acceptance,
    write_phase8a_acceptance_artifacts,
)


def _load_json_object(path: Path, *, label: str) -> dict[str, object]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read {label}: {path}") from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid UTF-8 JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be a JSON object")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FMP Phase 8A acceptance review tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    review = subparsers.add_parser(
        "review",
        help="review exact DEC-042 evidence and freeze/reject Phase 8A shadow candidate",
    )
    review.add_argument("--preflight", required=True, type=Path)
    review.add_argument("--selection", required=True, type=Path)
    review.add_argument("--out", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "review":
        preflight = _load_json_object(args.preflight, label="DEC-042 preflight")
        selection = _load_json_object(args.selection, label="DEC-042 selection")
        preflight_sha = hashlib.sha256(args.preflight.read_bytes()).hexdigest()
        selection_sha = hashlib.sha256(args.selection.read_bytes()).hexdigest()
        result = review_phase8a_acceptance(
            preflight=preflight,
            preflight_sha256=preflight_sha,
            selection=selection,
            selection_sha256=selection_sha,
        )
        write_phase8a_acceptance_artifacts(result, args.out)
        print(
            json.dumps(
                {
                    "acceptance": str(args.out / "acceptance.json"),
                    "manifest": str(args.out / "manifest.json"),
                    "outcome": result["outcome"],
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    raise AssertionError("unreachable Phase 8A acceptance command")


__all__ = ["build_parser", "main"]
