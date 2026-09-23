from __future__ import annotations

import argparse
import json
from pathlib import Path

from fmp.market_learning.outcome_evidence import (
    compile_outcome_evidence,
    write_outcome_evidence,
)


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Verify and index all nine EXP-044 market-outcome artifacts"
    )
    out.add_argument("--root", type=Path, required=True)
    out.add_argument("--code-commit", required=True)
    out.add_argument("--feature-evidence-fingerprint", required=True)
    out.add_argument("--out", type=Path, required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    evidence = compile_outcome_evidence(
        root=args.root,
        expected_code_commit=args.code_commit,
        expected_feature_evidence_fingerprint=args.feature_evidence_fingerprint,
    )
    write_outcome_evidence(evidence=evidence, path=args.out)
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
