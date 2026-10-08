from __future__ import annotations

"""DEC-625 assess-only. No installed guards or GitHub actions."""

import argparse
import json
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_review_manifest_identity_separation import (
    build_review_manifest_identity_separation,
    validate_review_manifest_identity_separation,
)


def _assess(args: argparse.Namespace) -> int:
    checkout = Path.cwd().resolve()
    target = args.out.resolve()
    if target.is_relative_to(checkout):
        raise ValueError("DEC-625 refuses report writes anywhere inside checkout")
    report = build_review_manifest_identity_separation(repository_root=checkout)
    validate_review_manifest_identity_separation(report)
    payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") != payload:
        raise ValueError("DEC-625 refuses conflicting report overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")
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
