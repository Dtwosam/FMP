"""DEC-1725: executable synthetic checks for DEC-1716's narrow CI skip.

Only isolated temp paths and in-memory fake workflow step labels are inspected;
no original installed workflow, admin API, protected artifact or annual runner.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
TARGET = HERE / "test_dec1716_installed_annual_workflow_blocker_contract.py"


def _load_in_mode(mode: str | None):
    with mock.patch.dict(os.environ, {}, clear=False):
        if mode is None:
            os.environ.pop("FMP_PREINSTALL_SNAPSHOT", None)
        else:
            os.environ["FMP_PREINSTALL_SNAPSHOT"] = mode
        spec = importlib.util.spec_from_file_location("dec1716_isolated", TARGET)
        if spec is None or spec.loader is None:
            raise RuntimeError("DEC-1716 test source missing")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def _run(module):
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        module.InstalledAnnualWorkflowBlockerContractTests
    )
    result = unittest.TestResult()
    suite.run(result)
    return result


def _synthetic_jobs(module):
    common = [
        "Checkout",
        "Require exact merged main manual dispatch",
        "Set up Python",
        "Install pinned annual catalogue runtime",
    ]
    jobs = {}
    for job in module.JOBS:
        if job == "annual_preflight":
            steps = common[:2] + [
                "Resolve required prior annual segment"
            ] + common[2:] + [
                module.FIRST_EVIDENCE[job],
                "Validate exact accepted EXP-044 source snapshots",
                module.AFTER_INSTALL_AUTH[job],
                "Fetch exact prior annual freeze evidence",
            ]
        else:
            steps = common + [
                module.AFTER_INSTALL_AUTH[job],
                module.FIRST_EVIDENCE[job],
            ]
        jobs[job] = (
            "  " + job + ":\n" +
            "\n".join("      - name: " + name for name in steps) +
            '\n          test "$GITHUB_REF" = "refs/heads/main"\n'
        )
    return jobs


def _run_assertion(module, jobs, name):
    case = module.InstalledAnnualWorkflowBlockerContractTests(name)
    case.jobs = jobs
    getattr(case, name)()


class PreinstallSkipExecutableNegativeControls(unittest.TestCase):
    def test_exact_snapshot_one_skips_all_twelve_without_file_read(self):
        module = _load_in_mode("1")
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(module, "WORKFLOW",
                                   Path(tmp) / "MISSING.yml"):
                result = _run(module)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.testsRun, 12)
        self.assertEqual(len(result.skipped), 12)

    def test_missing_installed_workflow_fails_closed_when_unset(self):
        module = _load_in_mode(None)
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(module, "WORKFLOW",
                                   Path(tmp) / "MISSING.yml"):
                result = _run(module)
        self.assertEqual(len(result.skipped), 0)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("FileNotFoundError", result.errors[0][1])

    def test_nonexact_snapshot_aliases_do_not_skip(self):
        for mode in ("0", "true", "01", "yes"):
            with self.subTest(mode=mode):
                module = _load_in_mode(mode)
                self.assertFalse(
                    getattr(module.InstalledAnnualWorkflowBlockerContractTests,
                            "__unittest_skip__", False)
                )

    def test_synthetic_unsafe_original_ordering_is_recognized(self):
        module = _load_in_mode(None)
        jobs = _synthetic_jobs(module)
        for name in (
            "test_checkout_is_first_step_in_every_job",
            "test_main_ref_shell_guard_is_post_checkout_in_every_job",
            "test_jobs_lack_precheckout_job_level_admission_condition",
            "test_setup_and_install_precede_runtime_authorization_in_all_jobs",
            "test_preflight_metadata_fetch_is_before_execution_authorization",
            "test_cell_and_freeze_authorization_still_precede_download",
        ):
            with self.subTest(assertion=name):
                _run_assertion(module, jobs, name)

    def test_synthetic_checkout_reordering_is_detected(self):
        module = _load_in_mode(None)
        jobs = _synthetic_jobs(module)
        job = "annual_freeze"
        jobs[job] = jobs[job].replace(
            "      - name: Checkout\n"
            "      - name: Require exact merged main manual dispatch",
            "      - name: Require exact merged main manual dispatch\n"
            "      - name: Checkout",
        )
        with self.assertRaises(AssertionError):
            _run_assertion(
                module, jobs, "test_checkout_is_first_step_in_every_job")

    def test_synthetic_lost_main_ref_assertion_is_detected(self):
        module = _load_in_mode(None)
        jobs = _synthetic_jobs(module)
        jobs["annual_cell"] = jobs["annual_cell"].replace(
            'test "$GITHUB_REF" = "refs/heads/main"',
            'test "$GITHUB_REF" = "refs/heads/any"',
        )
        with self.assertRaises(AssertionError):
            _run_assertion(
                module, jobs,
                "test_main_ref_shell_guard_is_post_checkout_in_every_job")

    def test_synthetic_job_level_if_is_detected(self):
        module = _load_in_mode(None)
        jobs = _synthetic_jobs(module)
        jobs["annual_cell"] = jobs["annual_cell"].replace(
            "  annual_cell:\n", "  annual_cell:\n    if: true\n",
        )
        with self.assertRaises(AssertionError):
            _run_assertion(
                module, jobs,
                "test_jobs_lack_precheckout_job_level_admission_condition")

    def test_synthetic_preflight_authorization_move_is_detected(self):
        module = _load_in_mode(None)
        jobs = _synthetic_jobs(module)
        job = "annual_preflight"
        steps = module._steps(jobs[job])
        fetch = module.FIRST_EVIDENCE[job]
        authorize = module.AFTER_INSTALL_AUTH[job]
        steps.remove(authorize)
        steps.insert(steps.index(fetch), authorize)
        jobs[job] = "\n".join("      - name: " + s for s in steps)
        with self.assertRaises(AssertionError):
            _run_assertion(
                module, jobs,
                "test_preflight_metadata_fetch_is_before_execution_authorization")

    def test_synthetic_cell_authorization_move_is_detected(self):
        module = _load_in_mode(None)
        jobs = _synthetic_jobs(module)
        job = "annual_cell"
        jobs[job] = jobs[job].replace(
            "      - name: " + module.AFTER_INSTALL_AUTH[job] + "\n"
            "      - name: " + module.FIRST_EVIDENCE[job],
            "      - name: " + module.FIRST_EVIDENCE[job] + "\n"
            "      - name: " + module.AFTER_INSTALL_AUTH[job],
        )
        with self.assertRaises(AssertionError):
            _run_assertion(
                module, jobs,
                "test_cell_and_freeze_authorization_still_precede_download")

    def test_no_ambient_snapshot_environment_mutation(self):
        before = os.environ.get("FMP_PREINSTALL_SNAPSHOT")
        for value in ("1", "0", None):
            _load_in_mode(value)
        self.assertEqual(os.environ.get("FMP_PREINSTALL_SNAPSHOT"), before)
