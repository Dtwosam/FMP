from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2022-runtime-install-executor.yml"
)


class AnnualPatternCatalogue2022RuntimeInstallExecutorTests(unittest.TestCase):
    def test_executor_is_path_scoped_exact_first_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2022-runtime-install-executor",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("  contents: write", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_executor_pins_exact_dec595_artifact_and_fingerprint(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37618517412",
            "1351125bb903f7d7b636d945c4446ad815a2efb1",
            "11480463531",
            "6ff7996ac313a5437c0862cf58931a1246c5caf85251a6df4e0829602d9c07e8",
            "3352e4254ce62247d56c9fd16c9eb6972c3c7210dce7e08d6582f4c46c5e4a51",
            "2b99a8b914ee01d27902daa626d2ca01e31384e17de1b3a63b99fcbb1c90070c",
            "90fbc26b51d50d019e39c467d461bd7ba6b4f22b",
            "8f7891820c91bcac1fec5627c7b93ee967ab3754",
            "73f92f57f382589cc97b974e764cac271891ca25",
        ):
            self.assertIn(value, text)

    def test_executor_distinguishes_preinstall_and_target_runtime_blobs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        preinstall = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"'
        )
        target = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "f2734c7ea32355b1024d1097812578b23fc4409d"'
        )
        self.assertEqual(text.count(preinstall), 2)
        self.assertEqual(text.count(target), 1)

    def test_executor_rechecks_history_and_unconsumed_384(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383}",
            text,
        )
        self.assertIn('382: (37443770076, "success")', text)
        self.assertIn('383: (37531960014, "success")', text)
        self.assertIn('row["run_number"] >= 384', text)

    def test_executor_mutates_only_frozen_gate_and_runtime(self) -> None:
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
        self.assertIn("git ls-files --others --exclude-standard", text)
        self.assertIn("expected-changed-files.txt", text)
        self.assertIn("git diff --cached --name-only", text)
        self.assertIn("git push origin HEAD:main", text)
        self.assertNotIn("git push --force", text)

    def test_executor_proves_2022_and_preserves_2021_before_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        proof = text.index("Prove installed runtime imports and exact run-384 gate")
        push = text.index("Commit and push exact install")
        self.assertLess(proof, push)
        self.assertIn('annual_segment_label="2022"', text)
        self.assertIn("run_number=384", text)
        self.assertIn("previous_annual_freeze_run_id=37531960014", text)
        self.assertIn('annual_segment_label="2021"', text)
        self.assertIn("run_number=383", text)
        self.assertIn("previous_annual_freeze_run_id=37443770076", text)
        self.assertIn("run_number=385", text)
        self.assertIn('git rev-parse origin/main', text)

    def test_executor_builds_receipt_but_never_dispatches(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2022_"
            "runtime_authorization_install_receipt.py",
            text,
        )
        self.assertIn('value["decision"] == "DEC-596"', text)
        self.assertIn('value["runtime_authorization_installed"] is True', text)
        self.assertIn('value["runtime_gate_active"] is True', text)
        self.assertIn('value["install_action_consumed"] is True', text)
        self.assertIn('value["annual_workflow_dispatch_authorized"] is False', text)
        self.assertIn('value["run_385_or_later_authorized"] is False', text)
        self.assertIn('value["protected_history_access_authorized"] is False', text)
        self.assertIn('value["cross_year_comparison_authorized"] is False', text)
        self.assertIn(
            '"READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2022_DISPATCH_PREFLIGHT"',
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

    def test_executor_has_no_stale_2020_proof_or_prior_decisions(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn('annual_segment_label="2020"', text)
        self.assertNotIn("DEC-585", text)
        self.assertNotIn("DEC-584", text)


if __name__ == "__main__":
    unittest.main()
