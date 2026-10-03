from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2016_run_freeze import (
    freeze_2016_run_review,
    validate_2016_run_freeze,
    validate_2016_run_freeze_sources,
)
from fmp.discovery.pattern_protocol import HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


HEAD = "a" * 40
RUN2_HEAD = "b" * 40
PREVIOUS_RUN_ID = 424242
RUN_ID = 525252


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _cell_job_names() -> list[str]:
    return [
        f"annual-cell-2016-{symbol}-{timeframe}-{horizon}m"
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
    ]


def _cell_artifact_names() -> list[str]:
    return [
        f"phase8a-annual-catalogue-cell-2016-{symbol}-{timeframe}-{horizon}m-{HEAD}"
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
    ]


def _artifact(artifact_id: int, name: str, digest: str) -> dict[str, object]:
    return {
        "id": artifact_id,
        "name": name,
        "digest": "sha256:" + digest,
        "size_in_bytes": 123,
    }


def _review() -> dict[str, object]:
    jobs = _cell_job_names()
    artifacts = _cell_artifact_names()
    value: dict[str, object] = {
        "decision": "DEC-512",
        "version": "fmp-annual-catalogue-2016-run-review-v1",
        "dispatch_preflight_source_blob_sha": "301214231775b83df99d1ff9f878f916ec76a07e",
        "segment_freeze_source_blob_sha": "1b14279864f01a1284c5be31552eee9bb3a2220c",
        "active_workflow_blob_sha": "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        "run_id": RUN_ID,
        "run_number": 3,
        "run_attempt": 1,
        "run_status": "completed",
        "run_conclusion": "success",
        "run_head_sha": HEAD,
        "preflight_job_id": 100,
        "freeze_job_id": 119,
        "cell_job_ids": {
            name: 101 + index
            for index, name in enumerate(jobs)
        },
        "preflight_artifact": _artifact(
            1000,
            f"phase8a-annual-catalogue-preflight-2016-{HEAD}",
            "e" * 64,
        ),
        "freeze_artifact": _artifact(
            1019,
            f"phase8a-annual-catalogue-freeze-2016-{HEAD}",
            "f" * 64,
        ),
        "cell_artifacts": {
            name: _artifact(1001 + index, name, "e" * 64)
            for index, name in enumerate(artifacts)
        },
        "source_dispatch_preflight_decision": "DEC-511",
        "source_dispatch_preflight_version": (
            "fmp-annual-catalogue-2016-dispatch-action-preflight-v1"
        ),
        "source_dispatch_preflight_fingerprint_sha256": "1" * 64,
        "annual_segment_label": "2016",
        "previous_annual_freeze_run_id": PREVIOUS_RUN_ID,
        "successful_2015_run_id": PREVIOUS_RUN_ID,
        "successful_2015_run_head_sha": RUN2_HEAD,
        "freeze_artifact_zip_sha256": "f" * 64,
        "freeze_evidence_canonical_sha256": "2" * 64,
        "freeze_evidence_fingerprint": "3" * 64,
        "annual_cell_count": 18,
        "directional_record_count": 89460,
        "evaluable_record_count": 18,
        "zero_support_record_count": 36,
        "total_support": 54,
        "dispatch_action_observed": True,
        "dispatch_action_preflight_consumed": True,
        "dispatch_authorization_consumed": True,
        "review_validated": True,
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
        "next_gate": "DETERMINISTIC_2016_RUNTIME_EVIDENCE_FREEZE",
    }
    value["review_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-513 requires the future DEC-512 review state",
)
class AnnualPatternCatalogue2016RunFreezeTests(unittest.TestCase):
    def test_source_pins_hardened_2016_reviewer(self) -> None:
        source = validate_2016_run_freeze_sources(repository_root=Path("."))
        self.assertEqual(
            source["run_review_source_blob_sha"],
            "b34720d135f06601e3a92432a90e041ee69fdd96",
        )

    def test_freeze_is_deterministic_and_preserves_runtime_identities(self) -> None:
        first = freeze_2016_run_review(
            _review(),
            repository_root=Path("."),
            expected_head_sha=HEAD,
        )
        second = freeze_2016_run_review(
            _review(),
            repository_root=Path("."),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2016_run_freeze(first), first)
        self.assertEqual(
            first["freeze_fingerprint_sha256"],
            second["freeze_fingerprint_sha256"],
        )
        self.assertEqual(first["decision"], "DEC-513")
        self.assertEqual(first["run_id"], RUN_ID)
        self.assertEqual(first["run_number"], 3)
        self.assertEqual(first["run_attempt"], 1)
        self.assertEqual(first["annual_segment_label"], "2016")
        self.assertEqual(first["previous_annual_freeze_run_id"], PREVIOUS_RUN_ID)
        self.assertEqual(first["successful_2015_run_head_sha"], RUN2_HEAD)
        self.assertTrue(first["dispatch_action_observed"])
        self.assertTrue(first["runtime_review_validated"])
        self.assertTrue(first["runtime_evidence_frozen"])
        self.assertFalse(first["next_segment_execution_authorized"])
        self.assertFalse(first["strategy_v1_synthesis_authorized"])
        self.assertFalse(first["trading_authorized"])

    def test_head_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "review head mismatch"):
            freeze_2016_run_review(
                _review(),
                repository_root=Path("."),
                expected_head_sha="c" * 40,
            )

    def test_refingerprinted_authority_tamper_is_rejected(self) -> None:
        value = freeze_2016_run_review(
            _review(),
            repository_root=Path("."),
            expected_head_sha=HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["next_segment_execution_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("freeze_fingerprint_sha256", None)
        tampered["freeze_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "next_segment_execution_authorized must remain false",
        ):
            validate_2016_run_freeze(tampered)

    def test_refingerprinted_review_inventory_tamper_is_rejected(self) -> None:
        review = _review()
        cell_job_ids = review["cell_job_ids"]
        assert isinstance(cell_job_ids, dict)
        first_name = next(iter(cell_job_ids))
        cell_job_ids[first_name] = review["preflight_job_id"]
        unsigned = dict(review)
        unsigned.pop("review_fingerprint_sha256", None)
        review["review_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "job ids must be unique"):
            freeze_2016_run_review(
                review,
                repository_root=Path("."),
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
