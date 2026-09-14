from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SessionSweepStateTests(unittest.TestCase):
    def test_exp006_is_closed_rejected_and_guardrails_remain_locked(self) -> None:
        decisions = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        spec = (ROOT / "docs/superpowers/specs/2026-09-14-phase4-session-sweep-rejection-design.md").read_text(encoding="utf-8")
        evidence = (ROOT / "docs/phase4-session-sweep-rejection-evidence.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")

        self.assertIn("DEC-026 — Phase 4 session high/low sweep-rejection baseline protocol", decisions)
        self.assertIn("DEC-027 — Phase 4 session high/low sweep-rejection experiment outcome", decisions)
        self.assertIn("**Status:** APPROVED — PREDECLARED", spec)
        self.assertIn("**Decision:** `DEC-026` — APPROVED", spec)
        self.assertIn("[00:00, 08:00) Europe/London", spec)
        self.assertIn("18 × 3 × 3 = 162", spec)
        self.assertIn("Normal EXP-006 tooling must reject any final-split request before loading market data", spec)

        self.assertIn("**Experiment result:** FAIL", evidence)
        self.assertIn("**Conclusion:** REJECT", evidence)
        self.assertIn("18/18 cells successful", evidence)
        self.assertIn("162/162", evidence)
        self.assertIn("zero of 27", evidence.lower())
        self.assertIn("USDJPY 5m / 2-pip buffer", evidence)
        self.assertIn("+1.9167%", evidence)
        self.assertIn("-15.4056%", evidence)
        self.assertIn("Final-test touched?: NO", evidence)

        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("experiment status: FAIL", state)
        self.assertIn("DEC-027 APPROVED", state)
        self.assertIn("All six planned baseline families have complete benchmark evidence and experiment-log entries", state)
        self.assertIn("USDJPY 15m", state)
        self.assertIn("USDJPY 1h / 2.0x", state)
        self.assertIn("final-test", state.lower())
        self.assertIn("## Phase 5 — ACTIVE", state)
        self.assertIn("Real-money trading: locked", state)


if __name__ == "__main__":
    unittest.main()
