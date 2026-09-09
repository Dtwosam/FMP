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
        "pair_side_breakdown": [
            {"pair": "EURUSD", "side": "ASK", "expected_manifests": 4250, "present_manifests": 4250, "missing_manifests": 0, "raw_backed_manifests": 4230, "manifest_only_inferred_not_found": 20, "raw_without_manifest": 0},
            {"pair": "EURUSD", "side": "BID", "expected_manifests": 4250, "present_manifests": 4250, "missing_manifests": 0, "raw_backed_manifests": 4230, "manifest_only_inferred_not_found": 20, "raw_without_manifest": 0},
            {"pair": "GBPUSD", "side": "ASK", "expected_manifests": 4250, "present_manifests": 4250, "missing_manifests": 0, "raw_backed_manifests": 4230, "manifest_only_inferred_not_found": 20, "raw_without_manifest": 0},
            {"pair": "GBPUSD", "side": "BID", "expected_manifests": 4250, "present_manifests": 4250, "missing_manifests": 0, "raw_backed_manifests": 4230, "manifest_only_inferred_not_found": 20, "raw_without_manifest": 0},
            {"pair": "USDJPY", "side": "ASK", "expected_manifests": 4250, "present_manifests": 4250, "missing_manifests": 0, "raw_backed_manifests": 4240, "manifest_only_inferred_not_found": 10, "raw_without_manifest": 0},
            {"pair": "USDJPY", "side": "BID", "expected_manifests": 4250, "present_manifests": 4250, "missing_manifests": 0, "raw_backed_manifests": 4240, "manifest_only_inferred_not_found": 10, "raw_without_manifest": 0},
        ],
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
        "acquisition_baseline_completed_at_utc": "2026-09-09T11:42:29Z",
        "acquisition_history_guard_version": 1,
        "acquisition_history_guard_started_at_utc": "2026-09-09T12:10:00Z",
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
        self.assertIn("to_char(", sql)
        self.assertIn("now() at time zone 'UTC'", sql)
        self.assertIn("'YYYY-MM-DD\"T\"HH24:MI:SS.MS\"Z\"'", sql)
        self.assertNotIn("now() as audited_at_utc", sql)

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

    def test_rejects_issue_samples_when_provenance_reports_zero_issues(self) -> None:
        provenance = provenance_report()
        provenance["issue_samples"] = [
            {
                "kind": "invalid_manifest",
                "pair": "EURUSD",
                "side": "BID",
                "date_utc": "2024-01-02",
                "detail": "contradictory sample",
            }
        ]

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["provenance_issue_samples_empty"])

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

    def test_rejects_missing_accounting_pair_side_breakdown(self) -> None:
        accounting = accounting_report()
        accounting["pair_side_breakdown"] = []

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting,
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["accounting_pair_side_breakdown_complete"])

    def test_rejects_duplicate_accounting_pair_side_row(self) -> None:
        accounting = accounting_report()
        breakdown = list(accounting["pair_side_breakdown"])
        breakdown[-1] = dict(breakdown[0])
        accounting["pair_side_breakdown"] = breakdown

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting,
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["accounting_pair_side_breakdown_complete"])

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

    def test_rejects_provenance_without_history_guard_version(self) -> None:
        provenance = provenance_report()
        provenance.pop("acquisition_history_guard_version")

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(
            report["checks"]["provenance_acquisition_history_guard_version"]
        )

    def test_rejects_provenance_without_history_guard_timestamp(self) -> None:
        provenance = provenance_report()
        provenance.pop("acquisition_history_guard_started_at_utc")

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(
            report["checks"]["provenance_acquisition_history_guard_started_at_utc"]
        )

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

    def test_rejects_zero_acquisition_baseline_run_id(self) -> None:
        provenance = provenance_report()
        provenance["acquisition_baseline_run_id"] = 0

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["provenance_acquisition_baseline_run_id"])

    def test_rejects_structural_evidence_older_than_acquisition_baseline(self) -> None:
        structural = structural_report()
        structural["audited_at_utc"] = "2026-09-09T11:00:00Z"

        report = evaluate_phase1_acceptance(
            structural,
            accounting_report(),
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["structural_after_acquisition_baseline"])

    def test_rejects_accounting_evidence_older_than_acquisition_baseline(self) -> None:
        accounting = accounting_report()
        accounting["audited_at_utc"] = "2026-09-09T11:00:00Z"

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting,
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["accounting_after_acquisition_baseline"])

    def test_rejects_malformed_acquisition_baseline_completion_time(self) -> None:
        provenance = provenance_report()
        provenance["acquisition_baseline_completed_at_utc"] = "not-a-timestamp"

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(
            report["checks"]["provenance_acquisition_baseline_completed_at_utc"]
        )

    def test_rejects_non_utc_structural_audit_timestamp(self) -> None:
        structural = structural_report()
        structural["audited_at_utc"] = "2026-09-09T13:05:00+01:00"

        report = evaluate_phase1_acceptance(
            structural,
            accounting_report(),
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["structural_audited_at_utc_valid"])

    def test_rejects_non_utc_accounting_audit_timestamp(self) -> None:
        accounting = accounting_report()
        accounting["audited_at_utc"] = "2026-09-09T13:05:00+01:00"

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting,
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["accounting_audited_at_utc_valid"])

    def test_rejects_non_utc_acquisition_baseline_completion_time(self) -> None:
        provenance = provenance_report()
        provenance["acquisition_baseline_completed_at_utc"] = "2026-09-09T12:42:29+01:00"

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(
            report["checks"]["provenance_acquisition_baseline_completed_at_utc"]
        )

    def test_rejects_future_structural_audit_timestamp(self) -> None:
        structural = structural_report()
        structural["audited_at_utc"] = "2099-01-01T00:00:00Z"

        report = evaluate_phase1_acceptance(
            structural,
            accounting_report(),
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["structural_audited_at_not_future"])

    def test_rejects_future_accounting_audit_timestamp(self) -> None:
        accounting = accounting_report()
        accounting["audited_at_utc"] = "2099-01-01T00:00:00Z"

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting,
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["accounting_audited_at_not_future"])

    def test_rejects_future_acquisition_baseline_completion_time(self) -> None:
        structural = structural_report()
        accounting = accounting_report()
        provenance = provenance_report()
        provenance["acquisition_baseline_completed_at_utc"] = "2099-01-01T00:00:00Z"
        structural["audited_at_utc"] = "2099-01-01T00:01:00Z"
        accounting["audited_at_utc"] = "2099-01-01T00:01:00Z"

        report = evaluate_phase1_acceptance(
            structural,
            accounting,
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(
            report["checks"]["provenance_acquisition_baseline_not_future"]
        )

    def test_rejects_structural_evidence_after_history_guard_start(self) -> None:
        structural = structural_report()
        structural["audited_at_utc"] = "2026-09-09T12:11:00Z"

        report = evaluate_phase1_acceptance(
            structural,
            accounting_report(),
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(
            report["checks"]["structural_not_after_provenance_history_guard"]
        )

    def test_rejects_accounting_evidence_after_history_guard_start(self) -> None:
        accounting = accounting_report()
        accounting["audited_at_utc"] = "2026-09-09T12:11:00Z"

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting,
            provenance_report(),
        )

        self.assertFalse(report["ready"])
        self.assertFalse(
            report["checks"]["accounting_not_after_provenance_history_guard"]
        )

    def test_rejects_issue_samples_when_provenance_claims_zero_issues(self) -> None:
        provenance = provenance_report()
        provenance["issue_samples"] = [
            {
                "kind": "raw_checksum_mismatch",
                "pair": "EURUSD",
                "side": "BID",
                "date_utc": "2024-01-02",
                "detail": "unexpected diagnostic evidence",
            }
        ]

        report = evaluate_phase1_acceptance(
            structural_report(),
            accounting_report(),
            provenance,
        )

        self.assertFalse(report["ready"])
        self.assertFalse(report["checks"]["provenance_issue_samples_empty"])

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

    def test_acceptance_cli_requires_fresh_acquisition_history(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "accept-phase1",
                    "--structural-json",
                    "structural.json",
                    "--accounting-json",
                    "accounting.json",
                    "--provenance-json",
                    "provenance.json",
                ]
            )

    def test_acceptance_cli_consumes_evidence_files_and_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            structural_path = root / "structural.json"
            accounting_path = root / "accounting.json"
            provenance_path = root / "provenance.json"
            workflow_runs_path = root / "workflow-runs.json"
            structural_path.write_text(json.dumps(structural_report()), encoding="utf-8")
            accounting_path.write_text(
                json.dumps({"phase1_recovery_accounting": accounting_report()}),
                encoding="utf-8",
            )
            provenance_path.write_text(json.dumps(provenance_report()), encoding="utf-8")
            workflow_runs_path.write_text(
                json.dumps(
                    [
                        {
                            "workflow_runs": [
                                {
                                    "id": 34113319817,
                                    "event": "push",
                                    "status": "completed",
                                    "updated_at": "2026-09-09T11:42:29Z",
                                    "head_commit": {
                                        "message": "[phase1-repair-batch] repair"
                                    },
                                },
                                {
                                    "id": 34113319999,
                                    "event": "push",
                                    "status": "completed",
                                    "updated_at": "2026-09-09T12:20:00Z",
                                    "head_commit": {
                                        "message": "[phase1-no-source] docs"
                                    },
                                },
                            ]
                        }
                    ]
                ),
                encoding="utf-8",
            )

            args = build_parser().parse_args(
                [
                    "accept-phase1",
                    "--structural-json",
                    str(structural_path),
                    "--accounting-json",
                    str(accounting_path),
                    "--provenance-json",
                    str(provenance_path),
                    "--workflow-runs-json",
                    str(workflow_runs_path),
                ]
            )
            output = StringIO()
            with redirect_stdout(output):
                code = args.func(args)

            self.assertEqual(code, 0)
            self.assertTrue(json.loads(output.getvalue())["ready"])

    def test_acceptance_cli_rejects_source_activity_after_provenance_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            structural_path = root / "structural.json"
            accounting_path = root / "accounting.json"
            provenance_path = root / "provenance.json"
            workflow_runs_path = root / "workflow-runs.json"
            structural_path.write_text(json.dumps(structural_report()), encoding="utf-8")
            accounting_path.write_text(
                json.dumps({"phase1_recovery_accounting": accounting_report()}),
                encoding="utf-8",
            )
            provenance_path.write_text(json.dumps(provenance_report()), encoding="utf-8")
            workflow_runs_path.write_text(
                json.dumps(
                    [
                        {
                            "workflow_runs": [
                                {
                                    "id": 34113319817,
                                    "event": "push",
                                    "status": "completed",
                                    "updated_at": "2026-09-09T11:42:29Z",
                                    "head_commit": {
                                        "message": "[phase1-repair-batch] repair"
                                    },
                                },
                                {
                                    "id": 34113320000,
                                    "event": "push",
                                    "status": "completed",
                                    "updated_at": "2026-09-09T12:20:00Z",
                                    "head_commit": {
                                        "message": "[phase1-repair-batch] later repair"
                                    },
                                },
                            ]
                        }
                    ]
                ),
                encoding="utf-8",
            )

            args = build_parser().parse_args(
                [
                    "accept-phase1",
                    "--structural-json",
                    str(structural_path),
                    "--accounting-json",
                    str(accounting_path),
                    "--provenance-json",
                    str(provenance_path),
                    "--workflow-runs-json",
                    str(workflow_runs_path),
                ]
            )
            output = StringIO()
            with redirect_stdout(output):
                code = args.func(args)

            report = json.loads(output.getvalue())
            self.assertEqual(code, 2)
            self.assertFalse(report["ready"])
            self.assertFalse(report["checks"]["pass_guard_no_source_activity_since_provenance"])


if __name__ == "__main__":
    unittest.main()
