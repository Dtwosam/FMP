from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_three_layer_admission_model import (
    ANNUAL_WORKFLOW_BLOB,
    ANNUAL_WORKFLOW_PATH,
    CHECKOUT,
    EARLY_GATE,
    EXISTING_MAIN_ONLY,
    FIRST_EVIDENCE_STEP,
    INSTALL,
    RUNTIME_GATE,
    SETUP,
    _adversarial_matrix,
    _candidate,
    _current_source,
    build_three_layer_admission_model,
    synthetic_three_layer_placement_matches,
    validate_three_layer_admission_model,
)

ROOT = Path(__file__).resolve().parents[1]


def _rehash(report: dict[str, object]) -> None:
    unsigned = dict(report)
    unsigned.pop("report_sha256", None)
    report["report_sha256"] = hashlib.sha256(
        (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-624 requires original installed annual workflow source",
)
class ThreeLayerAdmissionModelTests(unittest.TestCase):
    def test_original_main_ref_gate_follows_checkout_and_precedes_pip(self):
        current = _current_source(ROOT)
        self.assertEqual(len(current), 3)
        for job, steps in current.items():
            with self.subTest(job=job):
                self.assertLess(steps.index(CHECKOUT), steps.index(EXISTING_MAIN_ONLY))
                self.assertLess(steps.index(EXISTING_MAIN_ONLY), steps.index(SETUP))
                self.assertLess(steps.index(SETUP), steps.index(INSTALL))
                self.assertLess(steps.index(INSTALL), steps.index(FIRST_EVIDENCE_STEP[job]))
                self.assertNotIn(EARLY_GATE, steps)
                self.assertNotIn(RUNTIME_GATE, steps)

    def test_proposed_three_layers_only_exist_in_memory(self):
        current = _current_source(ROOT)
        candidate, admission = _candidate(current)
        self.assertTrue(synthetic_three_layer_placement_matches(candidate, admission))
        for job in candidate:
            with self.subTest(job=job):
                self.assertTrue(admission[job])
                self.assertLess(candidate[job].index(EXISTING_MAIN_ONLY), candidate[job].index(EARLY_GATE))
                self.assertLess(candidate[job].index(EARLY_GATE), candidate[job].index(SETUP))
                self.assertLess(candidate[job].index(SETUP), candidate[job].index(INSTALL))
                self.assertLess(candidate[job].index(INSTALL), candidate[job].index(RUNTIME_GATE))
                self.assertLess(candidate[job].index(RUNTIME_GATE), candidate[job].index(FIRST_EVIDENCE_STEP[job]))

    def test_eighteen_adverse_cases_fail_closed(self):
        candidate, admission = _candidate(_current_source(ROOT))
        rows = _adversarial_matrix(candidate, admission)
        self.assertEqual(len(rows), 18)
        self.assertEqual({r["job"] for r in rows}, set(candidate))
        self.assertEqual({r["adverse_case"] for r in rows}, {
            "admission_missing", "admission_retyped_integer",
            "early_missing", "early_after_install",
            "runtime_missing", "runtime_after_evidence",
        })
        self.assertTrue(all(not r["synthetic_three_layer_placement_matches"] for r in rows))

    def test_missing_duplicate_wrong_job_or_step_types_rejected(self):
        candidate, admission = _candidate(_current_source(ROOT))
        for modification in ("missing_job", "invented_job", "double_early", "double_runtime", "wrong_type", "unknown_admission"):
            with self.subTest(modification=modification):
                steps = copy.deepcopy(candidate)
                adm = dict(admission)
                if modification == "missing_job":
                    del steps["annual_cell"]
                elif modification == "invented_job":
                    steps["annual_other"] = []
                elif modification == "double_early":
                    steps["annual_preflight"].insert(3, EARLY_GATE)
                elif modification == "double_runtime":
                    steps["annual_freeze"].append(RUNTIME_GATE)
                elif modification == "wrong_type":
                    steps["annual_cell"] = "not a step list"
                else:
                    adm["annual_other"] = True
                self.assertFalse(synthetic_three_layer_placement_matches(steps, adm))

    def test_report_matches_pinned_original_and_no_authority(self):
        report = build_three_layer_admission_model(repository_root=ROOT)
        validate_three_layer_admission_model(report)
        self.assertEqual(report["source_annual_workflow_git_blob"], ANNUAL_WORKFLOW_BLOB)
        self.assertEqual(report["source_annual_workflow_path"], ANNUAL_WORKFLOW_PATH)
        self.assertEqual(report["adverse_scenario_count"], 18)
        self.assertTrue(report["dispatch_blocked"])
        for forbidden in (
            "workflow_job_admission_gate_installed",
            "preinstall_ref_sha_gate_installed",
            "runtime_ref_sha_gate_installed",
            "tag_created_or_mutated",
            "immutable_tag_proven",
            "admin_no_bypass_lock_proven",
            "github_context_authenticated_by_model",
            "annual_dispatch_authorized",
            "annual_run385_action_authorized",
            "retry_authorized",
            "trading_authorized",
        ):
            self.assertIs(report[forbidden], False)

    def test_rehashed_forgery_or_boolean_integer_type_confusion_rejected(self):
        baseline = build_three_layer_admission_model(repository_root=ROOT)
        for key, value in (
            ("annual_dispatch_authorized", True),
            ("preinstall_ref_sha_gate_installed", True),
            ("github_context_authenticated_by_model", True),
            ("admin_no_bypass_lock_proven", True),
            ("trading_authorized", True),
            ("dispatch_blocked", 1),
            ("synthetic_positive_placement_only_not_authorization", 1),
            ("adverse_scenario_count", 18.0),
            ("expected_run", 385.0),
            ("adverse_scenario_results", []),
        ):
            with self.subTest(key=key):
                forged = copy.deepcopy(baseline)
                forged[key] = value
                _rehash(forged)
                with self.assertRaisesRegex(ValueError, "source-pinned canonical report mismatch"):
                    validate_three_layer_admission_model(forged)

    def test_cli_has_only_assess_and_cannot_dispatch(self):
        path = ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_three_layer_admission_model.py"
        script = path.read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("assess")', script)
        self.assertIn("target.is_relative_to(checkout)", script)
        for prohibited in ("gh workflow run", "subprocess.", "requests.", "git push", "git tag", "os.system"):
            self.assertNotIn(prohibited, script)


if __name__ == "__main__":
    unittest.main()
