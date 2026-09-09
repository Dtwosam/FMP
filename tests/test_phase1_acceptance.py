from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from fmp.data.cli import build_parser
from fmp.data.phase1_acceptance import evaluate_phase1_acceptance


def structural_report() -> dict[str, object]:
    return {
        "report_version": 1,
        "scope": "phase1_structural_acceptance",
        "frozen_start_date": "2015-01-01",
        "frozen_end_date_exclusive": "2026-08-21",
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
        "plan_sha256": "2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6",
        "planned_chunks": 25500,
        "complete": 25400,
        "not_found": 100,
        "invalid_manifest": 0,
        "raw_checksum_mismatch": 0,
        "raw_size_mismatch": 0,
        "invalid_raw_audit": 0,
        "issues": 0,
        "issue_samples": [],
        "acquisition_baseline_run_id": 34113319817,
        "acquisition_unchanged_during_verification": True,
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

    def test_rejects_wrong_structural_snapshot_identity(self) -> None:
        structural = structural_report()
        structural["frozen_end_date_exclusive"] = "2026-08-20"

        report = evaluate_phase1_acceptance(
            structural,
            accounting_report(),
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["structural_frozen_snapshot"])

    def test_structural_audit_sql_emits_snapshot_identity(self) -> None:
        sql = Path("docs/phase1-final-acceptance-audit.sql").read_text(encoding="utf-8")
        self.assertIn("1 as report_version", sql)
        self.assertIn("'phase1_structural_acceptance' as scope", sql)
        self.assertIn("b.start_day as frozen_start_date", sql)
        self.assertIn("b.end_exclusive as frozen_end_date_exclusive", sql)

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

    def test_rejects_inconsistent_provenance_issue_subcount(self) -> None:
        provenance = provenance_report()
        provenance["raw_checksum_mismatch"] = 1
        provenance["issues"] = 0
        provenance["ready"] = True

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["provenance_raw_checksum_mismatch_zero"])

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

    def test_rejects_provenance_without_stable_acquisition_stamp(self) -> None:
        provenance = provenance_report()
        provenance["acquisition_unchanged_during_verification"] = False

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(
            report["checks"]["provenance_acquisition_unchanged_during_verification"]
        )

    def test_rejects_provenance_without_acquisition_baseline_run_id(self) -> None:
        provenance = provenance_report()
        provenance["acquisition_baseline_run_id"] = None

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["provenance_acquisition_baseline_run_id"])

    def test_rejects_wrong_provenance_snapshot_identity(self) -> None:
        provenance = provenance_report()
        provenance["plan_sha256"] = "0" * 64

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["provenance_frozen_plan_sha256"])

    def test_acceptance_cli_consumes_evidence_files_and_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            structural_path = root / "structural.json"
            accounting_path = root / "accounting.json"
            provenance_path = root / "provenance.json"
            structural_path.write_text(json.dumps(structural_report()), encoding="utf-8")
            accounting_path.write_text(
                json.dumps({"phase1_recovery_accounting": accounting_report()}),
                encoding="utf-8",
            )
            provenance_path.write_text(json.dumps(provenance_report()), encoding="utf-8")

            args = build_parser().parse_args(
                [
                    "accept-phase1",
                    "--structural-json",
                    str(structural_path),
                    "--accounting-json",
                    str(accounting_path),
                    "--provenance-json",
                    str(provenance_path),
                ]
            )
            output = StringIO()
            with redirect_stdout(output):
                code = args.func(args)

            self.assertEqual(code, 0)
            self.assertTrue(json.loads(output.getvalue())["ready"])


if __name__ == "__main__":
    unittest.main()
