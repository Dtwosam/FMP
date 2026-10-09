from __future__ import annotations

import argparse
import json
import sys
# The audit CLI is read-only even when environment bytecode suppression is off.
# Set this before importing the project package, not after argument parsing.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_lock_witness_coverage import (
    build_2023_run385_lock_witness_coverage,
    validate_2023_run385_lock_witness_coverage,
    parse_untrusted_witness_json,
)


def _assess(args: argparse.Namespace) -> int:
    root = Path.cwd().resolve()
    target = args.out.resolve()
    if target.is_relative_to(root):
        raise ValueError("DEC-620 report output cannot be inside the checkout")
    # Inputs are caller-supplied, offline and unauthenticated. All outputs
    # continue to deny effective lock proof, dispatch and trading authority.
    witness = parse_untrusted_witness_json(args.witness_json.read_text(encoding="utf-8"))
    report = build_2023_run385_lock_witness_coverage(
        repository_root=root, witness=witness,
    )
    validate_2023_run385_lock_witness_coverage(report)
    serialized = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") != serialized:
        raise ValueError("DEC-620 refuses conflicting report overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(serialized, encoding="utf-8")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DEC-620 offline unauthenticated lock interval gap review; no dispatch"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess")
    assess.add_argument("--witness-json", required=True, type=Path)
    assess.add_argument("--out", required=True, type=Path)
    assess.set_defaults(func=_assess)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
