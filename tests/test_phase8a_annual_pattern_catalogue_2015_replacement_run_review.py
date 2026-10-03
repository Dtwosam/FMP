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
from fmp.discovery.annual_pattern_catalogue_2015_replacement_run_review import (
    review_2015_replacement_run,
    validate_2015_replacement_run_review,
    validate_2015_replacement_run_review_sources,
)
from fmp.discovery.pattern_protocol import (
    HORIZONS_MINUTES,
    SYMBOLS,
    TIMEFRAMES,
)


HEAD = "a" * 40
RUN_ID = 424242


def _summary(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> ValidatedAnnualCellSummary:
    return ValidatedAnnualCellSummary(
        annual_segment_label="2015",
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
    summaries = [
        _summary(symbol, timeframe, horizon)
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
    ]
    return compile_annual_segment_freeze(
        summaries,
        annual_segment_label="2015",
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
        "run_number": 2,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    names = ["annual-preflight-2015"]
    names.extend(
        f"annual-cell-2015-{symbol}-{timeframe}-{horizon}m"
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
    )
    names.append("annual-freeze-2015")
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
        f"phase8a-annual-catalogue-preflight-2015-{HEAD}",
        *[
            (
                f"phase8a-annual-catalogue-cell-2015-"
                f"{symbol}-{timeframe}-{horizon}m-{HEAD}"
            )
            for symbol in SYMBOLS
            for timeframe in TIMEFRAMES
            for horizon in HORIZONS_MINUTES
        ],
        f"phase8a-annual-catalogue-freeze-2015-{HEAD}",
    ]
    rows = []
    for index, name in enumerate(names):
        digest = "f" * 64 if "freeze-2015" in name else "e" * 64
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


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-500 requires the authorized replacement runtime state",
)
class AnnualPatternCatalogue2015ReplacementRunReviewTests(unittest.TestCase):
    def test_sources_pin_dispatch_freeze_contract_and_workflow(self) -> None:
        source = validate_2015_replacement_run_review_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dispatch_preflight_source_blob_sha"],
            "6701d3607d1576a81848810ec699ffd5b7a858a1",
        )
        self.assertEqual(
            source["segment_freeze_source_blob_sha"],
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        )

    def test_successful_runtime_evidence_is_reviewed(self) -> None:
        value = review_2015_replacement_run(
            repository_root=Path("."),
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            freeze_evidence=_freeze(),
            freeze_artifact_zip_sha256="f" * 64,
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2015_replacement_run_review(value), value)
        self.assertEqual(value["decision"], "DEC-500")
        self.assertEqual(value["run_id"], RUN_ID)
        self.assertEqual(value["run_number"], 2)
        self.assertEqual(value["run_attempt"], 1)
        self.assertEqual(value["run_conclusion"], "success")
        self.assertEqual(value["annual_cell_count"], 18)
        self.assertEqual(value["directional_record_count"], 89460)
        self.assertTrue(value["replacement_authorization_consumed"])
        self.assertTrue(value["review_validated"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_failed_job_is_rejected(self) -> None:
        jobs = _jobs()
        rows = jobs["jobs"]
        assert isinstance(rows, list)
        rows[1] = dict(rows[1])
        rows[1]["conclusion"] = "failure"
        with self.assertRaisesRegex(ValueError, "job not successful"):
            review_2015_replacement_run(
                repository_root=Path("."),
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_artifacts(),
                freeze_evidence=_freeze(),
                freeze_artifact_zip_sha256="f" * 64,
                expected_head_sha=HEAD,
            )

    def test_missing_artifact_is_rejected(self) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows.pop()
        with self.assertRaisesRegex(ValueError, "artifact inventory count"):
            review_2015_replacement_run(
                repository_root=Path("."),
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                freeze_evidence=_freeze(),
                freeze_artifact_zip_sha256="f" * 64,
                expected_head_sha=HEAD,
            )

    def test_tampered_freeze_is_rejected(self) -> None:
        freeze = copy.deepcopy(_freeze())
        freeze["annual_cell_count"] = 17
        with self.assertRaisesRegex(ValueError, "evidence fingerprint mismatch"):
            review_2015_replacement_run(
                repository_root=Path("."),
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                freeze_evidence=freeze,
                freeze_artifact_zip_sha256="f" * 64,
                expected_head_sha=HEAD,
            )

    def test_wrong_run_number_is_rejected(self) -> None:
        run = _run()
        run["run_number"] = 3
        with self.assertRaisesRegex(ValueError, "run run_number mismatch"):
            review_2015_replacement_run(
                repository_root=Path("."),
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                freeze_evidence=_freeze(),
                freeze_artifact_zip_sha256="f" * 64,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
