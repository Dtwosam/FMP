from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PreviousDayRejectionStateTests(unittest.TestCase):
    def test_exp004_protocol_is_predeclared_and_guardrails_remain_locked(self) -> None:
        decisions = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        record = (ROOT / "docs/phase4-previous-day-rejection-predeclaration.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")

        self.assertIn("DEC-022 — Phase 4 previous-day high/low rejection baseline protocol", decisions)
        self.assertIn("**Status:** APPROVED", decisions)
        self.assertIn("# EXP-20260914-004 — Previous-Day High/Low Rejection Baseline", record)
        self.assertIn("**Status:** PREDECLARED", record)
        self.assertIn("Final-test touched?: NO", record)
        self.assertIn("[17:00 America/New_York, 17:00 America/New_York)", record)
        self.assertIn("exactly 0, 2, and 5 pips", record)
        self.assertIn("exactly 0.2, 0.5, and 1.0 pips", record)
        self.assertIn("162 benchmark rows", record)
        self.assertIn("AMBIGUOUS_DUAL_REJECTION", record)
        self.assertIn("No post-result parameter expansion", record)

        self.assertIn("## Phase 4 — PASS", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — PASS", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("EXP-20260914-004", state)
        self.assertIn("previous-day high/low rejection", state.lower())
        self.assertIn("USDJPY 15m", state)
        self.assertIn("final-test", state.lower())
        self.assertIn("Real-money trading: locked", state)


if __name__ == "__main__":
    unittest.main()
