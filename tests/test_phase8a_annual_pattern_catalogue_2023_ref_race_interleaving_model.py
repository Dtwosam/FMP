from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_ref_race_interleaving_model import (
    CHECK,
    MUTATE,
    POST,
    RESOLVE,
    REVIEWED_SHA,
    UNREVIEWED_SHA,
    _schedules,
    build_2023_run385_ref_race_interleaving_report,
    validate_2023_run385_ref_race_interleaving_report,
)

ROOT = Path(__file__).resolve().parents[1]


def _rehash(value: dict[str, object]) -> None:
    unsigned = dict(value)
    unsigned.pop("report_sha256", None)
    value["report_sha256"] = hashlib.sha256(
        (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-619 requires the installed original workflow for source-bound review",
)
class Run385RefRaceInterleavingTests(unittest.TestCase):
    def test_single_dangerous_dispatch_order_unlocked_main(self):
        rows = _schedules(mutation_allowed=True)
        self.assertEqual(len(rows), 4)
        self.assertEqual(len({tuple(x["event_order"]) for x in rows}), 4)
        counterexamples = [row for row in rows if row["wrong_sha_consumed_hypothetically"]]
        self.assertEqual(len(counterexamples), 1)
        self.assertEqual(
            counterexamples[0]["event_order"], [CHECK, MUTATE, RESOLVE, POST],
        )
        self.assertTrue(counterexamples[0]["client_sha_check_passed"])
        self.assertEqual(counterexamples[0]["server_dispatched_sha_hypothetical"], UNREVIEWED_SHA)
        self.assertTrue(counterexamples[0]["late_postcheck_cannot_undo_consumption"])
        self.assertFalse(counterexamples[0]["postcheck_accepts_hypothetically"])

    def test_ordered_precheck_and_postcheck_cases_distinguished(self):
        rows = _schedules(mutation_allowed=True)
        by_order = {tuple(row["event_order"]): row for row in rows}
        before = by_order[(MUTATE, CHECK, RESOLVE, POST)]
        self.assertFalse(before["client_sha_check_passed"])
        self.assertFalse(before["run385_consumed_hypothetically"])
        self.assertIsNone(before["server_dispatched_sha_hypothetical"])
        after_resolution = by_order[(CHECK, RESOLVE, MUTATE, POST)]
        self.assertEqual(after_resolution["server_dispatched_sha_hypothetical"], REVIEWED_SHA)
        self.assertFalse(after_resolution["wrong_sha_consumed_hypothetically"])
        self.assertTrue(after_resolution["postcheck_accepts_hypothetically"])
        after_postcheck = by_order[(CHECK, RESOLVE, POST, MUTATE)]
        self.assertEqual(after_postcheck["server_dispatched_sha_hypothetical"], REVIEWED_SHA)
        self.assertFalse(after_postcheck["wrong_sha_consumed_hypothetically"])

    def test_exclusive_lock_assumption_removes_counterexample_not_proof(self):
        rows = _schedules(mutation_allowed=False)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["server_dispatched_sha_hypothetical"] == REVIEWED_SHA for row in rows))
        self.assertTrue(all(not row["wrong_sha_consumed_hypothetically"] for row in rows))
        report = build_2023_run385_ref_race_interleaving_report(repository_root=ROOT)
        validate_2023_run385_ref_race_interleaving_report(report)
        self.assertEqual(report["expected_run_number"], 385)
        self.assertEqual(report["expected_run_attempt"], 1)
        self.assertEqual(report["expected_predecessor_run_id"], 37663157285)
        profiles = {p["name"]: p for p in report["profiles"]}
        self.assertEqual(set(profiles), {
            "unprotected_main", "main_exclusive_lock_assumed", "mutable_tag",
            "tag_ruleset_with_bypass_assumed", "tag_delete_recreate_allowed",
            "tag_no_bypass_lock_assumed",
        })
        self.assertEqual(profiles["unprotected_main"]["synthetic_counterexample_count"], 1)
        self.assertEqual(profiles["main_exclusive_lock_assumed"]["synthetic_counterexample_count"], 0)
        self.assertEqual(profiles["tag_ruleset_with_bypass_assumed"]["synthetic_counterexample_count"], 1)
        self.assertEqual(profiles["tag_no_bypass_lock_assumed"]["synthetic_counterexample_count"], 0)
        self.assertFalse(report["real_exclusive_main_lock_proven"])
        self.assertFalse(report["real_tag_immutability_proven"])
        self.assertFalse(report["live_annual_run385_consumption_state_verified"])
        self.assertFalse(report["annual_dispatch_authorized"])
        self.assertTrue(report["no_real_dispatch_performed"])
        self.assertTrue(report["dispatch_blocked"])

    def test_rehashed_fake_live_authority_or_modified_schedule_rejected(self):
        report = build_2023_run385_ref_race_interleaving_report(repository_root=ROOT)
        for key in (
            "real_exclusive_main_lock_proven", "real_tag_immutability_proven",
            "workflow_runtime_amendment_approved", "annual_dispatch_authorized",
            "run385_execution_authorized_by_this_report", "trading_authorized",
            "broker_mutation_authorized", "live_annual_run385_consumption_state_verified",
            "no_real_dispatch_performed", "dispatch_blocked",
        ):
            with self.subTest(key=key):
                forged = copy.deepcopy(report)
                forged[key] = not forged[key]
                _rehash(forged)
                with self.assertRaisesRegex(ValueError, "source-bound report payload mismatch"):
                    validate_2023_run385_ref_race_interleaving_report(forged)
        forged = copy.deepcopy(report)
        counterexample = next(row for row in forged["profiles"][0]["schedules"] if row["wrong_sha_consumed_hypothetically"])
        counterexample["wrong_sha_consumed_hypothetically"] = False
        _rehash(forged)
        with self.assertRaisesRegex(ValueError, "source-bound report payload mismatch"):
            validate_2023_run385_ref_race_interleaving_report(forged)

    def test_unknown_fields_and_substituted_profiles_rejected(self):
        report = build_2023_run385_ref_race_interleaving_report(repository_root=ROOT)
        changed = copy.deepcopy(report)
        changed["production_ready"] = True
        _rehash(changed)
        with self.assertRaisesRegex(ValueError, "source-bound report payload mismatch"):
            validate_2023_run385_ref_race_interleaving_report(changed)
        changed = copy.deepcopy(report)
        changed["profiles"].pop()
        _rehash(changed)
        with self.assertRaisesRegex(ValueError, "source-bound report payload mismatch"):
            validate_2023_run385_ref_race_interleaving_report(changed)

    def test_invalid_input_type_rejected_and_cli_is_assess_only(self):
        with self.assertRaises(TypeError):
            _schedules(mutation_allowed=1)
        script = (ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_ref_race_interleaving_model.py").read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("assess")', script)
        self.assertIn("source_checkout = Path(__file__).resolve().parents[1]", script)
        self.assertIn("target = args.out.resolve()", script)
        self.assertIn("if target.is_relative_to(source_checkout):", script)
        self.assertNotIn("target.is_relative_to(checkout)", script)
        for forbidden in ("git push", "git tag", "gh workflow run",
                          "subprocess.", "requests.", 'sub.add_parser("dispatch")'):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
