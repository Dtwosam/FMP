"""DEC-1816: seven-source source-only index; no external approval."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
SIX = ROOT / "scripts" / "dec1782_offline_security_handoff.py"
BLANK = ROOT / "scripts" / "dec1814_offline_blank_review_worksheet.py"


class InvalidReviewBundle(ValueError):
    """Fail closed when one source-only review packet drifts."""


def compile_blocked_review_bundle(docs_root=None, workflow=None, worksheet=None):
    six = runpy.run_path(str(SIX))
    blank = runpy.run_path(str(BLANK))
    docs = six["DOCS"] if docs_root is None else Path(docs_root)
    fixture = six["WORKFLOW"] if workflow is None else Path(workflow)
    blank_path = blank["WORKSHEET"] if worksheet is None else Path(worksheet)
    first = six["compile_blocked_handoff"](docs, fixture)
    second = blank["report_blocked_blank_worksheet"](blank_path)
    if not (
        type(first) is dict and type(second) is dict
        and first.get("schema") == "fmp_dec1782_offline_six_source_security_handoff_v1"
        and second.get("schema") == "fmp_dec1814_offline_blank_security_worksheet_v1"
        and first.get("disposition") == second.get("disposition") ==
            "BLOCKED_NO_EXECUTION_PERMISSION"
        and first.get("allowed_actions") == second.get("allowed_actions") == []
        and first.get("no_external_actions_performed") is True
        and second.get("no_external_actions_performed") is True
        and first.get("protected_2023_run385_authorized") is False
        and second.get("2023_run385_attempt1_authorized") is False
        and first.get("broker_order_or_real_money_authorized") is False
        and second.get("broker_demo_live_or_real_money_authorized") is False
        and second.get("independent_actual_evidence_verified") is False
        and first.get("continuous_admin_ref_lock_verified") is False
        and first.get("real_runner_os_isolation_verified") is False
        and first.get("fresh_one_shot_inventory_verified") is False
    ):
        raise InvalidReviewBundle("seven-source review must remain fully BLOCKED")
    proofs = first["eight_missing_independent_proofs"]
    if not (
        type(proofs) is list and len(proofs) == 8
        and proofs == second["eight_independent_proofs"]
        and all(type(row) is dict and row.get("status") == "MISSING"
                for row in proofs)
        and tuple(first["independent_proof_acceptance_criteria"]) ==
            tuple(row["id"] for row in proofs)
    ):
        raise InvalidReviewBundle("eight MISSING independent owners disagree")
    return {
        "schema": "fmp_dec1816_source_only_security_review_bundle_v1",
        "disposition": "BLOCKED_NO_EXECUTION_PERMISSION",
        "material": "six_historical_sources_and_one_pinned_blank_worksheet",
        "five_documentary_source_sha256": first["documentary_packet_source_sha256"],
        "historical_workflow_sha256":
            first["installed_workflow_historical_source_sha256"],
        "blank_worksheet_git_blob_sha1":
            second["pinned_historical_worksheet_git_blob_sha1"],
        "observed_main_sha_not_live_ref":
            first["source_main_sha_not_current_dispatch_ref"],
        "observed_date_utc_not_current_attestation":
            first["source_observation_date_utc_not_current_attestation"],
        "next_irreversible_annual_identity_no_dispatch":
            first["one_shot_run_identity"],
        "blocked_downstream_research_and_trading_stages":
            first["blocked_downstream_stages"],
        "eight_missing_independent_proofs": proofs,
        "independent_proof_acceptance_criteria":
            first["independent_proof_acceptance_criteria"],
        "independent_external_admin_runner_proof_verified": False,
        "2023_run385_attempt1_authorized": False,
        "broker_demo_live_or_real_money_authorized": False,
        "allowed_actions": [],
        "no_external_actions_performed": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Seven-source historical BLOCKED independent proof review"
    )
    parser.add_argument("--docs-root", type=Path)
    parser.add_argument("--workflow", type=Path)
    parser.add_argument("--worksheet", type=Path)
    args = parser.parse_args(argv)
    try:
        report = compile_blocked_review_bundle(
            args.docs_root, args.workflow, args.worksheet
        )
    except (OSError, UnicodeError, TypeError, ValueError, KeyError) as exc:
        print("BLOCKED: invalid source-only review: " + str(exc),
              file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return 3  # No action permission can be inferred from a valid report.


if __name__ == "__main__":
    raise SystemExit(main())
