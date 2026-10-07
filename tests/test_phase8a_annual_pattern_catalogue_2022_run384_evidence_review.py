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
from fmp.discovery.annual_pattern_catalogue_2022_run384_evidence_review import (
    review_2022_run384_evidence,
    validate_2022_run384_evidence_review,
    validate_2022_run384_evidence_review_sources,
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
        annual_segment_label="2022",
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
        annual_segment_label="2022",
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
        "run_number": 384,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    names = ["annual-preflight-2022"]
    names.extend(
        f"annual-cell-2022-{symbol}-{timeframe}-{horizon}m"
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
    )
    names.append("annual-freeze-2022")
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
        f"phase8a-annual-catalogue-preflight-2022-{HEAD}",
        *[
            (
                f"phase8a-annual-catalogue-cell-2022-"
                f"{symbol}-{timeframe}-{horizon}m-{HEAD}"
            )
            for symbol in SYMBOLS
            for timeframe in TIMEFRAMES
            for horizon in HORIZONS_MINUTES
        ],
        f"phase8a-annual-catalogue-freeze-2022-{HEAD}",
    ]
    rows = []
    for index, name in enumerate(names):
        digest = "f" * 64 if "freeze-2022" in name else "e" * 64
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
        "decision": "DEC-600",
        "stage": "ANNUAL_CATALOGUE_2022_RUN_384_DISPATCH_SUBMITTED",
        "source_preflight_decision": "DEC-599",
        "source_preflight_workflow_run_id": 37657193417,
        "source_preflight_workflow_head_sha": (
            "246a452bc146da3463d81aed2395294b3a53f58c"
        ),
        "source_preflight_artifact_id": 11500265123,
        "source_preflight_artifact_digest": (
            "sha256:05b22b33b49c10e5650a3fe7862846ee8ca7f7be8d042f39952161254043135a"
        ),
        "source_preflight_fingerprint_sha256": (
            "c046f502b6e231cb506e5b8c6430e259983ac2eb93d1d632840185aae40897bf"
        ),
        "dispatch_head_sha": HEAD,
        "annual_segment_label": "2022",
        "previous_annual_freeze_run_id": 37531960014,
        "run_id": RUN_ID,
        "run_number": 384,
        "run_attempt": 1,
        "run_head_sha": HEAD,
        "dispatch_submitted": True,
        "result_claimed": False,
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
        "next_gate": "REVIEW_2022_RUN_384_BEFORE_CROSS_YEAR_COMPARISON",
    }


@unittest.skipIf(
    PREINSTALL_SNAPSHOT,
    "DEC-601 requires the installed 2022 runtime state",
)
class AnnualPatternCatalogue2022Run384EvidenceReviewTests(unittest.TestCase):
    def test_sources_pin_current_runtime_and_preflight(self) -> None:
        source = validate_2022_run384_evidence_review_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["segment_evidence_source_blob_sha"],
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
        )
        self.assertEqual(
            source["dispatch_action_preflight_source_blob_sha"],
            "34a805b3ab9038e847097f51a3fcc1d5c1806a53",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        )

    def test_successful_run384_is_bound_read_only(self) -> None:
        value = review_2022_run384_evidence(
            repository_root=REPOSITORY_ROOT,
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            freeze_evidence=_freeze(),
            freeze_artifact_zip_sha256="f" * 64,
            dispatch_receipt=_receipt(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2022_run384_evidence_review(value), value)
        self.assertEqual(value["decision"], "DEC-601")
        self.assertEqual(value["annual_segment_label"], "2022")
        self.assertEqual(value["run_id"], RUN_ID)
        self.assertEqual(value["run_number"], 384)
        self.assertEqual(value["run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37531960014)
        self.assertEqual(value["annual_cell_count"], 18)
        self.assertEqual(value["directional_record_count"], 89460)
        self.assertTrue(value["dispatch_receipt_bound"])
        self.assertTrue(value["runtime_review_validated"])
        self.assertTrue(value["runtime_evidence_bound"])
        self.assertTrue(value["final_required_annual_segment_bound"])
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["retry_authorized"])
        self.assertFalse(value["replacement_run_authorized"])
        self.assertFalse(value["run_385_or_later_authorized"])
        self.assertFalse(value["protected_history_access_authorized"])
        self.assertFalse(value["cross_year_comparison_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertEqual(
            value["next_gate"],
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_CROSS_YEAR_COMPARISON_PREFLIGHT",
        )

    def test_failed_run384_is_rejected(self) -> None:
        run = _run()
        run["conclusion"] = "failure"
        with self.assertRaisesRegex(ValueError, "run conclusion mismatch"):
            review_2022_run384_evidence(
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
            review_2022_run384_evidence(
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
            review_2022_run384_evidence(
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
            review_2022_run384_evidence(
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
            review_2022_run384_evidence(
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
            / "scripts/phase8a_annual_pattern_catalogue_2022_run384_evidence_review.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("review")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
