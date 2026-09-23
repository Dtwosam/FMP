from __future__ import annotations

import argparse
import json
from pathlib import Path

from fmp.market_learning.materialize import run_market_outcome_materialization


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Materialize one verified EXP-044 market-outcome cell"
    )
    out.add_argument("--feature-root", type=Path, required=True)
    out.add_argument("--feature-evidence", type=Path, required=True)
    out.add_argument("--dataset-root", type=Path, required=True)
    out.add_argument("--processed-manifest", type=Path, required=True)
    out.add_argument("--symbol", required=True)
    out.add_argument("--timeframe", required=True)
    out.add_argument("--out", type=Path, required=True)
    out.add_argument("--code-commit", required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    manifest = run_market_outcome_materialization(
        feature_root=args.feature_root,
        feature_evidence_path=args.feature_evidence,
        dataset_root=args.dataset_root,
        processed_manifest_path=args.processed_manifest,
        symbol=args.symbol,
        timeframe=args.timeframe,
        output_root=args.out,
        code_commit=args.code_commit,
    )
    print(json.dumps(manifest, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
