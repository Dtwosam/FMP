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


HUMAN_REVIEW_REQUEST = (
    "Independent admins and security reviewers: validate inherited "
    "rulesets and bypass principals; continuous main freeze or separately "
    "approved immutable-ref amendment, installed early preaccess checks "
    "and privileged runner OS isolation; authenticate exact current "
    "source and complete fresh one-shot run inventory. Then require a "
    "separate human run385/attempt1 decision. This handoff grants none."
)

REVIEWED_RUNTIME_GATES = {
    "annual_preflight": 7,
    "annual_cell": 4,
    "annual_freeze": 4,
}

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
        "installed_workflow_historical_source_sha256":
            installed["historical_source_sha256"],
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
        "human_review_request": HUMAN_REVIEW_REQUEST,
    }


def _assert_human_review_evidence_is_frozen(report):
    """The Markdown renderer must reject forged *presentation* fields.

    These local source pins cannot grant admin, runner, run385 or trade access.
    They only ensure a rendered review packet did not change after creation.
    """
    docs = runpy.run_path(str(DOC_AUDIT))
    historical = runpy.run_path(str(WORKFLOW_AUDIT))
    expected_proofs = [
        {"id": key, "review_role": owner, "status": "MISSING"}
        for key, owner in zip(docs["PROOFS"], docs["OWNERS"])
    ]
    _require(
        type(report.get("eight_missing_independent_proofs")) is list
        and report["eight_missing_independent_proofs"] == expected_proofs,
        "proof identities, roles and missing states cannot be rewritten",
    )
    _require(
        report.get("documentary_packet_source_sha256")
            == docs["PINNED_SOURCE_SHA256"]
        and report.get("installed_workflow_historical_git_blob_sha1")
            == historical["EXPECTED_GIT_BLOB_SHA1"]
        and report.get("installed_workflow_historical_source_sha256")
            == historical["EXPECTED_HISTORICAL_WORKFLOW_SHA256"]
        and report.get("installed_workflow_historical_fixture_only") is True,
        "exact six-source historical fingerprints and fixture provenance required",
    )
    _require(
        report.get("one_shot_run_identity") == {
            "segment": "2023", "run_number": 385,
            "attempt_number": 1, "authorization": "BLOCKED",
        }
        and report.get("source_observation_date_utc_not_current_attestation")
            == "2026-10-19"
        and report.get("source_main_sha_not_current_dispatch_ref")
            == docs["OBSERVED_PUBLIC_MAIN_SHA"]
        and report.get("blocked_downstream_stages") == list(docs["STAGES"])
        and report.get("human_review_request") == HUMAN_REVIEW_REQUEST,
        "historical one-shot identity, stale source and next approval need review",
    )
    jobs = report.get("installed_jobs_pregate_and_runtime_gate")
    _require(
        type(jobs) is dict
        and tuple(jobs) == tuple(REVIEWED_RUNTIME_GATES)
        and report.get("installed_historical_cell_count") == 18
        and report.get("installed_historical_pair_timeframe_source_count") == 9
        and all(
            type(jobs[name]) is dict
            and jobs[name].get("runtime_gate_zero_based_index") == index
            and jobs[name].get("static_only_not_runner_trace") is True
            and type(jobs[name].get(
                "observed_setup_and_read_payloads_before_gate")) is list
            and all(
                type(item) is dict
                and set(item) == {
                    "name", "payload", "zero_based_step_index"
                }
                and type(item["name"]) is str
                and type(item["payload"]) is str
                and type(item["zero_based_step_index"]) is int
                for item in jobs[name][
                    "observed_setup_and_read_payloads_before_gate"]
            )
            and any(
                item["name"] == "Checkout"
                and item["zero_based_step_index"] == 0
                for item in jobs[name][
                    "observed_setup_and_read_payloads_before_gate"]
            )
            for name, index in REVIEWED_RUNTIME_GATES.items()
        ),
        "installed historical gate positions and matrix cannot be rewritten",
    )
    # A field-by-field snapshot comparison prevents a mutated human-facing
    # trace (step names, command labels, indexes, or injected Markdown rows)
    # from being rendered as the pinned workflow's reviewed command evidence.
    # This is NOT current GitHub or runner attestation.
    pinned_static = historical["report_blocked_admission"]()
    expected_trace = {
        job: {
            "runtime_gate_zero_based_index":
                pinned_static["observed_jobs"][job]["zero_based_in_job_gate_index"],
            "observed_setup_and_read_payloads_before_gate":
                pinned_static["historical_pregate_payloads"][job][
                    "actual_pregate_setup_and_read_payloads"],
            "static_only_not_runner_trace": True,
        }
        for job in REVIEWED_RUNTIME_GATES
    }
    _require(
        jobs == expected_trace,
        "human-facing pre-gate command trace differs from pinned source",
    )
    _require(
        all(report.get(flag) is False for flag in (
            "continuous_admin_ref_lock_verified",
            "real_runner_os_isolation_verified",
            "fresh_one_shot_inventory_verified",
            "protected_2023_run385_authorized",
            "annual_dispatch_or_retry_authorized",
            "broker_order_or_real_money_authorized",
        ))
        and report.get("preregistered_strategy_v1_profit") is None,
        "cannot render a claim of security or trading permission",
    )
    # The pinned six-source evidence is the canonical human handoff. Rebuild
    # it from local reviewed bytes, then compare lossless, strict JSON rather
    # than trusting a caller-edited dict's subset of safety fields.
    # This deliberately rejects unknown keys, fake permission indicators,
    # stale/missing fields, numeric aliases of bools, and nonfinite values.
    try:
        actual_json = json.dumps(
            report, sort_keys=True, separators=(",", ":"), allow_nan=False,
        )
        canonical_json = json.dumps(
            compile_blocked_handoff(),
            sort_keys=True, separators=(",", ":"), allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise InvalidHandoff(
            "human handoff includes unsupported or nonfinite data"
        ) from exc
    _require(
        actual_json == canonical_json,
        "human handoff differs from exact canonical six-source report",
    )


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
    _assert_human_review_evidence_is_frozen(report)
    proof_rows = report["eight_missing_independent_proofs"]
    entries = [
        "# Phase 8A — consolidated independent security-review handoff",
        "",
        "**BLOCKED. NOT AUTHORIZED. NO DISPATCH OR BROKER ORDERS.**",
        "",
        "Five exact source-only documentary packets and one frozen historical "
        "workflow fixture (NOT current installed workflow); nothing was executed "
        "or refreshed.",
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
        "## Irreversible annual research identity — NO DISPATCH",
        "",
        f"Annual segment: {report['one_shot_run_identity']['segment']}",
        f"Frozen next run: {report['one_shot_run_identity']['run_number']}",
        f"Attempt: {report['one_shot_run_identity']['attempt_number']}",
        "**Action status: BLOCKED — no one-shot run may be consumed.**",
        "",
        "## All downstream research and trading stages — BLOCKED",
        "",
        "| Stage | Status |",
        "| --- | --- |",
    ])
    for stage in report["blocked_downstream_stages"]:
        entries.append(f"| {stage} | **BLOCKED** |")
    entries.extend([
        "",
        "## Historical installed-workflow fixture scope (NOT CURRENT)",
        "",
        f"Declared historical research cells: "
        f"{report['installed_historical_cell_count']} "
        "(EURUSD, GBPUSD, USDJPY × 5m, 15m, 1h × 60/240-minute horizons).",
        f"Declared historical distinct pair/timeframe input sources: "
        f"{report['installed_historical_pair_timeframe_source_count']}.",
        "These declarations were not reauthenticated against any live runner "
        "or protected market dataset.",
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
        f"Installed workflow historical source SHA-256: "
        f"{report['installed_workflow_historical_source_sha256']}",
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
