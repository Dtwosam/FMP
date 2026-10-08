from __future__ import annotations

"""DEC-621: synthetic one-shot dispatch outcomes; no live submission or retry."""

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_disarmed_tag_amendment_preview import _source
from .annual_pattern_catalogue_2023_lock_witness_coverage import (
    _reject_duplicate_json_object_keys,
)
from .annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import (
    ANNUAL_WORKFLOW_BLOB,
    ANNUAL_WORKFLOW_PATH,
    REQUIRED_JOBS,
    _is_sha,
    verify_original_workflow_order,
)

DECISION = "DEC-621"
VERSION = "fmp-2023-run385-ambiguous-dispatch-terminal-hold-v1"
RUN_NUMBER = 385
RUN_ATTEMPT = 1
PREDECESSOR_RUN_ID = 37663157285
WORKFLOW = "phase8a-annual-pattern-catalogue"
OUTCOMES = frozenset((
    "not_called", "local_validation_failed", "http_accepted",
    "http_rejected", "transport_error", "timeout", "unknown",
))
INPUT_KEYS = frozenset((
    "schema", "reviewed_code_sha", "dispatch_call_made",
    "client_observed_outcome", "observed_runs",
))
RUN_KEYS = frozenset((
    "run_id", "run_number", "run_attempt", "event", "workflow",
    "head_sha", "previous_annual_freeze_run_id",
))
DENIED = (
    "live_annual_run_inventory_authenticated",
    "effective_main_or_tag_lock_proven",
    "workflow_runtime_amendment_approved",
    "annual_dispatch_authorized_by_report",
    "second_dispatch_authorized",
    "retry_authorized",
    "rerun_authorized",
    "replacement_run_authorized",
    "run386_or_later_authorized",
    "future_year_research_authorized",
    "protected_history_read_authorized_by_report",
    "strategy_synthesis_authorized",
    "promotion_authorized",
    "phase8b_authorized",
    "broker_mutation_authorized",
    "demo_order_authorized",
    "live_order_authorized",
    "real_money_authorized",
    "trading_authorized",
)


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _strict_int(value: object) -> bool:
    return type(value) is int and value > 0


def parse_untrusted_dispatch_simulation_json(source: str) -> dict[str, object]:
    doc = json.loads(source, object_pairs_hook=_reject_duplicate_json_object_keys)
    _validate_input(doc)
    return doc


