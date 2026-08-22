from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Callable, Iterable, Protocol

from .acquire import AcquisitionResult, acquire_chunk
from .cloud import GithubOidcTokenProvider, SupabaseRawMirror, mirror_acquisition_result
from .coverage import build_coverage_report, verify_snapshot
from .types import RawChunkKey

V1_PAIRS = ("EURUSD", "GBPUSD", "USDJPY")
SIDES = ("BID", "ASK")


class ObjectMirror(Protocol):
    def put_object(self, object_path: str, body: bytes) -> str: ...


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


def process_fetch_plan(
    keys: Iterable[RawChunkKey],
    root: Path,
    acquire_fn: Callable[[RawChunkKey, Path], AcquisitionResult],
    mirror: ObjectMirror | None = None,
) -> list[AcquisitionResult]:
    results: list[AcquisitionResult] = []
    for key in keys:
        result = acquire_fn(key, root)
        if mirror is not None:
            mirror_acquisition_result(root, result, mirror)  # type: ignore[arg-type]
        results.append(result)
    return results


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
    mirror = None
    if args.mirror_url:
        mirror = SupabaseRawMirror(
            endpoint=args.mirror_url,
            token_provider=GithubOidcTokenProvider.from_environment(),
        )

    def configured_acquire(key: RawChunkKey, configured_root: Path) -> AcquisitionResult:
        return acquire_chunk(
            key,
            configured_root,
            timeout_seconds=args.timeout,
            max_attempts=args.attempts,
            recheck_not_found=args.recheck_not_found,
        )

    acquired = process_fetch_plan(
        plan_keys(pairs, args.start, args.end),
        root,
        configured_acquire,
        mirror,
    )
    results: list[dict[str, object]] = []
    for result in acquired:
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


def run_verify(args: argparse.Namespace) -> int:
    pairs = V1_PAIRS if args.pair == "ALL" else (args.pair,)
    report = verify_snapshot(Path(args.out), pairs, args.start, args.end)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["ready"] else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FMP Phase 1 Dukascopy raw-data acquisition")
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch", help="acquire a UTC date range; end is exclusive")
    fetch.add_argument("--pair", choices=(*V1_PAIRS, "ALL"), required=True)
    fetch.add_argument("--start", type=_parse_date, required=True)
    fetch.add_argument("--end", type=_parse_date, required=True, help="exclusive end date")
    fetch.add_argument("--out", default="data")
    fetch.add_argument("--timeout", type=float, default=30.0)
    fetch.add_argument("--attempts", type=int, default=6)
    fetch.add_argument(
        "--mirror-url",
        help="HTTPS FMP raw-ingest endpoint; requires GitHub Actions OIDC environment",
    )
    fetch.add_argument(
        "--recheck-not-found",
        action="store_true",
        help="retry chunks previously recorded as HTTP 404; useful for recently published source history",
    )
    fetch.set_defaults(func=run_fetch)
    coverage = sub.add_parser("coverage", help="summarize acquisition manifests")
    coverage.add_argument("--out", default="data")
    coverage.set_defaults(func=run_coverage)
    verify = sub.add_parser("verify", help="verify every planned chunk has consistent acquisition provenance")
    verify.add_argument("--pair", choices=(*V1_PAIRS, "ALL"), required=True)
    verify.add_argument("--start", type=_parse_date, required=True)
    verify.add_argument("--end", type=_parse_date, required=True, help="exclusive end date")
    verify.add_argument("--out", default="data")
    verify.set_defaults(func=run_verify)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
