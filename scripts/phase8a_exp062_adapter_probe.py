from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.exp062_adapter_probe import (
    compile_exp062_adapter_probe,
    probe_exp062_adapter_cell,
)


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    payload = json.dumps(
        dict(value),
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing output: {path}")
    path.write_text(payload, encoding="utf-8")


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _cell(args: argparse.Namespace) -> int:
    value = probe_exp062_adapter_cell(
        feature_root=args.feature_root,
        outcome_root=args.outcome_root,
        feature_evidence_path=args.feature_evidence,
        outcome_evidence_path=args.outcome_evidence,
        symbol=args.symbol,
        timeframe=args.timeframe,
        code_commit=args.code_commit,
    )
    _write_json(args.out, value)
    return 0


def _aggregate(args: argparse.Namespace) -> int:
    paths = sorted(Path(args.result_root).rglob("probe.json"))
    if len(paths) != 9:
        raise ValueError("DEC-294 aggregate requires exactly nine probe.json files")
    cells = [_read_json(path) for path in paths]
    value = compile_exp062_adapter_probe(
        cells,
        code_commit=args.code_commit,
    )
    _write_json(args.out, value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="EXP-062 read-only real-data adapter probe"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    cell = sub.add_parser("cell")
    cell.add_argument("--feature-root", type=Path, required=True)
    cell.add_argument("--outcome-root", type=Path, required=True)
    cell.add_argument("--feature-evidence", type=Path, required=True)
    cell.add_argument("--outcome-evidence", type=Path, required=True)
    cell.add_argument("--symbol", required=True)
    cell.add_argument("--timeframe", required=True)
    cell.add_argument("--code-commit", required=True)
    cell.add_argument("--out", type=Path, required=True)
    cell.set_defaults(func=_cell)

    aggregate = sub.add_parser("aggregate")
    aggregate.add_argument("--result-root", type=Path, required=True)
    aggregate.add_argument("--code-commit", required=True)
    aggregate.add_argument("--out", type=Path, required=True)
    aggregate.set_defaults(func=_aggregate)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ValueError, PermissionError) as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
