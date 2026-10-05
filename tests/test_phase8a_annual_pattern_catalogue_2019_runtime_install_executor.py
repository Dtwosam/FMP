from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2019-runtime-install-executor.yml"
)


class AnnualPatternCatalogue2019RuntimeInstallExecutorTests(unittest.TestCase):
    def test_executor_is_path_scoped_exact_first_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2019-runtime-install-executor",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("  contents: write", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_executor_pins_exact_dec560_artifact_and_fingerprint(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37299664787",
            "bacb20c1d1541ac0b46076cef8ca9fe898559339",
            "11341025756",
            "dcd16ee2ddbdf9c5b17acfe6e79b54f1dbf6a38a839362ecc91a896f41520354",
            "c68df812693da1edfc5ab568afef50b2e70797a04b4c44cf22de7c3fc15bea35",
            "15cc0c8e3b93453ecaf6ba1dfd635133279acb6c",
            "5befb123f9d3f01cd4457c992c454c662a9f5b7d",
            "517b1756576b1eee47eb700ba8736fe730af26b1",
        ):
            self.assertIn(value, text)

    def test_executor_distinguishes_preinstall_and_target_runtime_blobs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        preinstall = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "410180c34a9e3500bbbb42310a5253b993ac7785"'
        )
        target = (
            'git hash-object src/fmp/discovery/annual_pattern_catalogue_runtime.py)" '
            '= "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e"'
        )
        self.assertEqual(text.count(preinstall), 2)
        self.assertEqual(text.count(target), 1)

    def test_executor_mutates_only_frozen_gate_and_runtime(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "annual_pattern_catalogue_2019_runtime_authorization.py.disabled",
            text,
        )
        self.assertIn(
            "annual_pattern_catalogue_runtime_with_2019_authorization.py.disabled",
            text,
        )
        self.assertIn(
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
            text,
        )
        self.assertIn(
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
            text,
        )
        self.assertIn("git ls-files --others --exclude-standard", text)
        self.assertIn("expected-changed-files.txt", text)
        self.assertIn("git diff --cached --name-only", text)
        self.assertIn("git push origin HEAD:main", text)
        self.assertNotIn("git push --force", text)

    def test_executor_rechecks_exact_annual_history_and_unconsumed_381(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "set(by_number) == {1, 376, 377, 378, 379, 380}",
            text,
        )
        self.assertIn('by_number[380]["conclusion"] == "success"', text)
        self.assertIn('row["run_number"] >= 381', text)

    def test_executor_proves_2019_gate_and_preserves_2018_route_before_push(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        proof = text.index("Prove installed runtime imports and exact run-381 gate")
        push = text.index("Commit and push exact install")
        self.assertLess(proof, push)
        self.assertIn('annual_segment_label="2019"', text)
        self.assertIn("run_number=381", text)
        self.assertIn("previous_annual_freeze_run_id=37237817538", text)
        self.assertIn('annual_segment_label="2018"', text)
        self.assertIn("run_number=380", text)
        self.assertIn("previous_annual_freeze_run_id=37227536041", text)
        self.assertIn("run_number=382", text)
        self.assertIn('git rev-parse origin/main', text)

    def test_executor_builds_receipt_but_never_dispatches_annual_workflow(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "phase8a_annual_pattern_catalogue_2019_"
            "runtime_authorization_install_receipt.py",
            text,
        )
        self.assertIn('value["decision"] == "DEC-561"', text)
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
