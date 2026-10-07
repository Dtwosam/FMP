from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-annual-catalogue-2022-runtime-install-executor-recovery.yml"
)


class AnnualPatternCatalogue2022RuntimeInstallExecutorRecoveryTests(
    unittest.TestCase
):
    def test_recovery_is_exact_first_push_with_write_only_for_install(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-runtime-install-executor-recovery",
            text,
        )
        self.assertIn("  contents: write", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('test "$(git rev-parse origin/main)" = "$GITHUB_SHA"', text)
        self.assertIn(
            'git merge-base --is-ancestor "$FAILED_DEC596_HEAD_SHA" "$GITHUB_SHA"',
            text,
        )

    def test_recovery_pins_failed_original_and_proves_no_mutation(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37631563591",
            "112826873575",
            "f5b738ab05ea03e10ffc066905a7e01dbd1924cc",
            "d4f380faf688dfc833a76d7094ff9bebe8f43c8d",
        ):
            self.assertIn(value, text)
        self.assertIn(
            'assert steps["Validate concrete DEC-595 action"] == "failure"',
            text,
        )
        for step in (
            "Apply exact two-file 2022 runtime authorization install",
            "Prove installed runtime imports and exact run-384 gate",
            "Commit and push exact install",
            "Verify installed main and build DEC-596 receipt",
            "Upload immutable DEC-596 install evidence",
        ):
            self.assertIn(f'assert steps["{step}"] == "skipped"', text)
        self.assertIn("assert artifacts == []", text)

    def test_recovery_pins_exact_dec595_and_correct_dec594_provenance(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37618517412",
            "1351125bb903f7d7b636d945c4446ad815a2efb1",
            "11480463531",
            "6ff7996ac313a5437c0862cf58931a1246c5caf85251a6df4e0829602d9c07e8",
            "3352e4254ce62247d56c9fd16c9eb6972c3c7210dce7e08d6582f4c46c5e4a51",
            "2b99a8b914ee01d27902daa626d2ca01e31384e17de1b3a63b99fcbb1c90070c",
        ):
            self.assertIn(value, text)
        self.assertIn(
            'assert value["source_preflight_workflow_run_id"] == 37616348059',
            text,
        )
        self.assertIn(
            'assert value["source_preflight_artifact_id"] == 11480120937',
            text,
        )
        self.assertNotIn(
            'assert value["source_preflight_workflow_run_id"] == 37486048003',
            text,
        )
        self.assertNotIn(
            'assert value["source_preflight_artifact_id"] == 11423396654',
            text,
        )

    def test_recovery_rechecks_unconsumed_run384_and_exact_preinstall(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        self.assertIn('383: (37531960014, "success")', text)
        self.assertIn('row["run_number"] >= 384', text)
        preinstall = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"'
        )
        self.assertEqual(text.count(preinstall), 2)
        self.assertIn(
            "test ! -e src/fmp/discovery/"
            "annual_pattern_catalogue_2022_runtime_authorization.py",
            text,
        )

    def test_recovery_applies_only_frozen_install_and_never_dispatches(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual_pattern_catalogue_2022_runtime_authorization.py.disabled",
            text,
        )
        self.assertIn(
            "annual_pattern_catalogue_runtime_with_2022_authorization.py.disabled",
            text,
        )
        self.assertIn("ecb21dc7106e7bd43447f4135c3a696251a75e05", text)
        self.assertIn("f2734c7ea32355b1024d1097812578b23fc4409d", text)
        self.assertIn("expected-changed-files.txt", text)
        self.assertIn("git diff --cached --name-only", text)
        self.assertIn("git push origin HEAD:main", text)
        self.assertNotIn("git push --force", text)
        self.assertIn('annual_segment_label="2022"', text)
        self.assertIn("run_number=384", text)
        self.assertIn('annual_segment_label="2021"', text)
        self.assertIn("run_number=383", text)
        self.assertIn("run_number=385", text)
        self.assertIn('value["decision"] == "DEC-596"', text)
        self.assertIn('value["runtime_authorization_installed"] is True', text)
        self.assertIn('value["runtime_gate_active"] is True', text)
        self.assertIn('value["annual_workflow_dispatch_authorized"] is False', text)
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
