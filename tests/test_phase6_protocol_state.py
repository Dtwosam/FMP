from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase6ProtocolStateTests(unittest.TestCase):
    def test_dec031_freezes_phase6_without_unlocking_later_gates(self) -> None:
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        spec = (
            ROOT
            / "docs/superpowers/specs/2026-09-15-phase6-statistical-ml-filter-design.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "DEC-031 — Phase 6 statistical / ML filter protocol — APPROVED",
            decision,
        )
        self.assertIn("## DEC-031 — Phase 6 statistical / ML filter protocol", decision)
        self.assertIn("**Status:** APPROVED", spec)
        self.assertIn("EXP-20260915-007", spec)
        self.assertIn("fit: 2015-01-01", decision.lower())
        self.assertIn("selection: 2019-01-01", decision.lower())
        self.assertIn("validation: 2021-01-01", decision.lower())
        self.assertIn("scikit-learn==1.9.1", decision)
        self.assertIn("0.75", decision)
        self.assertIn("0.50", decision)
        self.assertIn("0.25", decision)
        self.assertIn("no refit", decision.lower())

        self.assertIn("**Current phase:** Phase 7 — Walk-forward Evaluation", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — PASS", state)
        self.assertIn("EXP-20260915-007", state)
        self.assertIn("fmp-v1-phase5-features", state)
        self.assertIn("2024-01-01", state)
        self.assertIn("locked", state.lower())
        self.assertIn("real-money trading", state.lower())
        self.assertIn("## Phase 7 — PASS", state)
        self.assertNotIn("## Phase 8 — ACTIVE", state)


if __name__ == "__main__":
    unittest.main()
