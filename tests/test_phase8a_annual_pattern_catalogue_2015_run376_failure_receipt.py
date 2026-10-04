from __future__ import annotations

import copy
import unittest

from fmp.discovery.annual_pattern_catalogue_2015_run376_failure_receipt import (
    build_2015_run376_failure_receipt,
    validate_2015_run376_failure_receipt,
)


def _run() -> dict[str, object]:
    return {
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
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": 111404873333,
                "name": "annual-preflight-2015",
                "status": "completed",
                "conclusion": "failure",
            },
            {
                "id": 111404951408,
                "name": "annual-cell-skipped",
                "status": "completed",
                "conclusion": "skipped",
            },
            {
                "id": 111404951817,
                "name": "annual-freeze-skipped",
                "status": "completed",
                "conclusion": "skipped",
            },
        ]
    }


class AnnualCatalogue2015Run376FailureReceiptTests(unittest.TestCase):
    def test_exact_preflight_failure_is_frozen_without_new_authority(self) -> None:
        value = build_2015_run376_failure_receipt(
            run=_run(),
            jobs_payload=_jobs(),
        )
        self.assertIs(validate_2015_run376_failure_receipt(value), value)
        self.assertEqual(value["decision"], "DEC-526")
        self.assertEqual(value["run_number"], 376)
        self.assertEqual(value["run_conclusion"], "failure")
        self.assertTrue(value["downstream_jobs_skipped"])
        self.assertFalse(value["result_produced"])
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["retry_authorized"])
        self.assertFalse(value["run_377_authorized"])
        self.assertFalse(value["run_378_or_later_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_successful_run376_is_rejected(self) -> None:
        run = _run()
        run["conclusion"] = "success"
        with self.assertRaisesRegex(ValueError, "conclusion mismatch"):
            build_2015_run376_failure_receipt(
                run=run,
                jobs_payload=_jobs(),
            )

    def test_non_skipped_downstream_job_is_rejected(self) -> None:
        jobs = copy.deepcopy(_jobs())
        rows = jobs["jobs"]
        assert isinstance(rows, list)
        rows[1]["conclusion"] = "success"
        with self.assertRaisesRegex(ValueError, "downstream annual jobs"):
            build_2015_run376_failure_receipt(
                run=_run(),
                jobs_payload=jobs,
            )


if __name__ == "__main__":
    unittest.main()
