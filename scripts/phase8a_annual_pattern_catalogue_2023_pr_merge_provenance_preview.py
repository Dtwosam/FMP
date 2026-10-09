from __future__ import annotations

import argparse
import hashlib
import json
import sys

# Prevent project bytecode writes even if caller has not set the environment.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_pr_merge_provenance_preview import (
    classify_pr_ci_provenance,
)


def _assess(args: argparse.Namespace) -> int:
    checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target.is_relative_to(checkout):
        raise ValueError("DEC-633 refuses reports anywhere inside source checkout")
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    payload = {
        "decision": "DEC-633",
        "classification": classify_pr_ci_provenance(evidence),
        "evidence_source": "UNAUTHENTICATED_USER_SUPPLIED_OFFLINE_JSON",
        "github_context_authenticated": False,
        "actual_runner_checkout_attested": False,
        "independent_review_proven": False,
        "merge_authorized": False,
        "annual_dispatch_authorized": False,
        "run385_authorized": False,
        "trading_authorized": False,
        "dispatch_blocked": True,
    }
    canonical = (json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    report = dict(payload, report_sha256=hashlib.sha256(canonical).hexdigest())
    content = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if target.exists():
        if target.read_text(encoding="utf-8") != content:
            raise ValueError("DEC-633 refuses conflicting report overwrite")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DEC-633 inert offline PR CI tree scope audit")
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess")
    assess.add_argument("--evidence", type=Path, required=True)
    assess.add_argument("--out", type=Path, required=True)
    assess.set_defaults(func=_assess)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
