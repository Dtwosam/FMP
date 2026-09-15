from __future__ import annotations

import re
import unittest
from pathlib import Path


WORKFLOW = Path(".github/workflows/phase7-final-gate.yml")


class Phase7FinalGateWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_read_only_exact_two_candidate_matrix(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        lower = text.lower()
        self.assertIn("name: phase7-final-gate", text)
        self.assertRegex(text, r"on:\s*\n\s*workflow_dispatch:\s*\n")
        for trigger in ("pull_request:", "push:", "schedule:"):
            self.assertNotIn(trigger, text)
        self.assertNotIn("inputs:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("id-token", lower)
        self.assertEqual(len(re.findall(r"^\s*- candidate:\s*", text, re.MULTILINE)), 2)
        self.assertIn("candidate: session_breakout", text)
        self.assertIn("candidate: volatility_breakout", text)
        for forbidden in (
            "phase5",
            "dukascopy",
            "fmp-raw",
            "supabase",
            "oanda",
            "broker",
            "demo trading",
            "real-money",
            "--start",
            "--end",
            "--buffer-pips",
            "--range-multiplier",
            "--timeframe",
            "--symbol",
            "--allow-final",
        ):
            self.assertNotIn(forbidden, lower)

    def test_workflow_pins_only_accepted_phase2_usdjpy_identity(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "10327600628",
            "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72",
            "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
            "fmp-canonical-1m-v1",
            "USDJPY",
        ):
            self.assertIn(value, text)
        self.assertIn("actions/artifacts/${ARTIFACT_ID}/zip", text)
        self.assertGreaterEqual(text.count("sha256sum"), 2)

    def test_workflow_double_executes_compares_complete_file_sets_and_uploads_first_copy(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("scripts/phase7_final_gate.py"), 2)
        self.assertIn(".phase7-stage1-a", text)
        self.assertIn(".phase7-stage1-b", text)
        self.assertIn("find", text)
        self.assertIn("diff", text)
        self.assertIn("cmp", text)
        for name in ("stage1.json", "result.json", "manifest.json"):
            self.assertIn(name, text)
        self.assertIn("actions/upload-artifact@v6", text)
        self.assertRegex(text, r"path:\s*\.phase7-stage1-a/\$\{\{ matrix\.candidate \}\}")
        self.assertNotRegex(text, r"path:\s*\.phase7-stage1-b/")

    def test_workflow_audit_fails_closed_on_wrong_identity_or_non_2024_coverage(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "EXP-20260915-008",
            "5d387b7ca93d04c498eb04c376e0dd92f1fe1953",
            "2023-12-25T00:00:00Z",
            "2024-01-01T00:00:00Z",
            "2025-01-01T00:00:00Z",
            "STAGE1_PASS",
            "STAGE1_REJECT",
            "NOT_APPLICABLE_FIXED_RULE",
            "0.2",
            "0.5",
            "1.0",
            "opened_partition_keys",
            "scored_range",
            "warmup_range",
            "sha256",
            "size_bytes",
        ):
            self.assertIn(required, text)
        self.assertRegex(text, r">=\s*['\"]2025-01['\"]")
        self.assertIn("GITHUB_SHA", text)


if __name__ == "__main__":
    unittest.main()