def _validate_input(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != INPUT_KEYS:
        raise ValueError("DEC-621 invalid input field inventory")
    if value.get("schema") != VERSION:
        raise ValueError("DEC-621 input version mismatch")
    if not _is_sha(value.get("reviewed_code_sha")):
        raise ValueError("DEC-621 expected reviewed code SHA format mismatch")
    call = value.get("dispatch_call_made")
    if type(call) is not bool:
        raise ValueError("DEC-621 dispatch flag must be a strict boolean")
    outcome = value.get("client_observed_outcome")
    if not isinstance(outcome, str) or outcome not in OUTCOMES:
        raise ValueError("DEC-621 unrecognized client outcome")
    if not call and outcome not in ("not_called", "local_validation_failed"):
        raise ValueError("DEC-621 non-call cannot have a submission response")
    if call and outcome in ("not_called", "local_validation_failed"):
        raise ValueError("DEC-621 attempted call cannot have no-call outcome")
    runs = value.get("observed_runs")
    if not isinstance(runs, list) or len(runs) > 8:
        raise ValueError("DEC-621 observed run inventory must be a bounded list")
    seen: set[int] = set()
    for item in runs:
        if not isinstance(item, dict) or set(item) != RUN_KEYS:
            raise ValueError("DEC-621 run record shape mismatch")
        for key in ("run_id", "run_number", "run_attempt", "previous_annual_freeze_run_id"):
            if not _strict_int(item.get(key)):
                raise ValueError("DEC-621 run identity must contain positive integers")
        if item["run_id"] in seen:
            raise ValueError("DEC-621 duplicate observed run id")
        seen.add(item["run_id"])
        if not isinstance(item.get("workflow"), str) or not item["workflow"]:
            raise ValueError("DEC-621 invalid workflow")
        if item.get("event") != "workflow_dispatch":
            raise ValueError("DEC-621 only models workflow_dispatch run records")
        if not _is_sha(item.get("head_sha")):
            raise ValueError("DEC-621 invalid run head SHA")
    if not call and runs:
        raise ValueError("DEC-621 a non-call cannot have observed run records")
    return value


def _report(*, repository_root: Path, input_doc: object) -> dict[str, object]:
    doc = _validate_input(input_doc)
    workflow = _source(repository_root)
    if verify_original_workflow_order(workflow) != list(REQUIRED_JOBS):
        raise ValueError("DEC-621 installed guard/source mismatch")
    expected = doc["reviewed_code_sha"]
    rows: list[dict[str, object]] = []
    for item in doc["observed_runs"]:
        matches = bool(
            item["run_number"] == RUN_NUMBER
            and item["run_attempt"] == RUN_ATTEMPT
            and item["workflow"] == WORKFLOW
            and item["head_sha"] == expected
            and item["previous_annual_freeze_run_id"] == PREDECESSOR_RUN_ID
        )
        rows.append({"run_id": item["run_id"], "hypothetical_identity_matches": matches})
    matching = sum(1 for x in rows if x["hypothetical_identity_matches"])
    wrong = sum(1 for x in rows if not x["hypothetical_identity_matches"])
    call = doc["dispatch_call_made"]
    if not call:
        state = "NO_CALL_IN_THIS_SIMULATION_NOT_LIVE_INVENTORY_PROOF"
    elif matching == 1 and wrong == 0 and doc["client_observed_outcome"] == "http_accepted":
        state = "SIMULATED_ONE_EXACT_RUN_STILL_REQUIRE_INDEPENDENT_EVIDENCE"
    elif doc["observed_runs"]:
        state = "SIMULATED_RUN_CONFLICT_TERMINAL_HOLD_NO_RETRY"
    else:
        state = "SIMULATED_AMBIGUOUS_SUBMISSION_TERMINAL_HOLD_NO_RETRY"
    return {
        "decision": DECISION,
        "version": VERSION,
        "stage": "OFFLINE_NON_DISPATCHING_AMBIGUOUS_OUTCOME_MODEL_ONLY",
        "repository": "Dtwosam/FMP",
        "pinned_annual_workflow_path": ANNUAL_WORKFLOW_PATH,
        "pinned_annual_workflow_blob": ANNUAL_WORKFLOW_BLOB,
        "exact_expected_run_number": RUN_NUMBER,
        "exact_expected_run_attempt": RUN_ATTEMPT,
        "exact_predecessor_run_id": PREDECESSOR_RUN_ID,
        "simulated_call_made": call,
        "simulated_outcome": doc["client_observed_outcome"],
        "simulated_run_rows": rows,
        "simulated_matching_run_count": matching,
        "simulated_conflicting_run_count": wrong,
        "simulated_state": state,
        "untrusted_input": doc,
        "untrusted_input_sha256": _digest(doc),
        "server_may_have_accepted_even_if_client_loses_response": True,
        "http_failure_or_timeout_never_licenses_retry": True,
        "post_dispatch_sha_check_cannot_recover_run_number": True,
        "no_real_annual_dispatch_performed": True,
        "no_github_network_or_ref_mutation": True,
        "offline_source_only": True,
        "terminal_one_shot_hold": True,
        "dispatch_blocked": True,
        **{key: False for key in DENIED},
        "next_gate": "INDEPENDENT_GITHUB_RUN_INVENTORY_AND_ADMIN_LOCK_PROOF_THEN_DISTINCT_ONE_SHOT_DECISION",
    }


def build_2023_run385_ambiguous_dispatch_hold_report(
    *, repository_root: Path, input_doc: object,
) -> dict[str, object]:
    payload = _report(repository_root=Path(repository_root), input_doc=input_doc)
    payload["report_sha256"] = _digest(payload)
    validate_2023_run385_ambiguous_dispatch_hold_report(payload)
    return payload


def validate_2023_run385_ambiguous_dispatch_hold_report(value: Mapping[str, object]) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-621 report must be an object")
    unsigned = dict(value)
    fingerprint = unsigned.pop("report_sha256", None)
    if not isinstance(fingerprint, str) or not len(fingerprint) == 64:
        raise ValueError("DEC-621 malformed fingerprint")
    if _digest(unsigned) != fingerprint:
        raise ValueError("DEC-621 report fingerprint mismatch")
    expected = _report(
        repository_root=Path(__file__).resolve().parents[3],
        input_doc=unsigned.get("untrusted_input"),
    )
    if _canonical(unsigned) != _canonical(expected):
        raise ValueError("DEC-621 source-bound payload or permission mismatch")
