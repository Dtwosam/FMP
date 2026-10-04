from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-2018-execution-preflight.yml"
)


class AnnualCatalogue2018ExecutionPreflightWorkflowTests(unittest.TestCase):
    def test_workflow_is_read_only_one_shot_preflight(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-2018-execution-preflight",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn("  contents: read", text)
        self.assertIn("  actions: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("actions: write", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("gh workflow run ", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)

    def test_workflow_pins_exact_recovered_dec544_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "37228767187",
            "8169c07142fee231cf0fbe539954b876e2f0e240",
            "11313481023",
            "sha256:f48dd73bbae1587bf8c6e97408295ab94761ab4536c7124532ef5b6f55c2d1d1",
            "a454e3eef8a51260cc07f9103a7de0208f5408a18686bb1249ad05e349edd9ae",
            "ed579f80f947f9a04731b4a20e675c98e2101884c874fa385df5999ef419ff8b",
            "ed71113733ae0034d81914d4c0ab37efb5c4ce6e",
            "54f1bd8d58cd94284fd6584dfcdf0743e4864048",
            "67e45260a79be451d7484dfcef1fc36c4df12bf0",
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        ):
            self.assertIn(value, text)

    def test_workflow_requires_exact_five_run_history(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("assert len(rows) == 5", text)
        self.assertIn(
            "assert set(by_number) == {1, 376, 377, 378, 379}",
            text,
        )
        for run_id in (
            "37126711695",
            "37191637168",
            "37198002653",
            "37206992367",
            "37227536041",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            'assert not any(row["run_number"] >= 380 for row in rows)',
            text,
        )

    def test_workflow_freezes_2018_at_run380_without_authority(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'assert value["annual_segment_label"] == "2018"',
            text,
        )
        self.assertIn(
            'assert value["previous_annual_freeze_run_id"] == 37227536041',
            text,
        )
        self.assertIn(
            'assert value["expected_next_run_number"] == 380',
            text,
        )
        self.assertIn(
            'assert value["expected_next_run_attempt"] == 1',
            text,
        )
        self.assertIn('assert value["preflight_read_only"] is True', text)
        self.assertIn("assert value[field] is False, field", text)
        self.assertIn(
            "annual-catalogue-2018-dec545-execution-preflight-",
            text,
        )


if __name__ == "__main__":
    unittest.main()
