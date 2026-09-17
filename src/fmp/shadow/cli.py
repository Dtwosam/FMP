from __future__ import annotations

import argparse
import json
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime, timezone
from pathlib import Path

from .campaign import record_provider_closure, register_campaign
from .gates import Phase8ReviewOutcome, review_campaign
from .mt5_bridge import BridgeFileTail, discover_bridge_file
from .qualification import QualificationOutcome, qualify_bridge
from .reference import build_and_write_spread_reference
from .replay import replay_segment
from .runner import run_live_shadow_capture


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FMP Phase 8 MT5 demo shadow tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)
    qualify = subparsers.add_parser(
        "qualify",
        help="run bounded qualification of the fixed local MT5 demo bridge",
    )
    qualify.add_argument("--out", required=True, type=Path)
    run = subparsers.add_parser(
        "run",
        help="run one explicitly requested Phase 8 shadow capture segment from the local MT5 demo bridge",
    )
    run.add_argument("--campaign-dir", required=True, type=Path)
    replay = subparsers.add_parser(
        "replay",
        help="replay one captured Phase 8 segment without broker or network access",
    )
    replay.add_argument("--segment-dir", required=True, type=Path)
    reference = subparsers.add_parser(
        "build-reference",
        help="build the frozen Phase 8 historical spread reference offline",
    )
    reference.add_argument("--dataset-root", required=True, type=Path)
    reference.add_argument("--processed-manifest", required=True, type=Path)
    reference.add_argument("--out", required=True, type=Path)
    register = subparsers.add_parser(
        "register",
        help="register the immutable Phase 8 live-shadow campaign boundary",
    )
    register.add_argument("--reference", required=True, type=Path)
    register.add_argument("--campaign-dir", required=True, type=Path)
    record_closure = subparsers.add_parser(
        "record-closure",
        help="record a provider-documented full-market closure before its London date",
    )
    record_closure.add_argument("--campaign-dir", required=True, type=Path)
    record_closure.add_argument("--london-date", required=True, type=date.fromisoformat)
    record_closure.add_argument("--documentation", required=True)
    review = subparsers.add_parser(
        "review",
        help="review frozen Phase 8 campaign evidence without broker or network access",
    )
    review.add_argument("--campaign-dir", required=True, type=Path)
    return parser


def _write_json(path: Path, record: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        dict(record),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"
    path.write_text(payload, encoding="utf-8")


def _current_code_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        raise RuntimeError("unable to resolve current code commit") from None
    commit = completed.stdout.strip()
    if len(commit) != 40 or any(character not in "0123456789abcdef" for character in commit):
        raise RuntimeError("current code commit is invalid")
    return commit


def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    utc_now: Callable[[], datetime] | None = None,
    monotonic_ns: Callable[[], int] | None = None,
    bridge_discoverer: Callable[[], Path] = discover_bridge_file,
    tail_factory: Callable[[Path], BridgeFileTail] = BridgeFileTail,
    qualify_command: Callable[..., object] = qualify_bridge,
    run_command: Callable[..., int] = run_live_shadow_capture,
    replay_command: Callable[[Path], Mapping[str, object]] = replay_segment,
    reference_command: Callable[..., str] = build_and_write_spread_reference,
    register_command: Callable[..., Mapping[str, object]] = register_campaign,
    record_closure_command: Callable[..., object] = record_provider_closure,
    review_command: Callable[[Path], Phase8ReviewOutcome] = review_campaign,
    code_commit_resolver: Callable[[], str] = _current_code_commit,
) -> int:
    del environ
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "replay":
        result = replay_command(Path(args.segment_dir))
        return 0 if result.get("match") is True else 5

    if args.command == "build-reference":
        reference_command(
            dataset_root=Path(args.dataset_root),
            manifest_path=Path(args.processed_manifest),
            out_dir=Path(args.out),
            code_commit=code_commit_resolver(),
        )
        return 0

    if args.command == "register":
        now = utc_now or (lambda: datetime.now(timezone.utc))
        register_command(
            reference_dir=Path(args.reference),
            campaign_dir=Path(args.campaign_dir),
            code_commit=code_commit_resolver(),
            campaign_start_utc=now(),
        )
        return 0

    if args.command == "record-closure":
        now = utc_now or (lambda: datetime.now(timezone.utc))
        record_closure_command(
            campaign_dir=Path(args.campaign_dir),
            code_commit=code_commit_resolver(),
            london_date=args.london_date,
            documentation=args.documentation,
            recorded_at_utc=now(),
        )
        return 0

    if args.command == "review":
        outcome = review_command(Path(args.campaign_dir))
        return {
            Phase8ReviewOutcome.PASS: 0,
            Phase8ReviewOutcome.NEED_MORE_DATA: 2,
            Phase8ReviewOutcome.REJECT_OPERATIONAL: 3,
            Phase8ReviewOutcome.REJECT_MARKET: 4,
            Phase8ReviewOutcome.REJECT_FINANCIAL: 5,
            Phase8ReviewOutcome.REJECT_SAFETY: 6,
        }[outcome]

    now = utc_now or (lambda: datetime.now(timezone.utc))
    mono = monotonic_ns or time.monotonic_ns

    if args.command == "qualify":
        bridge_path = bridge_discoverer()
        tail = tail_factory(bridge_path)
        result = qualify_command(
            tail,
            utc_now=now,
            monotonic_ns=mono,
        )
        to_record = getattr(result, "to_record", None)
        if not callable(to_record):
            raise TypeError("qualification result must expose to_record()")
        _write_json(Path(args.out) / "qualification.json", to_record())
        outcome = getattr(result, "outcome", None)
        return {
            QualificationOutcome.PASS: 0,
            QualificationOutcome.INCONCLUSIVE: 2,
            QualificationOutcome.CONNECTOR_UNAVAILABLE: 3,
            QualificationOutcome.CONNECTOR_REJECTED: 4,
        }[outcome]

    if args.command == "run":
        bridge_path = bridge_discoverer()
        tail = tail_factory(bridge_path)
        return run_command(
            bridge_tail=tail,
            campaign_dir=Path(args.campaign_dir),
            code_commit=code_commit_resolver(),
            utc_now=now,
            monotonic_ns=mono,
        )

    parser.error("unsupported Phase 8 command")
    return 2


__all__ = ["build_parser", "main"]
