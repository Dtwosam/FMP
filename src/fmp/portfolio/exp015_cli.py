from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
import json
from pathlib import Path

from .challenger_discovery import (
    build_exp015_catalog_evidence,
    write_exp015_catalog_artifacts,
)
from .challenger_discovery_stage_a import (
    aggregate_exp015_stage_a_gates,
    evaluate_exp015_stage_a_cell,
    run_exp015_stage_a_cell,
    write_exp015_stage_a_authorization_artifacts,
    write_exp015_stage_a_cell_artifacts,
)


_SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
_TIMEFRAMES = ("5m", "15m", "1h")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FMP EXP-015 frozen Stage A challenger-discovery tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    catalog = subparsers.add_parser(
        "catalog",
        help="freeze the exact 567 EXP-015 strategy identities before Stage A results",
    )
    catalog.add_argument("--code-commit", required=True)
    catalog.add_argument("--out", required=True, type=Path)

    cell = subparsers.add_parser(
        "stage-a-cell",
        help="run one frozen EXP-015 pair/timeframe cell",
    )
    cell.add_argument("--dataset-root", required=True, type=Path)
    cell.add_argument("--manifest", required=True, type=Path)
    cell.add_argument("--symbol", required=True, choices=_SYMBOLS)
    cell.add_argument("--timeframe", required=True, choices=_TIMEFRAMES)
    cell.add_argument("--code-commit", required=True)
    cell.add_argument("--out", required=True, type=Path)

    authorize = subparsers.add_parser(
        "stage-a-authorize",
        help="aggregate the nine frozen EXP-015 Stage A gates",
    )
    authorize.add_argument("--inputs-root", required=True, type=Path)
    authorize.add_argument("--out", required=True, type=Path)
    return parser


def _load_gate_files(root: Path) -> list[Mapping[str, object]]:
    paths = sorted(Path(root).rglob("gate.json"))
    if len(paths) != 9:
        raise ValueError("EXP-015 Stage A authorization requires exactly nine gate.json files")
    gates: list[Mapping[str, object]] = []
    for path in paths:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read EXP-015 Stage A gate: {path}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"EXP-015 Stage A gate root must be an object: {path}")
        gates.append(value)
    return gates


def main(
    argv: Sequence[str] | None = None,
    *,
    stage_a_cell_command: Callable[..., Mapping[str, object]] = run_exp015_stage_a_cell,
    stage_a_gate_command: Callable[[Mapping[str, object]], Mapping[str, object]] = evaluate_exp015_stage_a_cell,
    stage_a_aggregate_command: Callable[[Sequence[Mapping[str, object]]], Mapping[str, object]] = aggregate_exp015_stage_a_gates,
) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "catalog":
        evidence = build_exp015_catalog_evidence(code_commit=args.code_commit)
        write_exp015_catalog_artifacts(evidence, args.out)
        print(
            json.dumps(
                {
                    "catalog": str(args.out / "catalog.json"),
                    "manifest": str(args.out / "manifest.json"),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "stage-a-cell":
        cell = dict(
            stage_a_cell_command(
                dataset_root=args.dataset_root,
                manifest_path=args.manifest,
                symbol=args.symbol,
                timeframe=args.timeframe,
                code_commit=args.code_commit,
            )
        )
        gate = dict(stage_a_gate_command(cell))
        write_exp015_stage_a_cell_artifacts(
            cell=cell,
            gate=gate,
            out_dir=args.out,
        )
        print(
            json.dumps(
                {
                    "cell": str(args.out / "cell.json"),
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
        authorization = dict(stage_a_aggregate_command(gates))
        write_exp015_stage_a_authorization_artifacts(
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

    raise AssertionError("unreachable EXP-015 command")


__all__ = ["build_parser", "main"]
