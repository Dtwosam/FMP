"""DEC-1730: falsified Phase 7 cost economics must fail the real audit.

Tests edit only temporary copies of the already published source-only report.
No private annual dataset or new profitability experiment is accessed.
"""
import tempfile
from pathlib import Path
import unittest
from unittest import mock

import test_dec1718_phase7_cost_fragility_baseline_audit as historical


class FrozenPhase7EconomicEvidenceAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = historical.EVIDENCE.read_text(encoding="utf-8")

    def _assert_published_cost_guard_detects_mutation(self, needle, replacement):
        self.assertEqual(self.original.count(needle), 1)
        forged = self.original.replace(needle, replacement, 1)
        self.assertNotEqual(forged, self.original)
        with tempfile.TemporaryDirectory() as location:
            candidate = Path(location) / "synthetic-forged-phase7.md"
            candidate.write_text(forged, encoding="utf-8")
            with mock.patch.object(historical, "EVIDENCE", candidate):
                rows = historical._cost_table()
        case = historical.Phase7HistoricalCostSensitivityAuditTests(
            "test_all_published_economic_metrics_match_frozen_evidence")
        case.rows = rows
        with self.assertRaises(AssertionError):
            case.test_all_published_economic_metrics_match_frozen_evidence()
        self.assertEqual(historical.EVIDENCE.read_text(encoding="utf-8"),
                         self.original)

    def test_detects_forged_low_return(self):
        self._assert_published_cost_guard_detects_mutation(
            "+0.757266%", "+9.757266%")

    def test_detects_forged_mid_return(self):
        self._assert_published_cost_guard_detects_mutation(
            "+0.262176%", "+9.262176%")

    def test_detects_forged_high_return(self):
        self._assert_published_cost_guard_detects_mutation(
            "-0.562118%", "+0.562118%")

    def test_detects_forged_low_pnl(self):
        self._assert_published_cost_guard_detects_mutation(
            "+$757.27", "+$5757.27")

    def test_detects_forged_mid_pnl(self):
        self._assert_published_cost_guard_detects_mutation(
            "+$262.18", "+$2262.18")

    def test_detects_forged_high_pnl(self):
        self._assert_published_cost_guard_detects_mutation(
            "-$562.12", "+$562.12")

    def test_detects_forged_low_profit_factor(self):
        self._assert_published_cost_guard_detects_mutation(
            "1.062731", "9.062731")

    def test_detects_forged_mid_profit_factor(self):
        self._assert_published_cost_guard_detects_mutation(
            "1.021310", "9.021310")

    def test_detects_forged_high_profit_factor(self):
        self._assert_published_cost_guard_detects_mutation(
            "0.955760", "1.955760")

    def test_detects_forged_low_trade_count(self):
        self._assert_published_cost_guard_detects_mutation(
            "| 0.2 pips | +0.757266% | +$757.27 | 199 |", "| 0.2 pips | +0.757266% | +$757.27 | 198 |")

    def test_detects_forged_mid_trade_count(self):
        self._assert_published_cost_guard_detects_mutation(
            "| 0.5 pips | +0.262176% | +$262.18 | 199 |", "| 0.5 pips | +0.262176% | +$262.18 | 198 |")

    def test_detects_forged_high_trade_count(self):
        self._assert_published_cost_guard_detects_mutation(
            "| 1.0 pips | -0.562118% | -$562.12 | 199 |", "| 1.0 pips | -0.562118% | -$562.12 | 198 |")

    def test_detects_forged_low_positive_windows(self):
        self._assert_published_cost_guard_detects_mutation(
            "| 5 of 7 | 35.061843% |", "| 6 of 7 | 35.061843% |")

    def test_detects_forged_mid_positive_windows(self):
        self._assert_published_cost_guard_detects_mutation(
            "| 4 of 7 | 39.223270% |", "| 5 of 7 | 39.223270% |")

    def test_detects_forged_stage2_promotion_label(self):
        original = "The authoritative Stage 2 status is therefore `PHASE7_PROMOTE_TO_SHADOW_DESIGN`."
        forged = "The authoritative Stage 2 status is therefore `PHASE7_APPROVED_FOR_LIVE_TRADING`."
        self.assertEqual(self.original.count(original), 1)
        case = historical.Phase7HistoricalCostSensitivityAuditTests(
            "test_phase7_outcome_authorizes_shadow_design_only")
        case.source = self.original.replace(original, forged, 1)
        with self.assertRaises(AssertionError):
            case.test_phase7_outcome_authorizes_shadow_design_only()

    def test_detects_forged_broker_trading_permission(self):
        original = "does not authorize broker integration, demo trading, live trading, order placement, or real-money trading"
        forged = "does authorize broker integration, demo trading, live trading, order placement, or real-money trading"
        self.assertEqual(self.original.count(original), 1)
        case = historical.Phase7HistoricalCostSensitivityAuditTests(
            "test_phase7_outcome_authorizes_shadow_design_only")
        case.source = self.original.replace(original, forged, 1)
        with self.assertRaises(AssertionError):
            case.test_phase7_outcome_authorizes_shadow_design_only()

    def test_pristine_frozen_historical_economics_control(self):
        case = historical.Phase7HistoricalCostSensitivityAuditTests(
            "test_all_published_economic_metrics_match_frozen_evidence")
        case.rows = historical._cost_table()
        case.test_all_published_economic_metrics_match_frozen_evidence()
        case.source = self.original
        case.test_phase7_outcome_authorizes_shadow_design_only()
