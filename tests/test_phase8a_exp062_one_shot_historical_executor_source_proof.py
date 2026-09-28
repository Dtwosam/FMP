from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp062-one-shot-historical-executor-source-proof.yml"
)


class Exp062OneShotHistoricalExecutorSourceProofTests(unittest.TestCase):
    def test_workflow_is_push_main_read_only_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp062-one-shot-historical-executor-source-proof",
            text,
        )
        self.assertIn("push:", text)
        self.assertIn("- main", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("actions: write", text)

    def test_workflow_pins_frozen_source_chain(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/exp062_historical_executor_activation_preflight.py": (
                "1d88fc3ad9dfce5ee61f1a5f9bdb304b3d7f8d1a"
            ),
            "src/fmp/discovery/exp062_historical_executor_activation_preflight_review.py": (
                "c540fb14c7048de2e6f368b0c96b51715c83e9a5"
            ),
            "src/fmp/discovery/exp062_historical_terminal_review_contract.py": (
                "fda2a45f74b101303467cf7b8527bec1bfc5e168"
            ),
            "src/fmp/discovery/exp062_historical_executor_activation_preflight_freeze.py": (
                "9cb660f06fc9da8a8d4927d8ff953413a6df13fe"
            ),
            "src/fmp/discovery/exp062_historical_executor_activation_preflight_runtime_freeze.py": (
                "9673e115eeb373c4881d36a8b5d91a2801cd8ad1"
            ),
            "src/fmp/discovery/exp062_historical_one_shot_executor_source.py": (
                "26ee48241550d6e52501fc901ab88aaa3f42e755"
            ),
            "src/fmp/discovery/exp062_historical_executor_activation_contract.py": (
                "35edfdfed85e52ebd723f2637060f4f102e7920b"
            ),
            "scripts/phase8a_exp062_historical_executor_activation_preflight.py": (
                "e91a2a2acb0e00d9d458ed5e15ecf746411caec7"
            ),
            ".github/workflows/phase8a-exp062-discovery.yml": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
            ".github/workflows/phase8a-exp062-historical-executor-activation-preflight.yml": (
                "d396cd27cabd2b8559d8d86121f9c59dc045c7ad"
            ),
            "requirements/exp061-discovery-run.txt": (
                "1ff32214dee10d877a067e750cd69ffad96d5fe5"
            ),
        }
        for path, blob in expected.items():
            with self.subTest(path=path):
                self.assertIn(f"git hash-object {path}", text)
                self.assertIn(blob, text)

    def test_workflow_rebuilds_frozen_evidence_without_dispatching(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "freeze_historical_executor_activation_preflight_runtime_evidence",
            text,
        )
        self.assertIn(
            "build_one_shot_historical_executor_source_contract",
            text,
        )
        self.assertIn(
            "actions/artifacts/10973597441/zip",
            text,
        )
        self.assertIn(
            "ee6e7ac2e8c18e1f8d276bba14ca942e20615143316ac185f4b814333804c2d5",
            text,
        )
        shell_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip().startswith("gh workflow run ")
        ]
        self.assertEqual(shell_lines, [])
        self.assertNotIn("actions: write", text)

    def test_workflow_requires_first_exact_main(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', text)
        self.assertIn('test "$(git rev-parse HEAD)" = "$GITHUB_SHA"', text)
        self.assertIn(
            'test "$(git rev-parse origin/main)" = "$GITHUB_SHA"',
            text,
        )
        self.assertIn('test -z "$(git status --porcelain)"', text)

    def test_workflow_proves_source_only_contract_and_all_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert contract["decision"] == "DEC-337"', text)
        self.assertIn(
            '"EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_AUTHORIZED_"',
            text,
        )
        self.assertIn(
            'assert contract["runtime_freeze_decision"] == "DEC-336"',
            text,
        )
        self.assertIn(
            'assert contract["terminal_review_decision"] == "DEC-334"',
            text,
        )
        self.assertIn(
            'assert contract["historical_result_attempt_count"] == 0',
            text,
        )
        self.assertIn(
            'assert contract["expected_target_run_number"] == 2',
            text,
        )
        self.assertIn(
            'assert contract["one_shot_historical_executor_source_authorized"] is True',
            text,
        )
        for field in (
            "historical_executor_available",
            "historical_result_dispatch_authorized",
            "historical_execute_mode_available",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIn(field, text)

    def test_workflow_persists_only_source_contract_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec338-one-shot-historical-executor-source-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "path: ${{ runner.temp }}/one-shot-historical-executor-source-contract.json",
            text,
        )
        self.assertNotIn("phase8a-exp062-cell-", text)
        self.assertNotIn("phase8a-exp062-aggregate-", text)


if __name__ == "__main__":
    unittest.main()
