from __future__ import annotations

from unittest.mock import patch
import unittest

from fmp.discovery import exp062_post_result_diagnostics as diag


class Exp062PostResultDiagnosticTests(unittest.TestCase):
    def test_exact_result_is_diagnosed_without_opening_new_authority(self) -> None:
        report = diag.build_exp062_post_result_diagnostic()

        self.assertEqual(report["decision"], "DEC-442")
        self.assertEqual(
            report["stage"],
            "EXP062_POST_RESULT_DIAGNOSTIC_REVIEWED_NO_PERSISTENT_VALIDATION_EDGE",
        )
        self.assertEqual(report["candidate_count"], 11)
        self.assertEqual(report["candidate_cell_count"], 6)
        self.assertEqual(report["all_candidates_horizon_minutes"], 240)
        self.assertEqual(
            report["symbols_with_confirmation_survivors"],
            ["EURUSD", "GBPUSD"],
        )
        self.assertEqual(report["usd_jpy_confirmation_survivor_count"], 0)
        self.assertEqual(report["horizon_60_confirmation_survivor_count"], 0)
        self.assertEqual(report["validation_accepted_count"], 0)
        self.assertEqual(
            report["validation_failure_reason_counts"],
            {
                "VALIDATION_POSITIVE_YEARS_LT_3": 11,
                "VALIDATION_AGGREGATE_MEAN_NOT_POSITIVE": 11,
                "VALIDATION_YEAR_SUPPORT_LT_40": 1,
            },
        )
        self.assertTrue(
            report["interpretation"][
                "all_candidates_failed_positive_year_persistence"
            ]
        )
        self.assertTrue(
            report["interpretation"][
                "all_candidates_failed_positive_aggregate_validation_mean"
            ]
        )
        self.assertFalse(
            report["interpretation"]["broad_validation_sample_size_shortage"]
        )
        self.assertFalse(report["rerun_authorized"])
        self.assertFalse(report["threshold_relaxation_authorized"])
        self.assertFalse(report["pattern_redefinition_authorized"])
        self.assertFalse(report["successor_protocol_source_open_authorized"])
        self.assertFalse(report["phase8b_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_every_confirmation_survivor_still_passes_confirmation_gate(self) -> None:
        report = diag.build_exp062_post_result_diagnostic()
        for row in report["candidate_diagnostics"]:
            self.assertGreaterEqual(
                row["confirmation_support"],
                diag.CONFIRMATION_MIN_SUPPORT,
            )
            self.assertGreater(row["confirmation_mean_net_pips_0p5"], 0)
            self.assertNotIn("CONFIRMATION_GATE_DRIFT", row["failure_reasons"])

    def test_candidate_identity_or_distribution_drift_fails_closed(self) -> None:
        with patch.object(diag, "CANDIDATES", diag.CANDIDATES[:-1]):
            with self.assertRaisesRegex(
                ValueError,
                "frozen candidate count drift",
            ):
                diag.build_exp062_post_result_diagnostic()

        duplicate = (*diag.CANDIDATES[:-1], diag.CANDIDATES[0])
        with patch.object(diag, "CANDIDATES", duplicate):
            with self.assertRaisesRegex(
                ValueError,
                "duplicate candidate fingerprint",
            ):
                diag.build_exp062_post_result_diagnostic()

    def test_validation_failure_accounting_drift_fails_closed(self) -> None:
        row = list(diag.CANDIDATES[0])
        row[9] = 1.0
        changed = (tuple(row), *diag.CANDIDATES[1:])
        with patch.object(diag, "CANDIDATES", changed):
            with self.assertRaisesRegex(
                ValueError,
                "validation failure accounting drift",
            ):
                diag.build_exp062_post_result_diagnostic()

    def test_diagnostic_does_not_treat_single_support_shortfall_as_broad_sparsity(
        self,
    ) -> None:
        report = diag.build_exp062_post_result_diagnostic()
        shortfalls = [
            row
            for row in report["candidate_diagnostics"]
            if "VALIDATION_YEAR_SUPPORT_LT_40" in row["failure_reasons"]
        ]
        self.assertEqual(len(shortfalls), 1)
        self.assertEqual(shortfalls[0]["symbol"], "GBPUSD")
        self.assertEqual(shortfalls[0]["timeframe"], "1h")
        self.assertEqual(shortfalls[0]["validation_min_year_support"], 29)

    def test_source_freeze_identity_is_pinned(self) -> None:
        report = diag.build_exp062_post_result_diagnostic()
        self.assertEqual(
            report["source_freeze_merge_sha"],
            "d5e8ad7cd98ec1511742d1b266e6779852155c96",
        )
        self.assertEqual(
            report["source_freeze_blob_sha"],
            "ae0353fce77e9ff03536f2323820804dbda7241c",
        )
        self.assertEqual(
            report["next_gate"],
            "EXPLICIT_POST_EXP062_RESEARCH_DIRECTION_DECISION_AFTER_DIAGNOSTIC",
        )


if __name__ == "__main__":
    unittest.main()
