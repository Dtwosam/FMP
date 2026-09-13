from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Protocol

from fmp.data.types import RawChunkKey

from .artifacts import ArtifactDigest, sha256_file, write_parquet_partition
from .normalize import normalize_day
from .quality import analyze_quality
from .raw_reader import CloudRawChunkReader, GithubRawReadOidcTokenProvider, RawChunkReader
from .resample import resample_canonical

GOLDEN_DAY = date(2024, 1, 2)
GOLDEN_PAIRS = ("EURUSD", "USDJPY")


class ReaderLike(Protocol):
    def read(self, key: RawChunkKey) -> bytes | None: ...


class RecordingRawChunkReader:
    def __init__(self, inner: ReaderLike) -> None:
        self.inner = inner
        self.evidence: list[dict[str, object]] = []

    def read(self, key: RawChunkKey) -> bytes | None:
        body = self.inner.read(key)
        if body is None:
            raise ValueError(
                f"cloud golden chunk unexpectedly not_found: {key.pair} {key.side} {key.day}"
            )
        self.evidence.append(
            {
                "pair": key.pair,
                "side": key.side,
                "date_utc": key.day.isoformat(),
                "sha256": hashlib.sha256(body).hexdigest(),
                "size_bytes": len(body),
                "status": "complete",
            }
        )
        return body


def _json_ready(value: object) -> object:
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("cloud golden JSON timestamps must use UTC")
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.part-", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(_json_ready(payload), handle, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _digest_record(digest: ArtifactDigest, root: Path) -> dict[str, object]:
    return {
        "path": _relative(Path(digest.path), root),
        "sha256": digest.sha256,
        "size_bytes": digest.size_bytes,
        "row_count": digest.row_count,
    }


def _json_digest(path: Path, root: Path, row_count: int) -> dict[str, object]:
    return {
        "path": _relative(path, root),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "row_count": row_count,
    }


def run_cloud_golden(
    reader: RawChunkReader | ReaderLike,
    output_root: Path,
    *,
    code_commit: str | None = None,
) -> dict[str, object]:
    root = Path(output_root)
    recording = RecordingRawChunkReader(reader)
    evidence: dict[str, dict[str, dict[str, object]]] = {}

    for pair in GOLDEN_PAIRS:
        canonical = normalize_day(recording, pair, GOLDEN_DAY)  # type: ignore[arg-type]
        if canonical.is_empty():
            raise ValueError(f"cloud golden canonical frame was empty for {pair}")

        pair_root = root / pair
        pair_evidence: dict[str, dict[str, object]] = {}
        one_minute = write_parquet_partition(canonical, pair_root / "1m.parquet")
        pair_evidence["1m"] = _digest_record(one_minute, root)

        quality = analyze_quality(canonical)
        quality_path = pair_root / "quality.json"
        _write_json(quality_path, quality)
        pair_evidence["quality"] = _json_digest(quality_path, root, canonical.height)

        for timeframe in ("5m", "15m", "1h"):
            derived = resample_canonical(canonical, timeframe)  # type: ignore[arg-type]
            digest = write_parquet_partition(derived, pair_root / f"{timeframe}.parquet")
            pair_evidence[timeframe] = _digest_record(digest, root)
        evidence[pair] = pair_evidence

    expected_identities = {
        (pair, side, GOLDEN_DAY.isoformat())
        for pair in GOLDEN_PAIRS
        for side in ("BID", "ASK")
    }
    observed_identities = {
        (str(item["pair"]), str(item["side"]), str(item["date_utc"]))
        for item in recording.evidence
    }
    if observed_identities != expected_identities or len(recording.evidence) != 4:
        raise ValueError("cloud golden proof did not read the exact bounded four-chunk plan")

    summary: dict[str, object] = {
        "protocol": "fmp-phase2-cloud-golden-v1",
        "date_utc": GOLDEN_DAY.isoformat(),
        "pairs": list(GOLDEN_PAIRS),
        "raw_chunks": recording.evidence,
        "evidence": evidence,
        "code_commit": code_commit,
    }
    _write_json(root / "summary.json", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the bounded source-free Phase 2 cloud golden proof")
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--code-commit")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    reader = CloudRawChunkReader(
        args.endpoint,
        GithubRawReadOidcTokenProvider.from_environment(),
    )
    summary = run_cloud_golden(reader, Path(args.out), code_commit=args.code_commit)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
