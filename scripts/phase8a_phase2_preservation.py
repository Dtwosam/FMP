from __future__ import annotations

import argparse
import json
from pathlib import Path

from fmp.market_learning.source_preservation import (
    build_preservation_manifest,
    validate_release_metadata,
    write_preservation_manifest,
)


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Build or validate the exact Phase 2 release-preservation contract"
    )
    sub = out.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--code-commit", required=True)
    build.add_argument("--out", type=Path, required=True)

    verify = sub.add_parser("verify-release")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--release-json", type=Path, required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "build":
        manifest = build_preservation_manifest(code_commit=args.code_commit)
        write_preservation_manifest(manifest=manifest, path=args.out)
        print(json.dumps(manifest, sort_keys=True, allow_nan=False))
        return 0

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    release = json.loads(args.release_json.read_text(encoding="utf-8"))
    result = validate_release_metadata(release=release, manifest=manifest)
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
