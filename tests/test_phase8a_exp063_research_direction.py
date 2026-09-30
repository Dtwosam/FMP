from __future__ import annotations

from unittest.mock import patch
import unittest

from fmp.discovery import exp063_research_direction as direction


class Exp063ResearchDirectionTests(unittest.TestCase):
    def test_direction_opens_protocol_source_only(self) -> None:
        report = direction.build_exp063_persistence_first_research_direction()

        self.assertEqual(report["decision"], "DEC-443")
        self.assertEqual(
            report["stage"],
            "EXP063_PERSISTENCE_FIRST_PROTOCOL_SOURCE_DESIGN_OPEN",
        )
        self.assertEqual(
            report["successor_experiment_id"],
            "EXP-20260930-063",
        )
        self.assertTrue(report["successor_protocol_source_open_authorized"])
        self.assertFalse(report["successor_execution_authorized"])
        self.assertFalse(report["successor_historical_result_authorized"])
        self.assertFalse(report["reserved_robustness_access_authorized"])
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["phase8b_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_diagnostic_drives_persistence_not_threshold_relaxation(self) -> None:
        report = direction.build_exp063_persistence_first_research_direction()

        basis = report["diagnostic_basis"]
        self.assertEqual(basis["confirmation_survivor_count"], 11)
        self.assertEqual(basis["validation_accepted_count"], 0)
        self.assertTrue(
            basis["all_failed_positive_aggregate_validation_mean"]
        )
        self.assertTrue(
            basis["all_failed_three_of_four_positive_validation_years"]
        )
        self.assertFalse(basis["broad_validation_sample_size_shortage"])

        research = report["research_direction"]
        self.assertTrue(research["persistence_first_selection_required"])
        self.assertTrue(research["retrospective_year_balance_required"])
        self.assertTrue(
            research["single_period_strength_must_not_dominate_selection"]
        )
        self.assertFalse(research["threshold_relaxation_permitted"])
        self.assertFalse(research["exp062_pattern_rescue_permitted"])

    def test_seen_validation_period_is_reclassified_as_design_evidence(self) -> None:
        report = direction.build_exp063_persistence_first_research_direction()
        chronology = report["chronology"]

        self.assertEqual(
            chronology["retrospective_design_start"],
            "2015-01-01",
        )
        self.assertEqual(
            chronology["retrospective_design_end"],
            "2022-12-31",
        )
        self.assertEqual(
            chronology["retrospective_design_label"],
            "ALREADY_SEEN_DESIGN_EVIDENCE",
        )
        self.assertTrue(
            chronology["2019_2022_may_not_be_called_fresh_validation"]
        )
        self.assertFalse(chronology["reserved_robustness_opened"])

    def test_universe_remains_bounded(self) -> None:
        report = direction.build_exp063_persistence_first_research_direction()
        universe = report["bounded_universe"]

        self.assertEqual(
            universe["symbols"],
            ["EURUSD", "GBPUSD", "USDJPY"],
        )
        self.assertEqual(universe["timeframes"], ["5m", "15m", "1h"])
        self.assertEqual(universe["horizons_minutes"], [60, 240])
        self.assertFalse(universe["new_features_authorized_by_dec443"])
        self.assertFalse(universe["new_symbols_authorized_by_dec443"])
        self.assertFalse(universe["new_timeframes_authorized_by_dec443"])
        self.assertFalse(universe["new_horizons_authorized_by_dec443"])

    def test_source_identity_or_successor_identity_drift_fails_closed(self) -> None:
        with patch.object(direction, "SOURCE_DIAGNOSTIC_DECISION", "DEC-999"):
            with self.assertRaisesRegex(
                ValueError,
                "source diagnostic decision drift",
            ):
                direction.build_exp063_persistence_first_research_direction()

        with patch.object(
            direction,
            "SUCCESSOR_EXPERIMENT_ID",
            direction.SOURCE_EXPERIMENT_ID,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "successor experiment identity must be new",
            ):
                direction.build_exp063_persistence_first_research_direction()

    def test_chronology_overlap_fails_closed(self) -> None:
        with patch.object(
            direction,
            "RETROSPECTIVE_DESIGN_END",
            "2023-01-01",
        ):
            with self.assertRaisesRegex(
                ValueError,
                "retrospective/reserved chronology overlap",
            ):
                direction.build_exp063_persistence_first_research_direction()


if __name__ == "__main__":
    unittest.main()
