from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
import json
from pathlib import Path

from .challenger_round1 import (
    evaluate_exp013_stage_a_cell_pair,
    run_exp013_stage_a_cell,
)
from .challenger_round1_evidence import (
    build_exp013_stage_a_authorization,
    build_exp013_stage_a_cell_evidence,
    write_exp013_stage_a_authorization,
    write_exp013_stage_a_cell_evidence,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FMP EXP-013 opening-range momentum Stage A evidence tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    cell = subparsers.add_parser(
        "cell",
        help="run one pair/timeframe development+validation Stage A cell",
    )
    cell.add_argument("--dataset-root", required=True, type=Path)
    cell.add_argument("--manifest", required=True, type=Path)
    cell.add_argument(
        "--symbol",
        required=True,
        choices=("EURUSD", "GBPUSD", "USDJPY"),
    )
    cell.add_argument(
        "--timeframe",
        required=True,
        choices=("5m", "15m", "1h"),
    )
    cell.add_argument("--code-commit", required=True)
    cell.add_argument("--out", required=True, type=Path)

    authorize = subparsers.add_parser(
        "authorize",
        help="aggregate all nine Stage A cell packages into Stage B authorization",
    )
    authorize.add_argument("--cells-root", required=True, type=Path)
    authorize.add_argument("--out", required=True, type=Path)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    cell_runner: Callable[..., Mapping[str, object]] = run_exp013_stage_a_cell,
    gate_evaluator: Callable[..., Mapping[str, object]] = evaluate_exp013_stage_a_cell_pair,
    cell_evidence_builder: Callable[..., Mapping[str, object]] = build_exp013_stage_a_cell_evidence,
    cell_writer: Callable[..., Mapping[str, object]] = write_exp013_stage_a_cell_evidence,
    authorization_builder: Callable[..., Mapping[str, object]] = build_exp013_stage_a_authorization,
    authorization_writer: Callable[..., Mapping[str, object]] = write_exp013_stage_a_authorization,
) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "cell":
        development = cell_runner(
            dataset_root=args.dataset_root,
            manifest_path=args.manifest,
            symbol=args.symbol,
            timeframe=args.timeframe,
            split_name="development",
            code_commit=args.code_commit,
        )
        validation = cell_runner(
            dataset_root=args.dataset_root,
            manifest_path=args.manifest,
            symbol=args.symbol,
            timeframe=args.timeframe,
            split_name="validation",
            code_commit=args.code_commit,
        )
        gate = gate_evaluator(
            development=development,
            validation=validation,
        )
        evidence = cell_evidence_builder(
            development=development,
            validation=validation,
            gate=gate,
        )
        cell_writer(evidence, args.out)
        print(
            json.dumps(
                {
                    "result": str(args.out / "cell-evidence.json"),
                    "manifest": str(args.out / "manifest.json"),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "authorize":
        files = tuple(sorted(args.cells_root.rglob("cell-evidence.json")))
        if len(files) != 9:
            raise ValueError(
                "EXP-013 Stage A authorization requires exactly nine cell-evidence files"
            )
        cells = []
        for path in files:
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(f"cannot read EXP-013 Stage A cell evidence: {path}") from exc
            if not isinstance(value, dict):
                raise ValueError("EXP-013 Stage A cell evidence root must be an object")
            cells.append(value)
        authorization = authorization_builder(cells)
        authorization_writer(authorization, args.out)
        print(
            json.dumps(
                {
                    "result": str(args.out / "stage-a-authorization.json"),
                    "manifest": str(args.out / "manifest.json"),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    raise AssertionError("unreachable EXP-013 Stage A command")


__all__ = ["build_parser", "main"]
