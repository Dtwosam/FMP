from __future__ import annotations

import re
import unittest
from pathlib import Path


WORKFLOW = Path(".github/workflows/phase7-walk-forward.yml")


class Phase7WalkForwardWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_read_only_with_only_authorization_inputs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        lower = text.lower()
        self.assertIn("name: phase7-walk-forward", text)
        self.assertIn("workflow_dispatch:", text)
        for trigger in ("pull_request:", "push:", "schedule:"):
            self.assertNotIn(trigger, text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("id-token", lower)

        for name in ("candidate:", "stage1_artifact_id:", "stage1_zip_sha256:"):
            self.assertIn(name, text)
        self.assertIn("type: choice", text)
        self.assertIn("session_breakout", text)
        self.assertIn("volatility_breakout", text)
        self.assertGreaterEqual(text.count("required: true"), 3)
        for forbidden in (
            "--start",
            "--end",
            "--buffer-pips",
            "--range-multiplier",
            "--timeframe",
            "--symbol",
            "--allow-final",
            "dukascopy",
            "fmp-raw",
            "supabase",
            "oanda",
            "broker",
            "demo trading",
            "real-money",
        ):
            self.assertNotIn(forbidden, lower)

    def test_stage1_artifact_digest_and_pass_are_verified_before_phase2_or_stage2(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        auth_pos = text.index("Verify Stage 1 PASS authorization")
        phase2_pos = text.index("Download and verify accepted Phase 2 USDJPY artifact")
        stage2_pos = text.index("scripts/phase7_walk_forward.py")
        self.assertLess(auth_pos, phase2_pos)
        self.assertLess(auth_pos, stage2_pos)

        auth = text[auth_pos:phase2_pos]
        for required in (
            "STAGE1_ARTIFACT_ID",
            "EXPECTED_STAGE1_ZIP_SHA256",
            "actions/artifacts/${STAGE1_ARTIFACT_ID}/zip",
            "sha256sum",
            "verify_stage1_evidence",
            "candidate_id=expected_candidate",
            "STAGE1_PASS",
            "manifest_sha256",
            "EXP-20260915-008",
            "5d387b7ca93d04c498eb04c376e0dd92f1fe1953",
            "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
        ):
            self.assertIn(required, auth)

    def test_workflow_pins_accepted_phase2_identity_after_authorization(self) -> None:
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

    def test_workflow_double_executes_complete_stage2_and_uploads_only_first_copy(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("scripts/phase7_walk_forward.py"), 2)
        self.assertIn(".phase7-stage2-a", text)
        self.assertIn(".phase7-stage2-b", text)
        self.assertIn("find", text)
        self.assertIn("diff", text)
        self.assertIn("cmp", text)
        for name in ("windows.json", "result.json", "manifest.json"):
            self.assertIn(name, text)
        self.assertIn("actions/upload-artifact@v6", text)
        self.assertRegex(text, r"path:\s*\.phase7-stage2-a/\$\{\{ inputs\.candidate \}\}")
        self.assertNotRegex(text, r"path:\s*\.phase7-stage2-b/")

    def test_evidence_audit_requires_exact_seven_windows_costs_and_bounds(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        required_windows = (
            ("2025-Q1", "2025-01-01T00:00:00Z", "2025-04-01T00:00:00Z"),
            ("2025-Q2", "2025-04-01T00:00:00Z", "2025-07-01T00:00:00Z"),
            ("2025-Q3", "2025-07-01T00:00:00Z", "2025-10-01T00:00:00Z"),
            ("2025-Q4", "2025-10-01T00:00:00Z", "2026-01-01T00:00:00Z"),
            ("2026-Q1", "2026-01-01T00:00:00Z", "2026-04-01T00:00:00Z"),
            ("2026-Q2", "2026-04-01T00:00:00Z", "2026-07-01T00:00:00Z"),
            ("2026-partial-Q3", "2026-07-01T00:00:00Z", "2026-08-21T00:00:00Z"),
        )
        for name, start, end in required_windows:
            self.assertIn(name, text)
            self.assertIn(start, text)
            self.assertIn(end, text)

        for required in (
            "NOT_APPLICABLE_FIXED_RULE",
            "{'0.2', '0.5', '1.0'}",
            "windows_by_slippage",
            "aggregate_by_slippage",
            "opened_partition_keys",
            "warmup_range",
            "stage1_identity",
            "PHASE7_PROMOTE_TO_SHADOW_DESIGN",
            "PHASE7_COMPLETE_REJECT",
            "len(rows) != 7",
            "actual_windows != expected_windows",
            "2026-08-21T00:00:00Z",
        ):
            self.assertIn(required, text)

    def test_stage2_audit_binds_stage1_manifest_identity_and_constituent_digests(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "stage1_manifest_sha256",
            "stage1_identity",
            "manifest_sha256",
            "sha256",
            "size_bytes",
            "EXP-20260915-008",
            "GITHUB_SHA",
        ):
            self.assertIn(required, text)
        self.assertRegex(text, r"stage1_identity\['candidate_id'\]\s*==\s*expected_candidate")


if __name__ == "__main__":
    unittest.main()
