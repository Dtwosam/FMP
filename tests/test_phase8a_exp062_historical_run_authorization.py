from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_run_authorization import (
    EXP062_HISTORICAL_RUN_AUTHORIZATION_DECISION,
    EXPECTED_PROOF_RUN,
    HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED,
    build_historical_run_authorization_contract,
    classify_historical_run_inventory,
    validate_historical_run_authorization_sources,
)


def _proof_run() -> dict[str, object]:
    return dict(EXPECTED_PROOF_RUN)


def _runs(*extra: dict[str, object]) -> dict[str, object]:
    return {
        "workflow_runs": [
            _proof_run(),
            *extra,
        ]
    }


def _historical_run(
    *,
    run_id: int = 40000000000,
    head_sha: str = "a" * 40,
    status: str = "queued",
    conclusion: str | None = None,
    run_number: int = 2,
    run_attempt: int = 1,
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": "phase8a-exp062-discovery",
        "path": ".github/workflows/phase8a-exp062-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "run_number": run_number,
        "run_attempt": run_attempt,
        "status": status,
        "conclusion": conclusion,
    }


class Exp062HistoricalRunAuthorizationTests(unittest.TestCase):
    def test_dec307_source_validator_pins_repaired_stack(self) -> None:
        self.assertTrue(HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED)
        report = validate_historical_run_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            report["decision"],
            EXP062_HISTORICAL_RUN_AUTHORIZATION_DECISION,
        )
        self.assertEqual(report["expected_cell_count"], 18)
        self.assertEqual(
            report["historical_data_end_exclusive"],
            "2023-01-01T00:00:00Z",
        )
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(
            report["historical_discovery_execution_authorized"]
        )
        self.assertFalse(report["reserved_robustness_access_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_exact_frozen_proof_leaves_historical_slot_available(self) -> None:
        report = classify_historical_run_inventory(_runs())
        self.assertEqual(
            report["stage"],
            "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE",
        )
        self.assertEqual(report["proof_run_count"], 1)
        self.assertEqual(report["historical_result_attempt_count"], 0)
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_source_authorized"])
        self.assertFalse(report["historical_result_dispatch_authorized"])

    def test_builder_authorizes_source_slot_but_not_dispatch(self) -> None:
        report = build_historical_run_authorization_contract(
            repository_root=Path("."),
            workflow_runs_payload=_runs(),
        )
        self.assertEqual(
            report["stage"],
            "EXP062_HISTORICAL_RESULT_SOURCE_AUTHORIZED_DISPATCH_LOCKED",
        )
        self.assertEqual(report["future_historical_run_number"], 2)
        self.assertEqual(report["future_historical_run_attempt"], 1)
        self.assertTrue(report["terminal_outcome_consumes_slot"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(
            report["historical_discovery_execution_authorized"]
        )
        self.assertFalse(report["discovery_result_authorized"])

    def test_one_later_attempt_consumes_slot_even_while_running(self) -> None:
        report = classify_historical_run_inventory(
            _runs(_historical_run(status="in_progress"))
        )
        self.assertEqual(
            report["stage"],
            "EXP062_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED",
        )
        self.assertEqual(report["historical_result_attempt_count"], 1)
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertFalse(report["rerun_authorized"])
        self.assertFalse(report["replacement_run_authorized"])

        with self.assertRaisesRegex(ValueError, "requires an unused slot"):
            build_historical_run_authorization_contract(
                repository_root=Path("."),
                workflow_runs_payload=_runs(
                    _historical_run(status="in_progress")
                ),
            )

    def test_terminal_failure_also_consumes_slot(self) -> None:
        report = classify_historical_run_inventory(
            _runs(
                _historical_run(
                    status="completed",
                    conclusion="failure",
                )
            )
        )
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertEqual(report["historical_result_run_conclusion"], "failure")

    def test_missing_or_changed_proof_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "exactly the frozen DEC-306 proof run",
        ):
            classify_historical_run_inventory({"workflow_runs": []})

        changed = _proof_run()
        changed["head_sha"] = "b" * 40
        with self.assertRaisesRegex(
            ValueError,
            "frozen proof run head_sha mismatch",
        ):
            classify_historical_run_inventory(
                {"workflow_runs": [changed]}
            )

    def test_second_historical_attempt_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "multiple attempts"):
            classify_historical_run_inventory(
                _runs(
                    _historical_run(run_id=40000000001),
                    _historical_run(
                        run_id=40000000002,
                        head_sha="b" * 40,
                    ),
                )
            )

    def test_historical_run_number_or_attempt_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "run number must be 2"):
            classify_historical_run_inventory(
                _runs(_historical_run(run_number=3))
            )

        with self.assertRaisesRegex(
            ValueError,
            "run attempt must remain 1",
        ):
            classify_historical_run_inventory(
                _runs(_historical_run(run_attempt=2))
            )

    def test_historical_run_cannot_reuse_proof_head(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "cannot reuse the frozen proof head",
        ):
            classify_historical_run_inventory(
                _runs(
                    _historical_run(
                        head_sha=str(EXPECTED_PROOF_RUN["head_sha"])
                    )
                )
            )

    def test_terminal_state_shape_is_strict(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "non-terminal.*cannot have a conclusion",
        ):
            classify_historical_run_inventory(
                _runs(
                    _historical_run(
                        status="in_progress",
                        conclusion="success",
                    )
                )
            )

        with self.assertRaisesRegex(
            ValueError,
            "completed.*requires a conclusion",
        ):
            classify_historical_run_inventory(
                _runs(
                    _historical_run(
                        status="completed",
                        conclusion=None,
                    )
                )
            )


if __name__ == "__main__":
    unittest.main()
