from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SessionSweepStateTests(unittest.TestCase):
    def test_exp006_is_predeclared_and_locked_to_approved_protocol(self) -> None:
        decisions = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        spec = (ROOT / "docs/superpowers/specs/2026-09-14-phase4-session-sweep-rejection-design.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")

        self.assertIn("DEC-026 — Phase 4 session high/low sweep-rejection baseline protocol", decisions)
        self.assertIn("**Status:** APPROVED — PREDECLARED", spec)
        self.assertIn("**Decision:** `DEC-026` — APPROVED", spec)
        self.assertIn("[00:00, 08:00) Europe/London", spec)
        self.assertIn("0 pips;", spec)
        self.assertIn("2 pips;", spec)
        self.assertIn("5 pips.", spec)
        self.assertIn("08:00 through 14:00", spec)
        self.assertIn("16:00", spec)
        self.assertIn("AMBIGUOUS_DUAL_SESSION_SWEEP", spec)
        self.assertIn("There is no same-day retry", spec)
        self.assertIn("18 × 3 × 3 = 162", spec)
        self.assertIn("Normal EXP-006 tooling must reject any final-split request before loading market data", spec)

        self.assertIn("experiment status: PREDECLARED", state)
        self.assertIn("DEC-026 APPROVED", state)
        self.assertIn("Final-test touched: NO", state)
        self.assertIn("## Phase 5 — UNSTARTED", state)
        self.assertIn("Real-money trading remains locked", state)
        self.assertIn("USDJPY 15m", state)
        self.assertIn("USDJPY 1h / 2.0x", state)


if __name__ == "__main__":
    unittest.main()
