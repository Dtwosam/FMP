from __future__ import annotations

"""DEC-626 report-only CLI. Never executes or modifies a workflow."""

import argparse
import json
import sys
# Enforce no checkout bytecode emission before importing the fmp package.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_precheckout_job_if_preview import (
    build_precheckout_job_if_preview,
    validate_precheckout_job_if_preview,
)


def _assess(args: argparse.Namespace) -> int:
    checkout = Path.cwd().resolve()
    # Preserve cwd for the offline assessment, but not for output containment.
    source_checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target.is_relative_to(source_checkout):
        raise ValueError("DEC-626 refuses output inside checkout")
    report = build_precheckout_job_if_preview(repository_root=checkout)
    validate_precheckout_job_if_preview(report)
    data = json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if target.exists():
        if target.read_text(encoding="utf-8") != data:
            raise ValueError("DEC-626 refuses conflicting report overwrite")
        # Never rewrite identical reports, including a hard-linked source inode.
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(data, encoding="utf-8")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DEC-626 inert three-job precheckout if preview")
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess")
    assess.add_argument("--out", required=True, type=Path)
    assess.set_defaults(func=_assess)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
