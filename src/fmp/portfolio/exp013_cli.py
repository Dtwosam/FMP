from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
import json
from pathlib import Path

from .challenger_round1 import (
    aggregate_exp013_stage_a_gates,
    evaluate_exp013_stage_a_cell_pair,
    run_exp013_stage_a_cell,
    write_exp013_stage_a_authorization_artifacts,
    write_exp013_stage_a_cell_artifacts,
)


_SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
_TIMEFRAMES = ("5m", "15m", "1h")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FMP EXP-013 opening-range momentum Stage A tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    cell = subparsers.add_parser(
        "stage-a-cell",
        help="run one frozen EXP-013 pair/timeframe cell across development and validation",
    )
    cell.add_argument("--dataset-root", required=True, type=Path)
    cell.add_argument("--manifest", required=True, type=Path)
    cell.add_argument("--symbol", required=True, choices=_SYMBOLS)
    cell.add_argument("--timeframe", required=True, choices=_TIMEFRAMES)
    cell.add_argument("--code-commit", required=True)
    cell.add_argument("--out", required=True, type=Path)

    authorize = subparsers.add_parser(
        "stage-a-authorize",
        help="aggregate the nine Stage A gate artifacts without opening Stage B source data",
    )
    authorize.add_argument("--inputs-root", required=True, type=Path)
    authorize.add_argument("--out", required=True, type=Path)
    return parser


def _load_gate_files(root: Path) -> list[Mapping[str, object]]:
    paths = sorted(Path(root).rglob("gate.json"))
    if len(paths) != 9:
        raise ValueError("EXP-013 Stage A authorization requires exactly nine gate.json files")
    gates: list[Mapping[str, object]] = []
    for path in paths:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read EXP-013 Stage A gate: {path}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"EXP-013 Stage A gate root must be an object: {path}")
        gates.append(value)
    return gates


def main(
    argv: Sequence[str] | None = None,
    *,
    stage_a_cell_command: Callable[..., Mapping[str, object]] = run_exp013_stage_a_cell,
    stage_a_gate_command: Callable[..., Mapping[str, object]] = evaluate_exp013_stage_a_cell_pair,
) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "stage-a-cell":
        development = dict(
            stage_a_cell_command(
                dataset_root=args.dataset_root,
                manifest_path=args.manifest,
                symbol=args.symbol,
                timeframe=args.timeframe,
                split_name="development",
                code_commit=args.code_commit,
            )
        )
        validation = dict(
            stage_a_cell_command(
                dataset_root=args.dataset_root,
                manifest_path=args.manifest,
                symbol=args.symbol,
                timeframe=args.timeframe,
                split_name="validation",
                code_commit=args.code_commit,
            )
        )
        gate = dict(
            stage_a_gate_command(
                development=development,
                validation=validation,
            )
        )
        write_exp013_stage_a_cell_artifacts(
            development=development,
            validation=validation,
            gate=gate,
            out_dir=args.out,
        )
        print(
            json.dumps(
                {
                    "development": str(args.out / "development.json"),
                    "validation": str(args.out / "validation.json"),
                    "gate": str(args.out / "gate.json"),
                    "manifest": str(args.out / "manifest.json"),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "stage-a-authorize":
        gates = _load_gate_files(args.inputs_root)
        authorization = aggregate_exp013_stage_a_gates(gates)
        write_exp013_stage_a_authorization_artifacts(
            authorization,
            args.out,
        )
        print(
            json.dumps(
                {
                    "authorization": str(args.out / "authorization.json"),
                    "manifest": str(args.out / "manifest.json"),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    raise AssertionError("unreachable EXP-013 command")


__all__ = ["build_parser", "main"]
