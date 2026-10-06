from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2021_dispatch_authorization import (
    build_2021_dispatch_authorization,
    validate_2021_dispatch_authorization,
)


def _read_json(path: Path) -> Mapping[str, object]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    destination = Path(path)
    payload = json.dumps(
        dict(value),
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing output: {destination}")
    destination.write_text(payload, encoding="utf-8")


def _cmd_authorize(args: argparse.Namespace) -> int:
    value = build_2021_dispatch_authorization(
        _read_json(args.preflight_json),
        repository_root=Path("."),
        authorization_head_sha=args.authorization_head_sha,
    )
    validate_2021_dispatch_authorization(value)
    _write_json(args.out, value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build source-only DEC-587 2021 dispatch authorization."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    authorize = subparsers.add_parser("authorize")
    authorize.add_argument("--preflight-json", type=Path, required=True)
    authorize.add_argument("--authorization-head-sha", required=True)
    authorize.add_argument("--out", type=Path, required=True)
    authorize.set_defaults(func=_cmd_authorize)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
