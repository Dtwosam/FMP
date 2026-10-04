from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2015_runtime_evidence_binding import (
    bind_2015_runtime_evidence,
    validate_2015_runtime_evidence_binding,
    validate_2015_runtime_evidence_binding_sources,
)


HEAD = "a" * 40


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


def _freeze() -> dict[str, object]:
    cell_job_ids = {
        f"annual-cell-2015-cell-{index:02d}": 1000 + index
        for index in range(18)
    }
    cell_artifacts = {
        f"phase8a-annual-catalogue-cell-2015-cell-{index:02d}-{HEAD}": _artifact(
            2000 + index,
            f"phase8a-annual-catalogue-cell-2015-cell-{index:02d}-{HEAD}",
            "d" * 64,
        )
        for index in range(18)
    }
    freeze: dict[str, object] = {
        "decision": "DEC-501",
        "version": "fmp-annual-catalogue-2015-replacement-run-freeze-v1",
        "run_review_source_blob_sha": "bfb9d286454b6bff14af7d0126c7d33ccb63b91f",
        "source_review_decision": "DEC-500",
        "source_review_version": "fmp-annual-catalogue-2015-replacement-run-review-v1",
        "stage": "ANNUAL_CATALOGUE_2015_REPLACEMENT_RUNTIME_EVIDENCE_FROZEN",
        "expected_head_sha": HEAD,
        "annual_segment_label": "2015",
        "run_id": 424242,
        "run_number": 377,
        "run_attempt": 1,
        "run_status": "completed",
        "run_conclusion": "success",
        "preflight_job_id": 9001,
        "freeze_job_id": 9002,
        "cell_job_ids": cell_job_ids,
        "preflight_artifact": _artifact(
            3001,
            f"phase8a-annual-catalogue-preflight-2015-{HEAD}",
            "e" * 64,
        ),
        "freeze_artifact": _artifact(
            3002,
            f"phase8a-annual-catalogue-freeze-2015-{HEAD}",
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
        "replacement_authorization_consumed": True,
        "runtime_review_validated": True,
        "runtime_evidence_frozen": True,
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
        "next_gate": "CONCRETE_2015_ANNUAL_PATTERN_CATALOGUE_RUNTIME_EVIDENCE_BINDING",
    }
    freeze["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(freeze)
    ).hexdigest()
    return freeze


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-502 requires the replacement runtime-freeze state",
)
class AnnualPatternCatalogue2015RuntimeEvidenceBindingTests(unittest.TestCase):
    def test_sources_pin_freeze_reviewer_and_repaired_workflow(self) -> None:
        source = validate_2015_runtime_evidence_binding_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["run_freeze_source_blob_sha"],
            "cf6accdf5137269fcdbad3eabd4fd6be1db4b3b3",
        )
        self.assertEqual(
            source["run_review_source_blob_sha"],
            "bfb9d286454b6bff14af7d0126c7d33ccb63b91f",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_binding_is_deterministic_and_preserves_concrete_inventory(self) -> None:
        first = bind_2015_runtime_evidence(
            _freeze(),
            repository_root=Path("."),
        )
        second = bind_2015_runtime_evidence(
            _freeze(),
            repository_root=Path("."),
        )
        self.assertIs(validate_2015_runtime_evidence_binding(first), first)
        self.assertEqual(
            first["binding_fingerprint_sha256"],
            second["binding_fingerprint_sha256"],
        )
        self.assertEqual(first["decision"], "DEC-502")
        self.assertEqual(first["run_number"], 377)
        self.assertEqual(first["run_attempt"], 1)
        self.assertEqual(len(first["cell_job_ids"]), 18)
        self.assertEqual(len(first["cell_artifacts"]), 18)
        self.assertEqual(first["annual_cell_count"], 18)
        self.assertEqual(first["directional_record_count"], 89460)
        self.assertTrue(first["replacement_authorization_consumed"])
        self.assertTrue(first["runtime_review_validated"])
        self.assertTrue(first["runtime_evidence_frozen"])
        self.assertTrue(first["runtime_evidence_bound"])
        self.assertFalse(first["next_segment_execution_authorized"])
        self.assertFalse(first["strategy_v1_synthesis_authorized"])
        self.assertFalse(first["trading_authorized"])

    def test_missing_cell_artifact_is_rejected_even_with_refingerprinted_freeze(self) -> None:
        freeze = _freeze()
        cell_artifacts = dict(freeze["cell_artifacts"])
        cell_artifacts.pop(next(iter(cell_artifacts)))
        freeze["cell_artifacts"] = cell_artifacts
        unsigned = dict(freeze)
        unsigned.pop("freeze_fingerprint_sha256", None)
        freeze["freeze_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "cell artifact inventory mismatch",
        ):
            bind_2015_runtime_evidence(
                freeze,
                repository_root=Path("."),
            )

    def test_refingerprinted_trading_authority_tamper_is_rejected(self) -> None:
        value = bind_2015_runtime_evidence(
            _freeze(),
            repository_root=Path("."),
        )
        tampered = copy.deepcopy(value)
        tampered["trading_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("binding_fingerprint_sha256", None)
        tampered["binding_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "trading_authorized must remain false",
        ):
            validate_2015_runtime_evidence_binding(tampered)

    def test_cli_is_bind_only(self) -> None:
        script = Path(
            "scripts/phase8a_annual_pattern_catalogue_2015_runtime_evidence_binding.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("bind")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
