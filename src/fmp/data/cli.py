from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

from .acquire import AcquisitionResult, acquire_chunk
from .coverage import build_coverage_report
from .types import RawChunkKey

V1_PAIRS = ("EURUSD", "GBPUSD", "USDJPY")
SIDES = ("BID", "ASK")


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must be YYYY-MM-DD") from exc


def iter_days(start: date, end_exclusive: date) -> Iterable[date]:
    if end_exclusive <= start:
        raise ValueError("end must be after start")
    current = start
    while current < end_exclusive:
        yield current
        current += timedelta(days=1)


def plan_keys(pairs: Iterable[str], start: date, end_exclusive: date) -> list[RawChunkKey]:
    return [
        RawChunkKey(pair, side, day)  # type: ignore[arg-type]
        for pair in pairs
        for day in iter_days(start, end_exclusive)
        for side in SIDES
    ]


def _result_json(result: AcquisitionResult) -> dict[str, object]:
    return {
        "pair": result.key.pair,
        "side": result.key.side,
        "date": result.key.day.isoformat(),
        "status": result.status.value,
        "records": result.records,
        "compressed_size": result.compressed_size,
        "sha256": result.sha256,
        "http_status": result.http_status,
    }


def run_fetch(args: argparse.Namespace) -> int:
    root = Path(args.out)
    pairs = V1_PAIRS if args.pair == "ALL" else (args.pair,)
    results: list[dict[str, object]] = []
    for key in plan_keys(pairs, args.start, args.end):
        result = acquire_chunk(
            key,
            root,
            timeout_seconds=args.timeout,
            max_attempts=args.attempts,
        )
        result_payload = _result_json(result)
        results.append(result_payload)
        print(json.dumps(result_payload, sort_keys=True), flush=True)
    summary: dict[str, int] = {}
    for item in results:
        status = str(item["status"])
        summary[status] = summary.get(status, 0) + 1
    print(json.dumps({"summary": summary, "chunks": len(results)}, sort_keys=True), flush=True)
    return 0


def run_coverage(args: argparse.Namespace) -> int:
    report = build_coverage_report(Path(args.out))
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FMP Phase 1 Dukascopy raw-data acquisition")
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch", help="acquire a UTC date range; end is exclusive")
    fetch.add_argument("--pair", choices=(*V1_PAIRS, "ALL"), required=True)
    fetch.add_argument("--start", type=_parse_date, required=True)
    fetch.add_argument("--end", type=_parse_date, required=True, help="exclusive end date")
    fetch.add_argument("--out", default="data")
    fetch.add_argument("--timeout", type=float, default=30.0)
    fetch.add_argument("--attempts", type=int, default=3)
    fetch.set_defaults(func=run_fetch)
    coverage = sub.add_parser("coverage", help="summarize acquisition manifests")
    coverage.add_argument("--out", default="data")
    coverage.set_defaults(func=run_coverage)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
