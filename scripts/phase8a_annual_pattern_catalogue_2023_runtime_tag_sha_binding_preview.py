from __future__ import annotations

import argparse
import json
import sys
# The audit CLI is read-only even when environment bytecode suppression is off.
# Set this before importing the project package, not after argument parsing.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_runtime_tag_sha_binding_preview import (
    build_2023_runtime_tag_sha_binding_preview,
    validate_2023_runtime_tag_sha_binding_preview,
)


def _assess(args: argparse.Namespace) -> int:
    checkout = Path.cwd().resolve()
    target = args.out.resolve()
    if target.is_relative_to(checkout):
        raise ValueError("DEC-622 refuses report writes anywhere inside checkout")
    report = build_2023_runtime_tag_sha_binding_preview(repository_root=checkout)
    validate_2023_runtime_tag_sha_binding_preview(report)
    content = json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") != content:
        raise ValueError("DEC-622 refuses conflicting output overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DEC-622 inert exact 2023 tag/runtime SHA tuple gate design preview"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess")
    assess.add_argument("--out", type=Path, required=True)
    assess.set_defaults(func=_assess)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
