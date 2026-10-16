"""DEC-1426: offline exact required CI job and acceptance-step review.

No CI runner, GitHub API, annual workflow, historical artifact, or trading
action is invoked. Only caller-supplied JSON-shaped synthetic dicts are read.
"""
from __future__ import annotations

import unittest

from test_dec1425_exact_ci_pr_affinity_offline import (
    ExactCommitCIIsNotRun385Permission, review_exact_pr_ci,
)

STEP_POLICY = {
    "tests": ("unit-tests", (
        "Run installed one-shot dispatch-authorization tests",
        "Run DEC-611 protected 2023 dispatch immutability audit tests",
        "Run DEC-612 2023 main lock readiness tests",
        "Run DEC-613 2023 administrator lock handoff tests",
        "Run DEC-626 inert three-job precheckout expression contract tests",
        "Run historical snapshot and general unit tests",
        "Compile package",
    )),
    "phase3-acceptance": ("acceptance", (
        "Generate deterministic Phase 3 acceptance evidence",
        "Verify evidence shape",
        "Upload Phase 3 acceptance evidence",
    )),
}


def review_exact_pr_ci_jobs(pr: object, runs: object,
                            jobs_by_run_id: object) -> tuple[str, ...]:
    """Snapshot check only; never return protected execution permission."""
    issues = list(review_exact_pr_ci(pr, runs))
    if type(jobs_by_run_id) is not dict:
        return tuple(sorted(set(issues + ["CI_JOB_SNAPSHOT_UNREVIEWED"])))
    if type(runs) is not list or not all(type(r) is dict for r in runs):
        return tuple(sorted(set(issues)))
    for name, (job_name, required_steps) in STEP_POLICY.items():
        matched = [r for r in runs if r.get("name") == name]
        if len(matched) != 1:
            continue
        run_id = matched[0].get("id")
        if type(run_id) is not int or run_id <= 0:
            continue
        jobs = jobs_by_run_id.get(run_id)
        if type(jobs) is not list or len(jobs) != 1 or type(jobs[0]) is not dict:
            issues.append(name + "_JOB_INVENTORY_UNREVIEWED")
            continue
        job = jobs[0]
        if job.get("name") != job_name:
            issues.append(name + "_JOB_NAME_UNREVIEWED")
        if type(job.get("run_id")) is not int or job["run_id"] != run_id:
            issues.append(name + "_JOB_RUN_ASSOCIATION_MISMATCH")
        if job.get("status") != "completed" or job.get("conclusion") != "success":
            issues.append(name + "_JOB_NOT_SUCCESSFUL")
        steps = job.get("steps")
        if type(steps) is not list or not all(type(s) is dict for s in steps):
            issues.append(name + "_JOB_STEPS_UNREVIEWED")
            continue
        numbers = [s.get("number") for s in steps]
        if not all(type(n) is int and n > 0 for n in numbers):
            issues.append(name + "_JOB_STEP_NUMBERS_UNREVIEWED")
        elif len(numbers) != len(set(numbers)):
            issues.append(name + "_JOB_STEP_NUMBERS_DUPLICATED")
        elif numbers != sorted(numbers):
            issues.append(name + "_JOB_STEP_SEQUENCE_UNREVIEWED")
        critical_positions = []
        for step_name in required_steps:
            matches = [s for s in steps if s.get("name") == step_name]
            if len(matches) != 1:
                issues.append(name + "_REQUIRED_STEP_INVENTORY_DRIFT")
                continue
            step = matches[0]
            if step.get("status") != "completed" or step.get("conclusion") != "success":
                issues.append(name + "_REQUIRED_STEP_NOT_SUCCESSFUL")
            if type(step.get("number")) is not int or step["number"] <= 0:
                issues.append(name + "_STEP_NUMBER_UNREVIEWED")
            else:
                critical_positions.append(step["number"])
        if (len(critical_positions) == len(required_steps) and
                critical_positions != sorted(set(critical_positions))):
            issues.append(name + "_CRITICAL_STEP_ORDER_DRIFT")
    return tuple(sorted(set(issues)))


