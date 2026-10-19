"""DEC-1782: consolidated BLOCKED human review of offline Phase 8A evidence.

Source-only process: load reviewed local files, no credentials, GitHub calls,
workflow dispatch, runner operations, broker access, or action authorization.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
WORKFLOW = ROOT / "tests" / "fixtures" / "dec1779-historical-phase8a-annual-workflow.yml"
DOC_AUDIT = ROOT / "scripts" / "dec1752_phase8a_readiness_report.py"
WORKFLOW_AUDIT = ROOT / "scripts" / "dec1779_annual_workflow_admission_audit.py"


class InvalidHandoff(ValueError):
    """Any mismatched source/readiness state must reject the complete report."""


def _require(condition, reason):
    if not condition:
        raise InvalidHandoff(reason)


def compile_blocked_handoff(docs_root=DOCS, workflow=WORKFLOW):
    docs_module = runpy.run_path(str(DOC_AUDIT))
    workflow_module = runpy.run_path(str(WORKFLOW_AUDIT))
    documentary = docs_module["render_readiness"](Path(docs_root))
    installed = workflow_module["report_blocked_admission"](Path(workflow))
    expected_proofs = docs_module["PROOFS"]
    _require(
        documentary["documentary_status"] == "BLOCKED"
        and documentary["mode"] == "OFFLINE_SOURCE_ONLY_NOT_A_GATE_OR_ATTESTATION"
        and documentary["allows_protected_run"] is False
        and documentary["allows_broker_actions"] is False
        and documentary["allows_live_trading"] is False
        and documentary["current_main_verified"] is False
        and documentary["current_rulesets_and_os_verified"] is False
        and documentary["fresh_run_inventory_verified"] is False
        and documentary["strategy_v1_profit"] is None
        and documentary["no_actions_were_performed"] is True,
        "documentary report is no longer unconditionally non-authorizing",
    )
    identity = documentary["one_shot_run_identity"]
    _require(
        identity == {
            "segment": "2023", "run_number": 385, "attempt_number": 1,
            "authorization": "BLOCKED",
        },
        "blocked 2023/run385/attempt1 one-shot identity changed",
    )
    proofs = documentary["missing_external_proofs"]
    _require(
        type(proofs) is list and len(proofs) == 8
        and tuple(row["id"] for row in proofs) == expected_proofs
        and all(row["status"] == "MISSING" for row in proofs),
        "all eight independent proof packages must remain missing",
    )
    _require(
        installed["disposition"] == "BLOCKED_NOT_EXECUTABLE_AND_NOT_ADMIN_ATTESTED"
        and installed["protected_2023_run385_attempt1_authorized"] is False
        and installed["annual_research_dispatch_authorized"] is False
        and installed["broker_or_trading_authorized"] is False
        and installed["precheckout_admission_proven"] is False
        and installed["preinstall_admission_proven"] is False
        and installed["authoritative_pre_dispatch_ref_lock_proven"] is False
        and installed["allowed_actions"] == [],
        "installed-workflow static report has no verified execution authority",
    )
    jobs = installed["observed_jobs"]
    trace = installed["historical_pregate_payloads"]
    matrix = installed["historical_matrix_inventory"]
    _require(
        tuple(jobs) == ("annual_preflight", "annual_cell", "annual_freeze")
        and tuple(trace) == tuple(jobs)
        and installed["job_count"] == 3
        and matrix["historical_cell_count"] == 18
        and matrix["historical_unique_pair_timeframe_inputs"] == 9
        and matrix["dataset_artifact_ids_and_hashes_not_reauthenticated"] is True,
        "installed job, pre-gate command or 18-cell scope evidence changed",
    )
    _require(
        all(
            jobs[job]["checkout_before_runtime_gate"] is True
            and jobs[job]["main_ref_check_after_checkout"] is True
            and trace[job]["static_source_only_not_actual_runner_trace"] is True
            and trace[job]["no_early_admission_or_immutable_server_ref_proven"] is True
            for job in jobs
        ),
        "unsafe pre-gate ordering and absent external admission must be explicit",
    )
    _require(
        "installed_three_job_precheckout_preinstall_preaccess_enforcement"
        in expected_proofs
        and documentary["source_observation_date_utc"] == "2026-10-19"
        and installed["installed_workflow_requires_main"] is True,
        "the reviewer must distinguish stale public observation from mutable main",
    )
    _require(
        len(documentary["blocked_downstream_stages"]) == 8
        and documentary["blocked_downstream_stages"] == list(docs_module["STAGES"]),
        "blocked downstream research/trading stage list changed",
    )
    return {
        "schema": "fmp_dec1782_offline_six_source_security_handoff_v1",
        "disposition": "BLOCKED_NO_EXECUTION_PERMISSION",
        "one_shot_run_identity": identity,
        "source_observation_date_utc_not_current_attestation":
            documentary["source_observation_date_utc"],
        "source_main_sha_not_current_dispatch_ref":
            documentary["source_main_sha"],
        "documentary_packet_source_sha256": documentary["source_sha256"],
        "installed_workflow_historical_git_blob_sha1":
            installed["historical_source_git_blob_sha1"],
        "installed_workflow_historical_fixture_only":
            installed["installed_workflow_file_absent_from_ci_not_an_attestation"],
        "eight_missing_independent_proofs": proofs,
        "blocked_downstream_stages": documentary["blocked_downstream_stages"],
        "installed_jobs_pregate_and_runtime_gate": {
            job: {
                "runtime_gate_zero_based_index":
                    jobs[job]["zero_based_in_job_gate_index"],
                "observed_setup_and_read_payloads_before_gate":
                    trace[job]["actual_pregate_setup_and_read_payloads"],
                "static_only_not_runner_trace": True,
            }
            for job in jobs
        },
        "installed_historical_cell_count": matrix["historical_cell_count"],
        "installed_historical_pair_timeframe_source_count":
            matrix["historical_unique_pair_timeframe_inputs"],
        "continuous_admin_ref_lock_verified": False,
        "real_runner_os_isolation_verified": False,
        "fresh_one_shot_inventory_verified": False,
        "preregistered_strategy_v1_profit": None,
        "protected_2023_run385_authorized": False,
        "annual_dispatch_or_retry_authorized": False,
        "broker_order_or_real_money_authorized": False,
        "allowed_actions": [],
        "no_external_actions_performed": True,
        "human_review_request": (
            "Independent admins and security reviewers: validate inherited "
            "rulesets and bypass principals; continuous main freeze or separately "
            "approved immutable-ref amendment, installed early preaccess checks "
            "and privileged runner OS isolation; authenticate exact current "
            "source and complete fresh one-shot run inventory. Then require a "
            "separate human run385/attempt1 decision. This handoff grants none."
        ),
    }


def format_blocked_handoff_markdown(report):
    _require(
        type(report) is dict
        and report.get("disposition") == "BLOCKED_NO_EXECUTION_PERMISSION"
        and report.get("protected_2023_run385_authorized") is False
        and report.get("annual_dispatch_or_retry_authorized") is False
        and report.get("broker_order_or_real_money_authorized") is False
        and report.get("allowed_actions") == []
        and report.get("no_external_actions_performed") is True,
        "human handoff must be BLOCKED and without executable actions",
    )
    proof_rows = report["eight_missing_independent_proofs"]
    _require(
        len(proof_rows) == 8
        and all(row["status"] == "MISSING" for row in proof_rows),
        "must show all eight missing independent proofs",
    )
    entries = [
        "# Phase 8A — consolidated independent security-review handoff",
        "",
        "**BLOCKED. NOT AUTHORIZED. NO DISPATCH OR BROKER ORDERS.**",
        "",
        "Five exact source-only document packets and one reviewed historical "
        "installed workflow definition; nothing was executed or refreshed.",
        "Public main observation is stale, not proof of current server "
        "ref continuity or an effective no-bypass admin lock.",
        "",
        "## Required independent proof — all missing",
        "",
        "| Required independent proof | Review role | Status |",
        "| --- | --- | --- |",
    ]
    for row in proof_rows:
        entries.append(
            f"| {row['id']} | {row['review_role']} | **MISSING** |"
        )
    entries.extend([
        "",
        "## Installed workflow observation, not runner attestation",
        "",
        "| Job | Zero-based in-job runtime gate index | Pre-gate source operations |",
        "| --- | ---: | --- |",
    ])
    for job, state in report["installed_jobs_pregate_and_runtime_gate"].items():
        names = ", ".join(
            item["name"]
            for item in state["observed_setup_and_read_payloads_before_gate"]
        )
        entries.append(
            f"| {job} | {state['runtime_gate_zero_based_index']} | {names} |"
        )
    entries.extend([
        "",
        "## Frozen documentary sources",
        "",
        f"Published observation date (STALE): "
        f"{report['source_observation_date_utc_not_current_attestation']}",
        f"Published main SHA (NOT A CURRENT DISPATCH REF): "
        f"{report['source_main_sha_not_current_dispatch_ref']}",
        f"Installed workflow historical Git blob SHA-1: "
        f"{report['installed_workflow_historical_git_blob_sha1']}",
    ])
    for key, sha in report["documentary_packet_source_sha256"].items():
        entries.append(f"{key}: sha256:{sha}")
    entries.extend([
        "",
        "## Outstanding decision",
        "",
        report["human_review_request"],
        "",
        "**This report cannot authorize annual run 385, Strategy V1, "
        "shadow, demo or live trading.**",
        "",
    ])
    return "\n".join(entries)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Non-authorizing, source-only six-source Phase8A audit")
    parser.add_argument("--docs-root", type=Path, default=DOCS)
    parser.add_argument("--workflow", type=Path, default=WORKFLOW)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args(argv)
    try:
        report = compile_blocked_handoff(args.docs_root, args.workflow)
        output = (
            format_blocked_handoff_markdown(report)
            if args.format == "markdown"
            else json.dumps(report, sort_keys=True, indent=2)
        )
    except (OSError, UnicodeError, KeyError, TypeError, ValueError) as exc:
        print("BLOCKED: source-only security handoff was invalid: " + str(exc),
              file=sys.stderr)
        return 2
    print(output, end="" if args.format == "markdown" else "\n")
    return 3  # Human-readable BLOCKED reporting, never an action greenlight.


if __name__ == "__main__":
    raise SystemExit(main())
