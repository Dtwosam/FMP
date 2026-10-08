from __future__ import annotations

import copy
import hashlib
import json
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_tag_ruleset_static_review import (
    EXPECTED_TAG_NAMESPACE,
    inspect_2023_tag_ruleset_snapshot,
    validate_2023_tag_ruleset_static_review,
)

TAG = EXPECTED_TAG_NAMESPACE + "reviewed-v1"
SHA = "a" * 40


def _ref():
    return {"ref": TAG, "object": {"type": "commit", "sha": SHA}}


def _rule():
    return {
        "target": "tag",
        "enforcement": "active",
        "bypass_actors": [],
        "conditions": {"ref_name": {"include": [TAG], "exclude": []}},
        "rules": [{"type": "update"}, {"type": "deletion"}],
    }


def _assess(**updates):
    value = {
        "tag_ref": TAG,
        "reviewed_commit_sha": SHA,
        "git_ref_response": _ref(),
        "rulesets": [_rule()],
        "includes_inherited_rulesets": True,
        "enumeration_complete": True,
    }
    value.update(updates)
    return inspect_2023_tag_ruleset_snapshot(**value)


def _resign(value):
    obj = dict(value)
    obj.pop("static_review_fingerprint_sha256", None)
    value["static_review_fingerprint_sha256"] = hashlib.sha256(
        (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


class TagRulesetStaticReviewTests(unittest.TestCase):
    def test_candidate_is_not_approval_even_with_perfect_claimed_snapshot(self):
        report = _assess()
        validate_2023_tag_ruleset_static_review(report)
        self.assertTrue(report["static_ruleset_candidate"])
        self.assertEqual(report["matching_strict_ruleset_count"], 1)
        self.assertTrue(report["tag_ref_matches_reviewed_commit_in_supplied_snapshot"])
        self.assertEqual(report["expected_annual_run_number"], 385)
        self.assertFalse(report["annual_workflow_tag_compatible"])
        self.assertTrue(report["dispatch_blocked"])
        for key in (
            "snapshot_authenticated", "immutable_tag_proven",
            "exclusive_tag_lock_proven", "tag_creation_authorized",
            "annual_workflow_dispatch_authorized", "dispatch_action_executed",
            "trading_authorized", "one_shot_dispatch_decision_present",
        ):
            self.assertFalse(report[key], key)

    def test_tag_retarget_and_annotated_tag_fail(self):
        for object_value in (
            {"type": "commit", "sha": "b" * 40},
            {"type": "tag", "sha": SHA},
            {"type": "commit", "sha": SHA.upper()},
            {"type": "commit", "sha": SHA, "extra": 1},
        ):
            with self.subTest(object_value=object_value):
                value = _assess(git_ref_response={"ref": TAG, "object": object_value})
                # Extra unrelated ref metadata is not a trust or permission signal.
                if object_value.get("extra"):
                    self.assertTrue(value["static_ruleset_candidate"])
                else:
                    self.assertFalse(value["static_ruleset_candidate"])
                    self.assertIn("TAG_REF_OR_COMMIT_NOT_EXACT", value["failed_static_checks"])
                self.assertTrue(value["dispatch_blocked"])

    def test_bypass_and_partial_rules_rejected(self):
        changes = (
            {"bypass_actors": [{"actor_id": 1, "actor_type": "Team", "bypass_mode": "always"}]},
            {"rules": [{"type": "update"}]},
            {"rules": [{"type": "deletion"}]},
            {"rules": [{"type": "update"}, {"type": "other"}]},
            {"target": "branch"},
            {"enforcement": "evaluate"},
            {"enforcement": "disabled"},
            {"bypass_actors": None},
        )
        for change in changes:
            with self.subTest(change=change):
                rule = _rule()
                rule.update(change)
                value = _assess(rulesets=[rule])
                self.assertFalse(value["static_ruleset_candidate"])
                self.assertIn(
                    "NO_ACTIVE_EXACT_UPDATE_DELETE_RULESET_WITHOUT_BYPASS",
                    value["failed_static_checks"],
                )
                self.assertFalse(value["annual_workflow_dispatch_authorized"])

    def test_ambiguous_rule_ref_scope_rejected(self):
        for ref_name in (
            {"include": ["refs/tags/fmp/phase8a/2023/run385/*"], "exclude": []},
            {"include": [TAG, "refs/tags/other"], "exclude": []},
            {"include": [TAG], "exclude": ["refs/tags/other"]},
            {"include": ["~ALL"], "exclude": []},
            {"include": [TAG]},
        ):
            with self.subTest(ref_name=ref_name):
                rule = _rule()
                rule["conditions"] = {"ref_name": ref_name}
                value = _assess(rulesets=[rule])
                self.assertFalse(value["static_ruleset_candidate"])

    def test_missing_inherited_visibility_fails_closed(self):
        for kwargs in (
            {"includes_inherited_rulesets": False},
            {"includes_inherited_rulesets": None},
            {"enumeration_complete": False},
            {"rulesets": []},
            {"rulesets": {}},
        ):
            with self.subTest(kwargs=kwargs):
                value = _assess(**kwargs)
                self.assertFalse(value["static_ruleset_candidate"])
                self.assertTrue(value["dispatch_blocked"])

    def test_rehashed_permission_escalation_is_rejected(self):
        initial = _assess()
        for flag in (
            "snapshot_authenticated", "immutable_tag_proven",
            "exclusive_tag_lock_proven", "annual_workflow_tag_compatible",
            "annual_workflow_dispatch_authorized", "dispatch_action_executed",
            "retry_authorized", "broker_mutation_authorized", "trading_authorized",
            "dispatch_blocked",
        ):
            with self.subTest(flag=flag):
                report = copy.deepcopy(initial)
                report[flag] = not report[flag]
                _resign(report)
                with self.assertRaisesRegex(ValueError, "forbidden or changed field"):
                    validate_2023_tag_ruleset_static_review(report)

    def test_rehashed_fictitious_candidate_is_rejected(self):
        report = _assess(rulesets=[])
        report["static_ruleset_candidate"] = True
        _resign(report)
        with self.assertRaisesRegex(ValueError, "inconsistency"):
            validate_2023_tag_ruleset_static_review(report)

    def test_fingerprint_extension_and_invalid_identity_fail(self):
        report = _assess()
        report["unauthorized_execution_token"] = "yes"
        _resign(report)
        with self.assertRaisesRegex(ValueError, "unauthorized fields"):
            validate_2023_tag_ruleset_static_review(report)
        for bad in (
            "refs/heads/main",
            "refs/tags/fmp/phase8a/2023/run385/",
            "refs/tags/fmp/phase8a/2023/run385/a.lock",
            "refs/tags/fmp/phase8a/2023/run385/../../other",
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    _assess(tag_ref=bad)
        with self.assertRaises(ValueError):
            _assess(reviewed_commit_sha="main")

    def test_cli_is_assess_only(self):
        from pathlib import Path
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts/phase8a_annual_pattern_catalogue_2023_tag_ruleset_static_review.py"
        ).read_text(encoding="utf-8")
        self.assertIn('add_parser("assess")', script)
        for forbidden in (
            "gh workflow run", "git push", "git tag",
            "requests.post", "subprocess.", 'add_parser("dispatch")',
        ):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
