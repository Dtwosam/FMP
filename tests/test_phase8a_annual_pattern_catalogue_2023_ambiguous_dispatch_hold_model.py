from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_ambiguous_dispatch_hold_model import (
    VERSION,
    WORKFLOW,
    _report,
    build_2023_run385_ambiguous_dispatch_hold_report,
    parse_untrusted_dispatch_simulation_json,
    validate_2023_run385_ambiguous_dispatch_hold_report,
)

ROOT = Path(__file__).resolve().parents[1]
A = "a" * 40
B = "b" * 40


def _simulation(*, called: bool = True, outcome: str = "timeout") -> dict[str, object]:
    return {
        "schema": VERSION,
        "reviewed_code_sha": A,
        "dispatch_call_made": called,
        "client_observed_outcome": outcome,
        "observed_runs": [],
    }


def _run(*, head_sha: str = A, run_number: int = 385, attempt: int = 1,
         run_id: int = 42, predecessor: int = 37663157285,
         workflow_path: str = ".github/workflows/phase8a-annual-pattern-catalogue.yml",
         annual_segment_label: str = "2023") -> dict[str, object]:
    return {
        "run_id": run_id,
        "run_number": run_number,
        "run_attempt": attempt,
        "event": "workflow_dispatch",
        "workflow": WORKFLOW,
        "workflow_path": workflow_path,
        "annual_segment_label": annual_segment_label,
        "head_sha": head_sha,
        "previous_annual_freeze_run_id": predecessor,
    }


