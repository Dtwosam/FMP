from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2018-runtime-install-executor.yml"
)


class AnnualPatternCatalogue2018RuntimeInstallExecutorTests(unittest.TestCase):
    def test_executor_is_path_scoped_exact_first_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-runtime-install-executor",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("  contents: write", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_executor_pins_exact_dec549_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37232388248",
            "3cfd1b38217c97bbd590214394f171075d2d0f54",
            "11313752760",
            "94c9ce6e08f013cb9ff8f662c78b3fafc0ba902fa590e5b27e89751ddd9069a3",
            "23abea26faf35d775d4f11a41ccf280d10eb78fd",
            "a2a07003fdcef2a4202594286becc562ee6fc718",
            "4e4b931150e2d2358c2187b3b52608f701b2fb59",
        ):
            self.assertIn(value, text)

    def test_executor_mutates_only_frozen_gate_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual_pattern_catalogue_2018_runtime_authorization.py.disabled",
            text,
        )
        self.assertIn(
            "annual_pattern_catalogue_runtime_with_2018_authorization.py.disabled",
            text,
        )
        self.assertIn(
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
            text,
        )
        self.assertIn(
            "410180c34a9e3500bbbb42310a5253b993ac7785",
            text,
        )
        self.assertIn("git ls-files --others --exclude-standard", text)
        self.assertIn("expected-changed-files.txt", text)
        self.assertIn("git diff --cached --name-only", text)
        self.assertIn("git push origin HEAD:main", text)
        self.assertNotIn("git push --force", text)

    def test_executor_proves_gate_before_push_and_rechecks_main(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        proof = text.index("Prove installed runtime imports and exact run-380 gate")
        push = text.index("Commit and push exact install")
        self.assertLess(proof, push)
        self.assertIn("run_number=380", text)
        self.assertIn("run_number=381", text)
        self.assertIn('annual_segment_label="2017"', text)
        self.assertIn("run_number=379", text)
        self.assertIn('git rev-parse origin/main', text)

    def test_executor_builds_receipt_but_never_dispatches_annual_workflow(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2018_runtime_authorization_install_receipt.py",
            text,
        )
        self.assertIn('value["decision"] == "DEC-550"', text)
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
