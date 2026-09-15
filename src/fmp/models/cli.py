from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .artifacts import write_phase6_artifacts
from .evaluation import run_phase6_strategy_cell


STRATEGIES = ("session_breakout", "volatility_breakout")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the frozen Phase 6 statistical ML filter experiment.",
    )
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--processed-manifest", required=True, type=Path)
    parser.add_argument("--feature-root", required=True, type=Path)
    parser.add_argument("--feature-manifest", required=True, type=Path)
    parser.add_argument("--strategy", required=True, choices=STRATEGIES)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--code-commit", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_phase6_strategy_cell(
        dataset_root=args.dataset_root,
        processed_manifest_path=args.processed_manifest,
        feature_root=args.feature_root,
        feature_manifest_path=args.feature_manifest,
        strategy_id=args.strategy,
        out_dir=args.out,
        code_commit=args.code_commit,
    )
    manifest = write_phase6_artifacts(result, args.out)
    print(
        json.dumps(
            {
                "result": str(args.out / "result.json"),
                "selection": str(args.out / "selection.json"),
                "artifact_manifest": manifest,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    )
    return 0
