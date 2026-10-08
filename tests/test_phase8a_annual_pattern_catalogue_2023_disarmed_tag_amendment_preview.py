from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_disarmed_tag_amendment_preview import (
    ANNUAL_WORKFLOW_PATH,
    HARD_STOP_MESSAGE,
    MAIN_REF_GUARD,
    NOT_APPROVED_REF,
    _preview,
    build_2023_disarmed_tag_amendment_preview,
    validate_2023_disarmed_tag_amendment_preview,
)
from fmp.discovery.annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import (
    verify_original_workflow_order,
)

ROOT = Path(__file__).resolve().parents[1]


def _recompute(value: dict[str, object]) -> None:
    unsigned = dict(value)
    unsigned.pop("preview_fingerprint_sha256", None)
    value["preview_fingerprint_sha256"] = hashlib.sha256(
        (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-618 requires active installed annual source to review offline",
)
class DisarmedTagAmendmentPreviewTests(unittest.TestCase):
    def test_original_source_preserved_and_preview_disarmed(self):
        old = (ROOT / ANNUAL_WORKFLOW_PATH).read_text(encoding="utf-8")
        self.assertEqual(len(verify_original_workflow_order(old)), 3)
        proposal, diff = _preview(old)
        self.assertNotEqual(proposal, old)
        self.assertEqual(proposal.count(HARD_STOP_MESSAGE), 3)
        self.assertEqual(proposal.count(NOT_APPROVED_REF), 3)
        self.assertEqual(proposal.count(MAIN_REF_GUARD), 0)
        self.assertEqual(proposal.replace(
            f'test "$GITHUB_REF" = "{NOT_APPROVED_REF}"\n'
            f'          echo "{HARD_STOP_MESSAGE}" >&2\n'
            '          exit 1',
            MAIN_REF_GUARD,
        ), old)
        self.assertEqual(diff.count("+          exit 1"), 3)
        self.assertEqual(diff.count("-          " + MAIN_REF_GUARD), 3)
        report = build_2023_disarmed_tag_amendment_preview(repository_root=ROOT)
        validate_2023_disarmed_tag_amendment_preview(report)
        self.assertEqual(report["preview_unified_diff"], diff)
        self.assertTrue(report["live_annual_workflow_unchanged"])
        self.assertFalse(report["candidate_workflow_installed"])
        self.assertFalse(report["workflow_tag_execution_compatible"])
        self.assertFalse(report["annual_workflow_dispatch_authorized"])
        self.assertFalse(report["run_385_current_state_independently_verified"])
        self.assertTrue(report["dispatch_blocked"])
        self.assertFalse(report["trading_authorized"])

    def test_unexpected_original_guards_cannot_generate_preview(self):
        original = (ROOT / ANNUAL_WORKFLOW_PATH).read_text(encoding="utf-8")
        for modified in (
            original.replace(MAIN_REF_GUARD, "", 1),
            original.replace(MAIN_REF_GUARD, MAIN_REF_GUARD + "\n          " + MAIN_REF_GUARD, 1),
            original.replace("  annual_cell:", "  altered_cell:", 1),
        ):
            with self.subTest(modified=modified[:40]):
                with self.assertRaises(ValueError):
                    _preview(modified)

    def test_rehashed_attempt_to_claim_authority_is_rejected(self):
        baseline = build_2023_disarmed_tag_amendment_preview(repository_root=ROOT)
        for name in (
            "candidate_workflow_installed", "runtime_amendment_installed",
            "workflow_tag_execution_compatible", "immutable_tag_proven",
            "annual_workflow_dispatch_authorized", "dispatch_action_executed",
            "tag_creation_authorized", "retry_authorized", "trading_authorized",
            "dispatch_blocked", "live_annual_workflow_unchanged",
        ):
            with self.subTest(name=name):
                changed = copy.deepcopy(baseline)
                changed[name] = not changed[name]
                _recompute(changed)
                with self.assertRaisesRegex(ValueError, "forbidden or changed field"):
                    validate_2023_disarmed_tag_amendment_preview(changed)

    def test_unexpected_extension_and_removed_stop_are_rejected(self):
        baseline = build_2023_disarmed_tag_amendment_preview(repository_root=ROOT)
        changed = copy.deepcopy(baseline)
        changed["approved_ref"] = "refs/tags/unsafe"
        _recompute(changed)
        with self.assertRaisesRegex(ValueError, "unauthorized report"):
            validate_2023_disarmed_tag_amendment_preview(changed)
        changed = copy.deepcopy(baseline)
        changed["preview_unified_diff"] = changed["preview_unified_diff"].replace("+          exit 1\n", "", 1)
        _recompute(changed)
        with self.assertRaisesRegex(ValueError, "hard-stop"):
            validate_2023_disarmed_tag_amendment_preview(changed)

    def test_preview_cli_cannot_dispatch_or_modify_workflow(self):
        source = (ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_disarmed_tag_amendment_preview.py").read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("assess")', source)
        for forbidden in (
            "git push", "git tag", "gh workflow run", "subprocess.",
            "gh api --method POST", 'sub.add_parser("dispatch")',
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
