from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2021-runtime-install-executor.yml"
)


class AnnualPatternCatalogue2021RuntimeInstallExecutorTests(unittest.TestCase):
    def test_executor_is_path_scoped_exact_first_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2021-runtime-install-executor",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("  contents: write", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_executor_pins_exact_dec584_artifact_and_fingerprint(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37490417862",
            "32927e836fcf6888a7f8567b28f5ba2fd0b48315",
            "11425666284",
            "d8e77b482e83250a56aafc99e4e6d2b81d94d1adb1227abbd1a0e49397e45ebe",
            "bffb48b795c1fc76f792aa8b00f5b8b94d23554cbc958bf3d11249eaa1058b04",
            "e0ec651509a6ff20afcf60029f413710faf3b232d5ba5924832ce2da5af071d2",
            "9ea8f4574ed1a85cbf0b95031a7450cc4f7fa705",
            "b088a8483ea555b28107462e88b8c16ec72b66b8",
            "9fc4fe670afd120b5cff90bca3b5ea4639260b02",
        ):
            self.assertIn(value, text)

    def test_executor_distinguishes_preinstall_and_target_runtime_blobs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        preinstall = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "4e124365430672fa63825b272001937c60151644"'
        )
        target = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"'
        )
        self.assertEqual(text.count(preinstall), 2)
        self.assertEqual(text.count(target), 1)

    def test_executor_rechecks_history_and_unconsumed_383(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382}",
            text,
        )
        self.assertIn('382: (37443770076, "success")', text)
        self.assertIn('row["run_number"] >= 383', text)

    def test_executor_mutates_only_frozen_gate_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual_pattern_catalogue_2021_runtime_authorization.py.disabled",
            text,
        )
        self.assertIn(
            "annual_pattern_catalogue_runtime_with_2021_authorization.py.disabled",
            text,
        )
        self.assertIn("cac68c905bedf3105aa7e766eaa968c87bff6ce9", text)
        self.assertIn("d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6", text)
        self.assertIn("git ls-files --others --exclude-standard", text)
        self.assertIn("expected-changed-files.txt", text)
        self.assertIn("git diff --cached --name-only", text)
        self.assertIn("git push origin HEAD:main", text)
        self.assertNotIn("git push --force", text)

    def test_executor_proves_2021_and_preserves_2020_before_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        proof = text.index("Prove installed runtime imports and exact run-383 gate")
        push = text.index("Commit and push exact install")
        self.assertLess(proof, push)
        self.assertIn('annual_segment_label="2021"', text)
        self.assertIn("run_number=383", text)
        self.assertIn("previous_annual_freeze_run_id=37443770076", text)
        self.assertIn('annual_segment_label="2020"', text)
        self.assertIn("run_number=382", text)
        self.assertIn("previous_annual_freeze_run_id=37310525635", text)
        self.assertIn("run_number=384", text)
        self.assertIn('git rev-parse origin/main', text)

    def test_executor_builds_receipt_but_never_dispatches(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2021_"
            "runtime_authorization_install_receipt.py",
            text,
        )
        self.assertIn('value["decision"] == "DEC-585"', text)
        self.assertIn('value["runtime_authorization_installed"] is True', text)
        self.assertIn('value["runtime_gate_active"] is True', text)
        self.assertIn('value["annual_workflow_dispatch_authorized"] is False', text)
        self.assertIn(
            '"READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2021_DISPATCH_PREFLIGHT"',
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
