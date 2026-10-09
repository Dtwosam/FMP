from __future__ import annotations

import argparse
import json
import sys
# The audit CLI is read-only even when environment bytecode suppression is off.
# Set this before importing the project package, not after argument parsing.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_ambiguous_dispatch_hold_model import (
    build_2023_run385_ambiguous_dispatch_hold_report,
    parse_untrusted_dispatch_simulation_json,
    validate_2023_run385_ambiguous_dispatch_hold_report,
)


def _assess(args: argparse.Namespace) -> int:
    checkout = Path.cwd().resolve()
    target = args.out.resolve()
    if target.is_relative_to(checkout):
        raise ValueError("DEC-621 refuses any report output inside checkout")
    input_doc = parse_untrusted_dispatch_simulation_json(
        args.simulation_json.read_text(encoding="utf-8")
    )
    report = build_2023_run385_ambiguous_dispatch_hold_report(
        repository_root=checkout, input_doc=input_doc,
    )
    validate_2023_run385_ambiguous_dispatch_hold_report(report)
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") != text:
        raise ValueError("DEC-621 refuses conflicting report overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DEC-621 offline simulated no-retry annual dispatch response holds"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess")
    assess.add_argument("--simulation-json", type=Path, required=True)
    assess.add_argument("--out", type=Path, required=True)
    assess.set_defaults(func=_assess)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
