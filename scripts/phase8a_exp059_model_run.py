from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Mapping

from fmp.market_learning.model_artifacts import (
    load_authoritative_cell_artifacts,
)
from fmp.market_learning.model_protocol import ModelCell
from fmp.market_learning.model_successor_fit_temporal_residual_regime_balance_utility_artifacts import (
    compile_fit_temporal_residual_regime_balance_utility_model_result_evidence,
    write_fit_temporal_residual_regime_balance_utility_model_result_evidence,
)
from fmp.market_learning.model_successor_fit_temporal_residual_regime_balance_utility_execution_gate import (
    build_fit_temporal_residual_regime_balance_utility_model_workflow_source_gate,
    require_authoritative_fit_temporal_residual_regime_balance_utility_model_execution,
)
from fmp.market_learning.model_successor_fit_temporal_residual_regime_balance_utility_training import (
    run_fit_temporal_residual_regime_balance_utility_model_cell_core,
)
from fmp.market_learning.readiness import load_training_readiness


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
        raise ValueError(
            "EXP-059 model runner code_commit must equal checkout HEAD"
        )


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
        raise ValueError(
            f"conflicting existing EXP-059 model result: {destination}"
        )
    destination.write_text(payload, encoding="utf-8")


def _load_result_files(root: Path) -> list[Mapping[str, object]]:
    paths = sorted(Path(root).rglob("result-*.json"))
    if len(paths) != 18:
        raise ValueError(
            "EXP-059 aggregate requires exactly 18 cell result files"
        )
    results: list[Mapping[str, object]] = []
    for path in paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(
                f"EXP-059 model result must be an object: {path}"
            )
        results.append(value)
    return results


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description=(
            "EXP-059 fit-temporal residual-regime-balance utility workflow source. "
            "Historical result execution remains fail-closed until a later "
            "decision."
        )
    )
    sub = out.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "status",
        help="report the frozen non-executable EXP-059 workflow source gate",
    )

    require = sub.add_parser(
        "require-execution",
        help="fail unless authoritative EXP-059 result execution is authorized",
    )
    require.add_argument("--code-commit", required=True)

    cell = sub.add_parser(
        "run-cell",
        help="run one EXP-059 successor cell when separately authorized",
    )
    cell.add_argument("--readiness", type=Path, required=True)
    cell.add_argument("--feature-root", type=Path, required=True)
    cell.add_argument("--outcome-root", type=Path, required=True)
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
        help="compile all 18 EXP-059 cell results when authorized",
    )
    aggregate.add_argument("--result-root", type=Path, required=True)
    aggregate.add_argument("--code-commit", required=True)
    aggregate.add_argument("--out", type=Path, required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)

    if args.command == "status":
        print(
            json.dumps(
                build_fit_temporal_residual_regime_balance_utility_model_workflow_source_gate(
                    repository_root=ROOT,
                ),
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )
        )
        return 0

    try:
        execution = (
            require_authoritative_fit_temporal_residual_regime_balance_utility_model_execution(
                repository_root=ROOT,
                code_commit=args.code_commit,
            )
        )
    except PermissionError as exc:
        raise SystemExit(str(exc)) from exc

    _require_exact_checkout(str(execution["code_commit"]))

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

    if args.command == "run-cell":
        readiness = load_training_readiness(args.readiness)
        loaded = load_authoritative_cell_artifacts(
            readiness=readiness,
            feature_root=args.feature_root,
            outcome_root=args.outcome_root,
            symbol=args.symbol,
            timeframe=args.timeframe,
        )
        result = run_fit_temporal_residual_regime_balance_utility_model_cell_core(
            features=loaded.feature_frame,
            outcomes=loaded.outcome_frame,
            cell=ModelCell(
                args.symbol,
                args.timeframe,
                args.horizon_minutes,
            ),
        )
        _write_json(args.out, result)
        return 0

    if args.command == "aggregate":
        evidence = (
            compile_fit_temporal_residual_regime_balance_utility_model_result_evidence(
                _load_result_files(args.result_root),
                code_commit=args.code_commit,
            )
        )
        write_fit_temporal_residual_regime_balance_utility_model_result_evidence(
            evidence,
            path=args.out,
        )
        return 0

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
