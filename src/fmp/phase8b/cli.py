from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

from .design import build_phase8b_design, write_phase8b_design_artifacts


def _load_json_object(path: Path) -> dict[str, object]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read Phase 8A acceptance artifact: {path}") from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Phase 8A acceptance artifact is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("Phase 8A acceptance artifact root must be an object")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FMP Phase 8B source-free shadow design tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    design = subparsers.add_parser(
        "design",
        help="compile an accepted Phase 8A shadow candidate into a frozen Phase 8B design",
    )
    design.add_argument("--acceptance", required=True, type=Path)
    design.add_argument("--code-commit", required=True)
    design.add_argument("--out", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "design":
        acceptance = _load_json_object(args.acceptance)
        acceptance_sha = hashlib.sha256(args.acceptance.read_bytes()).hexdigest()
        result = build_phase8b_design(
            acceptance=acceptance,
            acceptance_sha256=acceptance_sha,
            code_commit=args.code_commit,
        )
        write_phase8b_design_artifacts(result, args.out)
        print(
            json.dumps(
                {
                    "design": str(args.out / "design.json"),
                    "manifest": str(args.out / "manifest.json"),
                    "design_fingerprint": result["design_fingerprint"],
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0
    raise AssertionError("unreachable Phase 8B command")


__all__ = ["build_parser", "main"]
