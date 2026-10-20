"""DEC-1814: pinned blank worksheet audit. No approval or external action."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKSHEET = ROOT / "docs" / "dec1808-independent-owner-evidence-worksheet.md"
SOURCE_AUDIT = ROOT / "scripts" / "dec1752_phase8a_readiness_report.py"
PINNED_BLANK_WORKSHEET_GIT_BLOB_SHA1 = "c594c97ad9dbbff1a0265256818df25300b45f4b"


class InvalidBlankWorksheet(ValueError):
    """A changed or nonblank worksheet cannot pass a source-only audit."""


def report_blocked_blank_worksheet(path=WORKSHEET):
    source = runpy.run_path(str(SOURCE_AUDIT))
    raw = source["_read_regular_nofollow"](Path(path))
    actual = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + bytes((0,)) + raw
    ).hexdigest()
    if actual != PINNED_BLANK_WORKSHEET_GIT_BLOB_SHA1:
        raise InvalidBlankWorksheet(
            "worksheet bytes differ from pinned MISSING-only review request"
        )
    text = raw.decode("utf-8")
    proofs = source["PROOFS"]
    owners = source["OWNERS"]
    criteria = source["PROOF_ACCEPTANCE_CRITERIA"]
    if not (
        type(proofs) is tuple and type(owners) is tuple
        and len(proofs) == len(owners) == len(criteria) == 8
        and tuple(criteria) == proofs
        and text.count("**Status: MISSING — not authorization.**") == 8
        and all(
            f"### Proof {i}: `{key}`" in text
            and f"**Required reviewer role:** {owners[i - 1]}" in text
            and f"**Acceptance requirement (source-defined):** {criteria[key]}" in text
            for i, key in enumerate(proofs, start=1)
        )
    ):
        raise InvalidBlankWorksheet("blank eight-owner worksheet shape changed")
    return {
        "schema": "fmp_dec1814_offline_blank_security_worksheet_v1",
        "disposition": "BLOCKED_NO_EXECUTION_PERMISSION",
        "source_material": "exact_frozen_blank_worksheet_not_external_evidence",
        "pinned_historical_worksheet_git_blob_sha1": actual,
        "eight_independent_proofs": [
            {"id": key, "review_role": owner, "status": "MISSING"}
            for key, owner in zip(proofs, owners)
        ],
        "independent_actual_evidence_verified": False,
        "2023_run385_attempt1_authorized": False,
        "broker_demo_live_or_real_money_authorized": False,
        "allowed_actions": [],
        "no_external_actions_performed": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Offline frozen blank security worksheet; NEVER approves"
    )
    parser.add_argument("--worksheet", type=Path, default=WORKSHEET)
    args = parser.parse_args(argv)
    try:
        report = report_blocked_blank_worksheet(args.worksheet)
    except (OSError, UnicodeError, TypeError, ValueError) as exc:
        print("BLOCKED: invalid blank worksheet: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return 3  # Always BLOCKED, not a source of permission.


if __name__ == "__main__":
    raise SystemExit(main())
