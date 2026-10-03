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
)
from fmp.discovery.annual_pattern_catalogue_2015_replacement_run_freeze import (
    freeze_2015_replacement_run_review,
    validate_2015_replacement_run_freeze,
    validate_2015_replacement_run_freeze_sources,
)
from fmp.discovery.pattern_protocol import (
    HORIZONS_MINUTES,
    SYMBOLS,
    TIMEFRAMES,
)


HEAD = "a" * 40


def _summary(symbol: str, timeframe: str, horizon: int) -> ValidatedAnnualCellSummary:
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


def _freeze_evidence() -> dict[str, object]:
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
        "id": 424242,
        "name": "phase8a-annual-pattern-catalogue",
        "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": 376,
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
                "id": 100 + index,
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
    return {
        "artifacts": [
            {
                "id": 1000 + index,
                "name": name,
                "expired": False,
                "digest": (
                    "sha256:" + ("f" * 64 if "freeze-2015" in name else "e" * 64)
                ),
                "size_in_bytes": 123,
            }
            for index, name in enumerate(names)
        ]
    }


def _review() -> dict[str, object]:
    return review_2015_replacement_run(
        repository_root=Path("."),
        run=_run(),
        jobs_payload=_jobs(),
        artifacts_payload=_artifacts(),
        freeze_evidence=_freeze_evidence(),
        freeze_artifact_zip_sha256="f" * 64,
        expected_head_sha=HEAD,
    )


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-501 requires the replacement runtime-review state",
)
class AnnualPatternCatalogue2015ReplacementRunFreezeTests(unittest.TestCase):
    def test_source_pins_exact_reviewer(self) -> None:
        source = validate_2015_replacement_run_freeze_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["run_review_source_blob_sha"],
            "954718b9780004907c385ebb0496469d8433b844",
        )

    def test_freeze_is_deterministic_and_preserves_runtime_identities(self) -> None:
        first = freeze_2015_replacement_run_review(
            _review(),
            repository_root=Path("."),
            expected_head_sha=HEAD,
        )
        second = freeze_2015_replacement_run_review(
            _review(),
            repository_root=Path("."),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2015_replacement_run_freeze(first), first)
        self.assertEqual(
            first["freeze_fingerprint_sha256"],
            second["freeze_fingerprint_sha256"],
        )
        self.assertEqual(first["decision"], "DEC-501")
        self.assertEqual(first["run_number"], 376)
        self.assertEqual(first["run_attempt"], 1)
        self.assertEqual(first["annual_cell_count"], 18)
        self.assertEqual(first["directional_record_count"], 89460)
        self.assertTrue(first["replacement_authorization_consumed"])
        self.assertTrue(first["runtime_review_validated"])
        self.assertTrue(first["runtime_evidence_frozen"])
        self.assertFalse(first["next_segment_execution_authorized"])
        self.assertFalse(first["strategy_v1_synthesis_authorized"])
        self.assertFalse(first["trading_authorized"])

    def test_head_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "review head mismatch"):
            freeze_2015_replacement_run_review(
                _review(),
                repository_root=Path("."),
                expected_head_sha="b" * 40,
            )

    def test_refingerprinted_authority_tamper_is_rejected(self) -> None:
        value = freeze_2015_replacement_run_review(
            _review(),
            repository_root=Path("."),
            expected_head_sha=HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["trading_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("freeze_fingerprint_sha256", None)
        import hashlib
        import json
        payload = (
            json.dumps(
                unsigned,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
        tampered["freeze_fingerprint_sha256"] = hashlib.sha256(payload).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "trading_authorized must remain false",
        ):
            validate_2015_replacement_run_freeze(tampered)


if __name__ == "__main__":
    unittest.main()
