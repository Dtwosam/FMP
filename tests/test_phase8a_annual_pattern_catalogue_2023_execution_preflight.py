from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2023_execution_preflight import (
    build_2023_execution_preflight,
    validate_2023_execution_preflight,
    validate_2023_execution_preflight_sources,
)


ROOT = Path(__file__).resolve().parents[1]
MAIN_HEAD = "b" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _binding() -> dict[str, object]:
    return {
        "decision": "DEC-601",
        "annual_segment_label": "2022",
        "run_id": 37663157285,
        "run_number": 384,
        "run_attempt": 1,
        "run_status": "completed",
        "run_conclusion": "success",
        "binding_fingerprint_sha256": (
            "926832634d5836b158d780e21886692e762709104a6d0048c54a75c77ad2f352"
        ),
        "runtime_evidence_bound": True,
        "final_required_annual_segment_bound": True,
        "next_gate": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_CROSS_YEAR_COMPARISON_PREFLIGHT"
        ),
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_385_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "protected_history_access_authorized": False,
        "cross_year_comparison_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def _runs() -> dict[str, object]:
    rows = [
        (37126711695, 1, "fd85a886d07234ad584dcca08692b37e6af54b2e", "failure"),
        (37191637168, 376, "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3", "failure"),
        (37198002653, 377, "a89db974be9a94481e7ed0990476bc661012f1e4", "success"),
        (37206992367, 378, "2524fde355349581c9440a172d0384c3cbce31ed", "success"),
        (37227536041, 379, "7b4c1ef8573e280c067443b72f1534d9091d5b7f", "success"),
        (37237817538, 380, "30971a996f514670a6f836d8e45cf80137197a4f", "success"),
        (37310525635, 381, "8bcee3a7a834743f08bd9ad73109bfc09609a2fe", "success"),
        (37443770076, 382, "681e81e021d4970a67b18370142d55b17ec68864", "success"),
        (37531960014, 383, "a1e194907c273a2fcdddfb4c24d64a96cfd8d263", "success"),
        (37663157285, 384, "dd79687adc4ec179c56f91939cb600e6746fab5d", "success"),
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


class AnnualCatalogue2023ExecutionPreflightTests(unittest.TestCase):
    def _build(
        self,
        binding: dict[str, object] | None = None,
        runs: dict[str, object] | None = None,
    ) -> dict[str, object]:
        binding = binding or _binding()
        canonical = hashlib.sha256(_canonical_json(binding)).hexdigest()
        with (
            patch(
                "fmp.discovery.annual_pattern_catalogue_2023_execution_preflight."
                "validate_2022_run384_evidence_review",
                return_value=binding,
            ),
            patch(
                "fmp.discovery.annual_pattern_catalogue_2023_execution_preflight."
                "EXPECTED_RUNTIME_BINDING_CANONICAL_SHA256",
                canonical,
            ),
        ):
            return build_2023_execution_preflight(
                repository_root=ROOT,
                runtime_binding=binding,
                main_branch={"name": "main", "commit": {"sha": MAIN_HEAD}},
                annual_workflow_runs=runs or _runs(),
                expected_head_sha=MAIN_HEAD,
            )

    def test_sources_pin_dec601_method_protocol_and_workflow(self) -> None:
        value = validate_2023_execution_preflight_sources(repository_root=ROOT)
        self.assertEqual(
            value["runtime_binding_source_blob_sha"],
            "7048781474ce74b8bbed0fd380f8edf4ec51491d",
        )
        self.assertEqual(
            value["method_source_blob_sha"],
            "d7486296c2e953d6b4e7602c753c5529ccf5eef2",
        )
        self.assertEqual(
            value["protocol_source_blob_sha"],
            "5ddd987cc480e6e31c0cd45328eba16cf690dee9",
        )
        self.assertEqual(
            value["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_valid_2022_binding_builds_read_only_protected_2023_preflight(self) -> None:
        value = self._build()
        self.assertIs(validate_2023_execution_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-602")
        self.assertEqual(value["annual_segment_label"], "2023")
        self.assertEqual(value["prior_segment_label"], "2022")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37663157285)
        self.assertEqual(value["annual_workflow_run_count"], 10)
        self.assertEqual(value["successful_2022_run_number"], 384)
        self.assertEqual(value["expected_next_run_number"], 385)
        self.assertEqual(value["expected_next_run_attempt"], 1)
        self.assertTrue(
            value["source_terminal_successor_claim_superseded_by_dec469_dec470"]
        )
        self.assertEqual(value["governing_method_decision"], "DEC-469")
        self.assertEqual(value["governing_protocol_decision"], "DEC-470")
        self.assertEqual(value["collection_segment_count"], 12)
        self.assertTrue(value["protected_catalogue_segment"])
        self.assertTrue(value["protocol_full_collection_catalogue_use_authorized"])
        self.assertTrue(value["protocol_2023_2026_catalogue_use_authorized"])
        self.assertFalse(
            value["protocol_2023_2026_remains_untouched_oos_for_strategy_v1"]
        )
        self.assertTrue(value["preflight_read_only"])
        for field in (
            "annual_workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "run_386_or_later_authorized",
            "next_segment_execution_authorized",
            "protected_history_access_authorized",
            "cross_year_comparison_authorized",
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

    def test_run384_must_be_success(self) -> None:
        runs = copy.deepcopy(_runs())
        rows = runs["workflow_runs"]
        assert isinstance(rows, list)
        rows[-1]["conclusion"] = "failure"
        with self.assertRaisesRegex(
            ValueError,
            "annual run 384 conclusion mismatch",
        ):
            self._build(runs=runs)

    def test_source_binding_protected_access_tamper_is_rejected(self) -> None:
        binding = _binding()
        binding["protected_history_access_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "source binding protected_history_access_authorized drift",
        ):
            self._build(binding=binding)

    def test_cli_is_plan_only(self) -> None:
        text = (
            ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2023_execution_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', text)
        self.assertNotIn('subparsers.add_parser("dispatch")', text)
        self.assertNotIn("gh workflow run ", text)


if __name__ == "__main__":
    unittest.main()
