from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .oanda import OandaPracticePricingStream
from .qualification import QualificationOutcome, qualify_stream


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


def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    stream_factory: Callable[..., Any] = OandaPracticePricingStream,
    utc_now: Callable[[], datetime] | None = None,
    monotonic_ns: Callable[[], int] | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = os.environ if environ is None else environ

    account_id = env.get(_ACCOUNT_ENV)
    token = env.get(_TOKEN_ENV)
    if not isinstance(account_id, str) or not account_id.strip():
        parser.error(f"{_ACCOUNT_ENV} is required")
    if not isinstance(token, str) or not token.strip():
        parser.error(f"{_TOKEN_ENV} is required")

    if args.command != "qualify":
        parser.error("unsupported Phase 8 command")

    fingerprint = hashlib.sha256(account_id.encode("utf-8")).hexdigest()
    stream = stream_factory(account_id=account_id, token=token)
    result = qualify_stream(
        stream,
        utc_now=utc_now or (lambda: datetime.now(timezone.utc)),
        monotonic_ns=monotonic_ns or time.monotonic_ns,
        account_fingerprint=fingerprint,
    )
    _write_json(Path(args.out) / "qualification.json", result.to_record())

    return {
        QualificationOutcome.PASS: 0,
        QualificationOutcome.INCONCLUSIVE: 2,
        QualificationOutcome.CONNECTOR_UNAVAILABLE: 3,
        QualificationOutcome.CONNECTOR_REJECTED: 4,
    }[result.outcome]


__all__ = ["build_parser", "main"]
