from __future__ import annotations

import unittest

from fmp.data.phase1_acceptance import evaluate_phase1_acceptance


def structural_report() -> dict[str, object]:
    return {
        "expected_manifests": 25500,
        "present_manifests": 25500,
        "missing_manifests": 0,
        "completion_pct": "100.0000",
        "raw_objects": 25400,
        "unexpected_manifest_paths": 0,
        "raw_without_manifest": 0,
        "unexpected_raw_paths": 0,
        "latest_manifest_write": "2026-09-09T12:00:00+00:00",
        "audited_at_utc": "2026-09-09T12:05:00+00:00",
        "structural_gate_pass": True,
    }


def accounting_report() -> dict[str, object]:
    return {
        "report_version": 1,
        "scope": "phase1_recovery_accounting",
        "frozen_start_date": "2015-01-01",
        "frozen_end_date_exclusive": "2026-08-21",
        "audited_at_utc": "2026-09-09T12:05:00.000Z",
        "totals": {
            "expected_manifests": 25500,
            "present_manifests": 25500,
            "missing_manifests": 0,
            "raw_backed_manifests": 25400,
            "manifest_only_inferred_not_found": 100,
            "raw_without_manifest": 0,
            "unexpected_manifest_paths": 0,
            "unexpected_raw_paths": 0,
        },
        "pair_side_breakdown": [],
        "accounting_gate_pass": True,
    }


def provenance_report() -> dict[str, object]:
    return {
        "report_version": 1,
        "source": "dukascopy",
        "granularity": "1m",
        "scope": "cloud_snapshot_provenance",
        "planned_chunks": 25500,
        "complete": 25400,
        "not_found": 100,
        "invalid_manifest": 0,
        "raw_checksum_mismatch": 0,
        "raw_size_mismatch": 0,
        "invalid_raw_audit": 0,
        "issues": 0,
        "issue_samples": [],
        "ready": True,
    }


class Phase1AcceptanceTests(unittest.TestCase):
    def test_accepts_three_consistent_passing_evidence_reports(self) -> None:
        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance_report(),
        )

        self.assertTrue(report["ready"])
        self.assertEqual(report["frozen_manifest_target"], 25500)
        self.assertEqual(report["checks_failed"], 0)
        self.assertTrue(all(report["checks"].values()))

    def test_rejects_structural_failure_even_when_other_reports_pass(self) -> None:
        structural = structural_report()
        structural["structural_gate_pass"] = False

        report = evaluate_phase1_acceptance(
            structural,
            accounting_report(),
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["structural_gate_pass"])

    def test_rejects_complete_raw_count_cross_report_mismatch(self) -> None:
        provenance = provenance_report()
        provenance["complete"] = 25399
        provenance["not_found"] = 101

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["raw_backed_equals_provenance_complete"])
        self.assertFalse(report["checks"]["inferred_not_found_equals_provenance_not_found"])

    def test_rejects_cloud_provenance_that_does_not_cover_full_frozen_plan(self) -> None:
        provenance = provenance_report()
        provenance["planned_chunks"] = 25499

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["provenance_planned_chunks_25500"])

    def test_rejects_wrong_accounting_snapshot_identity(self) -> None:
        accounting = accounting_report()
        accounting["frozen_end_date_exclusive"] = "2026-08-20"

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting,
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["accounting_frozen_snapshot"])


if __name__ == "__main__":
    unittest.main()
