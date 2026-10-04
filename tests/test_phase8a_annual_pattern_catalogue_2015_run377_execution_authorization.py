from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2015_run377_execution_authorization import (
    build_2015_run377_execution_authorization,
    require_2015_run377_execution_authorized,
    validate_2015_run377_execution_authorization_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CODE_COMMIT = "a" * 40


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
        value = build_2015_run377_execution_authorization(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(value["decision"], "DEC-527")
        self.assertEqual(value["annual_segment_label"], "2015")
        self.assertEqual(value["expected_run_number"], 377)
        self.assertEqual(value["expected_run_attempt"], 1)
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
