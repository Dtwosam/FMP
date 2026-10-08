from __future__ import annotations

"""DEC-616: untrusted offline tag-ruleset shape review; never an action gate."""

import hashlib
import json
import re
from typing import Mapping

DECISION = "DEC-616"
VERSION = "fmp-2023-run385-tag-ruleset-static-review-v1"
REPOSITORY = "Dtwosam/FMP"
BASELINE_MAIN_SHA = "d2123d505d1cb8065a3e5afe9f74e28d4b1d2f0e"
FROZEN_ANNUAL_WORKFLOW_BLOB = "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
FROZEN_2023_GATE_BLOB = "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191"
FROZEN_RUNTIME_BLOB = "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3"
EXPECTED_TAG_NAMESPACE = "refs/tags/fmp/phase8a/2023/run385/"
REQUIRED_RULES = frozenset(("update", "deletion"))
LOCKED_FALSE = (
    "immutable_tag_proven",
    "exclusive_tag_lock_proven",
    "tag_creation_authorized",
    "tag_movement_authorized",
    "annual_workflow_tag_compatible",
    "annual_workflow_dispatch_authorized",
    "dispatch_action_executed",
    "protected_history_access_authorized",
    "rerun_authorized",
    "retry_authorized",
    "replacement_run_authorized",
    "run_386_or_later_authorized",
    "later_year_research_authorized",
    "cross_year_comparison_authorized",
    "strategy_promotion_authorized",
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


def _sha(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _ref(value: object) -> bool:
    if not isinstance(value, str) or not value.startswith(EXPECTED_TAG_NAMESPACE):
        return False
    suffix = value[len(EXPECTED_TAG_NAMESPACE):]
    return (
        0 < len(suffix) <= 80
        and re.fullmatch(r"[a-z0-9][a-z0-9._-]*", suffix) is not None
        and ".." not in suffix
        and not suffix.endswith((".", ".lock"))
    )


def _exact_no_bypass_rule(value: object, ref: str) -> bool:
    if not isinstance(value, Mapping):
        return False
    if value.get("target") != "tag" or value.get("enforcement") != "active":
        return False
    if value.get("bypass_actors") != []:
        return False
    conditions = value.get("conditions")
    if not isinstance(conditions, Mapping):
        return False
    ref_name = conditions.get("ref_name")
    if not isinstance(ref_name, Mapping):
        return False
    # Do not infer GitHub fnmatch/glob precedence or accept broad pattern scopes.
    if ref_name.get("include") != [ref] or ref_name.get("exclude") != []:
        return False
    # Unknown restriction shapes fail closed; both concrete update and delete rules
    # must be explicitly present in this same no-bypass active ruleset.
    rules = value.get("rules")
    if not isinstance(rules, list) or any(
        not isinstance(rule, Mapping) or not isinstance(rule.get("type"), str)
        for rule in rules
    ):
        return False
    return REQUIRED_RULES.issubset({rule["type"] for rule in rules})


def inspect_2023_tag_ruleset_snapshot(
    *,
    tag_ref: str,
    reviewed_commit_sha: str,
    git_ref_response: object,
    rulesets: object,
    includes_inherited_rulesets: bool,
    enumeration_complete: bool,
) -> dict[str, object]:
    """Inspect caller-supplied REST-shaped JSON, NOT authenticate or lock a ref.

    A 'static_ruleset_candidate' merely means supplied objects have the
    conservative documented shape. It never proves server state or permission.
    """
    errors: list[str] = []
    if not _ref(tag_ref):
        errors.append("INVALID_EXACT_TAG_NAMESPACE")
    if not _sha(reviewed_commit_sha):
        errors.append("INVALID_REVIEWED_COMMIT")

    ref_matches = (
        isinstance(git_ref_response, Mapping)
        and git_ref_response.get("ref") == tag_ref
        and isinstance(git_ref_response.get("object"), Mapping)
        and git_ref_response["object"].get("type") == "commit"
        and git_ref_response["object"].get("sha") == reviewed_commit_sha
    )
    if not ref_matches:
        errors.append("TAG_REF_OR_COMMIT_NOT_EXACT")

    # Caller-supplied completeness fields are only advisory. They do not
    # constitute authenticated evidence from the GitHub administrator API.
    if includes_inherited_rulesets is not True or enumeration_complete is not True:
        errors.append("INCOMPLETE_RULESET_VISIBILITY")

    if not isinstance(rulesets, list):
        errors.append("INVALID_RULESET_COLLECTION")
        rulesets = []
    matching = [r for r in rulesets if _exact_no_bypass_rule(r, tag_ref)]
    if not matching:
        errors.append("NO_ACTIVE_EXACT_UPDATE_DELETE_RULESET_WITHOUT_BYPASS")

    candidate = not errors
    payload: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        "stage": "TAG_RULESET_OFFLINE_STATIC_REVIEW_ONLY",
        "repository_full_name": REPOSITORY,
        "baseline_dec615_main_sha": BASELINE_MAIN_SHA,
        "frozen_annual_workflow_blob_sha": FROZEN_ANNUAL_WORKFLOW_BLOB,
        "frozen_2023_runtime_gate_blob_sha": FROZEN_2023_GATE_BLOB,
        "frozen_catalogue_runtime_blob_sha": FROZEN_RUNTIME_BLOB,
        "tag_ref": tag_ref,
        "reviewed_commit_sha": reviewed_commit_sha,
        "expected_annual_run_number": 385,
        "expected_annual_attempt": 1,
        "required_2022_predecessor_run_id": 37663157285,
        "snapshot_sha256": _digest({
            "git_ref_response": git_ref_response,
            "rulesets": rulesets,
            "includes_inherited_rulesets": includes_inherited_rulesets,
            "enumeration_complete": enumeration_complete,
        }),
        "tag_ref_matches_reviewed_commit_in_supplied_snapshot": ref_matches,
        "matching_strict_ruleset_count": len(matching),
        "static_ruleset_candidate": candidate,
        "failed_static_checks": errors,
        "snapshot_authenticated": False,
        "ruleset_enforcement_witnessed": False,
        "bypass_permissions_independently_reviewed": False,
        "source_runtime_amendment_reviewed": False,
        "one_shot_dispatch_decision_present": False,
        "dispatch_blocked": True,
        "read_only": True,
        **{key: False for key in LOCKED_FALSE},
        "next_gate": "HUMAN_ADMIN_TAG_RULESET_WITNESS_AND_SEPARATE_WORKFLOW_RUNTIME_AMENDMENT_REVIEW",
    }
    payload["static_review_fingerprint_sha256"] = _digest(payload)
    validate_2023_tag_ruleset_static_review(payload)
    return payload


def validate_2023_tag_ruleset_static_review(value: Mapping[str, object]) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-616 review must be an object")
    unsigned = dict(value)
    fp = unsigned.pop("static_review_fingerprint_sha256", None)
    if not isinstance(fp, str) or not re.fullmatch(r"[0-9a-f]{64}", fp):
        raise ValueError("DEC-616 fingerprint missing or malformed")
    if _digest(unsigned) != fp:
        raise ValueError("DEC-616 fingerprint mismatch")

    required = {
        "decision": DECISION,
        "version": VERSION,
        "stage": "TAG_RULESET_OFFLINE_STATIC_REVIEW_ONLY",
        "repository_full_name": REPOSITORY,
        "baseline_dec615_main_sha": BASELINE_MAIN_SHA,
        "frozen_annual_workflow_blob_sha": FROZEN_ANNUAL_WORKFLOW_BLOB,
        "frozen_2023_runtime_gate_blob_sha": FROZEN_2023_GATE_BLOB,
        "frozen_catalogue_runtime_blob_sha": FROZEN_RUNTIME_BLOB,
        "expected_annual_run_number": 385,
        "expected_annual_attempt": 1,
        "required_2022_predecessor_run_id": 37663157285,
        "snapshot_authenticated": False,
        "ruleset_enforcement_witnessed": False,
        "bypass_permissions_independently_reviewed": False,
        "source_runtime_amendment_reviewed": False,
        "one_shot_dispatch_decision_present": False,
        "dispatch_blocked": True,
        "read_only": True,
        "next_gate": "HUMAN_ADMIN_TAG_RULESET_WITNESS_AND_SEPARATE_WORKFLOW_RUNTIME_AMENDMENT_REVIEW",
        **{key: False for key in LOCKED_FALSE},
    }
    allowed = set(required) | {
        "tag_ref", "reviewed_commit_sha", "snapshot_sha256",
        "tag_ref_matches_reviewed_commit_in_supplied_snapshot",
        "matching_strict_ruleset_count", "static_ruleset_candidate",
        "failed_static_checks", "static_review_fingerprint_sha256",
    }
    if set(value) != allowed:
        raise ValueError("DEC-616 unauthorized fields")
    for key, expected in required.items():
        current = value.get(key)
        if type(expected) is bool:
            valid = current is expected
        elif type(expected) is int:
            valid = type(current) is int and current == expected
        else:
            valid = current == expected
        if not valid:
            raise ValueError("DEC-616 forbidden or changed field: " + key)
    if not _ref(value.get("tag_ref")) or not _sha(value.get("reviewed_commit_sha")):
        raise ValueError("DEC-616 invalid ref or commit")
    if not isinstance(value.get("snapshot_sha256"), str) or not re.fullmatch(
        r"[0-9a-f]{64}", value["snapshot_sha256"]
    ):
        raise ValueError("DEC-616 snapshot digest invalid")
    if type(value.get("tag_ref_matches_reviewed_commit_in_supplied_snapshot")) is not bool:
        raise ValueError("DEC-616 ref flag malformed")
    if type(value.get("static_ruleset_candidate")) is not bool:
        raise ValueError("DEC-616 candidate flag malformed")
    n = value.get("matching_strict_ruleset_count")
    if type(n) is not int or n < 0:
        raise ValueError("DEC-616 matching ruleset count malformed")
    errors = value.get("failed_static_checks")
    if not isinstance(errors, list) or any(not isinstance(s, str) for s in errors):
        raise ValueError("DEC-616 errors malformed")
    if value["static_ruleset_candidate"] != (len(errors) == 0):
        raise ValueError("DEC-616 static candidate/errors inconsistency")
    if value["static_ruleset_candidate"] and (
        n < 1 or not value["tag_ref_matches_reviewed_commit_in_supplied_snapshot"]
    ):
        raise ValueError("DEC-616 static candidate/ref/ruleset inconsistency")
