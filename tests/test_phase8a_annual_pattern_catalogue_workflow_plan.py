from __future__ import annotations

import unittest

from fmp.discovery.annual_pattern_catalogue_workflow_plan import (
    ARTIFACTS_PER_SEGMENT_RUN,
    CELLS_PER_SEGMENT,
    FULL_COLLECTION_CELL_COUNT,
    JOBS_PER_SEGMENT_RUN,
    SEGMENT_COUNT,
    expected_job_names,
    expected_segment_cells,
    segment_run_plan,
    workflow_plan_payload,
)


class AnnualPatternCatalogueWorkflowPlanTests(unittest.TestCase):
    def test_full_collection_shape_is_12_sequential_18_cell_segment_runs(self) -> None:
        payload = workflow_plan_payload()

        self.assertEqual(SEGMENT_COUNT, 12)
        self.assertEqual(CELLS_PER_SEGMENT, 18)
        self.assertEqual(JOBS_PER_SEGMENT_RUN, 20)
        self.assertEqual(ARTIFACTS_PER_SEGMENT_RUN, 20)
        self.assertEqual(FULL_COLLECTION_CELL_COUNT, 216)
        self.assertEqual(payload["annual_segment_count"], 12)
        self.assertEqual(payload["cells_per_segment_run"], 18)
        self.assertEqual(payload["jobs_per_segment_run"], 20)
        self.assertEqual(payload["full_collection_cell_count"], 216)
        self.assertTrue(payload["sequential_segment_freeze_required"])
        self.assertTrue(payload["cross_year_comparison_waits_for_all_segment_freezes"])
        self.assertTrue(payload["single_216_cell_workflow_forbidden"])

    def test_segment_order_matches_dec469_collection(self) -> None:
        payload = workflow_plan_payload()
        labels = payload["annual_segments_in_required_order"]

        self.assertEqual(labels[0], "2015")
        self.assertEqual(labels[-2], "2025")
        self.assertEqual(labels[-1], "2026_YTD_TO_2026_08_20")
        self.assertEqual(
            labels,
            [
                "2015",
                "2016",
                "2017",
                "2018",
                "2019",
                "2020",
                "2021",
                "2022",
                "2023",
                "2024",
                "2025",
                "2026_YTD_TO_2026_08_20",
            ],
        )

    def test_each_segment_has_exact_18_unique_cells_and_20_unique_jobs(self) -> None:
        for label in workflow_plan_payload()["annual_segments_in_required_order"]:
            cells = expected_segment_cells(label)
            jobs = expected_job_names(label)
            plan = segment_run_plan(label)

            self.assertEqual(len(cells), 18)
            self.assertEqual(len(set(cells)), 18)
            self.assertEqual(len(jobs), 20)
            self.assertEqual(len(set(jobs)), 20)
            self.assertEqual(plan["cell_count"], 18)
            self.assertEqual(plan["job_count"], 20)
            self.assertTrue(plan["annual_freeze_depends_on_all_18_cells"])
            self.assertTrue(plan["next_segment_must_wait_for_prior_segment_freeze"])
            self.assertFalse(plan["cross_year_comparison_in_this_run"])

    def test_invalid_segment_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "segment label drift"):
            expected_segment_cells("2027")

    def test_plan_installs_no_workflow_and_opens_no_authority(self) -> None:
        payload = workflow_plan_payload()

        self.assertEqual(payload["decision"], "DEC-476")
        self.assertEqual(payload["source_runtime_decision"], "DEC-475")
        self.assertEqual(
            payload["next_gate"],
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_SEGMENT_FREEZE_CONTRACT",
        )
        for field in (
            "workflow_source_authorized",
            "workflow_installed",
            "workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(payload[field], field)


if __name__ == "__main__":
    unittest.main()
