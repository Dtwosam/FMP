from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_lock_witness_coverage import (
    INTERVALS,
    REQUIRED_CLAIMS,
    VERSION,
    build_2023_run385_lock_witness_coverage,
    validate_2023_run385_lock_witness_coverage,
    parse_untrusted_witness_json,
)

ROOT = Path(__file__).resolve().parents[1]
SHA = "a" * 40
TAG = "refs/tags/fmp/phase8a/2023/run385/example-v1"


def _witness(*, ref: str = "refs/heads/main") -> dict[str, object]:
    return {
        "schema": VERSION,
        "ref": ref,
        "reviewed_commit_sha": SHA,
        "intervals": [
            {"interval": label, "resolved_ref_sha": SHA, **{k: True for k in REQUIRED_CLAIMS}}
            for label in INTERVALS
        ],
    }


def _rehash(value: dict[str, object]) -> None:
    unsigned = dict(value)
    unsigned.pop("report_sha256", None)
    value["report_sha256"] = hashlib.sha256(
        (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-620 uses frozen installed annual workflow source only",
)
class Run385LockWitnessCoverageTests(unittest.TestCase):
    def test_all_positive_claims_remain_unauthenticated_and_blocked(self):
        report = build_2023_run385_lock_witness_coverage(
            repository_root=ROOT, witness=_witness(),
        )
        validate_2023_run385_lock_witness_coverage(report)
        self.assertTrue(report["all_required_intervals_claimed_positive"])
        self.assertTrue(report["active_workflow_ref_compatible"])
        self.assertEqual(report["expected_run_number"], 385)
        self.assertEqual(report["expected_run_attempt"], 1)
        self.assertEqual(report["predecessor_2022_freeze_run_id"], 37663157285)
        self.assertEqual(report["missing_or_adverse_interval_claims"], [])
        self.assertFalse(report["exclusive_main_lock_proven"])
        self.assertFalse(report["witness_authenticated"])
        self.assertFalse(report["server_transaction_continuity_proven"])
        self.assertFalse(report["live_run385_state_verified"])
        self.assertFalse(report["workflow_dispatch_authorized_by_this_report"])
        self.assertTrue(report["dispatch_blocked"])
        self.assertFalse(report["trading_authorized"])

    def test_all_positive_tag_claims_cannot_amend_main_only_workflow(self):
        report = build_2023_run385_lock_witness_coverage(
            repository_root=ROOT, witness=_witness(ref=TAG),
        )
        self.assertEqual(report["ref_kind"], "tag")
        self.assertTrue(report["all_required_intervals_claimed_positive"])
        self.assertFalse(report["active_workflow_ref_compatible"])
        self.assertFalse(report["immutable_tag_lock_proven"])
        self.assertFalse(report["reviewed_workflow_runtime_amendment_approved"])
        self.assertFalse(report["run385_execution_authorized_by_this_report"])

    def test_each_missing_interval_marks_incomplete_coverage(self):
        for label in INTERVALS:
            with self.subTest(label=label):
                witness = _witness()
                witness["intervals"] = [
                    v for v in witness["intervals"] if v["interval"] != label
                ]
                report = build_2023_run385_lock_witness_coverage(
                    repository_root=ROOT, witness=witness,
                )
                self.assertFalse(report["all_required_intervals_claimed_positive"])
                self.assertIn(label + ":missing", report["missing_or_adverse_interval_claims"])
                self.assertTrue(report["dispatch_blocked"])

    def test_each_claim_revocation_and_sha_mismatch_breaks_coverage(self):
        for label in INTERVALS:
            for field in REQUIRED_CLAIMS:
                with self.subTest(label=label, field=field):
                    witness = _witness()
                    row = next(v for v in witness["intervals"] if v["interval"] == label)
                    row[field] = False
                    report = build_2023_run385_lock_witness_coverage(
                        repository_root=ROOT, witness=witness,
                    )
                    self.assertFalse(report["all_required_intervals_claimed_positive"])
                    self.assertIn(label + ":" + field, report["missing_or_adverse_interval_claims"])
            witness = _witness()
            next(v for v in witness["intervals"] if v["interval"] == label)[
                "resolved_ref_sha"
            ] = "b" * 40
            report = build_2023_run385_lock_witness_coverage(
                repository_root=ROOT, witness=witness,
            )
            self.assertIn(label + ":sha_drift", report["missing_or_adverse_interval_claims"])

    def test_malformed_witness_and_boolean_type_confusion_rejected(self):
        mutants = []
        a = _witness(); a["admin_approved"] = True; mutants.append(a)
        a = _witness(); a["schema"] = "bad"; mutants.append(a)
        a = _witness(); a["ref"] = "refs/heads/unapproved"; mutants.append(a)
        a = _witness(); a["reviewed_commit_sha"] = "A" * 40; mutants.append(a)
        a = _witness(); a["intervals"] = 42; mutants.append(a)
        a = _witness(); a["intervals"].append(copy.deepcopy(a["intervals"][0])); mutants.append(a)
        a = _witness(); a["intervals"][0]["unknown"] = True; mutants.append(a)
        a = _witness(); a["intervals"][0]["all_bypass_paths_blocked"] = 1; mutants.append(a)
        a = _witness(); a["intervals"][0]["resolved_ref_sha"] = "unknown"; mutants.append(a)
        a = _witness(); a["intervals"][0]["interval"] = "unknown"; mutants.append(a)
        for n, witness in enumerate(mutants):
            with self.subTest(case=n):
                with self.assertRaises(ValueError):
                    build_2023_run385_lock_witness_coverage(
                        repository_root=ROOT, witness=witness,
                    )

    def test_rehashed_permission_escalation_and_missing_gap_forgery_rejected(self):
        baseline = build_2023_run385_lock_witness_coverage(
            repository_root=ROOT, witness=_witness(),
        )
        for key in (
            "witness_authenticated", "server_transaction_continuity_proven",
            "exclusive_main_lock_proven", "immutable_tag_lock_proven",
            "live_run385_state_verified", "workflow_dispatch_authorized_by_this_report",
            "run385_execution_authorized_by_this_report", "trading_authorized",
            "dispatch_blocked",
        ):
            with self.subTest(key=key):
                report = copy.deepcopy(baseline)
                report[key] = not report[key]
                _rehash(report)
                with self.assertRaisesRegex(ValueError, "source-bound report payload mismatch"):
                    validate_2023_run385_lock_witness_coverage(report)
        witness = _witness()
        witness["intervals"][1]["all_bypass_paths_blocked"] = False
        report = build_2023_run385_lock_witness_coverage(
            repository_root=ROOT, witness=witness,
        )
        report["missing_or_adverse_interval_claims"] = []
        report["all_required_intervals_claimed_positive"] = True
        _rehash(report)
        with self.assertRaisesRegex(ValueError, "source-bound report payload mismatch"):
            validate_2023_run385_lock_witness_coverage(report)

    def test_rehashed_bool_integer_and_numeric_retyping_is_rejected(self):
        baseline = build_2023_run385_lock_witness_coverage(
            repository_root=ROOT, witness=_witness(),
        )
        for key, replacement in (
            ("witness_authenticated", 0),
            ("real_money_authorized", 0),
            ("dispatch_blocked", 1),
            ("source_only_analysis", 1),
            ("all_required_intervals_claimed_positive", 1),
            ("expected_run_number", 385.0),
        ):
            with self.subTest(key=key):
                report = copy.deepcopy(baseline)
                report[key] = replacement
                _rehash(report)
                with self.assertRaisesRegex(ValueError, "source-bound report payload mismatch"):
                    validate_2023_run385_lock_witness_coverage(report)

    def test_duplicate_json_keys_rejected_before_any_claim_is_accepted(self):
        valid = json.dumps(_witness(), sort_keys=True)
        self.assertEqual(parse_untrusted_witness_json(valid), _witness())
        malformed = (
            valid.replace(
                '"all_bypass_paths_blocked": true',
                '"all_bypass_paths_blocked": false, "all_bypass_paths_blocked": true',
                1,
            ),
            valid.replace(
                '"ref": "refs/heads/main"',
                '"ref": "refs/heads/malicious", "ref": "refs/heads/main"',
                1,
            ),
            valid.replace(
                '"resolved_ref_sha": "' + SHA + '"',
                '"resolved_ref_sha": "' + ("b" * 40) +
                '", "resolved_ref_sha": "' + SHA + '"',
                1,
            ),
        )
        for sample in malformed:
            with self.subTest(sample=sample[:100]):
                with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
                    parse_untrusted_witness_json(sample)

    def test_cli_is_only_offline_assess_and_blocks_checkout_output(self):
        script = (ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_lock_witness_coverage.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('sub.add_parser("assess")', script)
        self.assertIn("target.is_relative_to(root)", script)
        self.assertIn("parse_untrusted_witness_json(", script)
        for forbidden in (
            "gh workflow run", "git push", "git tag", "subprocess.",
            "requests.", "gh api --method POST", 'sub.add_parser("dispatch")',
        ):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
