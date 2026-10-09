from __future__ import annotations

import argparse
import json
import sys
# The audit CLI is read-only even when environment bytecode suppression is off.
# Set this before importing the project package, not after argument parsing.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_ref_race_interleaving_model import (
    build_2023_run385_ref_race_interleaving_report,
    validate_2023_run385_ref_race_interleaving_report,
)


def _assess(args: argparse.Namespace) -> int:
    checkout = Path.cwd().resolve()
    # Keep cwd for offline computation; source checkout owns output safety.
    source_checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target.is_relative_to(source_checkout):
        raise ValueError("DEC-619 refuses output inside repository checkout")
    report = build_2023_run385_ref_race_interleaving_report(repository_root=checkout)
    validate_2023_run385_ref_race_interleaving_report(report)
    content = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") != content:
        raise ValueError("DEC-619 refuses conflicting report overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DEC-619 read-only offline GitHub ref race interleaving analysis"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess")
    assess.add_argument("--out", type=Path, required=True)
    assess.set_defaults(func=_assess)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
