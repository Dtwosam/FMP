from __future__ import annotations

import argparse
import json
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Callable, Iterable, Protocol

from .acquire import AcquisitionError, AcquisitionResult, acquire_chunk
from .cloud import GithubOidcTokenProvider, SupabaseRawMirror, mirror_acquisition_result
from .cloud_audit import (
    GithubAuditOidcTokenProvider,
    SupabaseRawAuditClient,
    verify_cloud_keys,
)
from .coverage import build_coverage_report, verify_exact_keys, verify_snapshot
from .phase1_acceptance import evaluate_phase1_acceptance
from .repair_plan import load_exact_gap_plan
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
    *,
    source_delay_seconds: float = 0.0,
    sleep_fn: Callable[[float], None] = time.sleep,
    continue_on_acquisition_error: bool = False,
    on_acquisition_error: Callable[[RawChunkKey, AcquisitionError], None] | None = None,
) -> list[AcquisitionResult]:
    results: list[AcquisitionResult] = []
    first = True
    for key in keys:
        if not first and source_delay_seconds > 0:
            sleep_fn(source_delay_seconds)
        first = False
        try:
            result = acquire_fn(key, root)
        except AcquisitionError as exc:
            if not continue_on_acquisition_error:
                raise
            if on_acquisition_error is not None:
                on_acquisition_error(key, exc)
            continue
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


def _run_fetch_keys(args: argparse.Namespace, keys: Iterable[RawChunkKey]) -> int:
    if args.recheck_not_found and args.mirror_url:
        raise ValueError(
            "cloud-mirrored --recheck-not-found is unsupported: canonical cloud "
            "manifests are first-write immutable, so a not_found manifest cannot "
            "be promoted in place"
        )

    root = Path(args.out)
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

    failures: list[dict[str, object]] = []

    def record_acquisition_error(key: RawChunkKey, exc: AcquisitionError) -> None:
        payload: dict[str, object] = {
            "pair": key.pair,
            "side": key.side,
            "date": key.day.isoformat(),
            "status": "acquisition_error",
            "error": str(exc),
        }
        failures.append(payload)
        print(json.dumps(payload, sort_keys=True), flush=True)

    acquired = process_fetch_plan(
        keys,
        root,
        configured_acquire,
        mirror,
        source_delay_seconds=args.source_delay,
        continue_on_acquisition_error=args.continue_on_error,
        on_acquisition_error=record_acquisition_error if args.continue_on_error else None,
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
    if failures:
        summary["acquisition_error"] = len(failures)
    print(
        json.dumps(
            {"summary": summary, "chunks": len(results), "failed_chunks": len(failures)},
            sort_keys=True,
        ),
        flush=True,
    )
    # In continue mode, unresolved source chunks are intentionally left without
    # canonical manifests. The following verify/verify-plan step is the
    # fail-closed gate.
    return 0


def run_fetch(args: argparse.Namespace) -> int:
    pairs = V1_PAIRS if args.pair == "ALL" else (args.pair,)
    return _run_fetch_keys(args, plan_keys(pairs, args.start, args.end))


def run_fetch_plan(args: argparse.Namespace) -> int:
    keys = load_exact_gap_plan(Path(args.plan))
    return _run_fetch_keys(args, keys)


def run_coverage(args: argparse.Namespace) -> int:
    report = build_coverage_report(Path(args.out))
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


def run_verify(args: argparse.Namespace) -> int:
    pairs = V1_PAIRS if args.pair == "ALL" else (args.pair,)
    report = verify_snapshot(Path(args.out), pairs, args.start, args.end)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["ready"] else 2


def run_verify_plan(args: argparse.Namespace) -> int:
    keys = load_exact_gap_plan(Path(args.plan))
    report = verify_exact_keys(Path(args.out), keys)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["ready"] else 2


def run_verify_cloud(args: argparse.Namespace) -> int:
    pairs = V1_PAIRS if args.pair == "ALL" else (args.pair,)
    client = SupabaseRawAuditClient(
        endpoint=args.endpoint,
        token_provider=GithubAuditOidcTokenProvider.from_environment(),
        timeout_seconds=args.timeout,
    )
    report = verify_cloud_keys(
        plan_keys(pairs, args.start, args.end),
        client,
        batch_size=args.batch_size,
    )
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["ready"] else 2


def _load_json_object(path: str) -> dict[str, object]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON evidence file: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"JSON evidence file must contain an object: {path}")
    return payload


