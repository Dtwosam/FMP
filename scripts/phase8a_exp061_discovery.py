from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
from typing import Mapping

from fmp.discovery.execution_gate import (
    build_exp061_workflow_source_gate,
    require_exp061_historical_execution,
)
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
    compile_aggregate_evidence,
    run_contract_payload,
    validate_aggregate_evidence,
)
from fmp.market_learning.evidence import load_feature_evidence_index
from fmp.market_learning.outcome_evidence import load_outcome_evidence_index


ROOT = Path(__file__).resolve().parents[1]


def _git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def _require_exact_checkout(code_commit: str) -> None:
    if _git_head() != code_commit:
        raise ValueError("EXP-061 code_commit must equal checkout HEAD")


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(
            dict(value),
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )
    if (
        destination.exists()
        and destination.read_text(encoding="utf-8") != payload
    ):
        raise ValueError(f"conflicting existing EXP-061 output: {destination}")
    destination.write_text(payload, encoding="utf-8")


def _load_cell_evidence_files(root: Path) -> list[Mapping[str, object]]:
    paths = sorted(Path(root).rglob("cell-*.json"))
    if len(paths) != 18:
        raise ValueError("EXP-061 aggregate requires exactly 18 cell evidence files")
    out: list[Mapping[str, object]] = []
    for path in paths:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read EXP-061 cell evidence: {path}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"EXP-061 cell evidence root must be an object: {path}")
        out.append(validate_cell_evidence(value))
    return out


def _preflight_report(
    *,
    feature_evidence_path: Path,
    outcome_evidence_path: Path,
    code_commit: str,
) -> dict[str, object]:
    feature = load_feature_evidence_index(Path(feature_evidence_path))
    outcome = load_outcome_evidence_index(Path(outcome_evidence_path))
    feature_fingerprint = feature.get("evidence_fingerprint")
    outcome_fingerprint = outcome.get("evidence_fingerprint")
    if outcome.get("feature_evidence_fingerprint") != feature_fingerprint:
        raise ValueError("EXP-061 preflight outcome evidence is not bound to feature evidence")
    if not isinstance(feature_fingerprint, str) or len(feature_fingerprint) != 64:
        raise ValueError("EXP-061 preflight feature evidence fingerprint is invalid")
    if not isinstance(outcome_fingerprint, str) or len(outcome_fingerprint) != 64:
        raise ValueError("EXP-061 preflight outcome evidence fingerprint is invalid")
    return {
        "stage": "EXP061_PREFLIGHT_VALIDATED",
        "code_commit": code_commit,
        "feature_evidence_fingerprint": feature_fingerprint,
        "outcome_evidence_fingerprint": outcome_fingerprint,
        "run_contract": run_contract_payload(code_commit=code_commit),
        "reserved_robustness_opened": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description=(
            "EXP-061 discovery workflow source. Historical result execution "
            "remains fail-closed until separately authorized."
        )
    )
    sub = out.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "status",
        help="report the frozen non-executable EXP-061 workflow source gate",
    )

    require = sub.add_parser(
        "require-execution",
        help="fail unless authoritative EXP-061 historical discovery is authorized",
    )
    require.add_argument("--code-commit", required=True)

    preflight = sub.add_parser(
        "preflight",
        help="validate frozen EXP-044 aggregate evidence when execution is authorized",
    )
    preflight.add_argument("--feature-evidence", type=Path, required=True)
    preflight.add_argument("--outcome-evidence", type=Path, required=True)
    preflight.add_argument("--code-commit", required=True)
    preflight.add_argument("--out", type=Path, required=True)

    cell = sub.add_parser(
        "run-cell",
        help="run one frozen EXP-061 cell when separately authorized",
    )
    cell.add_argument("--feature-root", type=Path, required=True)
    cell.add_argument("--outcome-root", type=Path, required=True)
    cell.add_argument("--feature-evidence", type=Path, required=True)
    cell.add_argument("--outcome-evidence", type=Path, required=True)
    cell.add_argument(
        "--symbol",
        choices=("EURUSD", "GBPUSD", "USDJPY"),
        required=True,
    )
    cell.add_argument(
        "--timeframe",
        choices=("5m", "15m", "1h"),
        required=True,
    )
    cell.add_argument(
        "--horizon-minutes",
        type=int,
        choices=(60, 240),
        required=True,
    )
    cell.add_argument("--code-commit", required=True)
    cell.add_argument("--out", type=Path, required=True)

    aggregate = sub.add_parser(
        "aggregate",
        help="compile exact 18-cell EXP-061 evidence when authorized",
    )
    aggregate.add_argument("--cell-root", type=Path, required=True)
    aggregate.add_argument("--code-commit", required=True)
    aggregate.add_argument("--out", type=Path, required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)

    if args.command == "status":
        print(
            json.dumps(
                build_exp061_workflow_source_gate(repository_root=ROOT),
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )
        )
        return 0

    try:
        execution = require_exp061_historical_execution(
            repository_root=ROOT,
            code_commit=args.code_commit,
        )
    except PermissionError as exc:
        raise SystemExit(str(exc)) from exc

    code_commit = str(execution["code_commit"])
    _require_exact_checkout(code_commit)

    if args.command == "require-execution":
        print(
            json.dumps(
                execution,
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )
        )
        return 0

    if args.command == "preflight":
        report = _preflight_report(
            feature_evidence_path=args.feature_evidence,
            outcome_evidence_path=args.outcome_evidence,
            code_commit=code_commit,
        )
        _write_json(args.out, report)
        return 0

    if args.command == "run-cell":
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
            code_commit=code_commit,
            processed_manifest_sha256=loaded.processed_manifest_sha256,
            feature_manifest_sha256=loaded.feature_manifest_sha256,
            outcome_manifest_sha256=loaded.outcome_manifest_sha256,
            feature_evidence_fingerprint=loaded.feature_evidence_fingerprint,
            outcome_evidence_fingerprint=loaded.outcome_evidence_fingerprint,
        )
        validate_cell_evidence(evidence)
        _write_json(args.out, evidence)
        return 0

    if args.command == "aggregate":
        evidence = compile_aggregate_evidence(
            _load_cell_evidence_files(args.cell_root),
            code_commit=code_commit,
        )
        validate_aggregate_evidence(evidence)
        _write_json(args.out, evidence)
        return 0

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
