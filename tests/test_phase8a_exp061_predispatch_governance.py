from __future__ import annotations

import unittest

from fmp.discovery.market_learning_adapter import compile_cell_evidence
from fmp.discovery.pattern_miner import (
    ConfirmationReport,
    DiscoveryReport,
    InMemoryDiscoveryResult,
    StateModel,
    ValidationReport,
)
from fmp.discovery.predispatch_governance import (
    build_read_only_operator_plan,
    validate_first_run_guard,
    validate_no_prior_manual_main_runs,
    validate_read_only_operator_plan,
    validate_terminal_review,
)
from fmp.discovery.run_contract import (
    EXPECTED_CELLS,
    expected_artifact_names,
    expected_job_names,
)
from fmp.market_learning.evidence import EXPECTED_SOURCE_MANIFEST_SHA256


HEAD = "a" * 40
FEATURE_EVIDENCE = "b" * 64
OUTCOME_EVIDENCE = "c" * 64


def _run(
    *,
    run_id: int = 123,
    status: str = "queued",
    conclusion: str | None = None,
    head_sha: str = HEAD,
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": "phase8a-exp061-discovery",
        "path": ".github/workflows/phase8a-exp061-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "run_attempt": 1,
        "status": status,
        "conclusion": conclusion,
    }


def _listing(*runs: dict[str, object]) -> dict[str, object]:
    return {"workflow_runs": list(runs), "total_count": len(runs)}


def _empty_result(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> InMemoryDiscoveryResult:
    return InMemoryDiscoveryResult(
        state_model=StateModel(
            symbol=symbol,
            timeframe=timeframe,
            cutpoints=(),
        ),
        discovery=DiscoveryReport(
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon,
            active_continuous_features=(),
            enumerated_pattern_count=5,
            directional_hypothesis_count=10,
            qualifying_directional_hypothesis_count=0,
            deduplicated_directional_hypothesis_count=0,
            shortlist=(),
        ),
        confirmation=ConfirmationReport(evaluations=(), frozen=()),
        validation=ValidationReport(evaluations=(), validated=()),
    )


def _cell_evidence() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for symbol, timeframe, horizon in EXPECTED_CELLS:
        out.append(
            compile_cell_evidence(
                _empty_result(symbol, timeframe, horizon),
                code_commit=HEAD,
                processed_manifest_sha256=EXPECTED_SOURCE_MANIFEST_SHA256[symbol],
                feature_manifest_sha256=(
                    __import__("hashlib")
                    .sha256(f"feature:{symbol}:{timeframe}".encode())
                    .hexdigest()
                ),
                outcome_manifest_sha256=(
                    __import__("hashlib")
                    .sha256(f"outcome:{symbol}:{timeframe}".encode())
                    .hexdigest()
                ),
                feature_evidence_fingerprint=FEATURE_EVIDENCE,
                outcome_evidence_fingerprint=OUTCOME_EVIDENCE,
            )
        )
    return out


def _success_jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": index + 1,
                "name": name,
                "status": "completed",
                "conclusion": "success",
            }
            for index, name in enumerate(expected_job_names())
        ]
    }


def _success_artifacts() -> dict[str, object]:
    names = expected_artifact_names(code_commit=HEAD)
    return {
        "total_count": len(names),
        "artifacts": [
            {
                "id": index + 100,
                "name": name,
                "expired": False,
            }
            for index, name in enumerate(names)
        ],
    }


class Exp061PredispatchGovernanceTests(unittest.TestCase):
    def test_zero_prior_run_and_read_only_plan_expose_no_dispatch(self) -> None:
        zero = validate_no_prior_manual_main_runs(_listing())
        self.assertTrue(zero["authoritative_slot_observed_empty"])
        self.assertFalse(zero["workflow_dispatch_authorized"])

        plan = build_read_only_operator_plan(_listing())
        validate_read_only_operator_plan(plan)
        self.assertEqual(
            plan["stage"],
            "EXP061_READ_ONLY_AUTHORIZATION_GATE_REQUIRED",
        )
        self.assertTrue(plan["authoritative_slot_observed_empty"])
        self.assertNotIn("planned_dispatch_command", plan)
        self.assertNotIn("dispatch_command", plan)

    def test_first_run_guard_accepts_only_current_attempt_one_run(self) -> None:
        report = validate_first_run_guard(
            _listing(_run()),
            current_run_id=123,
            current_head_sha=HEAD,
        )
        self.assertTrue(report["first_run_guard_passed"])
        self.assertEqual(report["prior_manual_main_run_count"], 0)
        self.assertFalse(report["historical_discovery_execution_authorized"])

        with self.assertRaisesRegex(ValueError, "only manual-main run"):
            validate_first_run_guard(
                _listing(_run(run_id=122), _run(run_id=123)),
                current_run_id=123,
                current_head_sha=HEAD,
            )

    def test_operator_plan_fails_closed_on_multiple_runs(self) -> None:
        with self.assertRaisesRegex(ValueError, "multiple manual-main runs"):
            build_read_only_operator_plan(
                _listing(_run(run_id=1), _run(run_id=2))
            )

    def test_success_terminal_review_requires_exact_reproducible_evidence(self) -> None:
        from fmp.discovery.run_contract import compile_aggregate_evidence

        cells = _cell_evidence()
        aggregate = compile_aggregate_evidence(cells, code_commit=HEAD)
        review = validate_terminal_review(
            run=_run(status="completed", conclusion="success"),
            jobs_payload=_success_jobs(),
            artifacts_payload=_success_artifacts(),
            cell_evidence=cells,
            aggregate_evidence=aggregate,
        )
        self.assertEqual(
            review["stage"],
            "EXP061_HISTORICAL_RESULT_REVIEW_REQUIRED",
        )
        self.assertEqual(review["verified_cell_evidence_count"], 18)
        self.assertTrue(review["aggregate_evidence_verified"])
        self.assertEqual(review["validated_pattern_count"], 0)
        for field in (
            "workflow_dispatch_authorized",
            "historical_result_run_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
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
            self.assertFalse(review[field], field)

    def test_non_success_terminal_review_never_opens_retry(self) -> None:
        jobs = {
            "jobs": [
                {
                    "id": 1,
                    "name": "exp061-preflight",
                    "status": "completed",
                    "conclusion": "failure",
                }
            ]
        }
        artifacts = {
            "total_count": 1,
            "artifacts": [
                {
                    "id": 100,
                    "name": f"phase8a-exp061-preflight-{HEAD}",
                    "expired": False,
                }
            ],
        }
        review = validate_terminal_review(
            run=_run(status="completed", conclusion="failure"),
            jobs_payload=jobs,
            artifacts_payload=artifacts,
        )
        self.assertEqual(review["stage"], "EXP061_RUN_FAILURE_REVIEW_REQUIRED")
        self.assertEqual(review["failed_job_count"], 1)
        self.assertFalse(review["rerun_authorized"])
        self.assertFalse(review["retry_authorized"])
        self.assertFalse(review["replacement_run_authorized"])
        self.assertFalse(review["aggregate_artifact_present"])

    def test_success_rejects_missing_job_or_artifact(self) -> None:
        jobs = _success_jobs()
        raw_jobs = jobs["jobs"]
        assert isinstance(raw_jobs, list)
        raw_jobs.pop()
        with self.assertRaisesRegex(ValueError, "20-job inventory"):
            validate_terminal_review(
                run=_run(status="completed", conclusion="success"),
                jobs_payload=jobs,
                artifacts_payload=_success_artifacts(),
                cell_evidence=_cell_evidence(),
                aggregate_evidence=None,
            )


if __name__ == "__main__":
    unittest.main()
