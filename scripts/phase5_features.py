from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from fmp.features.cli import run_feature_generation


def _date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid ISO date: {value}") from exc


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(description="Generate frozen Phase 5 feature artifacts")
    out.add_argument("--dataset-root", type=Path, required=True)
    out.add_argument("--manifest", type=Path, required=True)
    out.add_argument("--symbol", required=True)
    out.add_argument("--timeframe", required=True)
    out.add_argument("--start", type=_date, required=True)
    out.add_argument("--end-exclusive", type=_date, required=True)
    out.add_argument("--out", type=Path, required=True)
    out.add_argument("--code-commit", required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    manifest = run_feature_generation(
        dataset_root=args.dataset_root,
        manifest_path=args.manifest,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start=args.start,
        end_exclusive=args.end_exclusive,
        output_root=args.out,
        code_commit=args.code_commit,
    )
    print(json.dumps(manifest, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
