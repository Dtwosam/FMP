from __future__ import annotations

import copy
import hashlib
import json
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
from fmp.discovery.annual_pattern_catalogue_2016_run_review import (
    review_2016_run,
    validate_2016_run_review,
    validate_2016_run_review_sources,
)
from fmp.discovery.pattern_protocol import (
    HORIZONS_MINUTES,
    SYMBOLS,
    TIMEFRAMES,
)


HEAD = "a" * 40
RUN2_HEAD = "b" * 40
RUN_ID = 525252
PREVIOUS_RUN_ID = 424242


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _dispatch_preflight() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-511",
        "version": "fmp-annual-catalogue-2016-dispatch-action-preflight-v1",
        "authorization_source_blob_sha": "8de76c1d3a576d365a3d99f15336868165123dd0",
        "active_workflow_blob_sha": "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        "annual_workflow_run_count": 2,
        "failed_first_run_id": 37126711695,
        "successful_2015_run_id": PREVIOUS_RUN_ID,
        "successful_2015_run_head_sha": RUN2_HEAD,
        "source_authorization_decision": "DEC-510",
        "source_authorization_version": "fmp-annual-catalogue-2016-dispatch-authorization-v1",
        "source_authorization_fingerprint_sha256": "1" * 64,
        "stage": "ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": HEAD,
        "install_commit_sha": HEAD,
        "active_workflow_path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "annual_segment_label": "2016",
        "previous_annual_freeze_run_id": PREVIOUS_RUN_ID,
        "expected_run_number": 3,
        "expected_run_attempt": 1,
        "dispatch_ref": "main",
        "dispatch_input_annual_segment_label": "2016",
        "dispatch_input_previous_annual_freeze_run_id": str(PREVIOUS_RUN_ID),
        "dispatch_parameters_frozen": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "preflight_read_only": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "fourth_or_later_run_authorized": False,
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
        "next_gate": "EXACT_2016_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN",
    }
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


def _summary(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> ValidatedAnnualCellSummary:
    return ValidatedAnnualCellSummary(
        annual_segment_label="2016",
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
        annual_segment_label="2016",
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
        "run_number": 3,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    names = ["annual-preflight-2016"]
    names.extend(
        f"annual-cell-2016-{symbol}-{timeframe}-{horizon}m"
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
    )
    names.append("annual-freeze-2016")
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
        f"phase8a-annual-catalogue-preflight-2016-{HEAD}",
        *[
            (
                f"phase8a-annual-catalogue-cell-2016-"
                f"{symbol}-{timeframe}-{horizon}m-{HEAD}"
            )
            for symbol in SYMBOLS
            for timeframe in TIMEFRAMES
            for horizon in HORIZONS_MINUTES
        ],
        f"phase8a-annual-catalogue-freeze-2016-{HEAD}",
    ]
    rows = []
    for index, name in enumerate(names):
        digest = "f" * 64 if "freeze-2016" in name else "e" * 64
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
    "DEC-512 requires the future successful 2016 runtime state",
)
class AnnualPatternCatalogue2016RunReviewTests(unittest.TestCase):
    def test_sources_pin_dispatch_preflight_freeze_contract_and_workflow(self) -> None:
        source = validate_2016_run_review_sources(repository_root=Path("."))
        self.assertEqual(
            source["dispatch_preflight_source_blob_sha"],
            "301214231775b83df99d1ff9f878f916ec76a07e",
        )
        self.assertEqual(
            source["segment_freeze_source_blob_sha"],
            "1b14279864f01a1284c5be31552eee9bb3a2220c",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        )

    def test_successful_future_2016_runtime_evidence_is_reviewed(self) -> None:
        value = review_2016_run(
            _dispatch_preflight(),
            repository_root=Path("."),
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            freeze_evidence=_freeze(),
            freeze_artifact_zip_sha256="f" * 64,
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2016_run_review(value), value)
        self.assertEqual(value["decision"], "DEC-512")
        self.assertEqual(value["run_id"], RUN_ID)
        self.assertEqual(value["run_number"], 3)
        self.assertEqual(value["run_attempt"], 1)
        self.assertEqual(value["annual_segment_label"], "2016")
        self.assertEqual(value["previous_annual_freeze_run_id"], PREVIOUS_RUN_ID)
        self.assertEqual(value["successful_2015_run_head_sha"], RUN2_HEAD)
        self.assertEqual(value["annual_cell_count"], 18)
        self.assertEqual(value["directional_record_count"], 89460)
        self.assertTrue(value["dispatch_action_observed"])
        self.assertTrue(value["dispatch_action_preflight_consumed"])
        self.assertTrue(value["dispatch_authorization_consumed"])
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
            review_2016_run(
                _dispatch_preflight(),
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
            review_2016_run(
                _dispatch_preflight(),
                repository_root=Path("."),
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                freeze_evidence=_freeze(),
                freeze_artifact_zip_sha256="f" * 64,
                expected_head_sha=HEAD,
            )

    def test_wrong_run_number_is_rejected(self) -> None:
        run = _run()
        run["run_number"] = 4
        with self.assertRaisesRegex(ValueError, "run run_number mismatch"):
            review_2016_run(
                _dispatch_preflight(),
                repository_root=Path("."),
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                freeze_evidence=_freeze(),
                freeze_artifact_zip_sha256="f" * 64,
                expected_head_sha=HEAD,
            )

    def test_dispatch_preflight_head_drift_is_rejected(self) -> None:
        preflight = _dispatch_preflight()
        preflight["expected_head_sha"] = "c" * 40
        unsigned = dict(preflight)
        unsigned.pop("preflight_fingerprint_sha256", None)
        preflight["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "install/main commit mismatch",
        ):
            review_2016_run(
                preflight,
                repository_root=Path("."),
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                freeze_evidence=_freeze(),
                freeze_artifact_zip_sha256="f" * 64,
                expected_head_sha=HEAD,
            )

    def test_refingerprinted_next_segment_authority_tamper_is_rejected(self) -> None:
        value = review_2016_run(
            _dispatch_preflight(),
            repository_root=Path("."),
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            freeze_evidence=_freeze(),
            freeze_artifact_zip_sha256="f" * 64,
            expected_head_sha=HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["next_segment_execution_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("review_fingerprint_sha256", None)
        tampered["review_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "next_segment_execution_authorized must remain false",
        ):
            validate_2016_run_review(tampered)


if __name__ == "__main__":
    unittest.main()
