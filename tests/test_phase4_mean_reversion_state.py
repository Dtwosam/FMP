from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MeanReversionStateTests(unittest.TestCase):
    def test_predeclaration_is_frozen_before_implementation(self) -> None:
        decisions = (ROOT / "docs/decision-log.md").read_text()
        predeclared = (ROOT / "docs/phase4-mean-reversion-predeclaration.md").read_text()
        state = (ROOT / "docs/project-state.md").read_text()

        self.assertIn("DEC-020 — Phase 4 mean-reversion baseline protocol — APPROVED", decisions)
        self.assertIn("# EXP-20260914-003 — Mean Reversion Baseline", predeclared)
        self.assertIn("**Status:** PLANNED", predeclared)
        self.assertIn("Final-test touched?: NO", predeclared)
        self.assertIn("exactly 4h, 8h, 16h", predeclared)
        self.assertIn("exactly 1.5σ and 2.0σ", predeclared)
        self.assertIn("Result-producing benchmark: NOT RUN", predeclared)
        self.assertIn("Conclusion: not assigned", predeclared)
        self.assertIn("mean-reversion baseline", state)
        self.assertIn("final-test data remains locked", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("## Phase 5 — UNSTARTED", state)
        self.assertIn("Real-money trading remains locked", state)


if __name__ == "__main__":
    unittest.main()
