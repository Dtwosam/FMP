from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT / ".github/workflows/phase8a-annual-catalogue-2023-dispatch-action-preflight.yml"
)


class AnnualCatalogue2023DispatchActionPreflightWorkflowTests(unittest.TestCase):
    def test_path_scoped_read_only_builder(self) -> None:
        value = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "name: phase8a-annual-catalogue-2023-dispatch-action-preflight",
            "  push:",
            "      - main",
            "  contents: read",
            "  actions: read",
            'test "$GITHUB_RUN_NUMBER" = "1"',
            'test "$GITHUB_RUN_ATTEMPT" = "1"',
            'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"',
        ):
            self.assertIn(required, value)
        for forbidden in (
            "contents: write", "actions: write", "workflow_dispatch:",
            "gh workflow run ", "gh run rerun", "git push", "git commit",
            "broker_order", "secrets:",
        ):
            self.assertNotIn(forbidden, value)

    def test_exact_dec609_provenance_and_runtime_pins(self) -> None:
        value = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "37770601661",
            "7d40ccaf79270162dd96a8a1e7024dd94c3a72b7",
            "11547430955",
            "8e33ab04cf87e0f2fe6b6b05fec53531dd0c9ff33fcc16abde920667ad154132",
            "af91a248811f0cf291aea1fd94f4fff72eddd7e016b8d2fce2afc543bccb88fe",
            "044f7ec28570660fa04fb886e6ab194c4a986427b8df86754241b44e6efbf3ad",
            "60923763b844b8a1348cbfcf2612b739b8c7c28a",
            "8b8870e1e0d14ed0eb4208a7a0ec5fbff52a5764",
            "b7f55dd68d5054c472b4e070521c411c02a4da3c",
            "fb4f8fa390e94a75a8d52c99cbc041e9bf1e8164",
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
            "phase8a-annual-catalogue-2023-dispatch-authorization.yml",
            "dec609-2023-dispatch-authorization.json",
            "source_authorization_protected_history_access_authorized",
        ):
            self.assertIn(required, value)

    def test_run385_stays_unconsumed_and_no_dispatch_occurs(self) -> None:
        value = WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "assert len(rows) == 10",
            "assert not any(x.get(\"run_number\", 0) >= 385 for x in rows)",
            'assert predecessor["id"] == 37663157285',
            'value["expected_run_number"] == 385',
            'value["preflight_read_only"] is True',
            'value["protected_history_access_authorized"] is False',
            'value["dispatch_action_executed"] is False',
            'value["trading_authorized"] is False',
            "annual-catalogue-2023-dec610-dispatch-action-preflight-",
            "if-no-files-found: error",
        ):
            self.assertIn(required, value)


if __name__ == "__main__":
    unittest.main()
