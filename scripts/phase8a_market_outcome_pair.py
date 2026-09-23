from __future__ import annotations

import argparse
import json
from pathlib import Path

from fmp.market_learning.materialize import run_market_outcome_pair_materialization


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Materialize all three verified EXP-044 market-outcome cells for one pair"
    )
    out.add_argument("--feature-root-5m", type=Path, required=True)
    out.add_argument("--feature-root-15m", type=Path, required=True)
    out.add_argument("--feature-root-1h", type=Path, required=True)
    out.add_argument("--feature-evidence", type=Path, required=True)
    out.add_argument("--dataset-root", type=Path, required=True)
    out.add_argument("--processed-manifest", type=Path, required=True)
    out.add_argument("--symbol", required=True)
    out.add_argument("--out-root", type=Path, required=True)
    out.add_argument("--code-commit", required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    manifests = run_market_outcome_pair_materialization(
        feature_roots={
            "5m": args.feature_root_5m,
            "15m": args.feature_root_15m,
            "1h": args.feature_root_1h,
        },
        feature_evidence_path=args.feature_evidence,
        dataset_root=args.dataset_root,
        processed_manifest_path=args.processed_manifest,
        symbol=args.symbol,
        output_root=args.out_root,
        code_commit=args.code_commit,
    )
    print(json.dumps(manifests, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
