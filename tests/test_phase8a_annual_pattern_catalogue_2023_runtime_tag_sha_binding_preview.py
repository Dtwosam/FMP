from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_runtime_tag_sha_binding_preview import (
    ANNUAL_WORKFLOW_PATH,
    FIXTURE_SHA,
    FIXTURE_TAG,
    PREDECESSOR_RUN_ID,
    RUNTIME_GIT_BLOB,
    RUNTIME_PATH,
    _fixture_context,
    _scenarios,
    _source_contract,
    build_2023_runtime_tag_sha_binding_preview,
    synthetic_runtime_tag_identity_matches,
    validate_2023_runtime_tag_sha_binding_preview,
)

ROOT = Path(__file__).resolve().parents[1]


def _rehash(report: dict[str, object]) -> None:
    unsigned = dict(report)
    unsigned.pop("report_sha256", None)
    report["report_sha256"] = hashlib.sha256(
        (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-622 requires pinned installed annual source and 2023 runtime",
)
class InertRuntimeTagShaBindingPreviewTests(unittest.TestCase):
    def test_exact_fixture_matches_only_synthetic_contract(self):
        fixture = _fixture_context()
        self.assertTrue(synthetic_runtime_tag_identity_matches(fixture))
        report = build_2023_runtime_tag_sha_binding_preview(repository_root=ROOT)
        validate_2023_runtime_tag_sha_binding_preview(report)
        self.assertEqual(report["scenario_count"], 23)
        self.assertTrue(report["scenario_results"][0]["synthetic_predicate_match"])
        self.assertTrue(all(
            not row["synthetic_predicate_match"]
            for row in report["scenario_results"][1:]
        ))
        self.assertEqual(report["expected_run_number"], 385)
        self.assertEqual(report["expected_run_attempt"], 1)
        self.assertEqual(report["expected_previous_2022_freeze_run_id"], PREDECESSOR_RUN_ID)
        self.assertEqual(report["fixture_tag_ref_not_approved"], FIXTURE_TAG)
        self.assertEqual(report["fixture_reviewed_sha_not_approved"], FIXTURE_SHA)
        self.assertFalse(report["installed_runtime_ref_sha_binding"])
        self.assertFalse(report["installed_workflow_tag_ref_binding"])
        self.assertFalse(report["authoritative_immutable_tag_proven"])
        self.assertFalse(report["live_github_context_authenticated"])
        self.assertFalse(report["annual_workflow_dispatch_authorized"])
        self.assertFalse(report["annual_run385_action_authorized"])
        self.assertFalse(report["trading_authorized"])
        self.assertTrue(report["dispatch_blocked"])

    def test_mismatched_event_repo_workflow_path_ref_sha_year_run_attempt(self):
        base = _fixture_context()
        self.assertEqual(len(_scenarios()), 19)
        for name, key, value in _scenarios():
            with self.subTest(name=name):
                item = dict(base)
                item[key] = value
                self.assertFalse(synthetic_runtime_tag_identity_matches(item))
        for key in ("github_sha", "github_ref", "github_workflow_ref",
                    "github_run_number", "annual_segment_label"):
            with self.subTest(missing_key=key):
                item = dict(base)
                del item[key]
                self.assertFalse(synthetic_runtime_tag_identity_matches(item))
        item = dict(base)
        item["immutable_tag_proven"] = True
        self.assertFalse(synthetic_runtime_tag_identity_matches(item))
        self.assertFalse(synthetic_runtime_tag_identity_matches(None))

    def test_installed_main_only_workflow_and_runtime_source_pinned(self):
        source = _source_contract(ROOT)
        self.assertEqual(source["source_annual_workflow_path"], ANNUAL_WORKFLOW_PATH)
        self.assertEqual(source["source_runtime_path"], RUNTIME_PATH)
        self.assertEqual(source["source_runtime_git_blob"], RUNTIME_GIT_BLOB)
        self.assertEqual(
            source["original_annual_jobs"],
            ["annual_preflight", "annual_cell", "annual_freeze"],
        )
        self.assertTrue(source["active_main_only_guard_detected"])
        self.assertTrue(source["active_runtime_only_checks_commit_syntax_not_exact_tag_binding"])

    def test_forged_permission_flags_and_retyped_boolean_are_rejected(self):
        baseline = build_2023_runtime_tag_sha_binding_preview(repository_root=ROOT)
        for key, modified in (
            ("annual_workflow_dispatch_authorized", True),
            ("annual_run385_action_authorized", True),
            ("authoritative_immutable_tag_proven", True),
            ("installed_runtime_ref_sha_binding", True),
            ("live_github_context_authenticated", True),
            ("retry_authorized", True),
            ("trading_authorized", True),
            ("dispatch_blocked", 1),
            ("one_synthetic_fixture_matches", 1),
            ("expected_run_number", 385.0),
        ):
            with self.subTest(key=key):
                forged = copy.deepcopy(baseline)
                forged[key] = modified
                _rehash(forged)
                with self.assertRaisesRegex(ValueError, "source-bound exact report mismatch"):
                    validate_2023_runtime_tag_sha_binding_preview(forged)

    def test_forged_scenario_or_source_record_fails_after_refingerprint(self):
        baseline = build_2023_runtime_tag_sha_binding_preview(repository_root=ROOT)
        for change in ("scenario", "source", "injected"):
            with self.subTest(change=change):
                forged = copy.deepcopy(baseline)
                if change == "scenario":
                    forged["scenario_results"][1]["synthetic_predicate_match"] = True
                elif change == "source":
                    forged["source_runtime_git_blob"] = "b" * 40
                else:
                    forged["approved_token"] = "invented"
                _rehash(forged)
                with self.assertRaisesRegex(ValueError, "source-bound exact report mismatch"):
                    validate_2023_runtime_tag_sha_binding_preview(forged)

    def test_cli_assess_only_cannot_write_checkout_or_dispatch(self):
        code = (
            ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_runtime_tag_sha_binding_preview.py"
        ).read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("assess")', code)
        self.assertIn("target.is_relative_to(checkout)", code)
        for prohibited in (
            "gh workflow run", "subprocess.", "requests.", "git push", "git tag",
            "os.system", 'sub.add_parser("dispatch")',
        ):
            self.assertNotIn(prohibited, code)


if __name__ == "__main__":
    unittest.main()
