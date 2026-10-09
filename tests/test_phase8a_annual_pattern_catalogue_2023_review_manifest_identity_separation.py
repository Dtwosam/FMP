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

from fmp.discovery.annual_pattern_catalogue_2023_review_manifest_identity_separation import (
    ANNUAL_WORKFLOW_BLOB,
    DENIED,
    FIXTURE_SHA,
    FIXTURE_TAG,
    RUNTIME_GIT_BLOB,
    _fixture_manifest,
    _fixture_observation,
    _negative_matrix,
    _source_pins,
    build_review_manifest_identity_separation,
    synthetic_separate_reviewed_and_observed_match,
    validate_review_manifest_identity_separation,
)

ROOT = Path(__file__).resolve().parents[1]


def _refingerprint(report: dict[str, object]) -> None:
    unsigned = dict(report)
    unsigned.pop("report_sha256", None)
    report["report_sha256"] = hashlib.sha256(
        (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-625 requires installed annual workflow snapshot",
)
class ReviewedIdentitySeparationTests(unittest.TestCase):
    def test_source_pins_original_workflow_and_live_runtime_unchanged(self):
        pins = _source_pins(ROOT)
        self.assertEqual(pins["source_workflow_blob"], ANNUAL_WORKFLOW_BLOB)
        self.assertEqual(pins["source_runtime_blob"], RUNTIME_GIT_BLOB)
        self.assertEqual(len(pins["source_three_jobs"]), 3)

    def test_separate_fixture_matches_only_as_synthetic_comparison(self):
        manifest = _fixture_manifest()
        context = _fixture_observation()
        self.assertTrue(synthetic_separate_reviewed_and_observed_match(manifest, context))
        self.assertEqual(manifest["reviewed_code_sha"], FIXTURE_SHA)
        self.assertEqual(manifest["reviewed_tag_ref"], FIXTURE_TAG)
        self.assertEqual(context["github_workflow_sha"], FIXTURE_SHA)
        self.assertIn("UNAPPROVED", manifest["provenance"])
        self.assertNotIn("dispatch_authorized", manifest)

    def test_all_twenty_five_adverse_cases_fail_closed(self):
        rows = _negative_matrix()
        self.assertEqual(len(rows), 25)
        self.assertEqual(len({item["case"] for item in rows}), 25)
        self.assertTrue(all(item["synthetic_match"] is False for item in rows))
        self.assertIn(
            "self_attested_sha_rebound_on_both_sides",
            {item["case"] for item in rows},
        )
        self.assertIn(
            "self_attested_tag_rebound_on_both_sides",
            {item["case"] for item in rows},
        )

    def test_both_sides_rebound_does_not_approve_new_sha_or_tag(self):
        m = _fixture_manifest()
        o = _fixture_observation()
        m["reviewed_code_sha"] = "b" * 40
        m["reviewed_workflow_sha"] = "b" * 40
        o["github_sha"] = "b" * 40
        o["github_workflow_sha"] = "b" * 40
        self.assertFalse(synthetic_separate_reviewed_and_observed_match(m, o))
        m, o = _fixture_manifest(), _fixture_observation()
        m["reviewed_tag_ref"] += "-retarget"
        o["github_ref"] = m["reviewed_tag_ref"]
        o["github_workflow_ref"] += "-retarget"
        self.assertFalse(synthetic_separate_reviewed_and_observed_match(m, o))

    def test_type_mismatch_unknown_missing_or_malformed_fields_fail(self):
        for field, value in [
            ("github_run_number", True),
            ("github_run_attempt", 1.0),
            ("github_ref", None),
            ("github_workflow_sha", FIXTURE_SHA.upper()),
        ]:
            with self.subTest(field=field):
                o = _fixture_observation()
                o[field] = value
                self.assertFalse(synthetic_separate_reviewed_and_observed_match(_fixture_manifest(), o))
        self.assertFalse(synthetic_separate_reviewed_and_observed_match(None, _fixture_observation()))
        self.assertFalse(synthetic_separate_reviewed_and_observed_match(_fixture_manifest(), None))
        m = _fixture_manifest()
        m["extra"] = "yes"
        self.assertFalse(synthetic_separate_reviewed_and_observed_match(m, _fixture_observation()))
        o = _fixture_observation()
        o.pop("github_sha")
        self.assertFalse(synthetic_separate_reviewed_and_observed_match(_fixture_manifest(), o))

    def test_report_never_grants_authority(self):
        report = build_review_manifest_identity_separation(repository_root=ROOT)
        validate_review_manifest_identity_separation(report)
        self.assertEqual(report["expected_annual_run"], 385)
        self.assertEqual(report["expected_annual_attempt"], 1)
        self.assertEqual(report["expected_predecessor_run_id"], 37663157285)
        self.assertEqual(report["synthetic_cases_rejected"], 25)
        self.assertIs(report["dispatch_blocked"], True)
        for name in DENIED:
            with self.subTest(permission=name):
                self.assertIs(report[name], False)

    def test_rehashed_forgery_or_type_confusion_rejected(self):
        baseline = build_review_manifest_identity_separation(repository_root=ROOT)
        for name, fake in [
            ("reviewed_commit_approved", True),
            ("review_manifest_independently_authenticated", True),
            ("annual_dispatch_authorized", True),
            ("run385_action_authorized", True),
            ("immutable_tag_proven", True),
            ("trading_authorized", True),
            ("dispatch_blocked", 1),
            ("synthetic_cases_rejected", 25.0),
            ("expected_annual_run", True),
            ("negative_cases", []),
            ("synthetic_exact_match_only_not_execution_authority", 1),
        ]:
            with self.subTest(field=name):
                tampered = copy.deepcopy(baseline)
                tampered[name] = fake
                _refingerprint(tampered)
                with self.assertRaisesRegex(ValueError, "forged or source-drifted"):
                    validate_review_manifest_identity_separation(tampered)

    def test_assess_subprocess_emits_no_bytecode_in_clean_checkout(self):
        # A source grep cannot establish read-only behavior: Python can write
        # __pycache__ before the CLI even evaluates its output-path guard.
        with tempfile.TemporaryDirectory(prefix="dec625-no-bytecode-") as directory:
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
            script = checkout / "scripts" / "phase8a_annual_pattern_catalogue_2023_review_manifest_identity_separation.py"
            script.parent.mkdir(parents=True)
            shutil.copy2(ROOT / "scripts" / script.name, script)
            outfile = temp_root / "review.json"
            env = os.environ.copy()
            env["PYTHONPATH"] = str(checkout / "src")
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            env.pop("PYTHONPYCACHEPREFIX", None)
            result = subprocess.run(
                [sys.executable, str(script), "assess", "--out", str(outfile)],
                cwd=checkout, env=env, text=True, capture_output=True,
                timeout=40, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(outfile.is_file())
            self.assertEqual(json.loads(outfile.read_text())["decision"], "DEC-625")
            self.assertEqual(
                list((checkout / "src").rglob("*.pyc")), [],
                "Assess-only CLI must never emit source-package bytecode",
            )

    def test_cli_source_only_assess_and_off_checkout_output(self):
        source = (ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_review_manifest_identity_separation.py").read_text()
        self.assertIn('add_parser("assess")', source)
        self.assertIn("target.is_relative_to(checkout)", source)
        for banned in ("gh workflow run", "subprocess.", "requests.", "git tag", "git push", "os.system"):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()
