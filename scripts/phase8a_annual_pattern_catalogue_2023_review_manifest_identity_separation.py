from __future__ import annotations

"""DEC-625 assess-only. No installed guards or GitHub actions."""

import argparse
import json
import sys
# Disable bytecode emission before importing any project modules. The audit is
# read-only even when PYTHONDONTWRITEBYTECODE is unset.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_external_report_create import write_once_external_report

from fmp.discovery.annual_pattern_catalogue_2023_review_manifest_identity_separation import (
    build_review_manifest_identity_separation,
    validate_review_manifest_identity_separation,
)


def _assess(args: argparse.Namespace) -> int:
    checkout = Path.cwd().resolve()
    # Preserve cwd for the offline assessment, but not for output containment.
    source_checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target.is_relative_to(source_checkout):
        raise ValueError("DEC-625 refuses report writes anywhere inside checkout")
    report = build_review_manifest_identity_separation(repository_root=checkout)
    validate_review_manifest_identity_separation(report)
    payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    write_once_external_report(target, payload, "DEC-625 refuses conflicting report overwrite")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DEC-625 inert reviewed-manifest/runner-context separation audit"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    assess = commands.add_parser("assess")
    assess.add_argument("--out", type=Path, required=True)
    assess.set_defaults(func=_assess)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
