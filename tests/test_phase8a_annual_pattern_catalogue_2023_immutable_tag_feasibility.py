from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_admin_lock_handoff import (
    build_2023_admin_lock_handoff,
)
from fmp.discovery.annual_pattern_catalogue_2023_immutable_tag_feasibility import (
    DEC614_HEAD_SHA,
    DEC614_HANDOFF_CANONICAL_SHA256,
    DEC614_HANDOFF_FINGERPRINT,
    MAIN_REF_GUARD,
    REQUIRED_JOBS,
    _main_guards,
    build_2023_immutable_tag_feasibility,
    validate_2023_immutable_tag_feasibility,
)
from test_phase8a_annual_pattern_catalogue_2023_admin_lock_handoff import (
    _annual, _dec612,
)

ROOT = Path(__file__).resolve().parents[1]
CURRENT_HEAD = "b" * 40
WORKFLOW = ROOT / ".github/workflows/phase8a-annual-pattern-catalogue.yml"


def _handoff() -> dict[str, object]:
    return build_2023_admin_lock_handoff(
        readiness=_dec612(),
        repository_root=ROOT,
        main_branch={
            "name": "main",
            "commit": {"sha": DEC614_HEAD_SHA},
            "protected": False,
        },
        annual_runs=_annual(),
        expected_head_sha=DEC614_HEAD_SHA,
    )


def _assess(*, handoff: object = None, protected: bool = False,
            main_sha: str = CURRENT_HEAD, annual: object = None) -> dict[str, object]:
    return build_2023_immutable_tag_feasibility(
        repository_root=ROOT,
        handoff=_handoff() if handoff is None else handoff,
        main_branch={
            "name": "main", "commit": {"sha": main_sha},
            "protected": protected,
        },
        annual_workflow_runs=_annual() if annual is None else annual,
        expected_head_sha=CURRENT_HEAD,
    )


def _recompute(value: dict[str, object]) -> None:
    obj = dict(value)
    obj.pop("feasibility_fingerprint_sha256", None)
    value["feasibility_fingerprint_sha256"] = hashlib.sha256(
        (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-615 requires installed protected 2023 runtime",
)
class AnnualCatalogue2023ImmutableTagFeasibilityTests(unittest.TestCase):
    def test_concrete_dec614_handoff_provenance(self) -> None:
        value = _handoff()
        canon = (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
        self.assertEqual(hashlib.sha256(canon).hexdigest(), DEC614_HANDOFF_CANONICAL_SHA256)
        self.assertEqual(value["handoff_fingerprint_sha256"], DEC614_HANDOFF_FINGERPRINT)
        self.assertTrue(value["dispatch_blocked"])
        self.assertFalse(value["dispatch_action_executed"])

    def test_current_tag_path_is_blocked_by_three_main_guards(self) -> None:
        result = _assess()
        self.assertIs(validate_2023_immutable_tag_feasibility(result), result)
        self.assertEqual(result["decision"], "DEC-615")
        self.assertEqual(result["required_main_ref_guard_jobs"], list(REQUIRED_JOBS))
        self.assertEqual(result["expected_run_number"], 385)
        self.assertEqual(result["expected_run_attempt"], 1)
        self.assertEqual(result["annual_workflow_run_count"], 10)
        self.assertTrue(result["github_workflow_dispatch_supports_branch_or_tag"])
        self.assertTrue(result["current_workflow_requires_main_ref"])
        self.assertTrue(result["requires_separate_annual_workflow_runtime_amendment"])
        self.assertFalse(result["tag_path_compatible_with_current_workflow"])
        self.assertTrue(result["dispatch_blocked"])
        self.assertFalse(result["alternate_ref_execution_authorized"])
        self.assertFalse(result["dispatch_action_executed"])
        self.assertFalse(result["trading_authorized"])

    def test_protected_main_does_not_authorize_tag_or_dispatch(self) -> None:
        value = _assess(protected=True)
        self.assertTrue(value["main_protected_reported"])
        self.assertFalse(value["immutable_tag_proven"])
        self.assertFalse(value["main_exclusive_lock_proven"])
        self.assertTrue(value["dispatch_blocked"])

    def test_missing_or_duplicated_job_ref_guard_is_rejected(self) -> None:
        original = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(_main_guards(original), list(REQUIRED_JOBS))
        self.assertEqual(original.count(MAIN_REF_GUARD), 3)
        with self.assertRaisesRegex(ValueError, "guard count"):
            _main_guards(original.replace(MAIN_REF_GUARD, "test \"$GITHUB_REF\" = \"refs/tags/test\"", 1))
        with self.assertRaisesRegex(ValueError, "guard count"):
            _main_guards(original.replace(MAIN_REF_GUARD, MAIN_REF_GUARD + "\n          " + MAIN_REF_GUARD, 1))
        with self.assertRaisesRegex(ValueError, "job set"):
            _main_guards(original.replace("  annual_freeze:", "  changed_freeze:", 1))

    def test_main_head_drift_and_consumed_run_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main SHA drift"):
            _assess(main_sha="c" * 40)
        inventory = _annual()
        rows = inventory["workflow_runs"]
        self.assertIsInstance(rows, list)
        rows.append({**rows[-1], "run_number": 385, "id": 999999})
        with self.assertRaises(ValueError):
            _assess(annual=inventory)

    def test_source_handoff_authority_tampering_rejected(self) -> None:
        altered = _handoff()
        altered["dispatch_blocked"] = False
        tmp = dict(altered)
        tmp.pop("handoff_fingerprint_sha256")
        altered["handoff_fingerprint_sha256"] = hashlib.sha256(
            (json.dumps(tmp, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
        ).hexdigest()
        with self.assertRaises(ValueError):
            _assess(handoff=altered)

    def test_rehashed_permission_escalation_remains_forbidden(self) -> None:
        for key, value in (
            ("dispatch_blocked", False),
            ("tag_path_compatible_with_current_workflow", True),
            ("tag_creation_or_movement_authorized", True),
            ("immutable_tag_proven", True),
            ("annual_workflow_dispatch_authorized", True),
            ("trading_authorized", True),
        ):
            with self.subTest(key=key):
                data = copy.deepcopy(_assess())
                data[key] = value
                _recompute(data)
                with self.assertRaisesRegex(ValueError, f"{key} mismatch"):
                    validate_2023_immutable_tag_feasibility(data)

    def test_fingerprint_and_field_extensions_rejected(self) -> None:
        data = _assess()
        data["unauthorized_tag_writer"] = True
        _recompute(data)
        with self.assertRaisesRegex(ValueError, "unauthorized fields"):
            validate_2023_immutable_tag_feasibility(data)
        data = _assess()
        data["expected_run_number"] = 386
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            validate_2023_immutable_tag_feasibility(data)

    def test_script_is_assessment_only(self) -> None:
        script = (
            ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_immutable_tag_feasibility.py"
        ).read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("assess")', script)
        for forbidden in (
            "gh workflow run ", "git push", "git commit",
            "gh api --method POST", 'sub.add_parser("dispatch")',
        ):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
