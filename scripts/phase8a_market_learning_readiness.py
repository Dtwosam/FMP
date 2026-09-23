from __future__ import annotations

import argparse
import json
from pathlib import Path

from fmp.market_learning.readiness import (
    compile_training_readiness,
    write_training_readiness,
)


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Verify EXP-044 feature/outcome evidence and emit training readiness"
    )
    out.add_argument("--feature-evidence", type=Path, required=True)
    out.add_argument("--outcome-evidence", type=Path, required=True)
    out.add_argument("--out", type=Path, required=True)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    readiness = compile_training_readiness(
        feature_evidence_path=args.feature_evidence,
        outcome_evidence_path=args.outcome_evidence,
    )
    write_training_readiness(readiness=readiness, path=args.out)
    print(json.dumps(readiness, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
