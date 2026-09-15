from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MeanReversionStateTests(unittest.TestCase):
    def test_predeclared_protocol_is_preserved_after_rejection(self) -> None:
        decisions = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        record = (ROOT / "docs/phase4-mean-reversion-predeclaration.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")

        self.assertIn("DEC-020 — Phase 4 mean-reversion baseline protocol — APPROVED", decisions)
        self.assertIn("# EXP-20260914-003 — Mean Reversion Baseline", record)
        self.assertIn("**Status:** FAIL", record)
        self.assertIn("Final-test touched?: NO", record)
        self.assertIn("exactly 4h, 8h, 16h", record)
        self.assertIn("exactly 1.5σ and 2.0σ", record)
        self.assertIn("exactly 0.2, 0.5, 1.0 pips", record)
        self.assertIn("18 pair/timeframe/split cells and 324 configuration rows", record)
        self.assertIn("No post-result parameter expansion", record)
        self.assertIn("87003a3982ca61eb6fd030c5291616d98dbb0c1a", record)
        self.assertIn("34875463677", record)
        self.assertIn("Conclusion: REJECT", record)
        self.assertIn("## Phase 4 — PASS", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — ACTIVE", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("previous-day high/low rejection", state.lower())
        self.assertIn("final-test", state.lower())
        self.assertIn("Real-money trading: locked", state)


if __name__ == "__main__":
    unittest.main()