def _rehash(value: dict[str, object]) -> None:
    original = dict(value)
    original.pop("report_sha256", None)
    value["report_sha256"] = hashlib.sha256(
        (json.dumps(original, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-621 uses the original installed annual workflow and pinned source",
)
class Run385AmbiguousDispatchHoldModelTests(unittest.TestCase):
    def test_not_submitted_model_stays_blocked(self):
        inp = _simulation(called=False, outcome="not_called")
        report = build_2023_run385_ambiguous_dispatch_hold_report(
            repository_root=ROOT, input_doc=inp,
        )
        self.assertEqual(report["simulated_state"], "NO_CALL_IN_THIS_SIMULATION_NOT_LIVE_INVENTORY_PROOF")
        self.assertEqual(report["exact_expected_run_number"], 385)
        self.assertEqual(report["exact_expected_run_attempt"], 1)
        self.assertEqual(report["exact_predecessor_run_id"], 37663157285)
        self.assertTrue(report["terminal_one_shot_hold"])
        self.assertTrue(report["no_real_annual_dispatch_performed"])
        self.assertTrue(report["dispatch_blocked"])
        self.assertFalse(report["annual_dispatch_authorized_by_report"])
        self.assertFalse(report["live_annual_run_inventory_authenticated"])
        self.assertFalse(report["retry_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_ambiguous_attempt_without_run_is_terminal_no_retry(self):
        for outcome in ("timeout", "transport_error", "http_rejected", "http_accepted", "unknown"):
            with self.subTest(outcome=outcome):
                report = build_2023_run385_ambiguous_dispatch_hold_report(
                    repository_root=ROOT, input_doc=_simulation(outcome=outcome),
                )
                self.assertEqual(report["simulated_state"], "SIMULATED_AMBIGUOUS_SUBMISSION_TERMINAL_HOLD_NO_RETRY")
                self.assertEqual(report["simulated_matching_run_count"], 0)
                self.assertFalse(report["second_dispatch_authorized"])
                self.assertFalse(report["retry_authorized"])
                self.assertTrue(report["dispatch_blocked"])

    def test_exact_synthetic_observation_never_confers_authority(self):
        inp = _simulation(outcome="http_accepted")
        inp["observed_runs"].append(_run())
        report = build_2023_run385_ambiguous_dispatch_hold_report(
            repository_root=ROOT, input_doc=inp,
        )
        self.assertEqual(report["simulated_state"], "SIMULATED_ONE_EXACT_RUN_STILL_REQUIRE_INDEPENDENT_EVIDENCE")
        self.assertEqual(report["simulated_matching_run_count"], 1)
        self.assertEqual(report["simulated_conflicting_run_count"], 0)
        self.assertFalse(report["live_annual_run_inventory_authenticated"])
        self.assertFalse(report["annual_dispatch_authorized_by_report"])
        self.assertFalse(report["rerun_authorized"])
        self.assertTrue(report["terminal_one_shot_hold"])
        self.assertFalse(report["trading_authorized"])

    def test_wrong_commit_or_attempt_or_predecessor_is_terminal(self):
        mutants = (
            {"head_sha": B},
            {"attempt": 2},
            {"run_number": 386},
            {"predecessor": 10},
            {"workflow_path": ".github/workflows/other-annual.yml"},
            {"annual_segment_label": "2024"},
        )
        for mutant in mutants:
            with self.subTest(mutant=mutant):
                inp = _simulation(outcome="http_accepted")
                inp["observed_runs"].append(_run(**mutant))
                report = build_2023_run385_ambiguous_dispatch_hold_report(
                    repository_root=ROOT, input_doc=inp,
                )
                self.assertEqual(report["simulated_matching_run_count"], 0)
                self.assertEqual(report["simulated_conflicting_run_count"], 1)
                self.assertEqual(report["simulated_state"], "SIMULATED_RUN_CONFLICT_TERMINAL_HOLD_NO_RETRY")
                self.assertFalse(report["replacement_run_authorized"])

    def test_multiple_observations_and_rejected_response_are_terminal(self):
        inp = _simulation(outcome="http_accepted")
        inp["observed_runs"].extend([_run(), _run(run_id=43)])
        report = build_2023_run385_ambiguous_dispatch_hold_report(
            repository_root=ROOT, input_doc=inp,
        )
        self.assertEqual(report["simulated_matching_run_count"], 2)
        self.assertEqual(report["simulated_state"], "SIMULATED_RUN_CONFLICT_TERMINAL_HOLD_NO_RETRY")
        inp = _simulation(outcome="http_rejected")
        inp["observed_runs"].append(_run())
        report = build_2023_run385_ambiguous_dispatch_hold_report(
            repository_root=ROOT, input_doc=inp,
        )
        self.assertEqual(report["simulated_state"], "SIMULATED_RUN_CONFLICT_TERMINAL_HOLD_NO_RETRY")

    def test_malformed_and_contradictory_inputs_rejected(self):
        inputs = []
        a = _simulation(); a["dispatch_call_made"] = 1; inputs.append(a)
        a = _simulation(); a["reviewed_code_sha"] = "A" * 40; inputs.append(a)
        a = _simulation(); a["client_observed_outcome"] = "maybe"; inputs.append(a)
        a = _simulation(called=False, outcome="not_called"); a["observed_runs"].append(_run()); inputs.append(a)
        a = _simulation(called=False, outcome="http_accepted"); inputs.append(a)
        a = _simulation(outcome="not_called"); inputs.append(a)
        a = _simulation(); a["observed_runs"] = [_run(), _run()]; inputs.append(a)
        a = _simulation(); a["observed_runs"] = [_run(attempt=True)]; inputs.append(a)
        a = _simulation(); a["observed_runs"] = [_run(head_sha="bad")]; inputs.append(a)
        a = _simulation(); a["observed_runs"] = [_run()]; a["observed_runs"][0]["unknown"] = 1; inputs.append(a)
        a = _simulation(); a["observed_runs"] = [_run()]; a["observed_runs"][0]["event"] = "push"; inputs.append(a)
        a = _simulation(); a["observed_runs"] = [_run()]; a["observed_runs"][0]["workflow_path"] = 12; inputs.append(a)
        a = _simulation(); a["observed_runs"] = [_run()]; a["observed_runs"][0]["annual_segment_label"] = False; inputs.append(a)
        a = _simulation(); a["observed_runs"] = [_run(run_id=i+1) for i in range(9)]; inputs.append(a)
        for idx, inp in enumerate(inputs):
            with self.subTest(idx=idx):
                with self.assertRaises(ValueError):
                    build_2023_run385_ambiguous_dispatch_hold_report(
                        repository_root=ROOT, input_doc=inp,
                    )

    def test_duplicate_json_keys_rejected_before_simulation(self):
        valid = json.dumps(_simulation(), sort_keys=True)
        self.assertEqual(parse_untrusted_dispatch_simulation_json(valid), _simulation())
        dup = valid.replace(
            '"dispatch_call_made": true',
            '"dispatch_call_made": false, "dispatch_call_made": true',
        )
        with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
            parse_untrusted_dispatch_simulation_json(dup)
        inp = _simulation(outcome="http_accepted")
        inp["observed_runs"].append(_run())
        raw = json.dumps(inp, sort_keys=True)
        raw = raw.replace(
            '"run_number": 385', '"run_number": 386, "run_number": 385',
        )
        with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
            parse_untrusted_dispatch_simulation_json(raw)

    def test_rehashed_permission_and_bool_int_tampering_rejected(self):
        original = build_2023_run385_ambiguous_dispatch_hold_report(
            repository_root=ROOT, input_doc=_simulation(outcome="timeout"),
        )
        for name, replacement in (
            ("annual_dispatch_authorized_by_report", True),
            ("retry_authorized", True),
            ("terminal_one_shot_hold", False),
            ("dispatch_blocked", 1),
            ("no_real_annual_dispatch_performed", 1),
            ("exact_expected_run_number", 385.0),
            ("live_annual_run_inventory_authenticated", 0),
        ):
            with self.subTest(name=name):
                change = copy.deepcopy(original)
                change[name] = replacement
                _rehash(change)
                with self.assertRaisesRegex(ValueError, "source-bound payload or permission mismatch"):
                    validate_2023_run385_ambiguous_dispatch_hold_report(change)
        change = copy.deepcopy(original)
        change["simulated_state"] = "APPROVED_TO_RETRY"
        _rehash(change)
        with self.assertRaisesRegex(ValueError, "source-bound payload or permission mismatch"):
            validate_2023_run385_ambiguous_dispatch_hold_report(change)

    def test_script_assess_only_and_no_checkout_writes(self):
        code = (ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_ambiguous_dispatch_hold_model.py").read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("assess")', code)
        self.assertIn("target.is_relative_to(checkout)", code)
        self.assertIn("parse_untrusted_dispatch_simulation_json(", code)
        for prohibited in (
            "gh workflow run", "gh api --method POST", "git push", "git tag",
            "subprocess.", "requests.", 'sub.add_parser("dispatch")',
        ):
            self.assertNotIn(prohibited, code)


if __name__ == "__main__":
    unittest.main()
