from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .execution_gate import (
    execution_gate_report,
    require_historical_execution_authorized,
)
from .market_learning_adapter import (
    adapt_market_learning_cell,
    compile_cell_evidence,
)
from .pattern_miner import run_in_memory_discovery
from .range_limited_loader import load_verified_exp061_cell_from_indexes
from .run_contract import (
    compile_aggregate_evidence,
    run_contract_payload,
    validate_aggregate_evidence,
)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read EXP-061 JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"EXP-061 JSON root must be an object: {path}")
    return value


def _contract(args: argparse.Namespace) -> int:
    payload = run_contract_payload(code_commit=args.code_commit)
    out = Path(args.out)
    _write_json(out / "run-contract.json", payload)
    return 0


def _execution_gate(args: argparse.Namespace) -> int:
    report = execution_gate_report(code_commit=args.code_commit)
    if args.out is not None:
        _write_json(Path(args.out), report)
    require_historical_execution_authorized(code_commit=args.code_commit)
    return 0


def _cell(args: argparse.Namespace) -> int:
    require_historical_execution_authorized(code_commit=args.code_commit)

    verified = load_verified_exp061_cell_from_indexes(
        feature_root=Path(args.feature_root),
        outcome_root=Path(args.outcome_root),
        feature_evidence_path=Path(args.feature_evidence),
        outcome_evidence_path=Path(args.outcome_evidence),
        symbol=args.symbol,
        timeframe=args.timeframe,
    )
    adapted = adapt_market_learning_cell(
        feature_frame=verified.feature_frame,
        outcome_frame=verified.outcome_frame,
        symbol=args.symbol,
        timeframe=args.timeframe,
    )
    result = run_in_memory_discovery(
        adapted.feature_observations,
        adapted.outcome_observations,
        symbol=args.symbol,
        timeframe=args.timeframe,
        horizon_minutes=args.horizon_minutes,
    )
    evidence = compile_cell_evidence(
        result,
        code_commit=args.code_commit,
        processed_manifest_sha256=verified.processed_manifest_sha256,
        feature_manifest_sha256=verified.feature_manifest_sha256,
        outcome_manifest_sha256=verified.outcome_manifest_sha256,
        feature_evidence_fingerprint=verified.feature_evidence_fingerprint,
        outcome_evidence_fingerprint=verified.outcome_evidence_fingerprint,
    )
    out = Path(args.out)
    _write_json(out / "cell-evidence.json", evidence)
    return 0


def _aggregate(args: argparse.Namespace) -> int:
    require_historical_execution_authorized(code_commit=args.code_commit)

    root = Path(args.inputs_root)
    paths = sorted(root.rglob("cell-evidence.json"))
    values = [_load_json(path) for path in paths]
    aggregate = compile_aggregate_evidence(
        values,
        code_commit=args.code_commit,
    )
    validate_aggregate_evidence(aggregate)
    out = Path(args.out)
    _write_json(out / "aggregate-evidence.json", aggregate)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phase8a_exp061",
        description="EXP-061 discovery-first source-only CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    contract = sub.add_parser("contract")
    contract.add_argument("--code-commit", required=True)
    contract.add_argument("--out", required=True)
    contract.set_defaults(func=_contract)

    gate = sub.add_parser("execution-gate")
    gate.add_argument("--code-commit", required=True)
    gate.add_argument("--out")
    gate.set_defaults(func=_execution_gate)

    cell = sub.add_parser("cell")
    cell.add_argument("--feature-root", required=True)
    cell.add_argument("--outcome-root", required=True)
    cell.add_argument("--feature-evidence", required=True)
    cell.add_argument("--outcome-evidence", required=True)
    cell.add_argument("--symbol", required=True)
    cell.add_argument("--timeframe", required=True)
    cell.add_argument("--horizon-minutes", required=True, type=int)
    cell.add_argument("--code-commit", required=True)
    cell.add_argument("--out", required=True)
    cell.set_defaults(func=_cell)

    aggregate = sub.add_parser("aggregate")
    aggregate.add_argument("--inputs-root", required=True)
    aggregate.add_argument("--code-commit", required=True)
    aggregate.add_argument("--out", required=True)
    aggregate.set_defaults(func=_aggregate)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (PermissionError, ValueError) as exc:
        parser.exit(73 if isinstance(exc, PermissionError) else 2, f"{exc}\n")


__all__ = ["build_parser", "main"]
