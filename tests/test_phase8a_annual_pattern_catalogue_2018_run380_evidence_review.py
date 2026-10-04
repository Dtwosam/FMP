from __future__ import annotations

import copy
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_evidence import (
    DIRECTIONAL_RECORDS_PER_ANNUAL_CELL,
    ValidatedAnnualCellSummary,
)
from fmp.discovery.annual_pattern_catalogue_segment_evidence import (
    compile_annual_segment_freeze,
)
from fmp.discovery.annual_pattern_catalogue_2018_run380_evidence_review import (
    review_2018_run380_evidence,
    validate_2018_run380_evidence_review,
    validate_2018_run380_evidence_review_sources,
)
from fmp.discovery.pattern_protocol import (
    HORIZONS_MINUTES,
    SYMBOLS,
    TIMEFRAMES,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PREINSTALL_SNAPSHOT = os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1"
HEAD = "a" * 40
RUN_ID = 777777


def _summary(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> ValidatedAnnualCellSummary:
    return ValidatedAnnualCellSummary(
        annual_segment_label="2018",
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon,
        code_commit=HEAD,
        evidence_fingerprint="1" * 64,
        catalogue_payload_sha256="2" * 64,
        processed_manifest_sha256="3" * 64,
        feature_manifest_sha256="4" * 64,
        outcome_manifest_sha256="5" * 64,
        feature_evidence_fingerprint="6" * 64,
        outcome_evidence_fingerprint="7" * 64,
        directional_record_count=DIRECTIONAL_RECORDS_PER_ANNUAL_CELL,
        evaluable_record_count=1,
        zero_support_record_count=2,
        total_support=3,
    )


def _freeze() -> dict[str, object]:
    return compile_annual_segment_freeze(
        [
            _summary(symbol, timeframe, horizon)
            for symbol in SYMBOLS
            for timeframe in TIMEFRAMES
            for horizon in HORIZONS_MINUTES
        ],
        annual_segment_label="2018",
        code_commit=HEAD,
    )


def _run() -> dict[str, object]:
    return {
        "id": RUN_ID,
        "name": "phase8a-annual-pattern-catalogue",
        "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": 380,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    names = ["annual-preflight-2018"]
    names.extend(
        f"annual-cell-2018-{symbol}-{timeframe}-{horizon}m"
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
    )
    names.append("annual-freeze-2018")
    return {
        "jobs": [
            {
                "id": index + 100,
                "name": name,
                "status": "completed",
                "conclusion": "success",
            }
            for index, name in enumerate(names)
        ]
    }


def _artifacts() -> dict[str, object]:
    names = [
        f"phase8a-annual-catalogue-preflight-2018-{HEAD}",
        *[
            (
                f"phase8a-annual-catalogue-cell-2018-"
                f"{symbol}-{timeframe}-{horizon}m-{HEAD}"
            )
            for symbol in SYMBOLS
            for timeframe in TIMEFRAMES
            for horizon in HORIZONS_MINUTES
        ],
        f"phase8a-annual-catalogue-freeze-2018-{HEAD}",
    ]
    rows = []
    for index, name in enumerate(names):
        digest = "f" * 64 if "freeze-2018" in name else "e" * 64
        rows.append(
            {
                "id": index + 1000,
                "name": name,
                "expired": False,
                "digest": "sha256:" + digest,
                "size_in_bytes": 123,
            }
        )
    return {"artifacts": rows}


def _receipt() -> dict[str, object]:
    return {
        "decision": "DEC-554",
        "stage": "ANNUAL_CATALOGUE_2018_RUN_380_DISPATCH_SUBMITTED",
        "source_preflight_decision": "DEC-553",
        "source_preflight_workflow_run_id": 37235949110,
        "source_preflight_workflow_head_sha": (
            "67b8baa1f6a5770c2add27189f86f65f46a263d6"
        ),
        "source_preflight_artifact_id": 11315522989,
        "source_preflight_artifact_digest": (
            "sha256:e4d9b6c8661442c1a1debebac843f2dabf07bca6e36054dc7d2ed43a74f1375e"
        ),
        "source_preflight_fingerprint_sha256": (
            "ba609f06481c1b08e10d16dc772290cd0f3988de9ba32eaa56c13b5561ab86c2"
        ),
        "dispatch_head_sha": HEAD,
        "annual_segment_label": "2018",
        "previous_annual_freeze_run_id": 37227536041,
        "run_id": RUN_ID,
        "run_number": 380,
        "run_attempt": 1,
        "run_head_sha": HEAD,
        "dispatch_submitted": True,
        "result_claimed": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_381_or_later_authorized": False,
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
        "next_gate": "REVIEW_2018_RUN_380_BEFORE_ANY_2019_EXECUTION",
    }


@unittest.skipIf(
    PREINSTALL_SNAPSHOT,
    "DEC-555 requires the installed 2018 runtime state",
)
class AnnualPatternCatalogue2018Run380EvidenceReviewTests(unittest.TestCase):
    def test_sources_pin_current_runtime_and_preflight(self) -> None:
        source = validate_2018_run380_evidence_review_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["segment_evidence_source_blob_sha"],
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
        )
        self.assertEqual(
            source["dispatch_action_preflight_source_blob_sha"],
            "67e2f0de14fe9ffcc8dce5473f816ed5c1ca9cb7",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        )

    def test_successful_run380_is_bound_read_only(self) -> None:
        value = review_2018_run380_evidence(
            repository_root=REPOSITORY_ROOT,
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            freeze_evidence=_freeze(),
            freeze_artifact_zip_sha256="f" * 64,
            dispatch_receipt=_receipt(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2018_run380_evidence_review(value), value)
        self.assertEqual(value["decision"], "DEC-555")
        self.assertEqual(value["annual_segment_label"], "2018")
        self.assertEqual(value["run_id"], RUN_ID)
        self.assertEqual(value["run_number"], 380)
        self.assertEqual(value["run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37227536041)
        self.assertEqual(value["annual_cell_count"], 18)
        self.assertEqual(value["directional_record_count"], 89460)
        self.assertTrue(value["dispatch_receipt_bound"])
        self.assertTrue(value["runtime_review_validated"])
        self.assertTrue(value["runtime_evidence_bound"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_failed_run380_is_rejected(self) -> None:
        run = _run()
        run["conclusion"] = "failure"
        with self.assertRaisesRegex(ValueError, "run conclusion mismatch"):
            review_2018_run380_evidence(
                repository_root=REPOSITORY_ROOT,
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                freeze_evidence=_freeze(),
                freeze_artifact_zip_sha256="f" * 64,
                dispatch_receipt=_receipt(),
                expected_head_sha=HEAD,
            )

    def test_dispatch_receipt_must_bind_target_run(self) -> None:
        receipt = _receipt()
        receipt["run_id"] = RUN_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "dispatch receipt run_id mismatch",
        ):
            review_2018_run380_evidence(
                repository_root=REPOSITORY_ROOT,
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                freeze_evidence=_freeze(),
                freeze_artifact_zip_sha256="f" * 64,
                dispatch_receipt=receipt,
                expected_head_sha=HEAD,
            )

    def test_dispatch_head_must_bind_target_head(self) -> None:
        receipt = _receipt()
        receipt["dispatch_head_sha"] = "b" * 40
        with self.assertRaisesRegex(
            ValueError,
            "dispatch receipt dispatch_head_sha mismatch",
        ):
            review_2018_run380_evidence(
                repository_root=REPOSITORY_ROOT,
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                freeze_evidence=_freeze(),
                freeze_artifact_zip_sha256="f" * 64,
                dispatch_receipt=receipt,
                expected_head_sha=HEAD,
            )

    def test_missing_artifact_is_rejected(self) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows.pop()
        with self.assertRaisesRegex(ValueError, "artifact inventory count"):
            review_2018_run380_evidence(
                repository_root=REPOSITORY_ROOT,
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                freeze_evidence=_freeze(),
                freeze_artifact_zip_sha256="f" * 64,
                dispatch_receipt=_receipt(),
                expected_head_sha=HEAD,
            )

    def test_tampered_freeze_is_rejected(self) -> None:
        freeze = copy.deepcopy(_freeze())
        freeze["annual_cell_count"] = 17
        with self.assertRaisesRegex(ValueError, "evidence fingerprint mismatch"):
            review_2018_run380_evidence(
                repository_root=REPOSITORY_ROOT,
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                freeze_evidence=freeze,
                freeze_artifact_zip_sha256="f" * 64,
                dispatch_receipt=_receipt(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_review_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2018_run380_evidence_review.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("review")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
