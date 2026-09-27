from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.market_learning_adapter import (
    adapt_market_learning_cell,
    compile_cell_evidence,
    validate_cell_evidence,
)
from fmp.discovery.pattern_miner import run_in_memory_discovery
from fmp.discovery.range_limited_loader import (
    load_verified_exp061_cell_from_indexes,
)
from fmp.discovery.run_contract import (
    EXPECTED_CELL_COUNT,
    compile_aggregate_evidence,
    validate_aggregate_evidence,
)
from fmp.discovery.workflow_source import (
    require_historical_execution_authorized,
    validate_source_snapshots,
    workflow_source_payload,
)


def _read_json(path: Path) -> Mapping[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        dict(value),
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing output: {destination}")
    destination.write_text(payload, encoding="utf-8")


def _cmd_status(args: argparse.Namespace) -> int:
    print(
        json.dumps(
            workflow_source_payload(code_commit=args.code_commit),
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
    )
    return 0


def _cmd_preflight(args: argparse.Namespace) -> int:
    report = validate_source_snapshots(
        feature_run=_read_json(args.feature_run_json),
        feature_artifacts=_read_json(args.feature_artifacts_json),
        outcome_run=_read_json(args.outcome_run_json),
        outcome_artifacts=_read_json(args.outcome_artifacts_json),
    )
    value = dict(report)
    value["code_commit"] = args.code_commit
    value["workflow_source"] = workflow_source_payload(
        code_commit=args.code_commit
    )
    _write_json(args.out, value)
    return 0


def _cmd_require_execution(args: argparse.Namespace) -> int:
    require_historical_execution_authorized(code_commit=args.code_commit)
    return 0


def _cmd_cell(args: argparse.Namespace) -> int:
    # This gate MUST remain before any artifact/evidence path is opened.
    require_historical_execution_authorized(code_commit=args.code_commit)

    loaded = load_verified_exp061_cell_from_indexes(
        feature_root=args.feature_root,
        outcome_root=args.outcome_root,
        feature_evidence_path=args.feature_evidence,
        outcome_evidence_path=args.outcome_evidence,
        symbol=args.symbol,
        timeframe=args.timeframe,
    )
    adapted = adapt_market_learning_cell(
        feature_frame=loaded.feature_frame,
        outcome_frame=loaded.outcome_frame,
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
        processed_manifest_sha256=loaded.processed_manifest_sha256,
        feature_manifest_sha256=loaded.feature_manifest_sha256,
        outcome_manifest_sha256=loaded.outcome_manifest_sha256,
        feature_evidence_fingerprint=loaded.feature_evidence_fingerprint,
        outcome_evidence_fingerprint=loaded.outcome_evidence_fingerprint,
    )
    validate_cell_evidence(evidence)
    _write_json(args.out, evidence)
    return 0


def _load_cell_evidence(root: Path) -> list[Mapping[str, object]]:
    paths = sorted(Path(root).rglob("cell-evidence.json"))
    if len(paths) != EXPECTED_CELL_COUNT:
        raise ValueError(
            f"aggregate requires exactly {EXPECTED_CELL_COUNT} cell-evidence.json files"
        )
    values: list[Mapping[str, object]] = []
    for path in paths:
        value = _read_json(path)
        validate_cell_evidence(value)
        values.append(value)
    return values


def _cmd_aggregate(args: argparse.Namespace) -> int:
    # This gate MUST remain before any historical result file is opened.
    require_historical_execution_authorized(code_commit=args.code_commit)

    evidence = compile_aggregate_evidence(
        _load_cell_evidence(args.result_root),
        code_commit=args.code_commit,
    )
    validate_aggregate_evidence(evidence)
    _write_json(args.out, evidence)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="EXP-061 dormant discovery workflow CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status")
    status.add_argument("--code-commit", required=True)
    status.set_defaults(func=_cmd_status)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--feature-run-json", type=Path, required=True)
    preflight.add_argument("--feature-artifacts-json", type=Path, required=True)
    preflight.add_argument("--outcome-run-json", type=Path, required=True)
    preflight.add_argument("--outcome-artifacts-json", type=Path, required=True)
    preflight.add_argument("--code-commit", required=True)
    preflight.add_argument("--out", type=Path, required=True)
    preflight.set_defaults(func=_cmd_preflight)

    require = subparsers.add_parser("require-execution")
    require.add_argument("--code-commit", required=True)
    require.set_defaults(func=_cmd_require_execution)

    cell = subparsers.add_parser("cell")
    cell.add_argument("--feature-root", type=Path, required=True)
    cell.add_argument("--outcome-root", type=Path, required=True)
    cell.add_argument("--feature-evidence", type=Path, required=True)
    cell.add_argument("--outcome-evidence", type=Path, required=True)
    cell.add_argument("--symbol", required=True)
    cell.add_argument("--timeframe", required=True)
    cell.add_argument("--horizon-minutes", type=int, required=True)
    cell.add_argument("--code-commit", required=True)
    cell.add_argument("--out", type=Path, required=True)
    cell.set_defaults(func=_cmd_cell)

    aggregate = subparsers.add_parser("aggregate")
    aggregate.add_argument("--result-root", type=Path, required=True)
    aggregate.add_argument("--code-commit", required=True)
    aggregate.add_argument("--out", type=Path, required=True)
    aggregate.set_defaults(func=_cmd_aggregate)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
