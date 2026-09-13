from __future__ import annotations

import argparse
import json
from pathlib import Path
from threading import Lock
from typing import Protocol

from .full_history import (
    DEFAULT_WORKERS,
    FULL_HISTORY_END_EXCLUSIVE,
    FULL_HISTORY_PAIRS,
    FULL_HISTORY_START,
    _validate_workers,
    materialize_pair,
)
from .raw_reader import CloudRawChunkReader, GithubRawReadOidcTokenProvider


class TokenProviderLike(Protocol):
    def get_token(self) -> str: ...


class SynchronizedTokenProvider:
    def __init__(self, inner: TokenProviderLike) -> None:
        self.inner = inner
        self._lock = Lock()

    def get_token(self) -> str:
        with self._lock:
            return self.inner.get_token()


def run_full_history_pair(
    endpoint: str,
    output_root: Path,
    pair: str,
    *,
    code_commit: str | None,
    workers: int = DEFAULT_WORKERS,
) -> dict[str, object]:
    if pair not in FULL_HISTORY_PAIRS:
        raise ValueError("full-history pair is outside frozen V1 scope")
    workers = _validate_workers(workers)
    provider = SynchronizedTokenProvider(GithubRawReadOidcTokenProvider.from_environment())
    reader = CloudRawChunkReader(endpoint, provider)
    return materialize_pair(
        reader,
        Path(output_root),
        pair,
        start=FULL_HISTORY_START,
        end_exclusive=FULL_HISTORY_END_EXCLUSIVE,
        code_commit=code_commit,
        workers=workers,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Materialize the frozen Phase 2 full-history snapshot")
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--pair", required=True, choices=FULL_HISTORY_PAIRS)
    parser.add_argument("--out", required=True)
    parser.add_argument("--code-commit")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workers = _validate_workers(args.workers)
    summary = run_full_history_pair(
        args.endpoint,
        Path(args.out),
        args.pair,
        code_commit=args.code_commit,
        workers=workers,
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
