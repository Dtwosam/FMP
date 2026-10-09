from __future__ import annotations

import copy
import hashlib
import json
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_workflow_sha_identity_preview import (
    EXPECTED,
    _adverse_cases,
    build_offline_workflow_sha_identity_report,
    synthetic_identity_matches,
    validate_offline_workflow_sha_identity_report,
)


def _refingerprint(report: dict[str, object]) -> None:
    original = dict(report)
    original.pop("report_sha256", None)
    report["report_sha256"] = hashlib.sha256(
        (json.dumps(original, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


class OfflineWorkflowShaIdentityPreviewTests(unittest.TestCase):
    def test_positive_synthetic_fixture_is_still_denied(self):
        self.assertTrue(synthetic_identity_matches(EXPECTED))
        report = build_offline_workflow_sha_identity_report()
        validate_offline_workflow_sha_identity_report(report)
        self.assertTrue(report["dispatch_blocked"])
        self.assertTrue(report["fixture_is_not_approved"])
        for key in (
            "real_git_ref_immutability_verified", "independent_review_present",
            "workflow_amendment_installed", "annual_workflow_dispatch_authorized",
            "run385_execution_authorized", "rerun_authorized", "trading_authorized",
        ):
            with self.subTest(key=key):
                self.assertIs(report[key], False)

    def test_workflow_sha_independent_of_matching_ref_and_source_sha(self):
        changed = dict(EXPECTED)
        changed["workflow_sha"] = "d" * 40
        self.assertEqual(changed["sha"], EXPECTED["sha"])
        self.assertEqual(changed["workflow_ref"], EXPECTED["workflow_ref"])
        self.assertFalse(synthetic_identity_matches(changed))
        changed = dict(EXPECTED)
        changed["sha"] = "b" * 40
        self.assertEqual(changed["workflow_sha"], EXPECTED["workflow_sha"])
        self.assertFalse(synthetic_identity_matches(changed))

    def test_every_negative_case_rejected(self):
        negatives = _adverse_cases()
        self.assertEqual(len(negatives), 22)
        self.assertEqual(len({name for name, _ in negatives}), len(negatives))
        for name, value in negatives:
            with self.subTest(name=name):
                self.assertFalse(synthetic_identity_matches(value))
        report = build_offline_workflow_sha_identity_report()
        self.assertEqual(report["adverse_scenario_count"], 22)
        self.assertTrue(all(row["matches"] is False for row in report["scenarios"][1:]))

    def test_rehashed_forged_permission_and_scenario_are_rejected(self):
        for mutation in ("permission", "scenario", "extra_field"):
            report = copy.deepcopy(build_offline_workflow_sha_identity_report())
            if mutation == "permission":
                report["run385_execution_authorized"] = True
            elif mutation == "scenario":
                report["scenarios"][1]["matches"] = True
            else:
                report["approval_from_report"] = True
            _refingerprint(report)
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, "source-bound report mismatch"):
                validate_offline_workflow_sha_identity_report(report)

    def test_missing_or_malformed_report_digest_rejected(self):
        report = build_offline_workflow_sha_identity_report()
        report.pop("report_sha256")
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            validate_offline_workflow_sha_identity_report(report)
        with self.assertRaisesRegex(ValueError, "must be a mapping"):
            validate_offline_workflow_sha_identity_report(None)


if __name__ == "__main__":
    unittest.main()
