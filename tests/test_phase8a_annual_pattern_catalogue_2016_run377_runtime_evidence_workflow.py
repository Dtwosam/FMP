from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2016-run377-runtime-evidence.yml"
)


class AnnualCatalogue2016Run377RuntimeEvidenceWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_successful_run378_reviewer(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2016-run378-runtime-evidence",
            text,
        )
        self.assertIn("  workflow_run:", text)
        self.assertIn("      - phase8a-annual-pattern-catalogue", text)
        self.assertIn(
            "github.event.workflow_run.run_number == 378",
            text,
        )
        self.assertIn(
            "github.event.workflow_run.conclusion == 'success'",
            text,
        )
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("  contents: write", text)
        self.assertNotIn("  actions: write", text)
        self.assertIn("  workflow_dispatch:", text)
        self.assertIn("target_run_id:", text)
        self.assertIn("target_head_sha:", text)
        self.assertIn("target_run_number:", text)
        self.assertNotIn("  push:", text)

    def test_workflow_pins_exact_dec522_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for blob in (
            "dcc4d71990e113acc25fd607ef9919734f2c0731",
            "9acc6bc7ce284dd7e82f037fa999d2fee02af44a",
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "1a4d9c975f79140f9d7e2173a4e102e4d07b2a6c",
            "1ff32214dee10d877a067e750cd69ffad96d5fe5",
        ):
            self.assertIn(blob, text)

    def test_workflow_requires_unique_digest_verified_dec521_receipt(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2016-dec521-run378-dispatch-",
            text,
        )
        self.assertIn(
            "if length == 1 then .[0].id else empty end",
            text,
        )
        self.assertIn(
            "if length == 1 then .[0].digest else empty end",
            text,
        )
        self.assertIn('case "$artifact_digest" in sha256:*)', text)
        self.assertIn('test "$actual_sha" = "$expected_sha"', text)
        self.assertIn(
            "dec521-run378-dispatch-receipt.json",
            text,
        )
        self.assertIn(
            "test \"$(jq -r '.run_id' "
            "\"$RUNNER_TEMP/dec521-receipt.json\")\" = \"$TARGET_RUN_ID\"",
            text,
        )

    def test_workflow_verifies_exact_freeze_and_runs_dec522(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'expected_name="phase8a-annual-catalogue-freeze-2016-$TARGET_HEAD_SHA"',
            text,
        )
        self.assertIn("annual-freeze.json", text)
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2016_run377_evidence_review.py",
            text,
        )
        self.assertIn('assert binding["decision"] == "DEC-522"', text)
        self.assertIn('assert binding["run_number"] == 378', text)
        self.assertIn('assert binding["run_attempt"] == 1', text)
        self.assertIn('assert binding["run_conclusion"] == "success"', text)
        self.assertIn('assert binding["runtime_evidence_bound"] is True', text)

    def test_workflow_has_no_dispatch_mutation_or_trading_surface(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for forbidden in (
            "gh workflow run ",
            "gh run rerun",
            "git push",
            "git commit",
            "git add ",
            "gh api --method POST",
            "gh api --method PUT",
            "gh api --method PATCH",
            "order_send(",
            "MetaTrader5",
            "mt5.",
            "broker_order",
            "live_order(",
        ):
            self.assertNotIn(forbidden, text)

    def test_binding_upload_keeps_2017_locked(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual-catalogue-2016-dec522-runtime-binding-",
            text,
        )
        for field in (
            "next_segment_execution_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertIn(f'"{field}",', text)
        self.assertIn("assert binding[field] is False, field", text)


if __name__ == "__main__":
    unittest.main()
