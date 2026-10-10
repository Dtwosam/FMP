from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec671_offline_run385_race_model.py"
spec = importlib.util.spec_from_file_location("dec671", SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class OfflineRun385RaceTests(unittest.TestCase):
    def test_mutable_main_and_competitor_are_both_unsafe(self):
        result = module.assess(False, False)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertGreater(result["unsafe_schedules"], 0)
        self.assertFalse(result["annual_run_385_consumed"])
        self.assertFalse(result["can_authorize_dispatch"])

    def test_ref_freeze_alone_is_insufficient(self):
        result = module.assess(True, False)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertGreater(result["unsafe_schedules"], 0)
        self.assertIn("competing dispatch", " ".join(result["findings"]))

    def test_dispatcher_exclusivity_alone_is_insufficient(self):
        result = module.assess(False, True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertGreater(result["unsafe_schedules"], 0)
        self.assertIn("mutable main", " ".join(result["findings"]))

    def test_two_assumed_locks_are_only_unverified_model(self):
        result = module.assess(True, True)
        self.assertEqual(result["status"], "MODEL_CONSISTENT_UNVERIFIED")
        self.assertEqual(result["unsafe_schedules"], 0)
        self.assertFalse(result["server_enforcement_verified"])
        self.assertFalse(result["can_authorize_dispatch"])

    def test_stale_review_then_changed_ref_consumes_wrong_commit(self):
        state = module.Model(freeze_ref=False, exclusive_dispatcher=True)
        for step in ("review_main", "update_main", "our_dispatch"):
            state.step(step)
        self.assertTrue(state.violated())
        self.assertEqual(state.our_allocated[0], 385)
        self.assertEqual(state.our_allocated[1], module.UNREVIEWED_SHA)

    def test_competing_dispatch_consumes_run385_before_ours(self):
        state = module.Model(freeze_ref=True, exclusive_dispatcher=False)
        for step in ("review_main", "competing_dispatch", "our_dispatch"):
            state.step(step)
        self.assertTrue(state.violated())
        self.assertEqual(state.allocations[0][0], 385)
        self.assertEqual(state.our_allocated[0], 386)

    def test_review_then_safe_dispatch_first_is_not_a_counterexample(self):
        state = module.Model(freeze_ref=False, exclusive_dispatcher=False)
        for step in ("review_main", "our_dispatch", "update_main", "competing_dispatch"):
            state.step(step)
        self.assertFalse(state.violated())

    def test_model_rejects_unrecognized_transition(self):
        with self.assertRaises(ValueError):
            module.Model(False, False).step("real_workflow_dispatch")

    def test_enumeration_exactly_six_interleavings(self):
        for freeze in (True, False):
            for exclusive in (True, False):
                with self.subTest(freeze=freeze, exclusive=exclusive):
                    self.assertEqual(module.explore(freeze, exclusive)["tested_schedules"], 6)

    def test_default_cli_blocks_and_does_not_dispatch(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT)],
                           capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        r = json.loads(p.stdout)
        self.assertFalse(r["annual_run_385_consumed"])
        self.assertFalse(r["can_authorize_dispatch"])

    def test_explicit_model_counterexample_cli_is_nonzero(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT), "--execute-offline-model"],
                           capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        self.assertGreater(json.loads(p.stdout)["unsafe_schedules"], 0)

    def test_assumed_both_locks_cli_is_still_nonzero_and_unverified(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT),
                            "--execute-offline-model", "--assume-ref-frozen",
                            "--assume-dispatch-exclusive"],
                           capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 3)
        r = json.loads(p.stdout)
        self.assertEqual(r["status"], "MODEL_CONSISTENT_UNVERIFIED")
        self.assertFalse(r["server_enforcement_verified"])

    def test_cli_rejects_real_github_dispatch_arguments(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT),
                            "--ref", "main", "--workflow", "annual"],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)


if __name__ == "__main__":
    unittest.main()
