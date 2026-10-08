from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2023-runtime-install-executor-recovery.yml"
)

class AnnualPatternCatalogue2023RuntimeInstallExecutorRecoveryTests(unittest.TestCase):
    def test_recovery_is_exact_first_push_installer(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2023-runtime-install-executor-recovery",
            text,
        )
        self.assertIn("  contents: write", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('test "$(git rev-parse origin/main)" = "$GITHUB_SHA"', text)
        self.assertNotIn("git push --force", text)

    def test_recovery_pins_failed_original_and_no_mutation(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37760015792",
            "113253869444",
            "27b888d96b629911a7471ff99bd0bb0d922c2292",
            "82e119153fefc6e663c2156115960bc9ceee2132",
        ):
            self.assertIn(value, text)
        self.assertIn(
            'assert steps["Validate concrete DEC-606 action"] == "failure"',
            text,
        )
        for name in (
            "Apply exact two-file 2023 runtime authorization install",
            "Prove installed runtime imports and exact run-385 gate",
            "Commit and push exact install",
            "Verify installed main and build DEC-607 receipt",
            "Upload immutable DEC-607 install evidence",
        ):
            self.assertIn(f'assert steps["{name}"] == "skipped"', text)
        self.assertIn("assert artifacts == []", text)

    def test_recovery_corrects_only_dec605_provenance_assertions(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'value["source_preflight_workflow_run_id"] == 37691460323',
            text,
        )
        self.assertIn(
            'value["source_preflight_artifact_id"] == 11513856300',
            text,
        )
        self.assertNotIn("37486048003", text)
        self.assertNotIn("11423396654", text)
        self.assertIn(
            'value["install_action_fingerprint_sha256"] == (',
            text,
        )
        self.assertIn(
            "585af9488ef0a2f6df018bc86051979fc68d151810a0575cc5091f051f18e763",
            text,
        )

    def test_recovery_preserves_exact_install_and_run385_boundary(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191", text)
        self.assertIn("f2734c7ea32355b1024d1097812578b23fc4409d", text)
        self.assertIn("0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3", text)
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383, 384}",
            text,
        )
        self.assertIn('row["run_number"] >= 385', text)
        self.assertIn('annual_segment_label="2023"', text)
        self.assertIn("run_number=385", text)
        self.assertIn("run_number=386", text)
        self.assertIn("git push origin HEAD:main", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)

    def test_recovery_builds_locked_dec607_receipt(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-607"', text)
        self.assertIn('value["runtime_authorization_installed"] is True', text)
        self.assertIn('value["runtime_gate_active"] is True', text)
        self.assertIn('value["install_action_consumed"] is True', text)
        self.assertIn(
            'value["source_authorization_protected_history_access_authorized"] '
            "is True",
            text,
        )
        self.assertIn('value["annual_workflow_dispatch_authorized"] is False', text)
        self.assertIn('value["run_386_or_later_authorized"] is False', text)
        self.assertIn('value["protected_history_access_authorized"] is False', text)
        self.assertIn(
            '"READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2023_DISPATCH_PREFLIGHT"',
            text,
        )

if __name__ == "__main__":
    unittest.main()
