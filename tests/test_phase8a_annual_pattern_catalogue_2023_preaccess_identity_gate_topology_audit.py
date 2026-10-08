from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_preaccess_identity_gate_topology_audit import (
    ANNUAL_WORKFLOW_BLOB,
    ANNUAL_WORKFLOW_PATH,
    CURRENT_AUTH,
    FIRST_EVIDENCE_STEP,
    INSTALL,
    SYNTHETIC_GATE,
    _extract_job_step_names,
    _negative_matrix,
    _synthetic_steps,
    assess_current_order,
    build_2023_preaccess_identity_topology_audit,
    synthetic_gate_precedes_evidence,
    validate_2023_preaccess_identity_topology_audit,
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
    "DEC-623 requires exact installed annual workflow source",
)
class InertPreaccessIdentityGateTopologyAuditTests(unittest.TestCase):
    def _current(self):
        return _extract_job_step_names((ROOT / ANNUAL_WORKFLOW_PATH).read_text(encoding="utf-8"))

    def test_current_preflight_metadata_api_before_execution_authorization(self):
        current = self._current()
        observed = assess_current_order(current)
        self.assertEqual(observed, {
            "annual_preflight": False, "annual_cell": True, "annual_freeze": True,
        })
        preflight = current["annual_preflight"]
        self.assertLess(preflight.index(INSTALL), preflight.index(FIRST_EVIDENCE_STEP["annual_preflight"]))
        self.assertLess(
            preflight.index(FIRST_EVIDENCE_STEP["annual_preflight"]),
            preflight.index(CURRENT_AUTH["annual_preflight"]),
        )
        self.assertFalse(synthetic_gate_precedes_evidence(current))

    def test_synthetic_early_gate_before_first_evidence_in_all_three_jobs(self):
        current = self._current()
        candidate = _synthetic_steps(current)
        self.assertTrue(synthetic_gate_precedes_evidence(candidate))
        for job, names in candidate.items():
            self.assertLess(names.index(INSTALL), names.index(SYNTHETIC_GATE))
            self.assertLess(names.index(SYNTHETIC_GATE), names.index(FIRST_EVIDENCE_STEP[job]))

    def test_missing_late_or_duplicated_gate_all_fail_closed(self):
        candidate = _synthetic_steps(self._current())
        adverse = _negative_matrix(candidate)
        self.assertEqual(len(adverse), 9)
        self.assertTrue(all(not row["synthetic_topology_valid"] for row in adverse))
        self.assertEqual({row["job"] for row in adverse}, set(candidate))
        self.assertEqual({row["mode"] for row in adverse}, {"missing", "late", "duplicate"})

    def test_reject_wrong_job_inventory_and_malformed_steps(self):
        candidate = _synthetic_steps(self._current())
        for change in ("missing_job", "extra_job", "malformed_type", "missing_remote", "missing_install"):
            with self.subTest(change=change):
                bad = copy.deepcopy(candidate)
                if change == "missing_job":
                    del bad["annual_freeze"]
                elif change == "extra_job":
                    bad["untrusted_job"] = []
                elif change == "malformed_type":
                    bad["annual_cell"] = "not-steps"
                elif change == "missing_remote":
                    bad["annual_preflight"].remove(FIRST_EVIDENCE_STEP["annual_preflight"])
                else:
                    bad["annual_freeze"].remove(INSTALL)
                self.assertFalse(synthetic_gate_precedes_evidence(bad))

    def test_report_requires_exact_pinned_source_and_denies_live_approval(self):
        report = build_2023_preaccess_identity_topology_audit(repository_root=ROOT)
        validate_2023_preaccess_identity_topology_audit(report)
        self.assertEqual(report["annual_workflow_git_blob"], ANNUAL_WORKFLOW_BLOB)
        self.assertEqual(report["synthetic_adverse_scenario_count"], 9)
        self.assertTrue(report["preflight_accepted_source_metadata_api_step_before_existing_execution_authorization"])
        self.assertTrue(report["dispatch_blocked"])
        for key in (
            "identity_gate_installed",
            "runtime_tag_sha_binding_installed",
            "immutable_tag_authenticated",
            "administrator_no_bypass_enforcement_authenticated",
            "annual_dispatch_authorized",
            "annual_run385_action_authorized",
            "retry_authorized",
            "trading_authorized",
        ):
            self.assertIs(report[key], False)

    def test_rehashed_authority_and_type_confusion_fails(self):
        base = build_2023_preaccess_identity_topology_audit(repository_root=ROOT)
        for key, new in (
            ("identity_gate_installed", True),
            ("immutable_tag_authenticated", True),
            ("annual_dispatch_authorized", True),
            ("annual_run385_action_authorized", True),
            ("trading_authorized", True),
            ("dispatch_blocked", 1),
            ("synthetic_adverse_scenario_count", 9.0),
            ("expected_run_number", 385.0),
            ("preflight_accepted_source_metadata_api_step_before_existing_execution_authorization", 1),
            ("current_execution_authorization_precedes_first_evidence_step_by_job", {}),
        ):
            with self.subTest(field=key):
                changed = copy.deepcopy(base)
                changed[key] = new
                _rehash(changed)
                with self.assertRaisesRegex(ValueError, "source-bound exact report mismatch"):
                    validate_2023_preaccess_identity_topology_audit(changed)

    def test_cli_only_assess_and_cannot_write_inside_checkout(self):
        script = (ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_preaccess_identity_gate_topology_audit.py").read_text()
        self.assertIn('sub.add_parser("assess")', script)
        self.assertIn("target.is_relative_to(checkout)", script)
        for prohibited in ("gh workflow run", "subprocess.", "requests.", "git push", "git tag", "os.system"):
            self.assertNotIn(prohibited, script)


if __name__ == "__main__":
    unittest.main()
