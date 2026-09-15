from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

# Source-free closure guard for the audited Phase 6 outcome and still-locked later gates.
class Phase6AcceptanceStateTests(unittest.TestCase):
    def test_phase6_is_pass_with_rejected_ml_challengers_and_checkpoint_created(self) -> None:
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        evidence = (ROOT / "docs/phase6-ml-filter-evidence.md").read_text(encoding="utf-8")
        experiments = (ROOT / "docs/experiment-log.md").read_text(encoding="utf-8")

        self.assertIn("## Phase 6 — PASS", state)
        self.assertIn("DEC-032", state)
        self.assertIn("Phase 7 remains UNSTARTED", state)
        self.assertNotIn("## Phase 7 — ACTIVE", state)
        self.assertIn("Final-test touched: NO", state)
        self.assertIn("fmp-v1-phase6-models", state)
        self.assertIn("5d387b7ca93d04c498eb04c376e0dd92f1fe1953", state)
        self.assertIn("Real-money trading: locked", state)

        self.assertEqual(
            decision.count("## DEC-032 — Phase 6 statistical / ML filter experiment outcome and acceptance review"),
            1,
        )
        self.assertIn(
            "- DEC-032 — Phase 6 statistical / ML filter experiment outcome and acceptance review — APPROVED",
            decision,
        )
        self.assertIn("EXP-20260915-007", decision)
        self.assertIn("34966406652", decision)
        self.assertIn("NO_ML_CHALLENGER", decision)
        self.assertIn("Phase 6 is formally PASS", decision)

        self.assertIn("**Result:** PASS", evidence)
        self.assertIn("**Decision:** DEC-032 — APPROVED", evidence)
        self.assertIn(
            "**Checkpoint:** `fmp-v1-phase6-models` — CREATED at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`",
            evidence,
        )
        self.assertIn("**Final-test touched?: NO**", evidence)
        self.assertIn("run `34966406652`", evidence)
        self.assertIn("`10395810196`", evidence)
        self.assertIn("`36cb9f80ca043da23250669dd974036eb9fb985c3f7f9ffd7844b9d99c96073d`", evidence)
        self.assertIn("`10395670751`", evidence)
        self.assertIn("`0cf71a4d725fb1e609a512bb95aa13e4ad8771ae2b5864dd09e2833fe160a8d2`", evidence)
        self.assertIn("session_breakout", evidence)
        self.assertIn("volatility_breakout", evidence)
        self.assertGreaterEqual(evidence.count("NO_ML_CHALLENGER"), 2)
        self.assertIn("ALL_NULL_FIT_COLUMN", evidence)
        self.assertIn("minutes_since_new_york_open", evidence)
        self.assertIn("all six", evidence.lower())
        self.assertIn("net_return_beats_baseline", evidence)
        self.assertIn("validation remained unopened", evidence.lower())

        self.assertEqual(experiments.count("### EXP-20260915-007 — Phase 6 statistical / ML candidate filters"), 1)
        phase6_record = experiments.split(
            "### EXP-20260915-007 — Phase 6 statistical / ML candidate filters", 1
        )[1]
        self.assertIn("- Status: PASS", phase6_record)
        self.assertIn("- Final-test touched?: NO", phase6_record)
        self.assertIn("- Conclusion: REJECT", phase6_record)
        self.assertIn("34966406652", phase6_record)
        self.assertIn("NO_ML_CHALLENGER", phase6_record)


if __name__ == "__main__":
    unittest.main()
