from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Phase4ExperimentRegistryTests(unittest.TestCase):
    def test_registry_and_outcome_statuses_are_complete(self) -> None:
        registry = (ROOT / "docs/experiment-log.md").read_text(encoding="utf-8")
        vol = (ROOT / "docs/phase4-volatility-breakout-evidence.md").read_text(encoding="utf-8")
        sweep = (ROOT / "docs/phase4-session-sweep-rejection-evidence.md").read_text(encoding="utf-8")
        for number in range(1, 7):
            exp_id = f"EXP-20260914-{number:03d}"
            self.assertEqual(registry.count(f"### {exp_id} —"), 1, exp_id)
        self.assertGreaterEqual(registry.count("Final-test touched?: NO"), 6)
        self.assertIn("**Outcome decision:** DEC-025 — APPROVED", vol)
        self.assertIn("**Outcome decision:** DEC-027 — APPROVED", sweep)
        self.assertNotIn("pending evidence-closure merge", vol)
        self.assertNotIn("pending evidence-closure merge", sweep)

if __name__ == "__main__":
    unittest.main()
