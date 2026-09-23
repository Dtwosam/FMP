from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from fmp.market_learning.features import run_market_feature_pair_generation


def _date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid ISO date: {value}") from exc


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Generate deterministic EXP-044 feature copies for all three timeframes of one pair"
    )
    out.add_argument("--dataset-root", type=Path, required=True)
    out.add_argument("--manifest", type=Path, required=True)
    out.add_argument("--symbol", required=True)
    out.add_argument("--start", type=_date, required=True)
    out.add_argument("--end-exclusive", type=_date, required=True)
    out.add_argument("--primary-root", type=Path, required=True)
    out.add_argument("--verification-root", type=Path, required=True)
    out.add_argument("--code-commit", required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    result = run_market_feature_pair_generation(
        dataset_root=args.dataset_root,
        manifest_path=args.manifest,
        symbol=args.symbol,
        start=args.start,
        end_exclusive=args.end_exclusive,
        primary_root=args.primary_root,
        verification_root=args.verification_root,
        code_commit=args.code_commit,
    )
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
