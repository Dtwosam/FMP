from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2017-runtime-install-executor.yml"
)


class AnnualPatternCatalogue2017RuntimeInstallExecutorTests(unittest.TestCase):
    def test_executor_is_path_scoped_exact_first_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2017-runtime-install-executor",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("  contents: write", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_executor_pins_exact_dec538_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37219170862",
            "7dfcf6cacca63719ac40a88858c69895fc68670b",
            "11310165235",
            "e210042872cbe191f4383fcba4a6ac9305fbdeb96acaed32d46e034acff1681d",
            "b6fd22c5eca66ca373d0479e63af51cd39068ed9",
            "c3662046efc7daf2c00637066aa78c885b85fa8e",
            "62faa349bd8768990f5af03a25082bdfc17d1706",
        ):
            self.assertIn(value, text)

    def test_executor_mutates_only_frozen_gate_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual_pattern_catalogue_2017_runtime_authorization.py.disabled",
            text,
        )
        self.assertIn(
            "annual_pattern_catalogue_runtime_with_2017_authorization.py.disabled",
            text,
        )
        self.assertIn(
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
            text,
        )
        self.assertIn(
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
            text,
        )
        self.assertIn("git ls-files --others --exclude-standard", text)
        self.assertIn("expected-changed-files.txt", text)
        self.assertIn("git diff --cached --name-only", text)
        self.assertIn("git push origin HEAD:main", text)
        self.assertNotIn("git push --force", text)

    def test_executor_proves_gate_before_push_and_rechecks_main(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        proof = text.index("Prove installed runtime imports and exact run-379 gate")
        push = text.index("Commit and push exact install")
        self.assertLess(proof, push)
        self.assertIn("run_number=379", text)
        self.assertIn("run_number=380", text)
        self.assertIn('git rev-parse origin/main', text)

    def test_executor_builds_receipt_but_never_dispatches_annual_workflow(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2017_runtime_authorization_install_receipt.py",
            text,
        )
        self.assertIn('value["decision"] == "DEC-539"', text)
        self.assertIn(
            'value["runtime_authorization_installed"] is True',
            text,
        )
        self.assertIn('value["runtime_gate_active"] is True', text)
        self.assertIn(
            'value["annual_workflow_dispatch_authorized"] is False',
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
