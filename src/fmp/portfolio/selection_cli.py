from __future__ import annotations

import argparse
import hashlib
from collections.abc import Callable, Mapping, Sequence
import json
from pathlib import Path

from .selection_runner import (
    build_dec042_preflight,
    run_dec042_selection,
    write_dec042_preflight_artifacts,
    write_dec042_result_artifacts,
)


_SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FMP DEC-042 frozen retrospective portfolio-selection tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser(
        "preflight",
        help="freeze exact eligible pool and portfolio-set universe before selection data opens",
    )
    preflight.add_argument("--exp015-final", required=True, type=Path)
    preflight.add_argument("--code-commit", required=True)
    preflight.add_argument("--out", required=True, type=Path)

    run = subparsers.add_parser(
        "run",
        help="run exact DEC-042 set universe from an immutable preflight artifact",
    )
    run.add_argument("--preflight", required=True, type=Path)
    run.add_argument(
        "--dataset-source",
        action="append",
        required=True,
        help="SYMBOL=DATASET_ROOT::MANIFEST_PATH",
    )
    run.add_argument("--code-commit", required=True)
    run.add_argument("--out", required=True, type=Path)
    return parser


def _load_json_with_sha(path: Path, *, label: str) -> tuple[dict[str, object], str]:
    try:
        payload = Path(path).read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read {label}: {path}") from exc
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} JSON is malformed") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value, hashlib.sha256(payload).hexdigest()


def _parse_dataset_sources(values: Sequence[str]) -> dict[str, tuple[Path, Path]]:
    sources: dict[str, tuple[Path, Path]] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(
                "dataset source must use SYMBOL=DATASET_ROOT::MANIFEST_PATH"
            )
        symbol, raw_paths = value.split("=", 1)
        if "::" not in raw_paths:
            raise ValueError(
                "dataset source must use SYMBOL=DATASET_ROOT::MANIFEST_PATH"
            )
        dataset_root, manifest_path = raw_paths.split("::", 1)
        symbol = symbol.strip()
        if symbol not in _SYMBOLS or not dataset_root or not manifest_path:
            raise ValueError(
                "dataset source must use supported SYMBOL=DATASET_ROOT::MANIFEST_PATH"
            )
        if symbol in sources:
            raise ValueError(f"duplicate dataset source for {symbol}")
        sources[symbol] = (Path(dataset_root), Path(manifest_path))
    return sources


def main(
    argv: Sequence[str] | None = None,
    *,
    preflight_command: Callable[..., Mapping[str, object]] = build_dec042_preflight,
    selection_command: Callable[..., Mapping[str, object]] = run_dec042_selection,
) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "preflight":
        final_result, final_sha = _load_json_with_sha(
            args.exp015_final,
            label="EXP-015 final shortlist",
        )
        preflight = dict(
            preflight_command(
                exp015_final_result=final_result,
                exp015_final_sha256=final_sha,
                runner_code_commit=args.code_commit,
            )
        )
        write_dec042_preflight_artifacts(preflight, args.out)
        print(
            json.dumps(
                {
                    "preflight": str(args.out / "preflight.json"),
                    "manifest": str(args.out / "manifest.json"),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "run":
        preflight, preflight_sha = _load_json_with_sha(
            args.preflight,
            label="DEC-042 selection preflight",
        )
        result = dict(
            selection_command(
                preflight=preflight,
                preflight_sha256=preflight_sha,
                dataset_sources=_parse_dataset_sources(args.dataset_source),
                code_commit=args.code_commit,
            )
        )
        write_dec042_result_artifacts(result, args.out)
        print(
            json.dumps(
                {
                    "result": str(args.out / "selection.json"),
                    "manifest": str(args.out / "manifest.json"),
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )
        return 0

    raise AssertionError("unreachable DEC-042 selection command")


__all__ = ["build_parser", "main"]
