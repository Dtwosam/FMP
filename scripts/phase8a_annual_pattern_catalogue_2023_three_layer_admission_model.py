from __future__ import annotations

import argparse
import json
import sys
# A read-only audit must disable bytecode writes before project imports.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_three_layer_admission_model import (
    build_three_layer_admission_model,
    validate_three_layer_admission_model,
)


def _assess(args: argparse.Namespace) -> int:
    checkout = Path.cwd().resolve()
    target = args.out.resolve()
    if target.is_relative_to(checkout):
        raise ValueError("DEC-624 refuses report writes anywhere inside checkout")
    report = build_three_layer_admission_model(repository_root=checkout)
    validate_three_layer_admission_model(report)
    data = json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") != data:
        raise ValueError("DEC-624 refuses conflicting output overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(data, encoding="utf-8")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DEC-624 inert three-layer 2023 tag/ref/SHA admission audit"
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
