from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2016-run378-evidence-successor-recovery.yml"
)


class AnnualCatalogue2016Run378EvidenceSuccessorRecoveryTests(unittest.TestCase):
    def test_recovery_is_exact_one_shot_push_successor(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2016-run378-evidence-successor-recovery",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)

    def test_recovery_pins_exact_run378_and_dec532_provenance(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37206992367",
            "2524fde355349581c9440a172d0384c3cbce31ed",
            "37206963024",
            "11304832641",
            "sha256:7be017eeeedf1ccacb87182971a24914772821a7c77a5b9b17d73d320c3ce3e6",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "ad182ce30d32aff985558f3b2fd9370ca1141cc2",
            "788af8cad3074bcfdb0dd65c993fdd108293fda7",
            "bd2ecdead7cf560cc560c266cbf5d796350807b3",
        ):
            self.assertIn(value, text)
        self.assertIn('"run_number": 378', text)
        self.assertIn('"conclusion": "success"', text)
        self.assertIn("assert len(jobs) == 20", text)
        self.assertIn("assert len(artifacts) == 20", text)

    def test_recovery_only_dispatches_dec522_reviewer(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        reviewer = (
            "gh workflow run \"$workflow\""
        )
        self.assertEqual(text.count(reviewer), 1)
        self.assertIn(
            'workflow="phase8a-annual-catalogue-2016-run377-runtime-evidence.yml"',
            text,
        )
        self.assertNotIn(
            "gh workflow run phase8a-annual-pattern-catalogue.yml",
            text,
        )
        self.assertNotIn("-f annual_segment_label=", text)
        self.assertIn("  actions: write", text)
        self.assertIn("  contents: read", text)
        self.assertNotIn("contents: write", text)

    def test_recovery_requires_absent_prior_reviewer(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("dec522-auto-before.json", text)
        self.assertIn("dec522-manual-before.json", text)
        self.assertIn(
            "dec522-auto-before.json\")\" = \"0\"",
            text,
        )
        self.assertIn(
            "dec522-manual-before.json\")\" = \"0\"",
            text,
        )

    def test_recovery_verifies_binding_and_keeps_later_authority_locked(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-533"', text)
        self.assertIn('"runtime_evidence_bound": True', text)
        for field in (
            "run379_or_later_authorized",
            "next_segment_execution_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertIn(f'"{field}": False', text)
        self.assertIn(
            '"next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_EXECUTION_PREFLIGHT"',
            text,
        )


if __name__ == "__main__":
    unittest.main()
