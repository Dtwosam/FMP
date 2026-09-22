from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

from .design import (
    build_phase9_demo_design_from_campaign,
    write_phase9_demo_design,
)


def _current_code_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        raise RuntimeError("unable to resolve current code commit") from None
    commit = completed.stdout.strip()
    if (
        len(commit) != 40
        or any(character not in "0123456789abcdef" for character in commit)
    ):
        raise RuntimeError("current code commit is invalid")
    return commit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FMP Phase 9 source-only demo design tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    design = subparsers.add_parser(
        "design-demo",
        help="freeze a Phase 9 demo design from an exact Phase 8B PASS review",
    )
    design.add_argument("--campaign-dir", required=True, type=Path)
    design.add_argument("--review-id", required=True)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    code_commit_resolver: Callable[[], str] = _current_code_commit,
) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "design-demo":
        result = build_phase9_demo_design_from_campaign(
            campaign_dir=args.campaign_dir,
            review_id=args.review_id,
            code_commit=code_commit_resolver(),
        )
        out_dir = (
            args.campaign_dir
            / "phase9"
            / "designs"
            / str(args.review_id)
        )
        manifest = write_phase9_demo_design(result, out_dir)
        print(
            json.dumps(
                {
                    "design": str(out_dir / "design.json"),
                    "manifest": str(out_dir / "manifest.json"),
                    "demo_design_fingerprint": result[
                        "demo_design_fingerprint"
                    ],
                    "demo_adapter_source_authorized": True,
                    "demo_execution_authorized": False,
                    "demo_order_authorized": False,
                    "phase10_authorized": False,
                    "artifact_count": len(manifest["artifacts"]),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0
    raise AssertionError("unreachable Phase 9 command")


__all__ = ["build_parser", "main"]
