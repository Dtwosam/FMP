from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase7AcceptanceStateTests(unittest.TestCase):
    def test_phase7_pass_and_shadow_design_eligibility_are_recorded_exactly(self) -> None:
        evidence = (ROOT / "docs/phase7-walk-forward-evidence.md").read_text(encoding="utf-8")
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        experiments = (ROOT / "docs/experiment-log.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")

        self.assertIn("35015277625", evidence)
        self.assertIn("10414817824", evidence)
        self.assertIn("2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4", evidence)
        self.assertIn("PHASE7_PROMOTE_TO_SHADOW_DESIGN", evidence)
        self.assertIn("0.757266%", evidence)
        self.assertIn("0.262176%", evidence)
        self.assertIn("1.062731", evidence)
        self.assertIn("1.021310", evidence)
        self.assertIn("199", evidence)
        self.assertIn("5 of 7", evidence)
        self.assertIn("35.061843%", evidence)
        self.assertIn("1.0-pip diagnostic", evidence)
        self.assertIn("-0.562118%", evidence)

        self.assertIn("DEC-035 — Phase 7 walk-forward outcome and acceptance review", decision)
        self.assertIn("Phase 7 is formally PASS", decision)
        self.assertIn("eligible for Phase 8 shadow design only", decision)

        self.assertIn("### EXP-20260915-008 — Phase 7 walk-forward evaluation", experiments)
        self.assertIn("- Status: PASS", experiments)
        self.assertIn("- Conclusion: PROMOTE", experiments)
        self.assertIn("35015277625", experiments)

        self.assertIn("**Current phase:** Phase 7 — Walk-forward Evaluation", state)
        self.assertIn("**Phase status:** PASS", state)
        self.assertIn("Final-test touched: YES — Stage 1 2024 and Stage 2 2025-2026", state)
        self.assertIn("Stage 2 outcome: `PHASE7_PROMOTE_TO_SHADOW_DESIGN`", state)
        self.assertIn("Phase 8 remains UNSTARTED", state)
        self.assertNotIn("## Phase 8 — ACTIVE", state)


if __name__ == "__main__":
    unittest.main()
