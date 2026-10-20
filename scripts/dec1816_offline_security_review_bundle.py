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


# Reviewed upstream report schemas are intentionally exact; projecting an
# unreviewed approval field away would mask a source producer inconsistency.
SIX_SOURCE_KEYS = frozenset((
    "schema",
    "disposition",
    "one_shot_run_identity",
    "source_observation_date_utc_not_current_attestation",
    "source_main_sha_not_current_dispatch_ref",
    "documentary_packet_source_sha256",
    "installed_workflow_historical_git_blob_sha1",
    "installed_workflow_historical_source_sha256",
    "installed_workflow_historical_fixture_only",
    "eight_missing_independent_proofs",
    "independent_proof_acceptance_criteria",
    "blocked_downstream_stages",
    "installed_jobs_pregate_and_runtime_gate",
    "installed_historical_cell_count",
    "installed_historical_pair_timeframe_source_count",
    "continuous_admin_ref_lock_verified",
    "real_runner_os_isolation_verified",
    "fresh_one_shot_inventory_verified",
    "preregistered_strategy_v1_profit",
    "protected_2023_run385_authorized",
    "annual_dispatch_or_retry_authorized",
    "broker_order_or_real_money_authorized",
    "allowed_actions",
    "no_external_actions_performed",
    "human_review_request",
))
BLANK_WORKSHEET_KEYS = frozenset((
    "schema",
    "disposition",
    "source_material",
    "pinned_historical_worksheet_git_blob_sha1",
    "eight_independent_proofs",
    "independent_actual_evidence_verified",
    "2023_run385_attempt1_authorized",
    "broker_demo_live_or_real_money_authorized",
    "allowed_actions",
    "no_external_actions_performed",
))


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
        type(first) is dict and set(first) == SIX_SOURCE_KEYS
        and type(second) is dict and set(second) == BLANK_WORKSHEET_KEYS
    ):
        raise InvalidReviewBundle(
            "unreviewed, missing or malformed upstream review evidence fields"
        )
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
        "unfulfilled_independent_review_requests": [
            {
                "id": row["id"],
                "review_role": row["review_role"],
                "acceptance_requirement":
                    first["independent_proof_acceptance_criteria"][row["id"]],
                "status": "MISSING",
                "evidence_ref": None,
                "reviewer_signoff": None,
            }
            for row in proofs
        ],
        "independent_external_admin_runner_proof_verified": False,
        "2023_run385_attempt1_authorized": False,
        "broker_demo_live_or_real_money_authorized": False,
        "allowed_actions": [],
        "no_external_actions_performed": True,
    }


def format_blocked_review_bundle_markdown(report):
    """Human-review display of exact re-derived offline evidence, never approval."""
    if type(report) is not dict:
        raise InvalidReviewBundle("human-readable bundle must be a frozen dict")
    try:
        actual = json.dumps(
            report, sort_keys=True, separators=(",", ":"), allow_nan=False)
        canonical = json.dumps(
            compile_blocked_review_bundle(),
            sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise InvalidReviewBundle(
            "unsupported or nonfinite seven-source review data") from exc
    if actual != canonical:
        raise InvalidReviewBundle(
            "human-readable bundle differs from canonical BLOCKED review index")
    identity = report["next_irreversible_annual_identity_no_dispatch"]
    lines = [
        "# Phase 8A — seven-source independent-review handoff",
        "",
        "**BLOCKED. NO PROTECTED RESEARCH, BROKER ORDER OR TRADING PERMISSION.**",
        "",
        "This is a frozen historical source-only request, NOT current GitHub "
        "administrator, runner, OS or one-shot inventory attestation.",
        "",
        "## Irreversible next annual identity — STILL BLOCKED",
        "",
        f"Annual segment: {identity['segment']}",
        f"Run: {identity['run_number']}",
        f"Attempt: {identity['attempt_number']}",
        f"Authorization: **{identity['authorization']}**",
        "",
        "## Eight independently owned proofs — all MISSING",
        "",
        "| Required proof | Reviewer role | Status |",
        "| --- | --- | --- |",
    ]
    for row in report["eight_missing_independent_proofs"]:
        lines.append(
            f"| {row['id']} | {row['review_role']} | **{row['status']}** |"
        )
    lines.extend([
        "",
        "## External acceptance requirements — NOT attestations",
        "",
    ])
    for row in report["unfulfilled_independent_review_requests"]:
        lines.extend([
            f"**{row['id']}** — {row['review_role']} (MISSING)",
            "",
            row["acceptance_requirement"],
            "",
            "Evidence reference: MISSING; reviewer signoff: MISSING.",
            "",
        ])
    lines.extend([
        "## Historical reviewed source identities — NOT LIVE",
        "",
        "Observation date (stale): "
        + report["observed_date_utc_not_current_attestation"],
        "Public main SHA (NOT current dispatch ref): "
        + report["observed_main_sha_not_live_ref"],
        "Pinned historical workflow SHA-256: "
        + report["historical_workflow_sha256"],
        "Pinned blank worksheet Git blob SHA-1: "
        + report["blank_worksheet_git_blob_sha1"],
    ])
    for key, value in report["five_documentary_source_sha256"].items():
        lines.append(f"{key}: sha256:{value}")
    lines.extend([
        "",
        "## Downstream research and trading — BLOCKED",
        "",
    ])
    for stage in report["blocked_downstream_research_and_trading_stages"]:
        lines.append(f"- {stage}: **BLOCKED**")
    lines.extend([
        "",
        "**No reviewer evidence was collected. No phase advancement, "
        "run385 dispatch/retry, shadow/demo/live broker action or real-money "
        "operation is authorized.**",
        "",
    ])
    return chr(10).join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Seven-source historical BLOCKED independent proof review"
    )
    parser.add_argument("--docs-root", type=Path)
    parser.add_argument("--workflow", type=Path)
    parser.add_argument("--worksheet", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args(argv)
    try:
        report = compile_blocked_review_bundle(
            args.docs_root, args.workflow, args.worksheet
        )
        output = (
            format_blocked_review_bundle_markdown(report)
            if args.format == "markdown"
            else json.dumps(report, sort_keys=True, indent=2, allow_nan=False)
        )
    except (OSError, UnicodeError, TypeError, ValueError, KeyError) as exc:
        print("BLOCKED: invalid source-only review: " + str(exc),
              file=sys.stderr)
        return 2
    print(output)
    return 3  # No action permission can be inferred from a valid report.


if __name__ == "__main__":
    raise SystemExit(main())
