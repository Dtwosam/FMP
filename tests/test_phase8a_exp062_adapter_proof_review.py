from __future__ import annotations

import unittest

from fmp.discovery.exp062_adapter_proof_review import (
    classify_exp062_adapter_proof_terminal,
    expected_artifact_names,
    expected_job_names,
)


HEAD = "a" * 40


def _run(*, conclusion: str = "success") -> dict[str, object]:
    return {
        "id": 41000000000,
        "name": "phase8a-exp062-adapter-proof",
        "path": ".github/workflows/phase8a-exp062-adapter-proof.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": conclusion,
    }


def _jobs(*, success: bool = True) -> dict[str, object]:
    names = expected_job_names()
    rows = []
    for index, name in enumerate(names, start=1):
        conclusion = "success"
        if not success and index == 1:
            conclusion = "failure"
        rows.append(
            {
                "id": 42000000000 + index,
                "name": name,
                "status": "completed",
                "conclusion": conclusion,
            }
        )
    return {"jobs": rows}


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": 43000000000 + index,
                "name": name,
                "expired": False,
            }
            for index, name in enumerate(
                expected_artifact_names(head_sha=HEAD),
                start=1,
            )
        ]
    }


class Exp062AdapterProofReviewTests(unittest.TestCase):
    def test_success_requires_exact_ten_jobs_and_artifacts(self) -> None:
        report = classify_exp062_adapter_proof_terminal(
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            report["stage"],
            "EXP062_ADAPTER_PROOF_SUCCESS_COMPLETE_REVIEW_REQUIRED",
        )
        self.assertTrue(report["proof_success_complete"])
        self.assertEqual(report["materialized_job_count"], 10)
        self.assertEqual(report["artifact_count"], 10)
        self.assertTrue(report["aggregate_content_review_required"])
        for field in (
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
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

    def test_success_missing_job_or_artifact_fails_closed(self) -> None:
        jobs = _jobs()
        jobs["jobs"] = jobs["jobs"][:-1]
        with self.assertRaisesRegex(
            ValueError,
            "exact ten-job inventory",
        ):
            classify_exp062_adapter_proof_terminal(
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_artifacts(),
                expected_head_sha=HEAD,
            )

        artifacts = _artifacts()
        artifacts["artifacts"] = artifacts["artifacts"][:-1]
        with self.assertRaisesRegex(
            ValueError,
            "exact ten-artifact inventory",
        ):
            classify_exp062_adapter_proof_terminal(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                expected_head_sha=HEAD,
            )

    def test_non_success_is_reviewable_but_authorizes_nothing(self) -> None:
        report = classify_exp062_adapter_proof_terminal(
            run=_run(conclusion="failure"),
            jobs_payload=_jobs(success=False),
            artifacts_payload={"artifacts": []},
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            report["stage"],
            "EXP062_ADAPTER_PROOF_NON_SUCCESS_REVIEW_REQUIRED",
        )
        self.assertFalse(report["proof_success_complete"])
        self.assertFalse(report["aggregate_content_review_required"])
        self.assertFalse(report["historical_discovery_execution_authorized"])
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_unexpected_job_or_artifact_is_rejected(self) -> None:
        jobs = _jobs()
        jobs["jobs"].append(
            {
                "id": 999,
                "name": "unexpected",
                "status": "completed",
                "conclusion": "success",
            }
        )
        with self.assertRaisesRegex(ValueError, "unexpected jobs"):
            classify_exp062_adapter_proof_terminal(
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_artifacts(),
                expected_head_sha=HEAD,
            )

        artifacts = _artifacts()
        artifacts["artifacts"].append(
            {
                "id": 999,
                "name": "unexpected",
                "expired": False,
            }
        )
        with self.assertRaisesRegex(ValueError, "artifact name is unexpected"):
            classify_exp062_adapter_proof_terminal(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                expected_head_sha=HEAD,
            )

    def test_wrong_head_attempt_or_nonterminal_run_is_rejected(self) -> None:
        run = _run()
        run["head_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "head_sha mismatch"):
            classify_exp062_adapter_proof_terminal(
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                expected_head_sha=HEAD,
            )

        run = _run()
        run["run_attempt"] = 2
        with self.assertRaisesRegex(ValueError, "run_attempt mismatch"):
            classify_exp062_adapter_proof_terminal(
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                expected_head_sha=HEAD,
            )

        run = _run()
        run["status"] = "in_progress"
        with self.assertRaisesRegex(ValueError, "status mismatch"):
            classify_exp062_adapter_proof_terminal(
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
