from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Phase4AcceptanceStateTests(unittest.TestCase):
    def test_phase4_is_pass_after_phase6_activation(self) -> None:
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        evidence = (ROOT / "docs/phase4-acceptance-evidence.md").read_text(encoding="utf-8")

        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("## Phase 4 — PASS", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — ACTIVE", state)
        self.assertIn("DEC-028", state)
        self.assertEqual(decision.count("## DEC-028 — Phase 4 baseline strategy research acceptance review"), 1)
        self.assertIn("- DEC-028 — Phase 4 baseline strategy research acceptance review — APPROVED", decision)
        self.assertIn("**Result:** PASS", evidence)
        self.assertIn("Final-test touched?: NO", evidence)
        self.assertIn("final-test period remains locked", state.lower())
        self.assertIn("Real-money trading: locked", state)


if __name__ == "__main__":
    unittest.main()
