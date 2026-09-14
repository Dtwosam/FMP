from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from fmp.research.reporting import write_benchmark_artifacts
from fmp.research.session_sweep_rejection import run_session_sweep_rejection_grid


SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
TIMEFRAMES = ("5m", "15m", "1h")
SPLITS = ("development", "validation")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the frozen Phase 4 session sweep-rejection research benchmark.",
    )
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--symbol", required=True, choices=SYMBOLS)
    parser.add_argument("--timeframe", required=True, choices=TIMEFRAMES)
    parser.add_argument("--split", required=True, choices=SPLITS)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--code-commit", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_session_sweep_rejection_grid(
        dataset_root=args.dataset_root,
        manifest_path=args.manifest,
        symbol=args.symbol,
        timeframe=args.timeframe,
        split_name=args.split,
        code_commit=args.code_commit,
    )
    manifest = write_benchmark_artifacts(result, args.out)
    print(
        json.dumps(
            {
                "benchmark": str(args.out / "benchmark.json"),
                "artifact_manifest": manifest,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
