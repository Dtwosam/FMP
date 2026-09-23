from __future__ import annotations

import argparse
import json
from pathlib import Path

from fmp.market_learning.execution_status import compile_execution_status


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(
        description="Report the exact evidence-gated EXP-044 execution status"
    )
    out.add_argument("--feature-run-json", type=Path)
    out.add_argument("--feature-evidence", type=Path)
    out.add_argument("--outcome-run-json", type=Path)
    out.add_argument("--outcome-evidence", type=Path)
    out.add_argument("--readiness", type=Path)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    status = compile_execution_status(
        feature_run_path=args.feature_run_json,
        feature_evidence_path=args.feature_evidence,
        outcome_run_path=args.outcome_run_json,
        outcome_evidence_path=args.outcome_evidence,
        readiness_path=args.readiness,
    )
    print(json.dumps(status, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
