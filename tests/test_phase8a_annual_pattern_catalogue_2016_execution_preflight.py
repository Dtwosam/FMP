from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2016_execution_preflight import (
    build_2016_execution_preflight,
    validate_2016_execution_preflight,
    validate_2016_execution_preflight_sources,
)


MAIN_HEAD = "c" * 40
RUN2_HEAD = "b" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _artifact(artifact_id: int, name: str, digest_hex: str) -> dict[str, object]:
    return {
        "id": artifact_id,
        "name": name,
        "digest": f"sha256:{digest_hex}",
        "size_in_bytes": 123,
    }


def _binding() -> dict[str, object]:
    cell_job_ids = {
        f"annual-cell-2015-cell-{index:02d}": 1000 + index
        for index in range(18)
    }
    cell_artifacts = {
        f"phase8a-annual-catalogue-cell-2015-cell-{index:02d}-{RUN2_HEAD}": _artifact(
            2000 + index,
            f"phase8a-annual-catalogue-cell-2015-cell-{index:02d}-{RUN2_HEAD}",
            "d" * 64,
        )
        for index in range(18)
    }
    value: dict[str, object] = {
        "decision": "DEC-502",
        "version": "fmp-annual-catalogue-2015-runtime-evidence-binding-v1",
        "run_freeze_source_blob_sha": "8e2a6ab27b4941e3ee12b5463247999200d33e69",
        "run_review_source_blob_sha": "883f82c85d2738c46284d3675278dc061f4ca07c",
        "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        "source_freeze_decision": "DEC-501",
        "source_freeze_version": "fmp-annual-catalogue-2015-replacement-run-freeze-v1",
        "stage": "ANNUAL_CATALOGUE_2015_CONCRETE_RUNTIME_EVIDENCE_BOUND",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2015",
        "run_id": 424242,
        "run_number": 376,
        "run_attempt": 1,
        "run_status": "completed",
        "run_conclusion": "success",
        "run_head_sha": RUN2_HEAD,
        "preflight_job_id": 9001,
        "freeze_job_id": 9002,
        "cell_job_ids": cell_job_ids,
        "preflight_artifact": _artifact(
            3001,
            f"phase8a-annual-catalogue-preflight-2015-{RUN2_HEAD}",
            "e" * 64,
        ),
        "freeze_artifact": _artifact(
            3002,
            f"phase8a-annual-catalogue-freeze-2015-{RUN2_HEAD}",
            "f" * 64,
        ),
        "cell_artifacts": cell_artifacts,
        "freeze_artifact_zip_sha256": "f" * 64,
        "freeze_evidence_canonical_sha256": "1" * 64,
        "freeze_evidence_fingerprint": "2" * 64,
        "annual_cell_count": 18,
        "directional_record_count": 89460,
        "evaluable_record_count": 123,
        "zero_support_record_count": 456,
        "total_support": 789,
        "review_fingerprint_sha256": "3" * 64,
        "runtime_freeze_fingerprint_sha256": "4" * 64,
        "replacement_authorization_consumed": True,
        "runtime_review_validated": True,
        "runtime_evidence_frozen": True,
        "runtime_evidence_bound": True,
        "next_segment_execution_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_PREFLIGHT",
    }
    value["binding_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": MAIN_HEAD}}


def _runs() -> dict[str, object]:
    return {
        "workflow_runs": [
            {
                "id": 424242,
                "run_number": 376,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": RUN2_HEAD,
                "status": "completed",
                "conclusion": "success",
            },
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
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-503 requires concrete 2015 runtime evidence",
)
class AnnualPatternCatalogue2016ExecutionPreflightTests(unittest.TestCase):
    def test_sources_pin_binding_runtime_and_repaired_workflow(self) -> None:
        source = validate_2016_execution_preflight_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["runtime_binding_source_blob_sha"],
            "bbb3bba32c3677d3bd971a2744eb93498868433b",
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            "ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_concrete_2015_binding_yields_read_only_2016_preflight(self) -> None:
        binding = _binding()
        value = build_2016_execution_preflight(
            repository_root=Path("."),
            runtime_binding=binding,
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=MAIN_HEAD,
        )
        self.assertIs(validate_2016_execution_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-503")
        self.assertEqual(value["annual_segment_label"], "2016")
        self.assertTrue(value["prior_segment_required"])
        self.assertEqual(value["prior_segment_label"], "2015")
        self.assertEqual(value["previous_annual_freeze_run_id"], 424242)
        self.assertEqual(
            value["previous_runtime_binding_fingerprint"],
            binding["binding_fingerprint_sha256"],
        )
        self.assertEqual(value["annual_workflow_run_count"], 2)
        self.assertEqual(value["expected_next_run_number"], 377)
        self.assertEqual(value["expected_next_run_attempt"], 1)
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_artifact_read_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["historical_result_production_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertTrue(value["preflight_read_only"])

    def test_missing_successful_replacement_run_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "exactly two prior annual-catalogue workflow runs",
        ):
            build_2016_execution_preflight(
                repository_root=Path("."),
                runtime_binding=_binding(),
                main_branch=_main(),
                annual_workflow_runs={
                    "workflow_runs": [_runs()["workflow_runs"][1]]
                },
                expected_head_sha=MAIN_HEAD,
            )

    def test_successful_replacement_identity_drift_is_rejected(self) -> None:
        runs = _runs()
        rows = list(runs["workflow_runs"])
        rows[0] = dict(rows[0])
        rows[0]["head_sha"] = "d" * 40
        with self.assertRaisesRegex(
            ValueError,
            "successful replacement run head_sha mismatch",
        ):
            build_2016_execution_preflight(
                repository_root=Path("."),
                runtime_binding=_binding(),
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=MAIN_HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2016_execution_preflight(
                repository_root=Path("."),
                runtime_binding=_binding(),
                main_branch={"name": "main", "commit": {"sha": "d" * 40}},
                annual_workflow_runs=_runs(),
                expected_head_sha=MAIN_HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        script = Path(
            "scripts/phase8a_annual_pattern_catalogue_2016_execution_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
