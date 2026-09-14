from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Phase5AcceptanceStateTests(unittest.TestCase):
    def test_phase5_is_pass_with_checkpoint_pending_and_later_gates_locked(self) -> None:
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        evidence = (ROOT / "docs/phase5-acceptance-evidence.md").read_text(encoding="utf-8")

        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("**Phase status:** PASS", state)
        self.assertIn("DEC-030", state)
        self.assertEqual(
            decision.count("## DEC-030 — Phase 5 leakage-safe feature-engine acceptance review"),
            1,
        )
        self.assertIn(
            "- DEC-030 — Phase 5 leakage-safe feature-engine acceptance review — APPROVED",
            decision,
        )
        self.assertIn("**Result:** PASS", evidence)
        self.assertIn("**Decision:** DEC-030 — APPROVED", evidence)
        self.assertIn("run `34910227756`", evidence)
        self.assertIn("`74dce1b945ad31a05416a4fc9e63443a884cb90c`", evidence)
        self.assertIn("9/9", evidence)
        self.assertIn("972/972", evidence)
        self.assertIn("Final-test touched?: NO", evidence)
        self.assertIn("`fmp-v1-phase5-features` — PENDING", evidence)
        self.assertIn("Phase 6", state)
        self.assertIn("UNSTARTED", state)
        self.assertIn("final-test", state.lower())
        self.assertIn("locked", state.lower())
        self.assertIn("Real-money trading: locked", state)


if __name__ == "__main__":
    unittest.main()
