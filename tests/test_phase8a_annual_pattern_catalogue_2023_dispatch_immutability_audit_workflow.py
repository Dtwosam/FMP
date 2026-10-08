from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase8a-annual-catalogue-2023-dispatch-immutability-audit.yml"


class AnnualCatalogue2023DispatchImmutabilityAuditWorkflowTests(unittest.TestCase):
    def test_first_push_read_only_without_action_permissions(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "name: phase8a-annual-catalogue-2023-dispatch-immutability-audit",
            "  push:",
            "      - main",
            "  contents: read",
            "  actions: read",
            'test "$GITHUB_RUN_NUMBER" = "1"',
            'test "$GITHUB_RUN_ATTEMPT" = "1"',
            'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"',
            '"dispatch_blocked"] is True',
            '"annual_workflow_dispatch_authorized"] is False',
            '"dispatch_action_executed"] is False',
            '"trading_authorized"] is False',
            "if-no-files-found: error",
        ):
            self.assertIn(required, text)
        for forbidden in (
            "  actions: write", "  contents: write",
            "workflow_dispatch:", "schedule:", "gh workflow run ",
            "gh run rerun", "git push", "git commit", "gh api --method POST",
        ):
            self.assertNotIn(forbidden, text)

    def test_audit_pins_verified_dec610_and_runtime_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "37773291427",
            "58d17adbaf2238b6b774cb69f0434259984d1cb7",
            "11547739610",
            "e093274fc52e8e5abdb1bd08455f0fcdb2374bab15f3d507abfea59b91a60143",
            "07f391338fe3d20c5e823f72a14cecdf454aec87a6e7638bdd8774f3c9b4b063",
            "176cadda04eac41454d401bbabeeadc91e701307bbdd94054890ae89bf65689e",
            "39b3898240b887a4f1418a9980fbe3b7b2c6f2d3",
            "f973680f11eeefa69c243c306fed5ecf70411a1c",
            "60923763b844b8a1348cbfcf2612b739b8c7c28a",
            "b7f55dd68d5054c472b4e070521c411c02a4da3c",
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "dec611-2023-dispatch-immutability-audit.json",
            "EXCLUSIVE_MAIN_LOCK_OR_REAUTHORIZED_IMMUTABLE_REF_DESIGN",
        ):
            self.assertIn(required, text)

    def test_year385_stays_unconsumed(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 10", text)
        self.assertIn('assert not any(r.get("run_number", 0) >= 385 for r in rows)', text)
        self.assertIn('value["expected_run_number"] == 385', text)
        self.assertIn('value["expected_run_attempt"] == 1', text)
        self.assertIn("annual-catalogue-2023-dec611-dispatch-immutability-audit-", text)


if __name__ == "__main__":
    unittest.main()
