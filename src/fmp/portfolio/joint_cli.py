from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
from datetime import date
import json
from pathlib import Path

from .contracts import PHASE8A_EXPERIMENT_ID
from .evidence import (
    build_joint_evidence_envelope,
    resolve_historical_strategy_records,
    write_joint_evidence_artifacts,
)
from .joint_research import Phase8AJointPortfolioPlan, run_phase8a_joint_portfolio
from .research_data import RetrospectiveRange


def _parse_dataset_sources(values: Sequence[str]) -> dict[str, tuple[Path, Path]]:
    sources: dict[str, tuple[Path, Path]] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(
                "dataset source must use SYMBOL=DATASET_ROOT::MANIFEST_PATH"
            )
        symbol, raw_paths = value.split("=", 1)
        if "::" not in raw_paths:
            raise ValueError(
                "dataset source must use SYMBOL=DATASET_ROOT::MANIFEST_PATH"
            )
        dataset_root, manifest_path = raw_paths.split("::", 1)
        symbol = symbol.strip()
        if not symbol or not dataset_root or not manifest_path:
            raise ValueError(
                "dataset source must use SYMBOL=DATASET_ROOT::MANIFEST_PATH"
            )
        if symbol in sources:
            raise ValueError(f"duplicate dataset source for {symbol}")
        sources[symbol] = (Path(dataset_root), Path(manifest_path))
    return sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FMP Phase 8A explicit joint-portfolio retrospective evidence tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve = subparsers.add_parser(
        "resolve",
        help="resolve exact historical strategy fingerprints without promotion",
    )
    resolve.add_argument(
        "--strategy-fingerprint",
        action="append",
        required=True,
    )

    run = subparsers.add_parser(
        "run",
        help="run one explicitly supplied frozen historical strategy set",
    )
    run.add_argument(
        "--strategy-fingerprint",
        action="append",
        required=True,
    )
    run.add_argument(
        "--dataset-source",
        action="append",
        required=True,
        help="SYMBOL=DATASET_ROOT::MANIFEST_PATH",
    )
    run.add_argument("--start", required=True, type=date.fromisoformat)
    run.add_argument("--end-exclusive", required=True, type=date.fromisoformat)
    run.add_argument(
        "--slippage-pips",
        required=True,
        type=float,
        choices=(0.2, 0.5, 1.0),
    )
    run.add_argument("--code-commit", required=True)
    run.add_argument("--experiment-id", default=PHASE8A_EXPERIMENT_ID)
    run.add_argument("--out", required=True, type=Path)
    return parser


def _resolve_payload(fingerprints: Sequence[str]) -> dict[str, object]:
    records = resolve_historical_strategy_records(fingerprints)
    return {
        "protocol": "fmp-phase8a-joint-resolve-v1",
        "experiment_id": PHASE8A_EXPERIMENT_ID,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "strategy_count": len(records),
        "strategies": [
            {
                "fingerprint": item.strategy.fingerprint,
                "family": item.strategy.family,
                "version": item.strategy.version,
                "symbol": item.strategy.symbol,
                "timeframe": item.strategy.timeframe,
                "parameters_json": item.strategy.parameters_json,
                "lifecycle": item.lifecycle.value,
                "evidence_id": item.evidence_id,
            }
            for item in records
        ],
    }


def main(
    argv: Sequence[str] | None = None,
    *,
    joint_command: Callable[..., Mapping[str, object]] = run_phase8a_joint_portfolio,
) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "resolve":
        print(
            json.dumps(
                _resolve_payload(args.strategy_fingerprint),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
        )
        return 0

    if args.command == "run":
        records = resolve_historical_strategy_records(args.strategy_fingerprint)
        sources = _parse_dataset_sources(args.dataset_source)
        required_symbols = {item.strategy.symbol for item in records}
        missing = sorted(required_symbols - set(sources))
        if missing:
            raise ValueError(f"missing dataset sources for strategy symbols: {missing}")

        plan = Phase8AJointPortfolioPlan(
            experiment_id=args.experiment_id,
            strategies=tuple(item.strategy for item in records),
            research_range=RetrospectiveRange(
                start=args.start,
                end_exclusive=args.end_exclusive,
            ),
            slippage_pips=args.slippage_pips,
            runner_code_commit=args.code_commit,
        )
        joint_result = joint_command(
            plan=plan,
            dataset_sources=sources,
        )
        envelope = build_joint_evidence_envelope(
            joint_result=joint_result,
            strategy_records=records,
        )
        write_joint_evidence_artifacts(envelope, args.out)
        print(
            json.dumps(
                {
                    "result": str(args.out / "joint-evidence.json"),
                    "manifest": str(args.out / "manifest.json"),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    raise AssertionError("unreachable Phase 8A joint command")


__all__ = ["build_parser", "main"]
