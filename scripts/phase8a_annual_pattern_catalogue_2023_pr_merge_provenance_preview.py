from __future__ import annotations

import argparse
import hashlib
import json
import sys

# Prevent project bytecode writes even if caller has not set the environment.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

MAX_EVIDENCE_BYTES = 1024 * 1024


def _unique_object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DEC-633 refuses duplicate JSON evidence keys")
        result[key] = value
    return result


def _invalid_json_constant(value: str) -> object:
    raise ValueError(f"DEC-633 refuses non-JSON numeric constant: {value}")


def _load_evidence(path: Path) -> object:
    with path.open("rb") as source:
        raw = source.read(MAX_EVIDENCE_BYTES + 1)
    if len(raw) > MAX_EVIDENCE_BYTES:
        raise ValueError("DEC-633 refuses oversized JSON evidence")
    return json.loads(
        raw.decode("utf-8"), object_pairs_hook=_unique_object_pairs,
        parse_constant=_invalid_json_constant,
    )

from fmp.discovery.annual_pattern_catalogue_2023_pr_merge_provenance_preview import (
    classify_pr_ci_provenance,
)


def _assess(args: argparse.Namespace) -> int:
    checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target.is_relative_to(checkout):
        raise ValueError("DEC-633 refuses reports anywhere inside source checkout")
    evidence = _load_evidence(args.evidence)
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
    # Exclusive creation closes the exists() -> write_text() overwrite race.
    try:
        with target.open("x", encoding="utf-8") as report_file:
            report_file.write(content)
    except FileExistsError:
        if target.read_text(encoding="utf-8") != content:
            raise ValueError("DEC-633 refuses conflicting report overwrite") from None
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
