from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase8a-annual-catalogue-2023-run385-dispatch.yml"


class AnnualCatalogue2023Run385DispatchWorkflowTests(unittest.TestCase):
    def test_one_shot_main_only_with_bounded_actions_write(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "name: phase8a-annual-catalogue-2023-run385-dispatch",
            "  push:",
            "      - main",
            "  contents: read",
            "  actions: write",
            'test "$GITHUB_REPOSITORY" = "Dtwosam/FMP"',
            'test "$GITHUB_EVENT_NAME" = "push"',
            'test "$GITHUB_REF" = "refs/heads/main"',
            'test "$GITHUB_RUN_NUMBER" = "1"',
            'test "$GITHUB_RUN_ATTEMPT" = "1"',
            'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"',
            'test "$(jq -r \'.commit.sha\' "$RUNNER_TEMP/main-before-dispatch.json")" = "$GITHUB_SHA"',
            "git diff --name-only",
        ):
            self.assertIn(required, text)
        for forbidden in ("contents: write", "workflow_dispatch:", "schedule:", "gh run rerun",
                          "git push", "git commit", "broker_mutation_authorized: True"):
            self.assertNotIn(forbidden, text)

    def test_dec610_exact_artifact_and_source_pins(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37773291427",
            "58d17adbaf2238b6b774cb69f0434259984d1cb7",
            "11547739610",
            "e093274fc52e8e5abdb1bd08455f0fcdb2374bab15f3d507abfea59b91a60143",
            "07f391338fe3d20c5e823f72a14cecdf454aec87a6e7638bdd8774f3c9b4b063",
            "176cadda04eac41454d401bbabeeadc91e701307bbdd94054890ae89bf65689e",
            "37770601661",
            "11547430955",
            "7d40ccaf79270162dd96a8a1e7024dd94c3a72b7",
            "60923763b844b8a1348cbfcf2612b739b8c7c28a",
            "b7f55dd68d5054c472b4e070521c411c02a4da3c",
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "dec610-2023-dispatch-action-preflight.json",
        ):
            self.assertIn(value, text)
        self.assertIn("assert hashlib.sha256(canonical).hexdigest()", text)
        self.assertIn('assert artifact["digest"] == os.environ["DEC610_ARTIFACT_DIGEST"]', text)

    def test_exact_single_dispatch_and_run385_binding(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(
            len(re.findall(r"(?m)^\s+gh workflow run phase8a-annual-pattern-catalogue\.yml", text)),
            1,
        )
        for required in (
            "-f annual_segment_label=2023",
            "-f previous_annual_freeze_run_id=37663157285",
            'assert len(by_number) == 10 and set(by_number) == set(expected)',
            'assert not any(r["run_number"] >= 385 for r in rows)',
            'r.get("run_number") == 385',
            'r.get("run_attempt") == 1',
            'r.get("head_sha") == os.environ["GITHUB_SHA"]',
            '"dispatch_submitted": True',
            '"result_claimed": False',
            '"run_386_or_later_authorized": False',
            '"next_segment_execution_authorized": False',
            '"cross_year_comparison_authorized": False',
            '"strategy_v1_synthesis_authorized": False',
            '"phase8b_authorized": False',
            '"broker_mutation_authorized": False',
            '"live_order_authorized": False',
            '"real_money_authorized": False',
            '"trading_authorized": False',
            'name: annual-catalogue-2023-dec611-run385-dispatch-',
            "if-no-files-found: error",
        ):
            self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
