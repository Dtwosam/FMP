"""DEC-1759 status-document refresh remains explicitly non-authorizing."""
from pathlib import Path
import unittest

DOC = (Path(__file__).resolve().parents[1] / "docs" / "project-state.md")


class CurrentPhase8AStatusCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DOC.read_text(encoding="utf-8")
        cls.checkpoint = cls.text.split(
            "## 2026-10-19 — Source-only Phase 8A external-admission"
            " blocker checkpoint (non-authorizing)", 1)[1].split(
                "## 2026-10-02 — DEC-473", 1)[0]

    def test_current_phase_still_eight_a_not_shadow(self):
        self.assertIn("**Current phase:** Phase 8A", self.text[:2500])
        self.assertIn("ACTIVE / BLOCKED ON INDEPENDENT SECURITY ADMISSION",
                      self.text[:3000])

    def test_observed_main_is_unprotected_not_a_future_witness(self):
        self.assertIn("53e203133bbc141b2f48c7b8b8241d56b35166a3",
                      self.checkpoint)
        self.assertIn("protected:false", self.checkpoint)
        self.assertIn("does **not** prove effective organization/enterprise",
                      self.checkpoint)

    def test_next_2023_one_shot_stays_blocked(self):
        self.assertIn("2023/run 385/attempt 1", self.checkpoint)
        self.assertIn("#779 remains unresolved", self.checkpoint)
        self.assertIn("distinct qualified human execution decision",
                      self.checkpoint)

    def test_research_method_and_past_year_distinguished(self):
        self.assertIn("DEC-469/DEC-268 discovery-first annual pattern catalogues",
                      self.checkpoint)
        self.assertIn("2022/run 384", self.checkpoint)
        self.assertIn("2024–2025 plus 2026 YTD cannot advance",
                      self.checkpoint)

    def test_later_drafts_are_not_source_of_truth_acceptance(self):
        self.assertIn("DRAFT / NEVER MERGE", self.checkpoint)
        self.assertIn("through PR #2005", self.checkpoint)
        self.assertIn("eight **MISSING** external independent proof",
                      self.checkpoint)

    def test_no_strategy_profit_or_downstream_trading_claim(self):
        self.assertIn("after-cost forward expectancy/profit is unknown",
                      self.checkpoint)
        self.assertIn("1.0-pip diagnostic result was negative",
                      self.checkpoint)
        self.assertIn("Phase11 real-money execution remain CLOSED",
                      self.checkpoint)
