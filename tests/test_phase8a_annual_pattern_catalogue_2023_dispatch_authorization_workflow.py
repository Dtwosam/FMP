from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase8a-annual-catalogue-2023-dispatch-authorization.yml"


class AnnualCatalogue2023DispatchAuthorizationWorkflowTests(unittest.TestCase):
    def test_first_push_builder_is_read_only_and_path_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "name: phase8a-annual-catalogue-2023-dispatch-authorization",
            "  push:", "      - main", "  contents: read", "  actions: read",
            'test "$GITHUB_RUN_NUMBER" = "1"',
            'test "$GITHUB_RUN_ATTEMPT" = "1"',
        ):
            self.assertIn(required, text)
        for forbidden in ("contents: write", "actions: write", "workflow_dispatch:", "gh workflow run ", "gh run rerun", "git push", "git commit"):
            self.assertNotIn(forbidden, text)

    def test_frozen_dec608_and_installed_runtime_are_pinned(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "37766405383", "d9194944f53d311a9030deaf3ee37bff465634ed",
            "11544233443", "7750c5d3b68b21dc7a4199e97ee3ce2fd8fdcb53fb6170c5270a78f695a512fc",
            "9f1533d5993c28c86f53d2c7bd0f219178465da2c0eb987ae923ac9af8aca695",
            "6044191b89bbd6b33338b86077715be7d925d30ac14cd38845c948523f6ae651",
            "b7f55dd68d5054c472b4e070521c411c02a4da3c",
            "341091275d57b1222aa4a6b3e00212f7609ec37d",
            "fb4f8fa390e94a75a8d52c99cbc041e9bf1e8164",
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
            ".github/workflows/phase8a-annual-catalogue-2023-dispatch-preflight.yml",
        ):
            self.assertIn(required, text)
        self.assertNotIn("DEC597_", text)
        self.assertNotIn("phase8a-annual-catalogue-2023-dispatch-preflight-recovery.yml", text)

    def test_unconsumed_run385_is_required(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 10", text)
        self.assertIn("assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382, 383, 384}", text)
        self.assertIn('row.get("run_number") >= 385', text)
        self.assertIn('384: (37663157285, "success")', text)
        self.assertIn('value["expected_run_number"] == 385', text)
        self.assertIn('value["previous_annual_freeze_run_id"] == 37663157285', text)

    def test_source_only_authorization_has_narrow_protected_scope(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            'value["decision"] == "DEC-609"',
            'value["source_only_authorization"] is True',
            'value["annual_workflow_dispatch_authorized"] is True',
            'value["protected_history_access_authorized"] is True',
            'value["source_authorization_protected_history_access_authorized"] is True',
            'value["authorization_scope"] == "2023_run_385_attempt_1_only"',
            '"run_386_or_later_authorized",',
            '"cross_year_comparison_authorized",',
            '"trading_authorized",',
            "assert value[field] is False, field",
        ):
            self.assertIn(required, text)
        self.assertIn('test "$(jq -r \'.protected_history_access_authorized\'', text)
        self.assertNotIn('"protected_history_access_authorized",\n              "cross_year_comparison_authorized",', text)


if __name__ == "__main__":
    unittest.main()
