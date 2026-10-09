from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_precheckout_job_if_preview import (
    DENIED,
    PLACEMENT,
    _candidate_expression,
    _candidate_jobs,
    _negatives,
    build_precheckout_job_if_preview,
    synthetic_precheckout_job_if_preview_matches,
    validate_precheckout_job_if_preview,
)

ROOT = Path(__file__).resolve().parents[1]


def _resign(report: dict[str, object]) -> None:
    unsigned = dict(report)
    unsigned.pop("report_sha256", None)
    report["report_sha256"] = hashlib.sha256(
        (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-626 requires installed annual workflow source",
)
class PrecheckoutJobIfPreviewTests(unittest.TestCase):
    def test_all_three_jobs_have_same_precheckout_static_gate(self):
        jobs = _candidate_jobs()
        self.assertEqual(set(jobs), {"annual_preflight", "annual_cell", "annual_freeze"})
        self.assertTrue(synthetic_precheckout_job_if_preview_matches(jobs))
        for job, spec in jobs.items():
            with self.subTest(job=job):
                self.assertEqual(spec["placement"], PLACEMENT)
                self.assertEqual(spec["expression"], _candidate_expression())

    def test_expression_is_literal_no_self_attested_expected_identity(self):
        expr = _candidate_expression()
        self.assertTrue(expr.startswith("$" + "{{ "))
        self.assertTrue(expr.endswith(" }}"))
        self.assertIn("github.event_name == 'workflow_dispatch'", expr)
        self.assertIn("github.ref_type == 'tag'", expr)
        self.assertIn("github.sha == '" + "a" * 40 + "'", expr)
        self.assertIn("github.workflow_sha == '" + "a" * 40 + "'", expr)
        self.assertIn("github.run_number == 385", expr)
        self.assertIn("github.run_attempt == 1", expr)
        self.assertIn("inputs.previous_annual_freeze_run_id == '37663157285'", expr)
        self.assertNotIn("github.sha == github.sha", expr)
        self.assertNotIn("github.ref == github.ref", expr)
        self.assertNotIn("github.workflow_sha == github.workflow_sha", expr)
        self.assertNotIn("vars.", expr)
        self.assertNotIn("secrets.", expr)

    def test_twenty_four_missing_late_weakened_retyped_cases_fail(self):
        rows = _negatives()
        self.assertEqual(len(rows), 24)
        self.assertTrue(all(x["candidate_exact_match"] is False for x in rows))
        self.assertEqual(len({(x["job"], x["attack"]) for x in rows}), 24)
        self.assertEqual(len({x["job"] for x in rows}), 3)

    def test_missing_job_unknown_job_wrong_type_or_extra_permission_fail(self):
        good = _candidate_jobs()
        cases = []
        missing = copy.deepcopy(good)
        del missing["annual_cell"]
        cases.append(missing)
        extra = copy.deepcopy(good)
        extra["annual_extra"] = {"placement": PLACEMENT, "expression": _candidate_expression()}
        cases.append(extra)
        wrong = copy.deepcopy(good)
        wrong["annual_preflight"] = ["wrong"]
        cases.append(wrong)
        extra_auth = copy.deepcopy(good)
        extra_auth["annual_freeze"]["dispatch"] = True
        cases.append(extra_auth)
        for case in cases:
            self.assertFalse(synthetic_precheckout_job_if_preview_matches(case))

    def test_report_source_bound_and_all_live_permissions_denied(self):
        report = build_precheckout_job_if_preview(repository_root=ROOT)
        validate_precheckout_job_if_preview(report)
        self.assertEqual(report["adversarial_case_count"], 24)
        self.assertEqual(
            report["source"]["source_workflow_blob"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertTrue(report["dispatch_blocked"])
        for item in DENIED:
            self.assertIs(report[item], False)

    def test_rehashed_authorization_and_type_confusion_rejected(self):
        report = build_precheckout_job_if_preview(repository_root=ROOT)
        variants = (
            ("annual_dispatch_authorized", True),
            ("candidate_job_if_installed", True),
            ("admin_no_bypass_lock_proven", True),
            ("trading_authorized", True),
            ("dispatch_blocked", 1),
            ("adversarial_case_count", 24.0),
            ("job_if_conditions_would_apply_to_all_three_jobs_before_checkout", 1),
            ("adversarial_cases", []),
            ("jobs", {}),
        )
        for key, value in variants:
            with self.subTest(field=key):
                forged = copy.deepcopy(report)
                forged[key] = value
                _resign(forged)
                with self.assertRaisesRegex(ValueError, "report body does not match pinned source"):
                    validate_precheckout_job_if_preview(forged)

    def test_assess_process_does_not_emit_bytecode_to_checkout(self):
        with tempfile.TemporaryDirectory(prefix="dec626-no-bytecode-") as directory:
            temp_root = Path(directory)
            checkout = temp_root / "checkout"
            shutil.copytree(
                ROOT / "src" / "fmp",
                checkout / "src" / "fmp",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            workflow = checkout / ".github" / "workflows" / "phase8a-annual-pattern-catalogue.yml"
            workflow.parent.mkdir(parents=True)
            shutil.copy2(ROOT / ".github" / "workflows" / workflow.name, workflow)
            script = checkout / "scripts" / "phase8a_annual_pattern_catalogue_2023_precheckout_job_if_preview.py"
            script.parent.mkdir(parents=True)
            shutil.copy2(ROOT / "scripts" / script.name, script)
            output = temp_root / "job-if.json"
            env = os.environ.copy()
            env["PYTHONPATH"] = str(checkout / "src")
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            env.pop("PYTHONPYCACHEPREFIX", None)
            proc = subprocess.run(
                [sys.executable, str(script), "assess", "--out", str(output)],
                cwd=checkout, env=env, text=True, capture_output=True,
                timeout=40, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(output.is_file())
            self.assertEqual(json.loads(output.read_text())["decision"], "DEC-626")
            self.assertEqual(list((checkout / "src").rglob("*.pyc")), [])

    def test_assess_only_command_source_has_no_execution_or_checkout_writes(self):
        content = (ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_precheckout_job_if_preview.py").read_text()
        self.assertIn('add_parser("assess")', content)
        self.assertIn("source_checkout = Path(__file__).resolve().parents[1]", content)
        self.assertIn("target = args.out.resolve()", content)
        self.assertIn("target.is_relative_to(source_checkout)", content)
        self.assertNotIn("target.is_relative_to(checkout)", content)
        for forbidden in ("gh workflow run", "subprocess.", "requests.", "git push", "git tag", "os.system"):
            self.assertNotIn(forbidden, content)


if __name__ == "__main__":
    unittest.main()
