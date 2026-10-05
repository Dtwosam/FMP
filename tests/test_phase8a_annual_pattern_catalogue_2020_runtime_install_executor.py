from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2020-runtime-install-executor.yml"
)


class AnnualPatternCatalogue2020RuntimeInstallExecutorTests(unittest.TestCase):
    def test_executor_is_path_scoped_exact_first_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2020-runtime-install-executor",
            text,
        )
        self.assertIn("  contents: write", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('"run_number": 2', text)

    def test_executor_pins_exact_dec571_artifact_and_fingerprint(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37327905209",
            "4ed1da1cdc5a8df1272fb1f06a803a57a8043427",
            "11352259131",
            "082c09ed64042f2c63252676be1d63aab6553c3cd92e3995256498ac4744b423",
            "0d617a5261a25d1fbdcc661fcc9518be63081ca442fb2ac068a2206f875e6939",
            "98043c92240d00a343087e4d5fcef56575ba319e",
            "7bcf5c20c5dce845901bca200e299b8dfeb364b3",
            "95092037ce42fa4c25c0c194c67c9a1f6cd40ab6",
        ):
            self.assertIn(value, text)

    def test_executor_distinguishes_current_and_target_runtime_blobs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        preinstall = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e"'
        )
        target = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "4e124365430672fa63825b272001937c60151644"'
        )
        self.assertEqual(text.count(preinstall), 2)
        self.assertEqual(text.count(target), 1)

    def test_executor_rechecks_exact_history_and_unconsumed_382(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381}",
            text,
        )
        self.assertIn('by_number[381]["conclusion"] == "success"', text)
        self.assertIn('row["run_number"] >= 382', text)

    def test_executor_proves_2020_gate_preserves_2019_and_rejects_383(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        proof = text.index("Prove installed runtime imports and exact run-382 gate")
        push = text.index("Commit and push exact install")
        self.assertLess(proof, push)
        self.assertIn('annual_segment_label="2020"', text)
        self.assertIn("run_number=382", text)
        self.assertIn("previous_annual_freeze_run_id=37310525635", text)
        self.assertIn('annual_segment_label="2019"', text)
        self.assertIn("run_number=381", text)
        self.assertIn("previous_annual_freeze_run_id=37237817538", text)
        self.assertIn("run_number=383", text)

    def test_executor_mutates_only_frozen_gate_and_runtime_without_dispatch(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual_pattern_catalogue_2020_runtime_authorization.py.disabled",
            text,
        )
        self.assertIn(
            "annual_pattern_catalogue_runtime_with_2020_authorization.py.disabled",
            text,
        )
        self.assertIn("695a50b418da752e1bd37d6302f209033ab611f5", text)
        self.assertIn("4e124365430672fa63825b272001937c60151644", text)
        self.assertIn("git diff --cached --name-only", text)
        self.assertIn("git push origin HEAD:main", text)
        self.assertNotIn("git push --force", text)
        self.assertIn('value["decision"] == "DEC-572"', text)
        self.assertIn('value["annual_workflow_dispatch_authorized"] is False', text)
        self.assertNotIn("gh workflow run ", text)


if __name__ == "__main__":
    unittest.main()
