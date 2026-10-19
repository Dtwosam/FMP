"""DEC-1752: offline diagnostic of UNAPPROVED Phase 8A evidence packets.

No GitHub API, protected market files, workflow dispatch, broker, network,
credential reads, permissions, or execution path are used here. This reporter
NEVER grants permission: it only displays the documentary blockers that are
present in five source-only packets. A stale snapshot is not live attestation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


FILES = {
    "annual": "dec1726-phase8a-sourceonly-segment-gate-ledger.json",
    "economics": "dec1739-phase8a-economic-evidence-before-shadow.json",
    "dependency": "dec1742-phase8a-blocked-dependency-graph.json",
    "preregistration": "dec1745-strategy-v1-economic-review-preregistration-template.json",
    "admin_snapshot": "dec1750-phase8a-admin-blocker-evidence-snapshot.json",
}
DECISIONS = ("DEC-1726", "DEC-1739", "DEC-1742", "DEC-1745", "DEC-1750")
PROOFS = (
    "effective_github_admin_and_inherited_ruleset_inventory",
    "exclusive_continuous_ref_lock_and_no_bypass",
    "independent_reviewed_source_sha_workflow_identity",
    "installed_three_job_precheckout_preinstall_preaccess_enforcement",
    "privileged_runner_os_isolation_and_publisher_witness",
    "frozen_dec609_dec610_provenance_reauthentication",
    "fresh_complete_authoritative_one_shot_annual_run_inventory",
    "separate_2023_run385_attempt1_human_execution_decision",
)
STAGES = (
    "annual_2023", "remaining_annual_years", "cross_year_economics",
    "strategy_v1", "prospective_shadow", "demo", "phase10",
    "phase11_real_money",
)
REVIEW_FLAGS = (
    "protected_annual_execution_authorized", "annual_catalogues_complete",
    "cross_year_analysis_permitted", "strategy_v1_selected",
    "strategy_v1_frozen", "profitability_accepted",
    "prospective_shadow_authorized", "demo_order_authorized",
    "live_trading_authorized", "market_data_read_by_packet",
    "predefined_thresholds_documented",
)
ECON_FLAGS = (
    "all_years_accepted", "cross_year_comparison_authorized",
    "strategy_v1_frozen", "phase8b_shadow_approved", "demo_approved",
    "phase10_approved", "live_real_money_approved",
    "has_forward_profit_evidence",
)
OWNERS = (
    "Independent repository administrator and ruleset reviewer",
    "Independent security reviewer of continuous exclusive main ref lock",
    "Independent reviewed SHA, source and workflow reviewer",
    "Installed three-job preaccess gate reviewer",
    "Privileged runner OS and publisher isolation reviewer",
    "Historical source and provenance custodian",
    "Independent fresh one-shot run-inventory witness",
    "Separate human run385/attempt1 decision authority",
)


class InvalidDocumentaryState(ValueError):
    """Offline inputs changed or are insufficient: never infer approval."""


def _strict_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise InvalidDocumentaryState("duplicate JSON member: " + key)
        out[key] = value
    return out


def _reject_constant(value):
    raise InvalidDocumentaryState("nonstandard JSON numeric constant: " + value)


def _require(condition, explanation):
    if not condition:
        raise InvalidDocumentaryState(explanation)


def _read_packets(root):
    packets, fingerprints = {}, {}
    for key, filename in FILES.items():
        payload = (root / filename).read_bytes()
        fingerprints[key] = hashlib.sha256(payload).hexdigest()
        packets[key] = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_strict_pairs,
            parse_constant=_reject_constant,
        )
    return packets, fingerprints


def render_readiness(docs_root: Path) -> dict[str, object]:
    """Create a deterministic, permanently nonauthorizing OFFLINE report.

    Only a source-only BLOCKED state is supported. If future packets change to
    claim any approval, fail closed for independent human review; do not
    convert that claim into permissions or an apparent 'READY' report.
    """
    docs, hashes = _read_packets(Path(docs_root))
    annual = docs["annual"]
    econ = docs["economics"]
    graph = docs["dependency"]
    review = docs["preregistration"]
    snap = docs["admin_snapshot"]

    _require(
        tuple(docs[key]["decision"] for key in FILES) == DECISIONS,
        "documentary decision identity mismatch",
    )
    _require(
        review["method"] == "DEC-268_DEC-469_YEAR_BY_YEAR_ANNUAL_FIRST",
        "annual-first method cannot be replaced by a strategy shortcut",
    )
    _require(
        snap["kind"] == "READ_ONLY_SOURCE_DOCUMENTATION_NOT_INDEPENDENT_ATTESTATION",
        "admin snapshot must remain nonauthorizing",
    )
    _require(snap["release_status"] == "BLOCKED", "snapshot cannot claim release")
    _require(
        snap["public_observation"]["main_branch_protected"] is False
        and snap["public_observation"]["observation_current_at_future_action_time"] is False
        and snap["public_observation"]["proof_of_effective_exclusive_lock"] is False,
        "historical main snapshot must never masquerade as live lock proof",
    )
    _require(
        snap["public_observation"]["observed_main_sha"]
        == annual["main_branch_last_public_observation"]["sha"]
        and annual["main_branch_last_public_observation"]["is_current_at_action_time"] is False,
        "stale main SHA identity mismatch",
    )
    _require(
        snap["public_observation"]["inherited_org_ruleset_scope_verified"] is False
        and snap["public_observation"]["independent_admin_scope_verified"] is False,
        "full effective ruleset/admin scope has not been independently established",
    )
    _require(
        annual["previous_annual_freeze"]["segment"] == "2022"
        and type(annual["previous_annual_freeze"]["run_number"]) is int
        and annual["previous_annual_freeze"]["run_number"] == 384
        and econ["annual_series"]["historical_last_run_number"] == 384
        and graph["last_frozen_historical_segment"] == "2022"
        and review["source_segments_historical_through"] == "2022"
        and snap["historical_provenance"]["historical_freeze_run"] == 384,
        "historical accepted predecessor mismatch",
    )
    run = snap["next_protected_action"]
    identities = (
        (run["segment"], run["run_number"], run["attempt_number"]),
        (annual["yearly_catalogue_status"][8]["segment"],
         annual["yearly_catalogue_status"][8]["expected_run_number"],
         annual["yearly_catalogue_status"][8]["expected_attempt"]),
        (econ["annual_series"]["next_protected_segment"],
         econ["annual_series"]["next_protected_run_number"],
         econ["annual_series"]["next_attempt"]),
        (graph["next_protected_segment"], graph["next_expected_run_number"],
         graph["next_expected_attempt"]),
        (review["next_one_shot_segment"], review["next_run_number"],
         review["attempt_number"]),
    )
    _require(all(identity[0] == "2023"
                 and all(type(v) is int for v in identity[1:])
                 and identity[1:] == (385, 1) for identity in identities),
             "protected 2023/run385/attempt1 identity or strict types mismatch")
    _require(
        annual["external_gate_status"] == "BLOCKED"
        and annual["live_administration_evidence_verified"] is False
        and annual["live_annual_run_385_inventory_verified"] is False
        and graph["external_authorization_established"] is False
        and econ["annual_series"]["independent_fresh_inventory_present"] is False,
        "annual external gating cannot silently change",
    )
    _require(
        snap["historical_provenance"]["independently_reauthenticated_for_future_dispatch"] is False
        and all(run[k] is False for k in (
            "dispatch_authorized", "retry_authorized",
            "run_inventory_currently_independently_verified",
            "run_385_unconsumed_currently_independently_proven",
        )),
        "fresh one-shot inventory/authority is not independently verified",
    )
    _require(
        len(snap["remediation_routes"]) == 2
        and {route["id"] for route in snap["remediation_routes"]} == {
            "ADMIN_EXCLUSIVE_CONTINUOUS_MAIN_LOCK",
            "SEPARATELY_APPROVED_IMMUTABLE_REF_CODE_AMENDMENT",
        }
        and all(route["status"] == "BLOCKED"
                and route["selected"] is False
                and route["independently_reviewed"] is False
                for route in snap["remediation_routes"]),
        "neither remediation route has an independent approval",
    )
    proof_rows = snap["external_proofs"]
    _require(
        tuple(p["id"] for p in proof_rows) == PROOFS
        and all(p["status"] == "MISSING"
                and p["evidence_ref"] is None
                and p["reviewer_signoff"] is None for p in proof_rows),
        "external proof entries must remain missing/unverified",
    )
    _require(
        tuple(snap["downstream_gate_state"]) == STAGES
        and all(snap["downstream_gate_state"][stage] == "BLOCKED" for stage in STAGES)
        and len(graph["nodes"]) == 14
        and all(n["status"] == "BLOCKED"
                and n["verified_current_evidence"] is False
                and n["authorizes_execution"] is False for n in graph["nodes"]),
        "required downstream gates cannot be represented as completed",
    )
    _require(
        len(annual["authority_flags"]) == 14
        and all(value is False for value in annual["authority_flags"].values())
        and all(econ[key] is False for key in ECON_FLAGS)
        and all(review[key] is False for key in REVIEW_FLAGS)
        and all(snap[key] is False for key in (
            "one_shot_annual_action_authorized",
            "broker_action_authorized", "trading_authorized",
            "snapshot_authorizes_anything",
        )),
        "strict false authority flags required across all documents",
    )
    _require(
        all(g["status"] == "NOT_EVALUATED"
            and g["evidence_ref"] is None
            and g["signoff"] is None for g in review["gates"])
        and len(review["gates"]) == 15
        and all(v is None for v in econ["reported_economic_measurements"].values())
        and snap["measured_strategy_v1_profit"] is None
        and review["profitability_measurements"] is None
        and review["candidate_strategy_identity"] is None
        and graph["live_strategy_v1_profit_evidence"] is None,
        "unevaluated strategy economics cannot be treated as proof",
    )
    _require(
        annual["authorized_actions"] == []
        and econ["allowed_execution_actions"] == []
        and graph["already_authorized_actions"] == []
        and review["allowed_actions"] == []
        and snap["approved_actions"] == [],
        "every source must deny executable actions",
    )

    return {
        "schema": "fmp_dec1752_offline_blocker_diagnostic_v1",
        "decision": "DEC-1752",
        "mode": "OFFLINE_SOURCE_ONLY_NOT_A_GATE_OR_ATTESTATION",
        "documentary_status": "BLOCKED",
        "allows_protected_run": False,
        "allows_broker_actions": False,
        "allows_shadow": False,
        "allows_demo": False,
        "allows_live_trading": False,
        "source_observation_date_utc": snap["observed_date_utc"],
        "source_main_sha": snap["public_observation"]["observed_main_sha"],
        "current_main_verified": False,
        "current_rulesets_and_os_verified": False,
        "fresh_run_inventory_verified": False,
        "one_shot_run_identity": {
            "segment": "2023", "run_number": 385, "attempt_number": 1,
            "authorization": "BLOCKED",
        },
        "missing_external_proofs": [
            {"id": proof, "review_role": owner, "status": "MISSING"}
            for proof, owner in zip(PROOFS, OWNERS)
        ],
        "blocked_downstream_stages": list(STAGES),
        "strategy_v1_profit": None,
        "proposed_remediation_paths_not_authorized": [
            route["id"] for route in snap["remediation_routes"]
        ],
        "source_sha256": hashes,
        "no_actions_were_performed": True,
        "next_human_milestone":
            "Independent administrator/security review must establish a safe "
            "continuous ref-lock path or separately approved immutable-ref "
            "amendment, verify actual runtime and a fresh unconsumed run385 "
            "inventory, and record a distinct human one-shot decision. "
            "This offline report grants none of those permissions.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Offline UNAUTHORIZED Phase8A blocker report; no dispatch")
    parser.add_argument(
        "--docs-root", type=Path,
        default=Path(__file__).resolve().parents[1] / "docs")
    args = parser.parse_args(argv)
    try:
        result = render_readiness(args.docs_root)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        print("BLOCKED: source evidence cannot be trusted: " + str(exc),
              file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0  # Reporting succeeded; NOT an action authorization.


if __name__ == "__main__":
    raise SystemExit(main())