def run_accept_phase1(args: argparse.Namespace) -> int:
    structural = _load_json_object(args.structural_json)
    accounting = _load_json_object(args.accounting_json)
    if (
        set(accounting) == {"phase1_recovery_accounting"}
        and isinstance(accounting["phase1_recovery_accounting"], dict)
    ):
        accounting = accounting["phase1_recovery_accounting"]
    provenance = _load_json_object(args.provenance_json)
    report = evaluate_phase1_acceptance(structural, accounting, provenance)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["ready"] else 2


def _add_fetch_runtime_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--out", default="data")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--attempts", type=int, default=6)
    parser.add_argument(
        "--source-delay",
        type=float,
        default=0.0,
        help="seconds to pause between consecutive Dukascopy source chunks",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help=(
            "continue attempting later source chunks after AcquisitionError; "
            "failed chunks remain absent so provenance verification still fails closed"
        ),
    )
    parser.add_argument(
        "--mirror-url",
        help="HTTPS FMP raw-ingest endpoint; requires GitHub Actions OIDC environment",
    )
    parser.add_argument(
        "--recheck-not-found",
        action="store_true",
        help=(
            "retry chunks previously recorded as HTTP 404 locally; cannot be "
            "combined with --mirror-url because canonical cloud manifests are "
            "first-write immutable"
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FMP Phase 1 Dukascopy raw-data acquisition")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch", help="acquire a UTC date range; end is exclusive")
    fetch.add_argument("--pair", choices=(*V1_PAIRS, "ALL"), required=True)
    fetch.add_argument("--start", type=_parse_date, required=True)
    fetch.add_argument("--end", type=_parse_date, required=True, help="exclusive end date")
    _add_fetch_runtime_arguments(fetch)
    fetch.set_defaults(func=run_fetch)

    fetch_plan = sub.add_parser(
        "fetch-plan",
        help="acquire only the explicit pair/date/side chunks in an exact-gap JSON plan",
    )
    fetch_plan.add_argument("--plan", required=True)
    _add_fetch_runtime_arguments(fetch_plan)
    fetch_plan.set_defaults(func=run_fetch_plan)

    coverage = sub.add_parser("coverage", help="summarize acquisition manifests")
    coverage.add_argument("--out", default="data")
    coverage.set_defaults(func=run_coverage)

    verify = sub.add_parser("verify", help="verify every planned chunk has consistent acquisition provenance")
    verify.add_argument("--pair", choices=(*V1_PAIRS, "ALL"), required=True)
    verify.add_argument("--start", type=_parse_date, required=True)
    verify.add_argument("--end", type=_parse_date, required=True, help="exclusive end date")
    verify.add_argument("--out", default="data")
    verify.set_defaults(func=run_verify)

    verify_plan = sub.add_parser(
        "verify-plan",
        help="verify acquisition provenance for only the chunks in an exact-gap JSON plan",
    )
    verify_plan.add_argument("--plan", required=True)
    verify_plan.add_argument("--out", default="data")
    verify_plan.set_defaults(func=run_verify_plan)

    verify_cloud = sub.add_parser(
        "verify-cloud",
        help="verify the cloud snapshot manifest provenance and raw SHA-256/size",
    )
    verify_cloud.add_argument("--endpoint", required=True)
    verify_cloud.add_argument("--pair", choices=(*V1_PAIRS, "ALL"), required=True)
    verify_cloud.add_argument("--start", type=_parse_date, required=True)
    verify_cloud.add_argument("--end", type=_parse_date, required=True, help="exclusive end date")
    verify_cloud.add_argument("--batch-size", type=int, default=100)
    verify_cloud.add_argument("--timeout", type=float, default=60.0)
    verify_cloud.set_defaults(func=run_verify_cloud)

    accept_phase1 = sub.add_parser(
        "accept-phase1",
        help="combine structural, recovery-accounting, and cloud-provenance evidence",
    )
    accept_phase1.add_argument("--structural-json", required=True)
    accept_phase1.add_argument("--accounting-json", required=True)
    accept_phase1.add_argument("--provenance-json", required=True)
    accept_phase1.set_defaults(func=run_accept_phase1)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
