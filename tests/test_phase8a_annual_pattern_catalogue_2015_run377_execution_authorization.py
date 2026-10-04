from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2015_run376_failure_receipt import (
    build_2015_run376_failure_receipt,
)
from fmp.discovery.annual_pattern_catalogue_2015_run377_execution_authorization import (
    build_2015_run377_execution_authorization,
    require_2015_run377_execution_authorized,
    validate_2015_run377_execution_authorization_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CODE_COMMIT = "a" * 40


def _run376_failure_receipt() -> dict[str, object]:
    return build_2015_run376_failure_receipt(
        run={
            "id": 37191637168,
            "name": "phase8a-annual-pattern-catalogue",
            "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3",
            "run_number": 376,
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "failure",
        },
        jobs_payload={
            "jobs": [
                {
                    "id": 111404873333,
                    "name": "annual-preflight-2015",
                    "status": "completed",
                    "conclusion": "failure",
                },
                {
                    "id": 111404951408,
                    "name": "annual-cell-${{ inputs.annual_segment_label }}-${{ matrix.dataset.symbol }}-${{ matrix.dataset.timeframe }}-${{ matrix.dataset.horizon }}m",
                    "status": "completed",
                    "conclusion": "skipped",
                },
                {
                    "id": 111404951817,
                    "name": "annual-freeze-${{ inputs.annual_segment_label }}",
                    "status": "completed",
                    "conclusion": "skipped",
                },
            ]
        },
    )


class AnnualCatalogue2015Run377ExecutionAuthorizationTests(unittest.TestCase):
    def test_sources_pin_failed_run376_corrected_install_and_active_workflow(self) -> None:
        value = validate_2015_run377_execution_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            value["run376_failure_source_blob_sha"],
            "b57b055129f57be1e3164c3b24a53bf5a0277a57",
        )
        self.assertEqual(
            value["corrected_install_source_blob_sha"],
            "9c8237350484e3153f938a4df86d7f1c9955582e",
        )
        self.assertEqual(
            value["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_exact_fresh_run377_is_authorized_without_retry_authority(self) -> None:
        receipt = _run376_failure_receipt()
        value = build_2015_run377_execution_authorization(
            repository_root=REPOSITORY_ROOT,
            run376_failure_receipt=receipt,
        )
        self.assertEqual(value["decision"], "DEC-527")
        self.assertEqual(value["annual_segment_label"], "2015")
        self.assertEqual(value["expected_run_number"], 377)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["source_failure_decision"], "DEC-526")
        self.assertEqual(value["failed_run_id"], 37191637168)
        self.assertEqual(value["failed_run_number"], 376)
        self.assertEqual(
            value["source_failure_receipt_fingerprint_sha256"],
            receipt["receipt_fingerprint_sha256"],
        )
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertFalse(value["rerun_run376_authorized"])
        self.assertFalse(value["retry_run376_authorized"])
        self.assertFalse(value["run_378_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["broker_mutation_authorized"])
        self.assertFalse(value["trading_authorized"])

        require_2015_run377_execution_authorized(
            annual_segment_label="2015",
            code_commit=CODE_COMMIT,
            run_number=377,
            run_attempt=1,
        )

    def test_run376_rerun_and_run378_are_rejected(self) -> None:
        for run_number in (376, 378):
            with self.subTest(run_number=run_number):
                with self.assertRaisesRegex(
                    PermissionError,
                    "only workflow run 377",
                ):
                    require_2015_run377_execution_authorized(
                        annual_segment_label="2015",
                        code_commit=CODE_COMMIT,
                        run_number=run_number,
                        run_attempt=1,
                    )

    def test_wrong_segment_or_attempt_is_rejected(self) -> None:
        with self.assertRaisesRegex(PermissionError, "only annual segment 2015"):
            require_2015_run377_execution_authorized(
                annual_segment_label="2016",
                code_commit=CODE_COMMIT,
                run_number=377,
                run_attempt=1,
            )
        with self.assertRaisesRegex(PermissionError, "attempt 1"):
            require_2015_run377_execution_authorized(
                annual_segment_label="2015",
                code_commit=CODE_COMMIT,
                run_number=377,
                run_attempt=2,
            )


if __name__ == "__main__":
    unittest.main()
