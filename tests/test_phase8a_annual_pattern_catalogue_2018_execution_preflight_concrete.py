from __future__ import annotations

import copy
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2018_execution_preflight import (
    build_2018_execution_preflight,
    validate_2018_execution_preflight,
    validate_2018_execution_preflight_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PREINSTALL_SNAPSHOT = os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1"
MAIN_HEAD = "b" * 40


def _binding() -> dict[str, object]:
    return {
        "decision": "DEC-544",
        "annual_segment_label": "2017",
        "run_id": 37227536041,
        "run_number": 379,
        "run_attempt": 1,
        "run_head_sha": "7b4c1ef8573e280c067443b72f1534d9091d5b7f",
        "run_conclusion": "success",
        "previous_annual_freeze_run_id": 37206992367,
        "binding_fingerprint_sha256": (
            "a454e3eef8a51260cc07f9103a7de0208f5408a18686bb1249ad05e349edd9ae"
        ),
        "freeze_evidence_fingerprint": (
            "ed579f80f947f9a04731b4a20e675c98e2101884c874fa385df5999ef419ff8b"
        ),
        "runtime_evidence_bound": True,
        "next_segment_execution_authorized": False,
        "trading_authorized": False,
    }


def _runs() -> dict[str, object]:
    return {
        "workflow_runs": [
            {
                "id": 37126711695,
                "run_number": 1,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": "fd85a886d07234ad584dcca08692b37e6af54b2e",
                "status": "completed",
                "conclusion": "failure",
            },
            {
                "id": 37191637168,
                "run_number": 376,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3",
                "status": "completed",
                "conclusion": "failure",
            },
            {
                "id": 37198002653,
                "run_number": 377,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": "a89db974be9a94481e7ed0990476bc661012f1e4",
                "status": "completed",
                "conclusion": "success",
            },
            {
                "id": 37206992367,
                "run_number": 378,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": "2524fde355349581c9440a172d0384c3cbce31ed",
                "status": "completed",
                "conclusion": "success",
            },
            {
                "id": 37227536041,
                "run_number": 379,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": "7b4c1ef8573e280c067443b72f1534d9091d5b7f",
                "status": "completed",
                "conclusion": "success",
            },
        ]
    }


class AnnualCatalogue2018ConcreteExecutionPreflightTests(unittest.TestCase):
    @unittest.skipIf(
        PREINSTALL_SNAPSHOT,
        "historical preinstall snapshot intentionally hides annual workflow",
    )
    def test_sources_pin_concrete_dec544_and_active_workflow(self) -> None:
        source = validate_2018_execution_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["runtime_binding_source_blob_sha"],
            "67e45260a79be451d7484dfcef1fc36c4df12bf0",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    @unittest.skipIf(
        PREINSTALL_SNAPSHOT,
        "historical preinstall snapshot intentionally hides annual workflow",
    )
    def test_concrete_history_builds_read_only_run380_preflight(self) -> None:
        binding = _binding()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2018_execution_preflight."
            "validate_2017_run379_evidence_review",
            return_value=binding,
        ):
            value = build_2018_execution_preflight(
                repository_root=REPOSITORY_ROOT,
                runtime_binding=binding,
                main_branch={"name": "main", "commit": {"sha": MAIN_HEAD}},
                annual_workflow_runs=_runs(),
                expected_head_sha=MAIN_HEAD,
            )

        self.assertIs(validate_2018_execution_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-545")
        self.assertEqual(value["annual_workflow_run_count"], 5)
        self.assertEqual(value["failed_run376_id"], 37191637168)
        self.assertEqual(value["successful_2015_run_number"], 377)
        self.assertEqual(value["successful_2016_run_number"], 378)
        self.assertEqual(value["successful_2017_run_number"], 379)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37227536041)
        self.assertEqual(value["expected_next_run_number"], 380)
        self.assertEqual(value["expected_next_run_attempt"], 1)
        self.assertEqual(
            value["source_runtime_binding_recovery_workflow_run_id"],
            37228767187,
        )
        self.assertEqual(
            value["source_runtime_binding_artifact_id"],
            11313481023,
        )
        self.assertTrue(value["preflight_read_only"])
        for field in (
            "annual_workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "next_segment_execution_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(value[field], field)

    @unittest.skipIf(
        PREINSTALL_SNAPSHOT,
        "historical preinstall snapshot intentionally hides annual workflow",
    )
    def test_successful_2017_run_cannot_be_rewritten(self) -> None:
        runs = copy.deepcopy(_runs())
        rows = runs["workflow_runs"]
        assert isinstance(rows, list)
        rows[4]["conclusion"] = "failure"
        binding = _binding()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2018_execution_preflight."
            "validate_2017_run379_evidence_review",
            return_value=binding,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "annual run 379 conclusion mismatch",
            ):
                build_2018_execution_preflight(
                    repository_root=REPOSITORY_ROOT,
                    runtime_binding=binding,
                    main_branch={"name": "main", "commit": {"sha": MAIN_HEAD}},
                    annual_workflow_runs=runs,
                    expected_head_sha=MAIN_HEAD,
                )

    @unittest.skipIf(
        PREINSTALL_SNAPSHOT,
        "historical preinstall snapshot intentionally hides annual workflow",
    )
    def test_runtime_binding_fingerprint_is_exact(self) -> None:
        binding = _binding()
        binding["binding_fingerprint_sha256"] = "0" * 64
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2018_execution_preflight."
            "validate_2017_run379_evidence_review",
            return_value=binding,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "runtime binding fingerprint mismatch",
            ):
                build_2018_execution_preflight(
                    repository_root=REPOSITORY_ROOT,
                    runtime_binding=binding,
                    main_branch={"name": "main", "commit": {"sha": MAIN_HEAD}},
                    annual_workflow_runs=_runs(),
                    expected_head_sha=MAIN_HEAD,
                )

    def test_cli_has_plan_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2018_execution_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
