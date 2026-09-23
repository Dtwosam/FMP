from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fmp.market_learning.source_availability import (
    compile_source_availability,
    load_optional_json,
    write_source_availability,
)
from fmp.market_learning.source_preflight import load_metadata_directory


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Resolve exact EXP-044 Phase 2 source availability"
    )
    out.add_argument("--metadata-root", type=Path, required=True)
    out.add_argument("--release-json", type=Path)
    out.add_argument("--preservation-manifest", type=Path)
    out.add_argument("--minimum-valid-hours", type=float, default=12.0)
    out.add_argument("--out", type=Path, required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.minimum_valid_hours < 0:
        raise SystemExit("--minimum-valid-hours must be non-negative")
    release = load_optional_json(args.release_json)
    manifest = load_optional_json(args.preservation_manifest)
    if (release is None) != (manifest is None):
        raise SystemExit(
            "--release-json and --preservation-manifest must be supplied together"
        )
    report = compile_source_availability(
        metadata_by_symbol=load_metadata_directory(args.metadata_root),
        now_utc=datetime.now(timezone.utc),
        minimum_remaining=timedelta(hours=args.minimum_valid_hours),
        release=release,
        preservation_manifest=manifest,
    )
    write_source_availability(report=report, path=args.out)
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
