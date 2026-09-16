from __future__ import annotations

from pathlib import Path
import unittest


PLAN = Path("docs/superpowers/plans/2026-09-15-phase8-live-shadow.md")


def _task(text: str, number: int) -> str:
    marker = f"### Task {number}:"
    start = text.index(marker)
    next_marker = f"### Task {number + 1}:"
    end = text.find(next_marker, start)
    return text[start:] if end == -1 else text[start:end]


class Phase8OperatorHandoffTests(unittest.TestCase):
    def test_operator_handoff_commands_match_implemented_cli(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        task17 = _task(text, 17)
        self.assertIn(
            "python scripts/phase8_shadow.py qualify --out evidence/phase8/qualification",
            task17,
        )

        task18 = _task(text, 18)
        self.assertIn("python scripts/phase8_shadow.py build-reference \\", task18)
        self.assertIn("--dataset-root <accepted-phase2-dataset-root> \\", task18)
        self.assertIn(
            "--processed-manifest <accepted-usdjpy-processed-manifest> \\",
            task18,
        )
        self.assertNotIn("python scripts/phase8_shadow.py reference \\", task18)
        self.assertIn(
            "python scripts/phase8_shadow.py register \\",
            task18,
        )

        task19 = _task(text, 19)
        self.assertIn(
            "python scripts/phase8_shadow.py run --campaign-dir evidence/phase8/campaign",
            task19,
        )
        self.assertIn(
            "python scripts/phase8_shadow.py replay --segment-dir evidence/phase8/campaign/<segment>",
            task19,
        )
        self.assertNotIn(
            "python scripts/phase8_shadow.py replay --campaign-dir",
            task19,
        )

        task20 = _task(text, 20)
        self.assertIn(
            "python scripts/phase8_shadow.py review --campaign-dir evidence/phase8/campaign",
            task20,
        )


if __name__ == "__main__":
    unittest.main()
