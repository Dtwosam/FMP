from __future__ import annotations

import copy
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2021_execution_preflight import (
    build_2021_execution_preflight,
    validate_2021_execution_preflight,
    validate_2021_execution_preflight_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PREINSTALL_SNAPSHOT = os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1"
MAIN_HEAD = "b" * 40


def _binding() -> dict[str, object]:
    return {
        "decision": "DEC-579",
        "annual_segment_label": "2020",
        "run_id": 37443770076,
        "run_number": 382,
        "run_attempt": 1,
        "run_head_sha": "681e81e021d4970a67b18370142d55b17ec68864",
        "run_conclusion": "success",
        "previous_annual_freeze_run_id": 37310525635,
        "binding_fingerprint_sha256": "ebde4b5ee78421cc2afb4c12c4ff2603b6d01f1990fbfe683aed11d00653a76c",
        "freeze_evidence_fingerprint": "53cd4475b2e9f70252bc4962666ce421daf7795d3e78defbb38ec948448e1c3c",
        "runtime_evidence_bound": True,
        "next_segment_execution_authorized": False,
        "trading_authorized": False,
    }


def _runs() -> dict[str, object]:
    rows = [
        (
            37126711695,
            1,
            "fd85a886d07234ad584dcca08692b37e6af54b2e",
            "failure",
        ),
        (
            37191637168,
            376,
            "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3",
            "failure",
        ),
        (
            37198002653,
            377,
            "a89db974be9a94481e7ed0990476bc661012f1e4",
            "success",
        ),
        (
            37206992367,
            378,
            "2524fde355349581c9440a172d0384c3cbce31ed",
            "success",
        ),
        (
            37227536041,
            379,
            "7b4c1ef8573e280c067443b72f1534d9091d5b7f",
            "success",
        ),
        (
            37237817538,
            380,
            "30971a996f514670a6f836d8e45cf80137197a4f",
            "success",
        ),
        (
            37310525635,
            381,
            "8bcee3a7a834743f08bd9ad73109bfc09609a2fe",
            "success",
        ),
        (
            37443770076,
            382,
            "681e81e021d4970a67b18370142d55b17ec68864",
            "success",
        ),
    ]
    return {
        "workflow_runs": [
            {
                "id": run_id,
                "run_number": run_number,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": head_sha,
                "status": "completed",
                "conclusion": conclusion,
            }
            for run_id, run_number, head_sha, conclusion in rows
        ]
    }


class AnnualCatalogue2021ExecutionPreflightTests(unittest.TestCase):
    @unittest.skipIf(
        PREINSTALL_SNAPSHOT,
        "historical preinstall snapshot intentionally hides annual workflow",
    )
    def test_sources_pin_dec579_and_active_workflow(self) -> None:
        value = validate_2021_execution_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            value["runtime_binding_source_blob_sha"],
            "7c721121197b83e687fd2c76773773f8ab4c07ae",
        )
        self.assertEqual(
            value["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    @unittest.skipIf(
        PREINSTALL_SNAPSHOT,
        "historical preinstall snapshot intentionally hides annual workflow",
    )
    def test_valid_2020_binding_builds_read_only_run383_preflight(self) -> None:
        binding = _binding()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2021_execution_preflight."
            "validate_2020_run382_recovery_evidence",
            return_value=binding,
        ):
            value = build_2021_execution_preflight(
                repository_root=REPOSITORY_ROOT,
                runtime_binding=binding,
                main_branch={"name": "main", "commit": {"sha": MAIN_HEAD}},
                annual_workflow_runs=_runs(),
                expected_head_sha=MAIN_HEAD,
            )

        self.assertIs(validate_2021_execution_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-580")
        self.assertEqual(value["annual_segment_label"], "2021")
        self.assertEqual(value["prior_segment_label"], "2020")
        self.assertEqual(value["annual_workflow_run_count"], 8)
        self.assertEqual(value["successful_2019_run_id"], 37310525635)\n        self.assertEqual(value["successful_2020_run_id"], 37443770076)
        self.assertEqual(value["successful_2019_run_number"], 381)\n        self.assertEqual(value["successful_2020_run_number"], 382)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37443770076)
        self.assertEqual(value["expected_next_run_number"], 383)
        self.assertEqual(value["expected_next_run_attempt"], 1)
        self.assertEqual(
            value["source_runtime_binding_recovery_workflow_run_id"],
            37447286936,
        )
        self.assertEqual(
            value["source_runtime_binding_recovery_head_sha"],
            "2fdbcb85f4509ca5e4342cc06a284e1bcd109cc4",
        )
        self.assertEqual(
            value["source_runtime_binding_artifact_id"],
            11404455773,
        )
        self.assertEqual(
            value["source_runtime_binding_artifact_digest"],
            "sha256:bfd0286ed48e1ee8690921275ec34485025d95f92579519d8e68398867d45d5c",
        )
        self.assertEqual(
            value["source_runtime_binding_fingerprint_sha256"],
            "ebde4b5ee78421cc2afb4c12c4ff2603b6d01f1990fbfe683aed11d00653a76c",
        )
        self.assertEqual(
            value["source_freeze_evidence_fingerprint_sha256"],
            "53cd4475b2e9f70252bc4962666ce421daf7795d3e78defbb38ec948448e1c3c",
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
    def test_run382_must_be_success(self) -> None:
        runs = copy.deepcopy(_runs())
        rows = runs["workflow_runs"]
        assert isinstance(rows, list)
        rows[-1]["conclusion"] = "failure"
        binding = _binding()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2021_execution_preflight."
            "validate_2020_run382_recovery_evidence",
            return_value=binding,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "annual run 382 conclusion mismatch",
            ):
                build_2021_execution_preflight(
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
    def test_binding_must_name_exact_run382(self) -> None:
        binding = _binding()
        binding["run_id"] = 1
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2021_execution_preflight."
            "validate_2020_run382_recovery_evidence",
            return_value=binding,
        ):
            with self.assertRaisesRegex(ValueError, "2020 run id mismatch"):
                build_2021_execution_preflight(
                    repository_root=REPOSITORY_ROOT,
                    runtime_binding=binding,
                    main_branch={"name": "main", "commit": {"sha": MAIN_HEAD}},
                    annual_workflow_runs=_runs(),
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
            "fmp.discovery.annual_pattern_catalogue_2021_execution_preflight."
            "validate_2020_run382_recovery_evidence",
            return_value=binding,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "runtime binding fingerprint mismatch",
            ):
                build_2021_execution_preflight(
                    repository_root=REPOSITORY_ROOT,
                    runtime_binding=binding,
                    main_branch={"name": "main", "commit": {"sha": MAIN_HEAD}},
                    annual_workflow_runs=_runs(),
                    expected_head_sha=MAIN_HEAD,
                )

    def test_cli_is_plan_only(self) -> None:
        text = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2021_execution_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', text)
        self.assertNotIn('subparsers.add_parser("dispatch")', text)
        self.assertNotIn("gh workflow run ", text)


if __name__ == "__main__":
    unittest.main()
