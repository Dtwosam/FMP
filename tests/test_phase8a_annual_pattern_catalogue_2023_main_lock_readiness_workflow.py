from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase8a-annual-catalogue-2023-main-lock-readiness.yml"


class Annual2023MainLockReadinessWorkflowTests(unittest.TestCase):
    def test_only_read_only_push_or_manual_audit(self) -> None:
        w = WORKFLOW.read_text(encoding="utf-8")
        for expected in (
            "name: phase8a-annual-catalogue-2023-main-lock-readiness",
            "  push:", "      - main", "  workflow_dispatch:",
            "  contents: read", "  actions: read",
            'test "$GITHUB_RUN_ATTEMPT" = "1"',
            'test "$GITHUB_RUN_NUMBER" = "1"',
            'test "$GITHUB_REF" = "refs/heads/main"',
            'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"',
            "Fetch optional GitHub lock policy snapshots, fail closed",
            '"main_exclusive_lock_proven"] is False',
            '"annual_workflow_dispatch_authorized"] is False',
            '"dispatch_action_executed"] is False',
            '"trading_authorized"] is False',
            "if-no-files-found: error",
        ):
            self.assertIn(expected, w)
        for forbidden in (
            "  actions: write", "  contents: write",
            "gh workflow run ", "gh run rerun",
            "gh api --method POST", "gh api -X POST",
            "git push", "git commit", "broker order",
        ):
            self.assertNotIn(forbidden, w)

    def test_concrete_dec611_provenance(self) -> None:
        w = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "37778086874",
            "329e467a924ec00956505355f6cc1da7a589207c",
            "11550716769",
            "3a9412e93cabd68eb5f19e73bf2769fa610c081ea10ce5fa370fa2ba59bf1e93",
            "f1842fd06bdba200be7ab521ed2735a9429df4836408a18297888d9c3d6416a5",
            "5de4c3b87b64795c14f84211c838c9d9e1400c4c32b06d46946cb10a00e3a026",
            "e4c76ef4993f03d51200139dee708250cf40e80f",
            "001a7bfc2e689cf11a0992de86aeeb481647856d",
            "39b3898240b887a4f1418a9980fbe3b7b2c6f2d3",
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
            "dec612-main-lock-readiness.json",
        ):
            self.assertIn(required, w)

    def test_no_missing_api_visibility_can_unlock(self) -> None:
        w = WORKFLOW.read_text(encoding="utf-8")
        for path in (
            "branches/main/protection",
            "rules/branches/main",
            "rulesets?includes_parents=true",
        ):
            self.assertIn(path, w)
        self.assertEqual(w.count("printf 'null\\n'"), 3)
        self.assertIn("r[\"dispatch_blocked\"] is True", w)
        self.assertIn("r[\"expected_run_number\"] == 385", w)
        self.assertIn("len(rows) == 10", w)
        self.assertIn('not any(r["run_number"] >= 385 for r in rows)', w)


if __name__ == "__main__":
    unittest.main()
