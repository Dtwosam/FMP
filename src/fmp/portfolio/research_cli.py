from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
from datetime import date
import json
from pathlib import Path

from .contracts import PHASE8A_EXPERIMENT_ID
from .research_batch import (
    Phase8ABatchPlan,
    run_phase8a_retrospective_batch,
    select_historical_inventory,
    write_phase8a_batch_artifacts,
)
from .research_data import RetrospectiveRange

_SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
_TIMEFRAMES = ("5m", "15m", "1h")
_FAMILIES = (
    "mean_reversion",
    "previous_day_rejection",
    "session_breakout",
    "session_sweep_rejection",
    "trend_continuation",
    "volatility_breakout",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FMP Phase 8A retrospective multi-strategy research tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory = subparsers.add_parser(
        "inventory",
        help="show the frozen historical strategy identities for one pair/timeframe cell",
    )
    inventory.add_argument("--symbol", required=True, choices=_SYMBOLS)
    inventory.add_argument("--timeframe", required=True, choices=_TIMEFRAMES)
    inventory.add_argument("--family", action="append", choices=_FAMILIES)

    batch = subparsers.add_parser(
        "batch",
        help="run retrospective diagnostics over frozen historical strategy identities",
    )
    batch.add_argument("--dataset-root", required=True, type=Path)
    batch.add_argument("--manifest", required=True, type=Path)
    batch.add_argument("--symbol", required=True, choices=_SYMBOLS)
    batch.add_argument("--timeframe", required=True, choices=_TIMEFRAMES)
    batch.add_argument("--start", required=True, type=date.fromisoformat)
    batch.add_argument("--end-exclusive", required=True, type=date.fromisoformat)
    batch.add_argument("--out", required=True, type=Path)
    batch.add_argument("--code-commit", required=True)
    batch.add_argument("--experiment-id", default=PHASE8A_EXPERIMENT_ID)
    batch.add_argument("--family", action="append", choices=_FAMILIES)
    return parser


def _inventory_record(args: argparse.Namespace) -> dict[str, object]:
    records = select_historical_inventory(
        symbol=args.symbol,
        timeframe=args.timeframe,
        families=args.family,
    )
    families = sorted({item.strategy.family for item in records})
    return {
        "protocol": "fmp-phase8a-inventory-v1",
        "experiment_id": PHASE8A_EXPERIMENT_ID,
        "promotion_authorized": False,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "families": families,
        "strategy_identity_count": len(records),
        "strategies": [
            {
                "fingerprint": item.strategy.fingerprint,
                "family": item.strategy.family,
                "version": item.strategy.version,
                "parameters_json": item.strategy.parameters_json,
                "historical_lifecycle": item.lifecycle.value,
                "historical_evidence_id": item.evidence_id,
            }
            for item in records
        ],
    }


def main(
    argv: Sequence[str] | None = None,
    *,
    batch_command: Callable[..., Mapping[str, object]] = run_phase8a_retrospective_batch,
) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "inventory":
        print(
            json.dumps(
                _inventory_record(args),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
        )
        return 0

    if args.command == "batch":
        plan = Phase8ABatchPlan(
            experiment_id=args.experiment_id,
            symbol=args.symbol,
            timeframe=args.timeframe,
            research_range=RetrospectiveRange(
                start=args.start,
                end_exclusive=args.end_exclusive,
            ),
            runner_code_commit=args.code_commit,
            families=tuple(args.family) if args.family else tuple(sorted(_FAMILIES)),
        )
        result = batch_command(
            plan=plan,
            dataset_root=args.dataset_root,
            manifest_path=args.manifest,
        )
        write_phase8a_batch_artifacts(result, args.out)
        print(
            json.dumps(
                {
                    "result": str(args.out / "batch.json"),
                    "manifest": str(args.out / "manifest.json"),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    raise AssertionError("unreachable Phase 8A research command")


__all__ = ["build_parser", "main"]