class ActualRequiredStepEvidenceIsNotProtectedExecutionConsent(unittest.TestCase):
    def setUp(self):
        # Reuse only the synthetic fixture; do not re-inherit its 18 tests.
        ExactCommitCIIsNotRun385Permission.setUp(self)
        self.jobs_by_run = {}
        for i, name in enumerate(("phase3-acceptance", "tests")):
            run = next(r for r in self.runs if r["name"] == name)
            job_name, required_steps = STEP_POLICY[name]
            steps = [
                {"name": label, "number": num, "status": "completed",
                 "conclusion": "success"}
                for num, label in enumerate(required_steps, start=1)
            ]
            self.jobs_by_run[run["id"]] = [
                {"name": job_name, "id": 10000+i, "run_id": run["id"],
                 "status": "completed", "conclusion": "success",
                 "steps": steps}
            ]

    def verdict(self):
        return review_exact_pr_ci_jobs(self.pr, self.runs, self.jobs_by_run)

    def test_exact_successful_job_and_step_evidence_is_consistent(self):
        self.assertEqual(self.verdict(), ())

    def test_missing_historical_unit_test_step_is_not_green(self):
        self.jobs_by_run[8001][0]["steps"].pop(-2)
        self.assertIn("tests_REQUIRED_STEP_INVENTORY_DRIFT", self.verdict())

    def test_skipped_historical_unit_test_step_is_not_green(self):
        self.jobs_by_run[8001][0]["steps"][-2]["conclusion"] = "skipped"
        self.assertIn("tests_REQUIRED_STEP_NOT_SUCCESSFUL", self.verdict())

    def test_failed_compile_step_is_not_green(self):
        self.jobs_by_run[8001][0]["steps"][-1]["conclusion"] = "failure"
        self.assertIn("tests_REQUIRED_STEP_NOT_SUCCESSFUL", self.verdict())

    def test_missing_phase3_evidence_verification_is_not_green(self):
        self.jobs_by_run[8000][0]["steps"].pop(1)
        self.assertIn("phase3-acceptance_REQUIRED_STEP_INVENTORY_DRIFT",
                      self.verdict())

    def test_skipped_phase3_evidence_upload_is_not_green(self):
        self.jobs_by_run[8000][0]["steps"][2]["conclusion"] = "skipped"
        self.assertIn("phase3-acceptance_REQUIRED_STEP_NOT_SUCCESSFUL",
                      self.verdict())

    def test_duplicate_required_step_needs_review(self):
        self.jobs_by_run[8001][0]["steps"].append(
            dict(self.jobs_by_run[8001][0]["steps"][0]))
        self.assertIn("tests_REQUIRED_STEP_INVENTORY_DRIFT", self.verdict())

    def test_wrong_job_name_needs_review(self):
        self.jobs_by_run[8001][0]["name"] = "another-job"
        self.assertIn("tests_JOB_NAME_UNREVIEWED", self.verdict())

    def test_wrong_run_id_on_job_needs_review(self):
        self.jobs_by_run[8000][0]["run_id"] = 999
        self.assertIn("phase3-acceptance_JOB_RUN_ASSOCIATION_MISMATCH",
                      self.verdict())

    def test_job_failed_even_with_success_steps_needs_review(self):
        self.jobs_by_run[8001][0]["conclusion"] = "failure"
        self.assertIn("tests_JOB_NOT_SUCCESSFUL", self.verdict())

    def test_missing_job_list_needs_review(self):
        self.jobs_by_run.pop(8001)
        self.assertIn("tests_JOB_INVENTORY_UNREVIEWED", self.verdict())

    def test_duplicate_jobs_needs_review(self):
        self.jobs_by_run[8000].append(dict(self.jobs_by_run[8000][0]))
        self.assertIn("phase3-acceptance_JOB_INVENTORY_UNREVIEWED",
                      self.verdict())

    def test_absent_steps_array_needs_review(self):
        self.jobs_by_run[8000][0].pop("steps")
        self.assertIn("phase3-acceptance_JOB_STEPS_UNREVIEWED", self.verdict())

    def test_boolean_step_number_is_not_an_integer_proof(self):
        self.jobs_by_run[8001][0]["steps"][0]["number"] = True
        self.assertIn("tests_STEP_NUMBER_UNREVIEWED", self.verdict())

    def test_no_job_snapshot_is_not_green(self):
        self.assertIn("CI_JOB_SNAPSHOT_UNREVIEWED",
                      review_exact_pr_ci_jobs(self.pr, self.runs, None))

    def test_successful_source_job_summary_never_authorizes_annual_run(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())

    def test_reversing_historical_critical_step_numbers_is_flagged(self):
        a, b = self.jobs_by_run[8001][0]["steps"][-2:]
        a["number"], b["number"] = b["number"], a["number"]
        self.assertIn("tests_CRITICAL_STEP_ORDER_DRIFT", self.verdict())

    def test_reversing_phase3_verification_upload_order_is_flagged(self):
        steps = self.jobs_by_run[8000][0]["steps"]
        steps[1]["number"], steps[2]["number"] = (steps[2]["number"],
                                                  steps[1]["number"])
        self.assertIn("phase3-acceptance_CRITICAL_STEP_ORDER_DRIFT",
                      self.verdict())

    def test_duplicate_step_numbers_are_not_silent(self):
        steps = self.jobs_by_run[8001][0]["steps"]
        steps[1]["number"] = steps[0]["number"]
        self.assertIn("tests_JOB_STEP_NUMBERS_DUPLICATED", self.verdict())

    def test_out_of_order_step_array_is_not_silent(self):
        steps = self.jobs_by_run[8000][0]["steps"]
        steps.reverse()
        self.assertIn("phase3-acceptance_JOB_STEP_SEQUENCE_UNREVIEWED",
                      self.verdict())

    def test_zero_critical_step_number_is_not_silent(self):
        self.jobs_by_run[8000][0]["steps"][0]["number"] = 0
        self.assertIn("phase3-acceptance_JOB_STEP_NUMBERS_UNREVIEWED",
                      self.verdict())

    def test_boolean_critical_step_number_is_not_silent(self):
        self.jobs_by_run[8001][0]["steps"][0]["number"] = False
        self.assertIn("tests_JOB_STEP_NUMBERS_UNREVIEWED", self.verdict())

    def test_canonical_required_steps_have_monotone_unique_indices(self):
        self.assertEqual(self.verdict(), ())
        for jobs in self.jobs_by_run.values():
            indices = [step["number"] for step in jobs[0]["steps"]]
            self.assertEqual(indices, sorted(set(indices)))

    def test_phase3_generation_cannot_appear_after_upload(self):
        steps = self.jobs_by_run[8000][0]["steps"]
        steps[0]["number"], steps[2]["number"] = (steps[2]["number"],
                                                  steps[0]["number"])
        self.assertIn("phase3-acceptance_CRITICAL_STEP_ORDER_DRIFT",
                      self.verdict())


