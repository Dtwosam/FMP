from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fmp.market_learning.source_preflight import (
    compile_source_preflight,
    load_metadata_directory,
    write_source_preflight,
)


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Validate the frozen Phase 2 source artifacts before EXP-044 execution"
    )
    out.add_argument("--metadata-root", type=Path, required=True)
    out.add_argument("--minimum-valid-hours", type=float, default=12.0)
    out.add_argument("--out", type=Path, required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.minimum_valid_hours < 0:
        raise SystemExit("--minimum-valid-hours must be non-negative")
    metadata = load_metadata_directory(args.metadata_root)
    report = compile_source_preflight(
        metadata_by_symbol=metadata,
        now_utc=datetime.now(timezone.utc),
        minimum_remaining=timedelta(hours=args.minimum_valid_hours),
    )
    write_source_preflight(report=report, path=args.out)
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
