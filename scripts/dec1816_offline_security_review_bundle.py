"""DEC-1816: seven-source source-only index; no external approval."""
from __future__ import annotations

import argparse
import hashlib
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


# Historical reviewer issue references are navigation only. Open issues
# are NOT attestations, signatures, or permissions to dispatch/trade.
REVIEW_ISSUE_REFERENCES = {
    "effective_github_admin_and_inherited_ruleset_inventory": ("https://github.com/Dtwosam/FMP/issues/779",),
    "exclusive_continuous_ref_lock_and_no_bypass": ("https://github.com/Dtwosam/FMP/issues/779", "https://github.com/Dtwosam/FMP/pull/821"),
    "independent_reviewed_source_sha_workflow_identity": ("https://github.com/Dtwosam/FMP/pull/821",),
    "installed_three_job_precheckout_preinstall_preaccess_enforcement": ("https://github.com/Dtwosam/FMP/pull/820", "https://github.com/Dtwosam/FMP/pull/821"),
    "privileged_runner_os_isolation_and_publisher_witness": ("https://github.com/Dtwosam/FMP/pull/820",),
    "frozen_dec609_dec610_provenance_reauthentication": ("https://github.com/Dtwosam/FMP/issues/779",),
    "fresh_complete_authoritative_one_shot_annual_run_inventory": ("https://github.com/Dtwosam/FMP/issues/779", "https://github.com/Dtwosam/FMP/pull/821"),
    "separate_2023_run385_attempt1_human_execution_decision": ("https://github.com/Dtwosam/FMP/issues/779", "https://github.com/Dtwosam/FMP/pull/821"),
}


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
        and set(REVIEW_ISSUE_REFERENCES) == {
            row["id"] for row in proofs
        }
    ):
        raise InvalidReviewBundle("eight MISSING independent owners disagree")
    payload = {
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
                "tracking_refs_not_approvals": list(
                    REVIEW_ISSUE_REFERENCES[row["id"]]
                ),
            }
            for row in proofs
        ],
        "independent_external_admin_runner_proof_verified": False,
        "2023_run385_attempt1_authorized": False,
        "broker_demo_live_or_real_money_authorized": False,
        "allowed_actions": [],
        "no_external_actions_performed": True,
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    payload["offline_request_fingerprint_sha256"] = hashlib.sha256(
        encoded).hexdigest()
    return payload


