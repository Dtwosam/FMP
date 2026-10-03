from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2017_execution_preflight import (
    build_2017_execution_preflight,
    validate_2017_execution_preflight,
    validate_2017_execution_preflight_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MAIN_HEAD = "c" * 40
RUN376_HEAD = "a" * 40
RUN377_HEAD = "b" * 40
RUN376_ID = 666666
RUN377_ID = 777777


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _binding() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-522",
        "version": "fmp-annual-catalogue-2016-run377-evidence-review-v1",
        "stage": "ANNUAL_CATALOGUE_2016_RUN377_CONCRETE_RUNTIME_EVIDENCE_BOUND",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2016",
        "run_id": RUN377_ID,
        "run_number": 377,
        "run_attempt": 1,
        "run_status": "completed",
        "run_conclusion": "success",
        "run_head_sha": RUN377_HEAD,
        "source_dispatch_receipt_decision": "DEC-521",
        "previous_annual_freeze_run_id": RUN376_ID,
        "dispatch_receipt_bound": True,
        "freeze_artifact_zip_sha256": "1" * 64,
        "freeze_evidence_canonical_sha256": "2" * 64,
        "freeze_evidence_fingerprint": "3" * 64,
        "annual_cell_count": 18,
        "directional_record_count": 89460,
        "evaluable_record_count": 18,
        "zero_support_record_count": 36,
        "total_support": 54,
        "cell_job_ids": {
            f"cell-{index:02d}": 1000 + index
            for index in range(18)
        },
        "cell_artifacts": {
            f"artifact-{index:02d}": {"id": 2000 + index}
            for index in range(18)
        },
        "runtime_review_validated": True,
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
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_EXECUTION_PREFLIGHT",
    }
    value["binding_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


def _runs() -> dict[str, object]:
    return {
        "workflow_runs": [
            {
                "id": RUN377_ID,
                "run_number": 377,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": RUN377_HEAD,
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
            {
                "id": RUN376_ID,
                "run_number": 376,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": RUN376_HEAD,
                "status": "completed",
                "conclusion": "success",
            },
        ]
    }


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": MAIN_HEAD}}


def _refingerprint_binding(value: dict[str, object]) -> None:
    unsigned = dict(value)
    unsigned.pop("binding_fingerprint_sha256", None)
    value["binding_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(unsigned)
    ).hexdigest()


class AnnualPatternCatalogue2017ExecutionPreflightTests(unittest.TestCase):
    def test_sources_pin_dec522_and_corrected_workflow(self) -> None:
        source = validate_2017_execution_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["runtime_binding_source_blob_sha"],
            "b186c8049b045761ccd0f693feaf7637a4807e53",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_concrete_2016_binding_yields_read_only_2017_preflight(self) -> None:
        value = build_2017_execution_preflight(
            repository_root=REPOSITORY_ROOT,
            runtime_binding=_binding(),
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=MAIN_HEAD,
        )
        self.assertIs(validate_2017_execution_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-523")
        self.assertEqual(value["annual_segment_label"], "2017")
        self.assertEqual(value["prior_segment_label"], "2016")
        self.assertEqual(value["annual_workflow_run_count"], 3)
        self.assertEqual(value["successful_2015_run_number"], 376)
        self.assertEqual(value["successful_2016_run_number"], 377)
        self.assertEqual(value["previous_annual_freeze_run_id"], RUN377_ID)
        self.assertEqual(value["expected_next_run_number"], 378)
        self.assertEqual(value["expected_next_run_attempt"], 1)
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_artifact_read_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["historical_result_production_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_extra_annual_run_is_rejected(self) -> None:
        runs = _runs()
        rows = list(runs["workflow_runs"])
        rows.append(
            {
                "id": 888888,
                "run_number": 378,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": MAIN_HEAD,
                "status": "completed",
                "conclusion": "success",
            }
        )
        with self.assertRaisesRegex(
            ValueError,
            "exactly three annual workflow dispatch runs",
        ):
            build_2017_execution_preflight(
                repository_root=REPOSITORY_ROOT,
                runtime_binding=_binding(),
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=MAIN_HEAD,
            )

    def test_2015_predecessor_identity_mismatch_is_rejected(self) -> None:
        binding = _binding()
        binding["previous_annual_freeze_run_id"] = 999999
        _refingerprint_binding(binding)
        with self.assertRaisesRegex(
            ValueError,
            "successful 2015 run id mismatch",
        ):
            build_2017_execution_preflight(
                repository_root=REPOSITORY_ROOT,
                runtime_binding=binding,
                main_branch=_main(),
                annual_workflow_runs=_runs(),
                expected_head_sha=MAIN_HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2017_execution_preflight(
                repository_root=REPOSITORY_ROOT,
                runtime_binding=_binding(),
                main_branch={
                    "name": "main",
                    "commit": {"sha": "d" * 40},
                },
                annual_workflow_runs=_runs(),
                expected_head_sha=MAIN_HEAD,
            )

    def test_refingerprinted_dispatch_authority_tamper_is_rejected(self) -> None:
        value = build_2017_execution_preflight(
            repository_root=REPOSITORY_ROOT,
            runtime_binding=_binding(),
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=MAIN_HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["annual_workflow_dispatch_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("preflight_fingerprint_sha256", None)
        tampered["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "annual_workflow_dispatch_authorized mismatch",
        ):
            validate_2017_execution_preflight(tampered)

    def test_cli_is_plan_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2017_execution_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
