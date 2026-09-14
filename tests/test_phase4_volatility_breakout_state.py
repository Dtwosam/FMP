from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class VolatilityBreakoutStateTests(unittest.TestCase):
    def test_exp005_protocol_is_predeclared_and_guardrails_remain_locked(self) -> None:
        decisions = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        record = (ROOT / "docs/phase4-volatility-breakout-predeclaration.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")

        self.assertIn("DEC-024 — Phase 4 volatility-breakout baseline protocol", decisions)
        self.assertIn("**Status:** APPROVED", decisions)
        self.assertIn("# EXP-20260914-005 — Rolling Volatility-Breakout Baseline", record)
        self.assertIn("**Status:** PREDECLARED", record)
        self.assertIn("Final-test touched?: NO", record)
        self.assertIn("[T - 8h, T)", record)
        self.assertIn("1.0x, 1.5x, and 2.0x", record)
        self.assertIn("exactly **1.0R**", record)
        self.assertIn("0.2, 0.5, and 1.0 pips", record)
        self.assertIn("162 benchmark rows", record)
        self.assertIn("NO_VOLATILITY_BREAKOUT", record)
        self.assertIn("No post-result parameter expansion", record)

        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("EXP-20260914-005", state)
        self.assertIn("PREDECLARED", state)
        self.assertIn("USDJPY 15m", state)
        self.assertIn("session high/low sweep/rejection", state.lower())
        self.assertIn("final-test", state.lower())
        self.assertIn("## Phase 5 — UNSTARTED", state)
        self.assertIn("Real-money trading remains locked", state)


if __name__ == "__main__":
    unittest.main()
