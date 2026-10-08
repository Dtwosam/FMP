from __future__ import annotations

from pathlib import Path
import unittest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2023-runtime-install-executor.yml"
)

class AnnualPatternCatalogue2023RuntimeInstallExecutorTests(unittest.TestCase):
    def test_executor_is_path_scoped_exact_first_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2023-runtime-install-executor",
            text,
        )
        self.assertIn("  contents: write", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_executor_pins_exact_dec606_artifact_and_fingerprint(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37693786078",
            "14478b3d8e6026a834d4e5d5d34bdf0b0d0dfd30",
            "11514552382",
            "9ef098ec8f9e91ad640ce1e08c94b0942b5a18115a4b0257269845688d06fdde",
            "585af9488ef0a2f6df018bc86051979fc68d151810a0575cc5091f051f18e763",
            "927c05ce7d59782a10e148d7345a3a93bedc6587e3acb0632c9dcd531eb262b4",
            "42477932452d07a445d7c85650a01b3692fa755c",
            "a8cc32730ab16e9d876725363ddc6d53fa09890a",
            "0442532abc272e2046b3722560ac3e687dba919f",
        ):
            self.assertIn(value, text)

    def test_executor_distinguishes_preinstall_and_target_runtime_blobs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        preinstall = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "f2734c7ea32355b1024d1097812578b23fc4409d"'
        )
        target = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3"'
        )
        self.assertGreaterEqual(text.count(preinstall), 2)
        self.assertEqual(text.count(target), 1)
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2023_runtime_authorization.py",
            text,
        )

    def test_executor_rechecks_history_and_unconsumed_385(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383, 384}",
            text,
        )
        self.assertIn('383: (37531960014, "success")', text)
        self.assertIn('384: (37663157285, "success")', text)
        self.assertIn('row["run_number"] >= 385', text)

    def test_executor_mutates_only_frozen_gate_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual_pattern_catalogue_2023_runtime_authorization.py.disabled",
            text,
        )
        self.assertIn(
            "annual_pattern_catalogue_runtime_with_2023_authorization.py.disabled",
            text,
        )
        self.assertIn("cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191", text)
        self.assertIn("0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3", text)
        self.assertIn("git ls-files --others --exclude-standard", text)
        self.assertIn("expected-changed-files.txt", text)
        self.assertIn("git diff --cached --name-only", text)
        self.assertIn("git push origin HEAD:main", text)
        self.assertNotIn("git push --force", text)

    def test_executor_proves_2023_and_preserves_prior_years_before_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        proof = text.index("Prove installed runtime imports and exact run-385 gate")
        push = text.index("Commit and push exact install")
        self.assertLess(proof, push)
        self.assertIn('annual_segment_label="2023"', text)
        self.assertIn("run_number=385", text)
        self.assertIn("previous_annual_freeze_run_id=37663157285", text)
        self.assertIn('annual_segment_label="2022"', text)
        self.assertIn("run_number=384", text)
        self.assertIn("previous_annual_freeze_run_id=37531960014", text)
        self.assertIn('annual_segment_label="2021"', text)
        self.assertIn("run_number=383", text)
        self.assertIn("previous_annual_freeze_run_id=37443770076", text)
        self.assertIn("run_number=386", text)

    def test_executor_builds_receipt_but_never_dispatches(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2023_"
            "runtime_authorization_install_receipt.py",
            text,
        )
        self.assertIn('value["decision"] == "DEC-607"', text)
        self.assertIn(
            'value["source_authorization_protected_history_access_authorized"] '
            "is True",
            text,
        )
        self.assertIn('value["runtime_authorization_installed"] is True', text)
        self.assertIn('value["runtime_gate_active"] is True', text)
        self.assertIn('value["install_action_consumed"] is True', text)
        self.assertIn('value["annual_workflow_dispatch_authorized"] is False', text)
        self.assertIn('value["run_386_or_later_authorized"] is False', text)
        self.assertIn('value["protected_history_access_authorized"] is False', text)
        self.assertIn('value["cross_year_comparison_authorized"] is False', text)
        self.assertIn(
            '"READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2023_DISPATCH_PREFLIGHT"',
            text,
        )
        for forbidden in (
            "gh workflow run ",
            "gh run rerun",
            "rerun-failed-jobs",
            "order_send(",
            "MetaTrader5",
            "mt5.",
            "broker_order",
            "live_order(",
        ):
            self.assertNotIn(forbidden, text)

if __name__ == "__main__":
    unittest.main()
