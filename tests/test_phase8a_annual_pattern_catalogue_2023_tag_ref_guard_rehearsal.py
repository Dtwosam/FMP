from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import (
    ANNUAL_WORKFLOW_PATH,
    EXPECTED_RUN_NUMBER,
    MAIN_REF_GUARD,
    REQUIRED_JOBS,
    build_2023_tag_ref_guard_rehearsal,
    synthetic_candidate_guard_matches,
    validate_2023_tag_ref_guard_rehearsal,
    verify_original_workflow_order,
)

ROOT = Path(__file__).resolve().parents[1]
TAG = "refs/tags/fmp/phase8a/2023/run385/reviewed-v1"
SHA = "a" * 40


def _args() -> dict[str, object]:
    return {
        "expected_tag_ref": TAG,
        "reviewed_commit_sha": SHA,
        "event_name": "workflow_dispatch",
        "github_ref": TAG,
        "github_sha": SHA,
        "annual_segment_label": "2023",
        "run_number": EXPECTED_RUN_NUMBER,
        "run_attempt": 1,
        "previous_annual_freeze_run_id": 37663157285,
    }


def _rehash(value: dict[str, object]) -> None:
    obj = dict(value)
    obj.pop("rehearsal_fingerprint_sha256", None)
    value["rehearsal_fingerprint_sha256"] = hashlib.sha256(
        (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-617 requires installed annual workflow for offline rehearsal",
)
class AnnualCatalogue2023TagRefGuardRehearsalTests(unittest.TestCase):
    def test_exact_original_source_and_guard_order(self):
        source = (ROOT / ANNUAL_WORKFLOW_PATH).read_text(encoding="utf-8")
        self.assertEqual(verify_original_workflow_order(source), list(REQUIRED_JOBS))
        report = build_2023_tag_ref_guard_rehearsal(
            repository_root=ROOT, candidate_tag_ref=TAG, reviewed_commit_sha=SHA,
        )
        validate_2023_tag_ref_guard_rehearsal(report)
        self.assertTrue(report["synthetic_matching_tuple_accepted_by_rehearsal"])
        self.assertEqual(report["reviewed_job_order"], list(REQUIRED_JOBS))
        self.assertEqual(report["expected_run_attempt"], 1)
        self.assertEqual(report["expected_predecessor_run_id"], 37663157285)
        self.assertFalse(report["active_workflow_tag_compatible"])
        self.assertFalse(report["candidate_guard_installed"])
        self.assertFalse(report["annual_workflow_dispatch_authorized"])
        self.assertTrue(report["dispatch_blocked"])
        self.assertFalse(report["trading_authorized"])

    def test_missing_duplicated_or_changed_job_guards_fail(self):
        source = (ROOT / ANNUAL_WORKFLOW_PATH).read_text(encoding="utf-8")
        for changed in (
            source.replace(MAIN_REF_GUARD, "", 1),
            source.replace(MAIN_REF_GUARD, MAIN_REF_GUARD + "\n          " + MAIN_REF_GUARD, 1),
            source.replace("  annual_cell:", "  corrupted_cell:", 1),
            source.replace('test "$GITHUB_EVENT_NAME" = "workflow_dispatch"', "", 1),
        ):
            with self.subTest(change=changed[:100]):
                with self.assertRaises(ValueError):
                    verify_original_workflow_order(changed)

    def test_reordering_guard_after_installer_is_rejected(self):
        source = (ROOT / ANNUAL_WORKFLOW_PATH).read_text(encoding="utf-8")
        first = source.index(MAIN_REF_GUARD)
        removed = source[:first] + source[first + len(MAIN_REF_GUARD):]
        insert_at = removed.index("- name: Fetch exact accepted EXP-044 source snapshots")
        moved = removed[:insert_at] + MAIN_REF_GUARD + "\n      " + removed[insert_at:]
        with self.assertRaisesRegex(ValueError, "ordering"):
            verify_original_workflow_order(moved)

    def test_synthetic_predicate_rejects_near_misses(self):
        baseline = _args()
        self.assertTrue(synthetic_candidate_guard_matches(**baseline))
        mutants = [
            {"event_name": "push"},
            {"github_ref": "refs/heads/main"},
            {"github_ref": TAG + "-moved"},
            {"github_sha": "b" * 40},
            {"annual_segment_label": "2024"},
            {"run_number": 384},
            {"run_number": 386},
            {"run_number": True},
            {"run_attempt": 2},
            {"run_attempt": True},
            {"previous_annual_freeze_run_id": 1},
            {"previous_annual_freeze_run_id": "37663157285"},
            {"expected_tag_ref": "refs/tags/fmp/phase8a/2023/run385/../bad"},
            {"reviewed_commit_sha": "A" * 40},
        ]
        for changed in mutants:
            with self.subTest(changed=changed):
                args = dict(baseline)
                args.update(changed)
                self.assertFalse(synthetic_candidate_guard_matches(**args))

    def test_recomputed_permission_and_execution_escalation_rejected(self):
        report = build_2023_tag_ref_guard_rehearsal(
            repository_root=ROOT, candidate_tag_ref=TAG, reviewed_commit_sha=SHA,
        )
        for key in (
            "dispatch_blocked", "active_workflow_tag_compatible",
            "candidate_guard_installed", "workflow_amendment_authorized",
            "runtime_amendment_authorized", "immutable_tag_proven",
            "annual_workflow_dispatch_authorized", "dispatch_action_executed",
            "retry_authorized", "broker_mutation_authorized", "trading_authorized",
        ):
            with self.subTest(key=key):
                tampered = copy.deepcopy(report)
                tampered[key] = not tampered[key]
                _rehash(tampered)
                with self.assertRaisesRegex(ValueError, "forbidden or changed field"):
                    validate_2023_tag_ref_guard_rehearsal(tampered)

    def test_unknown_field_and_invalid_tags_rejected(self):
        report = build_2023_tag_ref_guard_rehearsal(
            repository_root=ROOT, candidate_tag_ref=TAG, reviewed_commit_sha=SHA,
        )
        report["production_ready"] = True
        _rehash(report)
        with self.assertRaisesRegex(ValueError, "unauthorized report fields"):
            validate_2023_tag_ref_guard_rehearsal(report)
        for candidate in ("refs/heads/main", "refs/tags/fmp/phase8a/2023/run385/",
                          "refs/tags/fmp/phase8a/2023/run385/a.lock"):
            with self.assertRaisesRegex(ValueError, "invalid proposed"):
                build_2023_tag_ref_guard_rehearsal(
                    repository_root=ROOT, candidate_tag_ref=candidate,
                    reviewed_commit_sha=SHA,
                )

    def test_cli_assess_only_no_runtime_or_dispatch(self):
        script = (ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_tag_ref_guard_rehearsal.py").read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("assess")', script)
        for forbidden in (
            "gh workflow run", "git push", "git tag", "subprocess.",
            "gh api --method POST", 'sub.add_parser("dispatch")',
        ):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
