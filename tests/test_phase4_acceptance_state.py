from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Phase4AcceptanceStateTests(unittest.TestCase):
    def test_phase4_is_pass_after_phase7_closure(self) -> None:
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        evidence = (ROOT / "docs/phase4-acceptance-evidence.md").read_text(encoding="utf-8")

        self.assertIn("**Phase status:** PASS", state)
        self.assertIn("## Phase 4 — PASS", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — PASS", state)
        self.assertIn("## Phase 7 — PASS", state)
        self.assertIn("DEC-028", state)
        self.assertEqual(decision.count("## DEC-028 — Phase 4 baseline strategy research acceptance review"), 1)
        self.assertIn("- DEC-028 — Phase 4 baseline strategy research acceptance review — APPROVED", decision)
        self.assertIn("**Result:** PASS", evidence)
        self.assertIn("Final-test touched?: NO", evidence)
        self.assertIn("Final-test touched: YES — Stage 1 2024 and Stage 2 2025-2026", state)
        self.assertIn("Real-money trading: locked", state)
        self.assertNotIn("## Phase 8 — ACTIVE", state)


if __name__ == "__main__":
    unittest.main()
