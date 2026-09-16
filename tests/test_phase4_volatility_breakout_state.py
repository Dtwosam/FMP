from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class VolatilityBreakoutStateTests(unittest.TestCase):
    def test_exp005_is_closed_promoted_and_guardrails_remain_locked(self) -> None:
        decisions = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        record = (ROOT / "docs/phase4-volatility-breakout-predeclaration.md").read_text(encoding="utf-8")
        evidence = (ROOT / "docs/phase4-volatility-breakout-evidence.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")

        self.assertIn("DEC-024 — Phase 4 volatility-breakout baseline protocol", decisions)
        self.assertIn("DEC-025 — Phase 4 volatility-breakout experiment outcome", decisions)
        self.assertIn("# EXP-20260914-005 — Rolling Volatility-Breakout Baseline", record)
        self.assertIn("**Status:** CLOSED", record)
        self.assertIn("**Outcome decision:** DEC-025 — PASS / PROMOTE", record)
        self.assertIn("Final-test touched?: NO", record)
        self.assertIn("[T - 8h, T)", record)
        self.assertIn("1.0x, 1.5x, and 2.0x", record)
        self.assertIn("exactly **1.0R**", record)
        self.assertIn("0.2, 0.5, and 1.0 pips", record)
        self.assertIn("No post-result parameter expansion", record)

        self.assertIn("**Experiment result:** PASS", evidence)
        self.assertIn("**Conclusion:** PROMOTE", evidence)
        self.assertIn("18/18 cells successful", evidence)
        self.assertIn("162/162", evidence)
        self.assertIn("USDJPY 1h / 2.0x", evidence)
        self.assertIn("+11.4235%", evidence)
        self.assertIn("+5.5971%", evidence)
        self.assertIn("+6.5350%", evidence)
        self.assertIn("+3.2953%", evidence)

        self.assertIn("## Phase 4 — PASS", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — PASS", state)
        self.assertIn("## Phase 7 — PASS", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("experiment status: PASS", state)
        self.assertIn("DEC-025 APPROVED", state)
        self.assertIn("USDJPY 15m", state)
        self.assertIn("USDJPY 1h / 2.0x", state)
        self.assertIn("session high/low sweep-rejection", state.lower())
        self.assertIn("final-test", state.lower())
        self.assertIn("Real-money trading: locked", state)
        self.assertIn("## Phase 8 — ACTIVE", state)


if __name__ == "__main__":
    unittest.main()