def validate_review_index_fingerprint(report):
    """Check exact local JSON identity, NOT any external witness/signature."""
    if type(report) is not dict:
        raise InvalidReviewBundle("frozen index must be an ordinary dict")
    fingerprint = report.get("offline_request_fingerprint_sha256")
    if not (
        type(fingerprint) is str and len(fingerprint) == 64
        and all(c in "0123456789abcdef" for c in fingerprint)
    ):
        raise InvalidReviewBundle("source-only index digest is missing/malformed")
    data = {k: v for k, v in report.items()
            if k != "offline_request_fingerprint_sha256"}
    try:
        canonical = json.dumps(
            data, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise InvalidReviewBundle("source-only index has unsupported/nonfinite fields") from exc
    if hashlib.sha256(canonical).hexdigest() != fingerprint:
        raise InvalidReviewBundle("source-only index contents differ from SHA-256")
    return True


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
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise InvalidReviewBundle(
            "unsupported or nonfinite seven-source review data") from exc
    if actual != canonical:
        raise InvalidReviewBundle(
            "human-readable bundle differs from canonical BLOCKED review index")
    validate_review_index_fingerprint(report)
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
            "Related unresolved review: " + ", ".join(
                row["tracking_refs_not_approvals"]),
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
        "Offline request identity SHA-256 (NOT an attestation): "
        + report["offline_request_fingerprint_sha256"],
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


def format_unfulfilled_review_requests(report):
    """Export only MISSING evidence tasks from the exact canonical offline index."""
    if type(report) is not dict:
        raise InvalidReviewBundle("review requests need an ordinary frozen index")
    validate_review_index_fingerprint(report)
    try:
        received = json.dumps(
            report, sort_keys=True, separators=(",", ":"), allow_nan=False)
        reference = json.dumps(
            compile_blocked_review_bundle(),
            sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise InvalidReviewBundle("unsupported/nonfinite review request") from exc
    if received != reference:
        raise InvalidReviewBundle("review requests are not canonical BLOCKED evidence")
    items = report["unfulfilled_independent_review_requests"]
    if not (
        type(items) is list and len(items) == 8
        and all(
            type(item) is dict
            and item["status"] == "MISSING"
            and item["evidence_ref"] is None
            and item["reviewer_signoff"] is None
            for item in items
        )
    ):
        raise InvalidReviewBundle("independent requests cannot be marked complete")
    return {
        "schema": "fmp_dec1826_offline_unfulfilled_review_requests_v1",
        "disposition": "BLOCKED_NO_EXECUTION_PERMISSION",
        "source_only_not_current_admin_or_runner_attestation": True,
        "parent_offline_index_sha256": report["offline_request_fingerprint_sha256"],
        "protected_annual_identity": report[
            "next_irreversible_annual_identity_no_dispatch"],
        "unfulfilled_independent_review_requests": items,
        "independent_external_proofs_verified": False,
        "annual_dispatch_or_retry_authorized": False,
        "broker_demo_live_or_real_money_authorized": False,
        "allowed_actions": [],
    }


def _read_strict_saved_json(path):
    """Single bounded, nofollow, duplicate-free JSON-object trust boundary."""
    audit = runpy.run_path(str(runpy.run_path(str(SIX))["DOC_AUDIT"]))
    raw = audit["_read_regular_nofollow"](Path(path))
    try:
        saved = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=audit["_strict_pairs"],
            parse_constant=audit["_reject_constant"],
        )
    except (UnicodeError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise InvalidReviewBundle(
            "saved reviewer packet has malformed or unsupported JSON"
        ) from exc
    if type(saved) is not dict:
        raise InvalidReviewBundle(
            "saved reviewer packet must be exactly one JSON object"
        )
    return saved


def verify_saved_blocked_review_packet(path):
    """Verify saved JSON against new pinned local inputs; never authorizes."""
    saved = _read_strict_saved_json(path)
    try:
        fresh = compile_blocked_review_bundle()
        saved_bytes = json.dumps(
            saved, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
        fresh_bytes = json.dumps(
            fresh, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (UnicodeError, TypeError, ValueError, KeyError, OverflowError, RecursionError) as exc:
        raise InvalidReviewBundle("saved BLOCKED packet is invalid JSON") from exc
    validate_review_index_fingerprint(saved)
    if saved_bytes != fresh_bytes:
        raise InvalidReviewBundle(
            "saved BLOCKED packet differs from freshly pinned seven-source review"
        )
    return fresh


def verify_saved_unfulfilled_review_requests(path):
    """Validate compact MISSING-only requests against freshly pinned evidence."""
    saved = _read_strict_saved_json(path)
    try:
        canonical_saved = json.dumps(
            saved, sort_keys=True, separators=(",", ":"), allow_nan=False,
        )
        fresh = format_unfulfilled_review_requests(
            compile_blocked_review_bundle())
        canonical_fresh = json.dumps(
            fresh, sort_keys=True, separators=(",", ":"), allow_nan=False,
        )
    except (UnicodeError, TypeError, ValueError, KeyError, OverflowError, RecursionError) as exc:
        raise InvalidReviewBundle(
            "saved unfulfilled requests have malformed or unsupported JSON"
        ) from exc
    if canonical_saved != canonical_fresh:
        raise InvalidReviewBundle(
            "saved independent requests differ from fresh MISSING-only evidence"
        )
    return fresh


def verify_saved_blocked_markdown(path):
    """Accept only byte-exact canonical CLI Markdown from frozen inputs."""
    audit = runpy.run_path(str(runpy.run_path(str(SIX))["DOC_AUDIT"]))
    raw = audit["_read_regular_nofollow"](Path(path))
    fresh = compile_blocked_review_bundle()
    # The CLI's print() adds its trailing LF to the renderer's own ending LF.
    canonical = (format_blocked_review_bundle_markdown(fresh) + chr(10)).encode(
        "utf-8"
    )
    if raw != canonical:
        raise InvalidReviewBundle(
            "saved Markdown differs from freshly reconstructed BLOCKED review"
        )
    return fresh


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Seven-source historical BLOCKED independent proof review"
    )
    parser.add_argument("--docs-root", type=Path)
    parser.add_argument("--workflow", type=Path)
    parser.add_argument("--worksheet", type=Path)
    parser.add_argument(
        "--verify-report", type=Path,
        help="Check saved BLOCKED JSON against freshly re-read pinned sources",
    )
    parser.add_argument(
        "--verify-requests", type=Path,
        help="Check saved compact MISSING-only requests against pinned sources",
    )
    parser.add_argument(
        "--verify-markdown", type=Path,
        help="Check saved exact CLI Markdown against freshly pinned BLOCKED evidence",
    )
    parser.add_argument(
        "--format", choices=("json", "markdown", "requests"), default="json")
    args = parser.parse_args(argv)
    active = sum(path is not None for path in (
        args.verify_report, args.verify_requests, args.verify_markdown
    ))
    if (
        active > 1
        or (active and any(x is not None for x in (
            args.docs_root, args.workflow, args.worksheet)))
        or (args.verify_markdown is not None and args.format == "requests")
        or (args.verify_requests is not None and args.format == "markdown")
    ):
        print(
            "BLOCKED: saved verification modes cannot be combined or override sources",
            file=sys.stderr,
        )
        return 2
    try:
        if args.verify_markdown is not None:
            output = format_blocked_review_bundle_markdown(
                verify_saved_blocked_markdown(args.verify_markdown))
        elif args.verify_requests is not None:
            output = json.dumps(
                verify_saved_unfulfilled_review_requests(args.verify_requests),
                sort_keys=True, indent=2, allow_nan=False,
            )
        else:
            report = (
                verify_saved_blocked_review_packet(args.verify_report)
                if args.verify_report is not None
                else compile_blocked_review_bundle(
                    args.docs_root, args.workflow, args.worksheet)
            )
            if args.format == "markdown":
                output = format_blocked_review_bundle_markdown(report)
            elif args.format == "requests":
                output = json.dumps(
                    format_unfulfilled_review_requests(report),
                    sort_keys=True, indent=2, allow_nan=False,
                )
            else:
                output = json.dumps(
                    report, sort_keys=True, indent=2, allow_nan=False,
                )
    except (OSError, UnicodeError, TypeError, ValueError, KeyError, OverflowError, RecursionError) as exc:
        print("BLOCKED: invalid source-only review: " + str(exc),
              file=sys.stderr)
        return 2
    print(output)
    return 3  # No action permission can be inferred from a valid report.


if __name__ == "__main__":
    raise SystemExit(main())
