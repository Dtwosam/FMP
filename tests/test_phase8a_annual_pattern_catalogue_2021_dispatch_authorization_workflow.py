from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2021-dispatch-authorization.yml"
)


class AnnualPatternCatalogue2021DispatchAuthorizationWorkflowTests(
    unittest.TestCase
):
    def test_workflow_is_path_scoped_read_only_push_builder(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2021-dispatch-authorization",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_workflow_pins_exact_dec573_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37501665304",
            "b62616de10cc4362ff4f372e44e73fcd2be91366",
            "11430072006",
            "e973c65ad1b72531e372a86cb028687733b8dfd9414fd901009c83d396621837",
            "55a2c7cbeec4a0ae54b96f1a2687e79e929b79cc4e484b442a9729e62da8f84a",
            "6039cf03b7b22f6982a3fdebda7b3be8d709c70a4ad5e84890f164bd47d2cf33",
            "17a7b4de05f3d27bc96ecbc182347ac1fc7926af",
            "2bf19008e1d4011847775ebdf0afc1118c9c99cf",
            "a2454464ad9445dfd3ac788797f1c7633b67e116",
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        ):
            self.assertIn(value, text)

    def test_workflow_rechecks_unconsumed_run382_slot(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379, 380, 381, 382}",
            text,
        )
        self.assertIn('row.get("run_number") >= 383', text)
        self.assertIn('value["expected_run_number"] == 383', text)
        self.assertIn(
            'value["previous_annual_freeze_run_id"] == 37443770076',
            text,
        )

    def test_workflow_emits_source_only_authorization(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('value["decision"] == "DEC-587"', text)
        self.assertIn('value["source_only_authorization"] is True', text)
        self.assertIn(
            'value["annual_workflow_dispatch_authorized"] is True',
            text,
        )
        self.assertIn('assert value[field] is False, field', text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("rerun-failed-jobs", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)


if __name__ == "__main__":
    unittest.main()
