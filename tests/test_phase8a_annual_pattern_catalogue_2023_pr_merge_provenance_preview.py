from __future__ import annotations

import copy
import hashlib
import json
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_pr_merge_provenance_preview import (
    _counterexamples,
    build_pr_ci_provenance_preview,
    classify_pr_ci_provenance,
    fixture,
    validate_pr_ci_provenance_preview,
)


def refingerprint(value: dict[str, object]) -> None:
    raw = dict(value)
    raw.pop("report_sha256", None)
    value["report_sha256"] = hashlib.sha256(
        (json.dumps(raw, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


class PrMergeProvenancePreviewTests(unittest.TestCase):
    def test_synthetic_identical_tree_evidence_still_does_not_authorize_merge(self):
        self.assertEqual(classify_pr_ci_provenance(fixture()), "REPORTED_HEAD_TREE_EQUIVALENT")
        report = build_pr_ci_provenance_preview()
        validate_pr_ci_provenance_preview(report)
        for field in (
            "workflow_checkout_attested_by_runner", "real_review_proven",
            "actual_pr_merge_permitted", "annual_dispatch_authorized",
            "run385_authorized", "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(report[field], False)
        self.assertIs(report["dispatch_blocked"], True)

    def test_tree_difference_distinct_from_bad_ci(self):
        name, payload = _counterexamples()[0]
        self.assertEqual(name, "tree_difference")
        self.assertEqual(classify_pr_ci_provenance(payload), "REPORTED_SYNTHETIC_MERGE_ONLY")
        self.assertNotEqual(payload["head_tree_sha"], payload["synthetic_merge_tree_sha"])

    def test_stale_merge_and_failed_or_skipped_ci_are_rejected(self):
        cases = _counterexamples()
        self.assertEqual(len(cases), 26)
        self.assertEqual(len({n for n, _ in cases}), len(cases))
        for name, sample in cases[1:]:
            with self.subTest(name=name):
                self.assertEqual(classify_pr_ci_provenance(sample), "REJECTED")

    def test_wrong_input_shapes_are_rejected(self):
        for malformed in (None, "head", [], 123, True, {"pr_number": 99999}):
            with self.subTest(value=repr(malformed)):
                self.assertEqual(classify_pr_ci_provenance(malformed), "REJECTED")
        self.assertEqual(classify_pr_ci_provenance(dict(fixture(), repository="other/FMP")), "REJECTED")

    def test_source_bound_validator_rejects_rehashed_forged_authority(self):
        for field, altered in (
            ("actual_pr_merge_permitted", True),
            ("run385_authorized", True),
            ("trading_authorized", True),
            ("dispatch_blocked", False),
            ("source_is_synthetic_not_live", False),
            ("counterexample_count", 0),
            ("untrusted_review", "approved"),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(build_pr_ci_provenance_preview())
                changed[field] = altered
                refingerprint(changed)
                with self.assertRaisesRegex(ValueError, "source-bound exact report mismatch"):
                    validate_pr_ci_provenance_preview(changed)

    def test_source_bound_validator_rejects_rehashed_scenario_forgery(self):
        changed = build_pr_ci_provenance_preview()
        changed["cases"][2]["classification"] = "REPORTED_HEAD_TREE_EQUIVALENT"
        refingerprint(changed)
        with self.assertRaisesRegex(ValueError, "source-bound exact report mismatch"):
            validate_pr_ci_provenance_preview(changed)

    def test_wrong_fingerprint_and_wrong_shape_rejected(self):
        changed = build_pr_ci_provenance_preview()
        changed.pop("report_sha256")
        with self.assertRaisesRegex(ValueError, "report digest mismatch"):
            validate_pr_ci_provenance_preview(changed)
        with self.assertRaisesRegex(ValueError, "must be a mapping"):
            validate_pr_ci_provenance_preview(None)


if __name__ == "__main__":
    unittest.main()
