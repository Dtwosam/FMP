from __future__ import annotations

"""DEC-633: pure offline PR CI provenance classifier, never a merge gate.

Inputs are fabricated metadata. This is not an authenticated GitHub API result,
review, checkout attestation, workflow admission, or dispatch permission.
"""

import hashlib
import json
import re
from collections.abc import Mapping

DECISION = "DEC-633"
REPOSITORY = "Dtwosam/FMP"
PR_FIELDS = frozenset({
    "repository", "pr_number", "base_sha", "head_sha", "head_tree_sha",
    "synthetic_merge_sha", "synthetic_merge_tree_sha", "merge_parents",
    "run_evidence",
})
RUN_FIELDS = frozenset({
    "workflow_path", "event", "run_head_sha", "run_pr_number",
    "run_pr_head_sha", "run_pr_base_sha", "attempt", "status", "conclusion",
})
WORKFLOWS = (
    ".github/workflows/tests.yml",
    ".github/workflows/phase3-acceptance.yml",
)
# Fabricated object hashes: NOT actual commits, CI runs, or approvals.
_BASE = "a" * 40
_HEAD = "b" * 40
_MERGE = "c" * 40
_TREE = "d" * 40
_OTHER_TREE = "e" * 40


def _run(path: str) -> dict[str, object]:
    return {
        "workflow_path": path,
        "event": "pull_request",
        "run_head_sha": _HEAD,
        "run_pr_number": 99999,
        "run_pr_head_sha": _HEAD,
        "run_pr_base_sha": _BASE,
        "attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def fixture() -> dict[str, object]:
    return {
        "repository": REPOSITORY,
        "pr_number": 99999,
        "base_sha": _BASE,
        "head_sha": _HEAD,
        "head_tree_sha": _TREE,
        "synthetic_merge_sha": _MERGE,
        "synthetic_merge_tree_sha": _TREE,
        "merge_parents": [_BASE, _HEAD],
        "run_evidence": [_run(p) for p in WORKFLOWS],
    }


def _is_sha(value: object) -> bool:
    return type(value) is str and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def classify_pr_ci_provenance(value: object) -> str:
    """Classify *reported Git metadata*, never independently certify a checkout.

    Result is one of:
      REJECTED: incomplete/stale/failed/invalid CI or synthetic-merge join
      REPORTED_HEAD_TREE_EQUIVALENT: same Git tree at source and synthetic merge
      REPORTED_SYNTHETIC_MERGE_ONLY: valid joins, but trees differ
    """
    if not isinstance(value, Mapping) or set(value) != PR_FIELDS:
        return "REJECTED"
    if type(value["repository"]) is not str or value["repository"] != REPOSITORY:
        return "REJECTED"
    if type(value["pr_number"]) is not int or value["pr_number"] <= 0:
        return "REJECTED"
    for key in ("base_sha", "head_sha", "head_tree_sha", "synthetic_merge_sha", "synthetic_merge_tree_sha"):
        if not _is_sha(value[key]):
            return "REJECTED"
    if value["base_sha"] == value["head_sha"] or value["synthetic_merge_sha"] in (value["head_sha"], value["base_sha"]):
        return "REJECTED"
    parents = value["merge_parents"]
    if type(parents) is not list or parents != [value["base_sha"], value["head_sha"]]:
        return "REJECTED"
    runs = value["run_evidence"]
    if type(runs) is not list or len(runs) != len(WORKFLOWS):
        return "REJECTED"
    seen: set[str] = set()
    for run in runs:
        if not isinstance(run, Mapping) or set(run) != RUN_FIELDS:
            return "REJECTED"
        path = run["workflow_path"]
        if type(path) is not str or path not in WORKFLOWS or path in seen:
            return "REJECTED"
        seen.add(path)
        if (
            type(run["event"]) is not str or run["event"] != "pull_request"
            or not _is_sha(run["run_head_sha"]) or run["run_head_sha"] != value["head_sha"]
            or type(run["run_pr_number"]) is not int or run["run_pr_number"] != value["pr_number"]
            or not _is_sha(run["run_pr_head_sha"]) or run["run_pr_head_sha"] != value["head_sha"]
            or not _is_sha(run["run_pr_base_sha"]) or run["run_pr_base_sha"] != value["base_sha"]
            or type(run["attempt"]) is not int or run["attempt"] != 1
            or type(run["status"]) is not str or run["status"] != "completed"
            or type(run["conclusion"]) is not str or run["conclusion"] != "success"
        ):
            return "REJECTED"
    if seen != set(WORKFLOWS):
        return "REJECTED"
    return (
        "REPORTED_HEAD_TREE_EQUIVALENT"
        if value["head_tree_sha"] == value["synthetic_merge_tree_sha"]
        else "REPORTED_SYNTHETIC_MERGE_ONLY"
    )


def _counterexamples() -> tuple[tuple[str, dict[str, object]], ...]:
    """Every counterexample must be rejected except the deliberate tree difference."""
    cases: list[tuple[str, dict[str, object]]] = []
    def add(name: str, change) -> None:
        sample = fixture()
        change(sample)
        cases.append((name, sample))

    add("tree_difference", lambda d: d.__setitem__("synthetic_merge_tree_sha", _OTHER_TREE))
    add("stale_merge_parent", lambda d: d.__setitem__("merge_parents", [_BASE, "f" * 40]))
    add("swapped_merge_parents", lambda d: d.__setitem__("merge_parents", [_HEAD, _BASE]))
    add("missing_merge_parent", lambda d: d.__setitem__("merge_parents", [_HEAD]))
    add("different_base", lambda d: d.__setitem__("base_sha", "f" * 40))
    add("different_head", lambda d: d.__setitem__("head_sha", "f" * 40))
    add("bool_pr_number", lambda d: d.__setitem__("pr_number", True))
    add("missing_merge_tree", lambda d: d.pop("synthetic_merge_tree_sha"))
    add("head_is_base", lambda d: d.__setitem__("head_sha", _BASE))
    add("not_a_merge_commit", lambda d: d.__setitem__("synthetic_merge_sha", _HEAD))
    add("head_run_stale", lambda d: d["run_evidence"][0].__setitem__("run_head_sha", "f" * 40))
    add("acceptance_run_stale", lambda d: d["run_evidence"][1].__setitem__("run_pr_head_sha", "f" * 40))
    add("run_base_drift", lambda d: d["run_evidence"][0].__setitem__("run_pr_base_sha", "f" * 40))
    add("run_wrong_pr", lambda d: d["run_evidence"][0].__setitem__("run_pr_number", 99998))
    add("run_pr_number_bool", lambda d: d["run_evidence"][0].__setitem__("run_pr_number", True))
    add("run_event_push", lambda d: d["run_evidence"][0].__setitem__("event", "push"))
    add("run_2_attempt", lambda d: d["run_evidence"][1].__setitem__("attempt", 2))
    add("run_bool_attempt", lambda d: d["run_evidence"][1].__setitem__("attempt", True))
    add("run_failed", lambda d: d["run_evidence"][0].__setitem__("conclusion", "failure"))
    add("run_skipped", lambda d: d["run_evidence"][0].__setitem__("conclusion", "skipped"))
    add("run_pending", lambda d: d["run_evidence"][1].__setitem__("status", "in_progress"))
    add("two_tests_without_acceptance", lambda d: d["run_evidence"][1].__setitem__("workflow_path", WORKFLOWS[0]))
    add("extra_run", lambda d: d["run_evidence"].append(_run(WORKFLOWS[0])))
    add("missing_run", lambda d: d["run_evidence"].pop())
    add("unexpected_authorization", lambda d: d.__setitem__("merge_authorized", True))
    add("run_forged_permission", lambda d: d["run_evidence"][0].__setitem__("trusted_checkout", True))
    return tuple(cases)


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _payload() -> dict[str, object]:
    rows = [{"case": "positive_synthetic_evidence", "classification": classify_pr_ci_provenance(fixture())}]
    rows += [{"case": n, "classification": classify_pr_ci_provenance(v)} for n, v in _counterexamples()]
    if rows[0]["classification"] != "REPORTED_HEAD_TREE_EQUIVALENT":
        raise ValueError("DEC-633 positive fixture drift")
    if rows[1]["classification"] != "REPORTED_SYNTHETIC_MERGE_ONLY":
        raise ValueError("DEC-633 differing-tree fixture drift")
    if any(row["classification"] != "REJECTED" for row in rows[2:]):
        raise ValueError("DEC-633 negative fixture drift")
    return {
        "decision": DECISION,
        "stage": "INERT_PR_CI_TREE_PROVENANCE_EVIDENCE_PREVIEW",
        "cases": rows,
        "counterexample_count": len(rows) - 1,
        "source_is_synthetic_not_live": True,
        "workflow_checkout_attested_by_runner": False,
        "real_review_proven": False,
        "actual_pr_merge_permitted": False,
        "annual_dispatch_authorized": False,
        "run385_authorized": False,
        "trading_authorized": False,
        "dispatch_blocked": True,
        "next_gate": "INDEPENDENT_EXACT_HEAD_REVIEW_AND_GITHUB_WORKFLOW_SOURCE_PROVENANCE",
    }


def build_pr_ci_provenance_preview() -> dict[str, object]:
    report = _payload()
    return {**report, "report_sha256": _digest(report)}


def validate_pr_ci_provenance_preview(value: object) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-633 report must be a mapping")
    v = dict(value)
    fingerprint = v.pop("report_sha256", None)
    if type(fingerprint) is not str or len(fingerprint) != 64 or _digest(v) != fingerprint:
        raise ValueError("DEC-633 report digest mismatch")
    if _canonical(v) != _canonical(_payload()):
        raise ValueError("DEC-633 source-bound exact report mismatch")
