from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .oanda import OandaPracticePricingStream
from .qualification import QualificationOutcome, qualify_stream
from .replay import replay_segment
from .runner import run_live_shadow_capture


_ACCOUNT_ENV = "OANDA_PRACTICE_ACCOUNT_ID"
_TOKEN_ENV = "OANDA_PRACTICE_TOKEN"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FMP Phase 8 live-shadow tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)
    qualify = subparsers.add_parser(
        "qualify",
        help="run the bounded OANDA Practice quote-source qualification",
    )
    qualify.add_argument("--out", required=True, type=Path)
    run = subparsers.add_parser(
        "run",
        help="run one explicitly requested Phase 8 shadow capture segment",
    )
    run.add_argument("--campaign-dir", required=True, type=Path)
    replay = subparsers.add_parser(
        "replay",
        help="replay one captured Phase 8 segment without network access",
    )
    replay.add_argument("--segment-dir", required=True, type=Path)
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
    stream_factory: Callable[..., Any] = OandaPracticePricingStream,
    utc_now: Callable[[], datetime] | None = None,
    monotonic_ns: Callable[[], int] | None = None,
    run_command: Callable[..., int] = run_live_shadow_capture,
    replay_command: Callable[[Path], Mapping[str, object]] = replay_segment,
    code_commit_resolver: Callable[[], str] = _current_code_commit,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "replay":
        result = replay_command(Path(args.segment_dir))
        return 0 if result.get("match") is True else 5

    env = os.environ if environ is None else environ
    account_id = env.get(_ACCOUNT_ENV)
    token = env.get(_TOKEN_ENV)
    if not isinstance(account_id, str) or not account_id.strip():
        parser.error(f"{_ACCOUNT_ENV} is required")
    if not isinstance(token, str) or not token.strip():
        parser.error(f"{_TOKEN_ENV} is required")

    now = utc_now or (lambda: datetime.now(timezone.utc))
    mono = monotonic_ns or time.monotonic_ns

    if args.command == "qualify":
        fingerprint = hashlib.sha256(account_id.encode("utf-8")).hexdigest()
        stream = stream_factory(account_id=account_id, token=token)
        result = qualify_stream(
            stream,
            utc_now=now,
            monotonic_ns=mono,
            account_fingerprint=fingerprint,
        )
        _write_json(Path(args.out) / "qualification.json", result.to_record())
        return {
            QualificationOutcome.PASS: 0,
            QualificationOutcome.INCONCLUSIVE: 2,
            QualificationOutcome.CONNECTOR_UNAVAILABLE: 3,
            QualificationOutcome.CONNECTOR_REJECTED: 4,
        }[result.outcome]

    if args.command == "run":
        return run_command(
            account_id=account_id,
            token=token,
            campaign_dir=Path(args.campaign_dir),
            code_commit=code_commit_resolver(),
            utc_now=now,
            monotonic_ns=mono,
            stream_factory=stream_factory,
        )

    parser.error("unsupported Phase 8 command")
    return 2


__all__ = ["build_parser", "main"]
