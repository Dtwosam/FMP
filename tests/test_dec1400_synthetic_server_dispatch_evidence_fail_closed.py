"""DEC-1400: synthetic one-shot server/ref evidence review, always BLOCKED.

A JSON-like object here is an untrusted fixture, never an authenticated
GitHub server attestation. There is NO web request, GitHub dispatch, real
run number allocation, annual source import, or protected artifact access.
"""
from __future__ import annotations

import copy
import unittest

REVIEWED = "a" * 40
UNREVIEWED = "b" * 40


def synthetic_server_report() -> dict:
    return {
        "ref": "refs/heads/main",
        "operator_checked_sha": REVIEWED,
        "server_resolved_sha": REVIEWED,
        "branch_protected": False,
        "repository_ruleset_count": 0,
        "exclusive_update_lock_witness": "",
        "bypass_inventory_witness": "",
        "single_authorized_dispatcher_witness": "",
        "run_number": 385,
        "run_attempt": 1,
        "no_retry_witness": "",
    }


def offline_one_shot_review(value: object) -> dict:
    """Can detect rejection reasons; can NEVER authorize or reserve a run."""
    blockers = []
    if type(value) is not dict:
        blockers.append("UNTRUSTED_REPORT_NOT_MAPPING")
    else:
        required = set(synthetic_server_report())
        if set(value) != required:
            blockers.append("FIELD_INVENTORY_NOT_EXACT")
        if value.get("ref") != "refs/heads/main":
            blockers.append("DISPATCH_REF_DRIFT")
        checked = value.get("operator_checked_sha")
        resolved = value.get("server_resolved_sha")
        for sha in (checked, resolved):
            if type(sha) is not str or len(sha) != 40:
                blockers.append("MISSING_40_HEX_SOURCE")
                break
            try:
                int(sha, 16)
            except ValueError:
                blockers.append("NONHEX_SOURCE")
                break
        if checked != resolved:
            blockers.append("SERVER_REF_RESOLUTION_RACE_OR_MISMATCH")
        if value.get("branch_protected") is not True:
            blockers.append("BRANCH_NOT_REPORTED_PROTECTED")
        rulesets = value.get("repository_ruleset_count")
        if type(rulesets) is not int or rulesets <= 0:
            blockers.append("NO_REPOSITORY_RULESET_EVIDENCE")
        for name in (
            "exclusive_update_lock_witness",
            "bypass_inventory_witness",
            "single_authorized_dispatcher_witness",
            "no_retry_witness",
        ):
            if type(value.get(name)) is not str or not value[name].strip():
                blockers.append("MISSING_" + name.upper())
        if (type(value.get("run_number")) is not int
                or value.get("run_number") != 385
                or type(value.get("run_attempt")) is not int
                or value.get("run_attempt") != 1):
            blockers.append("ONE_SHOT_SLOT_DRIFT")
    return {
        "status": "BLOCKED",
        "dispatch_authorized": False,
        "server_side_attestation_authenticated": False,
        "slot_reserved_or_allocated": False,
        "blockers": tuple(sorted(set(blockers))),
    }


class OfflineUntrustedRefSnapshotCannotAuthorizeProtectedRun385(unittest.TestCase):
    def setUp(self):
        self.snapshot = synthetic_server_report()

    def test_missing_real_branch_protection_is_detected(self):
        self.assertIn("BRANCH_NOT_REPORTED_PROTECTED",
                      offline_one_shot_review(self.snapshot)["blockers"])

    def test_no_repo_rulesets_is_detected(self):
        self.assertIn("NO_REPOSITORY_RULESET_EVIDENCE",
                      offline_one_shot_review(self.snapshot)["blockers"])

    def test_unaudited_bypass_and_dispatcher_are_separate_blockers(self):
        problems = offline_one_shot_review(self.snapshot)["blockers"]
        self.assertIn("MISSING_BYPASS_INVENTORY_WITNESS", problems)
        self.assertIn("MISSING_SINGLE_AUTHORIZED_DISPATCHER_WITNESS", problems)

    def test_operator_approved_sha_can_differ_from_server_resolved_sha(self):
        self.snapshot["server_resolved_sha"] = UNREVIEWED
        self.assertIn("SERVER_REF_RESOLUTION_RACE_OR_MISMATCH",
                      offline_one_shot_review(self.snapshot)["blockers"])

    def test_wrong_attempt_and_wrong_run_number_are_disallowed(self):
        for field, changed in (("run_number", 386), ("run_attempt", 2)):
            with self.subTest(field=field):
                v = copy.deepcopy(self.snapshot)
                v[field] = changed
                self.assertIn("ONE_SHOT_SLOT_DRIFT",
                              offline_one_shot_review(v)["blockers"])

    def test_boolean_run_number_cannot_pass_as_integer(self):
        self.snapshot["run_number"] = True
        self.assertIn("ONE_SHOT_SLOT_DRIFT",
                      offline_one_shot_review(self.snapshot)["blockers"])

    def test_invalid_sha_shape_is_rejected(self):
        self.snapshot["operator_checked_sha"] = "not-a-sha"
        self.assertIn("MISSING_40_HEX_SOURCE",
                      offline_one_shot_review(self.snapshot)["blockers"])

    def test_nonhex_sha_is_rejected(self):
        self.snapshot["server_resolved_sha"] = "z" * 40
        self.assertIn("NONHEX_SOURCE",
                      offline_one_shot_review(self.snapshot)["blockers"])

    def test_an_unexpected_proof_claim_cannot_silently_extend_schema(self):
        self.snapshot["server_really_approved"] = True
        self.assertIn("FIELD_INVENTORY_NOT_EXACT",
                      offline_one_shot_review(self.snapshot)["blockers"])

    def test_fully_populated_fake_witnesses_still_do_not_authorize(self):
        self.snapshot.update({
            "branch_protected": True,
            "repository_ruleset_count": 1,
            "exclusive_update_lock_witness": "UNTRUSTED_FAKE_LOCK",
            "bypass_inventory_witness": "UNTRUSTED_FAKE_BYPASS_LIST",
            "single_authorized_dispatcher_witness": "UNTRUSTED_FAKE_OWNER",
            "no_retry_witness": "UNTRUSTED_FAKE_ONE_SHOT",
        })
        report = offline_one_shot_review(self.snapshot)
        self.assertEqual(report["blockers"], ())
        self.assertEqual(report["status"], "BLOCKED")
        self.assertIs(report["dispatch_authorized"], False)
        self.assertIs(report["slot_reserved_or_allocated"], False)

    def test_nonmapping_input_fails_without_allocating_anything(self):
        report = offline_one_shot_review([])
        self.assertIn("UNTRUSTED_REPORT_NOT_MAPPING", report["blockers"])
        self.assertIs(report["slot_reserved_or_allocated"], False)
