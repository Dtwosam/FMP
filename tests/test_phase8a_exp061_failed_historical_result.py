from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.historical_failed_result_decision import (
    EXPECTED_CELL_FAILURE_FEATURES,
    EXP061_FAILED_RESULT_DECISION,
    EXP061_HISTORICAL_HEAD_SHA,
    EXP061_HISTORICAL_RUN_ID,
    freeze_failed_historical_result,
    validate_failed_result_sources,
)


def _run() -> dict[str, object]:
    return {
        "id": EXP061_HISTORICAL_RUN_ID,
        "name": "phase8a-exp061-discovery",
        "path": ".github/workflows/phase8a-exp061-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": EXP061_HISTORICAL_HEAD_SHA,
        "run_number": 2,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _jobs() -> dict[str, object]:
    jobs: list[dict[str, object]] = [
        {
            "id": 1,
            "name": "exp061-preflight",
            "status": "completed",
            "conclusion": "success",
        }
    ]
    for index, name in enumerate(sorted(EXPECTED_CELL_FAILURE_FEATURES), start=2):
        jobs.append(
            {
                "id": index,
                "name": name,
                "status": "completed",
                "conclusion": "failure",
            }
        )
    jobs.append(
        {
            "id": 20,
            "name": "exp061-aggregate",
            "status": "completed",
            "conclusion": "skipped",
        }
    )
    return {"jobs": jobs}


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": 10937316246,
                "name": (
                    "phase8a-exp061-preflight-"
                    "a7b3bc2d0b196da2631b64c19331efb3af12c98e"
                ),
                "digest": (
                    "sha256:e9a898df51317250944ad0a111d01d96"
                    "d2081d708ea80872ed11b5cee48d356f"
                ),
                "expired": False,
            }
        ]
    }


def _executor_artifact() -> dict[str, object]:
    return {
        "id": 10936194549,
        "digest": (
            "sha256:e7ffe1f08ce358eca210ef4139716519"
            "6cb64bee31696a180c7fd02af8c68f1c"
        ),
        "expired": False,
    }


class Exp061FailedHistoricalResultTests(unittest.TestCase):
    def test_sources_bind_exact_failed_run_stack(self) -> None:
        report = validate_failed_result_sources(repository_root=Path("."))
        self.assertEqual(
            report["market_learning_adapter"],
            "978a33554fad7e9d78b002778c4896be0af3333a",
        )
        self.assertEqual(
            report["terminal_review"],
            "2df4caa00aa683b8d627d061ae806178fbd5cd9c",
        )

    def test_exact_failure_is_frozen_and_closes_slot(self) -> None:
        report = freeze_failed_historical_result(
            repository_root=Path("."),
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            executor_artifact=_executor_artifact(),
            cell_failure_features=EXPECTED_CELL_FAILURE_FEATURES,
        )
        self.assertEqual(report["decision"], EXP061_FAILED_RESULT_DECISION)
        self.assertEqual(
            report["stage"],
            "EXP061_HISTORICAL_RESULT_FAILED_AND_FROZEN",
        )
        self.assertEqual(report["failed_cell_count"], 18)
        self.assertEqual(report["preflight_conclusion"], "success")
        self.assertEqual(report["aggregate_conclusion"], "skipped")
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertTrue(report["failure_before_pattern_mining"])
        self.assertFalse(report["pattern_hypothesis_result_produced"])
        self.assertEqual(
            report["observed_nonfinite_features"],
            ["realized_vol_1h", "realized_vol_8h"],
        )
        for field in (
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(report[field], field)

    def test_failure_signature_drift_is_rejected(self) -> None:
        signatures = dict(EXPECTED_CELL_FAILURE_FEATURES)
        signatures["exp061-cell-EURUSD-5m-60m"] = "return_1h"
        with self.assertRaisesRegex(
            ValueError,
            "cell failure signature map mismatch",
        ):
            freeze_failed_historical_result(
                repository_root=Path("."),
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                executor_artifact=_executor_artifact(),
                cell_failure_features=signatures,
            )

    def test_any_cell_success_is_rejected(self) -> None:
        jobs = _jobs()
        rows = jobs["jobs"]
        assert isinstance(rows, list)
        rows[1]["conclusion"] = "success"
        with self.assertRaisesRegex(
            ValueError,
            "every cell job to fail",
        ):
            freeze_failed_historical_result(
                repository_root=Path("."),
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_artifacts(),
                executor_artifact=_executor_artifact(),
                cell_failure_features=EXPECTED_CELL_FAILURE_FEATURES,
            )

    def test_extra_result_artifact_is_rejected(self) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows.append(
            {
                "id": 999,
                "name": "unexpected",
                "digest": "sha256:" + "0" * 64,
                "expired": False,
            }
        )
        with self.assertRaises(ValueError):
            freeze_failed_historical_result(
                repository_root=Path("."),
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                executor_artifact=_executor_artifact(),
                cell_failure_features=EXPECTED_CELL_FAILURE_FEATURES,
            )


if __name__ == "__main__":
    unittest.main()
