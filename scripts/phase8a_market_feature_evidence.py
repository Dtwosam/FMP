from __future__ import annotations

import argparse
import json
from pathlib import Path

from fmp.market_learning.evidence import compile_feature_evidence, write_feature_evidence


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Verify and index all nine EXP-044 market-feature artifacts"
    )
    out.add_argument("--root", type=Path, required=True)
    out.add_argument("--code-commit", required=True)
    out.add_argument("--out", type=Path, required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    evidence = compile_feature_evidence(
        root=args.root,
        expected_code_commit=args.code_commit,
    )
    write_feature_evidence(evidence=evidence, path=args.out)
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
