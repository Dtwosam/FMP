from __future__ import annotations

import argparse
import json
import sys
# The audit CLI is read-only even when environment bytecode suppression is off.
# Set this before importing the project package, not after argument parsing.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_preaccess_identity_gate_topology_audit import (
    build_2023_preaccess_identity_topology_audit,
    validate_2023_preaccess_identity_topology_audit,
)


def _assess(args: argparse.Namespace) -> int:
    checkout = Path.cwd().resolve()
    # Keep cwd for offline computation; source checkout owns output safety.
    source_checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target.is_relative_to(source_checkout):
        raise ValueError("DEC-623 refuses writes anywhere inside checkout")
    report = build_2023_preaccess_identity_topology_audit(repository_root=checkout)
    validate_2023_preaccess_identity_topology_audit(report)
    content = json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if target.exists():
        if target.read_text(encoding="utf-8") != content:
            raise ValueError("DEC-623 refuses conflicting output overwrite")
        # Avoid changing inode metadata on repeated identical outside reports.
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DEC-623 inert annual three-job pre-evidence tag/SHA gate topology audit"
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