class RequiredJobStepFixtureIsolation(unittest.TestCase):
    def test_job_step_suite_does_not_inherit_unrelated_ci_tests(self):
        self.assertFalse(
            issubclass(
                ActualRequiredStepEvidenceIsNotProtectedExecutionConsent,
                ExactCommitCIIsNotRun385Permission,
            )
        )

    def test_job_step_suite_has_exactly_24_locally_defined_test_methods(self):
        # DEC-1426: 16, DEC-1427: 8; do not double count parent tests.
        names = [
            name for name, member in
            ActualRequiredStepEvidenceIsNotProtectedExecutionConsent.__dict__.items()
            if name.startswith("test_") and callable(member)
        ]
        self.assertEqual(len(names), 24)

    def test_local_job_step_fixture_still_builds_matching_run_evidence(self):
        case = ActualRequiredStepEvidenceIsNotProtectedExecutionConsent(
            methodName="test_exact_successful_job_and_step_evidence_is_consistent"
        )
        case.setUp()
        self.assertEqual(case.verdict(), ())
        self.assertEqual(set(case.jobs_by_run), {8000, 8001})


class AnnualSecurityCIProbeMustReallyRun(unittest.TestCase):
    def setUp(self):
        self.fixture = ActualRequiredStepEvidenceIsNotProtectedExecutionConsent(
            methodName="test_exact_successful_job_and_step_evidence_is_consistent"
        )
        self.fixture.setUp()

    def verdict(self):
        return self.fixture.verdict()

    def test_reviewed_2023_security_step_names_are_pinned_in_order(self):
        required = STEP_POLICY["tests"][1]
        self.assertEqual(required[:5], (
            "Run installed one-shot dispatch-authorization tests",
            "Run DEC-611 protected 2023 dispatch immutability audit tests",
            "Run DEC-612 2023 main lock readiness tests",
            "Run DEC-613 2023 administrator lock handoff tests",
            "Run DEC-626 inert three-job precheckout expression contract tests",
        ))
        self.assertEqual(self.verdict(), ())

    def test_missing_installed_dispatch_authorization_step_is_detected(self):
        self.fixture.jobs_by_run[8001][0]["steps"].pop(0)
        self.assertIn("tests_REQUIRED_STEP_INVENTORY_DRIFT", self.verdict())

    def test_skipped_2023_immutability_audit_step_is_detected(self):
        self.fixture.jobs_by_run[8001][0]["steps"][1]["conclusion"] = "skipped"
        self.assertIn("tests_REQUIRED_STEP_NOT_SUCCESSFUL", self.verdict())

    def test_failed_main_lock_readiness_step_is_detected(self):
        self.fixture.jobs_by_run[8001][0]["steps"][2]["conclusion"] = "failure"
        self.assertIn("tests_REQUIRED_STEP_NOT_SUCCESSFUL", self.verdict())

    def test_missing_administrator_handoff_step_is_detected(self):
        self.fixture.jobs_by_run[8001][0]["steps"].pop(3)
        self.assertIn("tests_REQUIRED_STEP_INVENTORY_DRIFT", self.verdict())

    def test_skipped_precheckout_expression_guard_test_is_detected(self):
        self.fixture.jobs_by_run[8001][0]["steps"][4]["conclusion"] = "skipped"
        self.assertIn("tests_REQUIRED_STEP_NOT_SUCCESSFUL", self.verdict())

    def test_synthetic_reviewed_steps_are_not_security_admission(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
