from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_admin_lock_handoff import (
    REQUIRED_HUMAN_PROOFS,
    build_2023_admin_lock_handoff,
    validate_2023_admin_lock_handoff,
)
from fmp.discovery.annual_pattern_catalogue_2023_main_lock_readiness import (
    build_2023_main_lock_readiness,
)
from test_phase8a_annual_pattern_catalogue_2023_main_lock_readiness import (
    _annual, _upstream,
)

ROOT = Path(__file__).resolve().parents[1]
DEC612_HEAD = "895b9ad311bd5159b2591dcfc8da714191574d00"
CURRENT_HEAD = "a" * 40


def _dec612() -> dict[str, object]:
    return build_2023_main_lock_readiness(
        dec611_audit=_upstream(),
        repository_root=ROOT,
        main_branch={"name": "main", "commit": {"sha": DEC612_HEAD}, "protected": False},
        annual_workflow_runs=_annual(),
        branch_protection=None,
        effective_branch_rules=None,
        inherited_rulesets=None,
        expected_head_sha=DEC612_HEAD,
    )


def _handoff(*, main: object = None, annual: object = None, source: object = None):
    return build_2023_admin_lock_handoff(
        readiness=_dec612() if source is None else source,
        repository_root=ROOT,
        main_branch={"name": "main", "commit": {"sha": CURRENT_HEAD}, "protected": False} if main is None else main,
        annual_runs=_annual() if annual is None else annual,
        expected_head_sha=CURRENT_HEAD,
    )


def _refingerprint(obj: dict[str, object]) -> dict[str, object]:
    tmp = dict(obj)
    tmp.pop("handoff_fingerprint_sha256", None)
    obj["handoff_fingerprint_sha256"] = hashlib.sha256(
        (json.dumps(tmp, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()
    return obj


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-613 requires installed protected 2023 catalogue source",
)
class Annual2023AdminLockHandoffTests(unittest.TestCase):
    def test_concrete_dec612_evidence_hashes(self) -> None:
        val = _dec612()
        canon = (json.dumps(val, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
        self.assertEqual(
            hashlib.sha256(canon).hexdigest(),
            "cc89cf90e820341a48d41cdd5518105dd99f3c867c9ec43b8c7d989a2535d0c5",
        )
        self.assertEqual(
            val["readiness_fingerprint_sha256"],
            "d9555c20a7d7a5a2d4bc79f9dd621e7a6d73e1ac9340cfec81348dc4e5f6a787",
        )

    def test_valid_handoff_is_always_read_only(self) -> None:
        val = _handoff()
        self.assertIs(validate_2023_admin_lock_handoff(val), val)
        self.assertEqual(val["decision"], "DEC-613")
        self.assertEqual(val["source_dec612_artifact_id"], 11555414803)
        self.assertEqual(val["expected_head_sha"], CURRENT_HEAD)
        self.assertEqual(val["annual_workflow_run_count"], 10)
        self.assertEqual(val["expected_run_number"], 385)
        self.assertTrue(val["dispatch_blocked"])
        self.assertFalse(val["admin_evidence_gathered_by_this_packet"])
        self.assertTrue(val["human_proof_required"])
        self.assertEqual(tuple(val["required_human_proofs"]), REQUIRED_HUMAN_PROOFS)
        self.assertFalse(val["annual_workflow_dispatch_authorized"])
        self.assertFalse(val["dispatch_action_executed"])
        self.assertFalse(val["trading_authorized"])

    def test_even_protected_main_does_not_grant_authority(self) -> None:
        val = _handoff(main={
            "name": "main", "commit": {"sha": CURRENT_HEAD}, "protected": True,
        })
        self.assertIs(val["current_main_protected_reported"], True)
        self.assertFalse(val["main_exclusive_lock_proven"])
        self.assertFalse(val["dispatch_atomic_to_vetted_sha"])
        self.assertTrue(val["dispatch_blocked"])

    def test_refdrift_and_consumed_run_385_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main changed"):
            _handoff(main={"name": "main", "commit": {"sha": "b" * 40}, "protected": False})
        runs = _annual()
        rows = runs["workflow_runs"]
        self.assertIsInstance(rows, list)
        rows.append({**rows[-1], "id": 8899, "run_number": 385})
        with self.assertRaises(ValueError):
            _handoff(annual=runs)

    def test_upstream_dec612_tampering_cannot_be_accepted(self) -> None:
        val = _dec612()
        val["dispatch_blocked"] = False
        unsigned = dict(val)
        unsigned.pop("readiness_fingerprint_sha256")
        val["readiness_fingerprint_sha256"] = hashlib.sha256(
            (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
        ).hexdigest()
        with self.assertRaises(ValueError):
            _handoff(source=val)

    def test_rehashed_escalation_is_rejected(self) -> None:
        for field in (
            "dispatch_blocked", "main_exclusive_lock_proven",
            "annual_workflow_dispatch_authorized", "dispatch_action_executed",
            "trading_authorized", "human_proof_required",
            "admin_evidence_gathered_by_this_packet",
        ):
            with self.subTest(field=field):
                val = copy.deepcopy(_handoff())
                val[field] = field not in {"dispatch_blocked", "human_proof_required"}
                _refingerprint(val)
                with self.assertRaisesRegex(ValueError, f"{field} mismatch"):
                    validate_2023_admin_lock_handoff(val)

    def test_mutated_checklist_or_extra_field_rejected(self) -> None:
        val = _handoff()
        val["required_human_proofs"].pop()
        with self.assertRaisesRegex(ValueError, "required_human_proofs mismatch"):
            validate_2023_admin_lock_handoff(_refingerprint(val))
        val = _handoff()
        val["controller_armed"] = True
        with self.assertRaisesRegex(ValueError, "unauthorized handoff fields"):
            validate_2023_admin_lock_handoff(_refingerprint(val))

    def test_cli_is_never_a_dispatcher(self) -> None:
        text = (
            ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_admin_lock_handoff.py"
        ).read_text()
        self.assertIn('sub.add_parser("prepare")', text)
        for forbidden in ("gh workflow run ", "gh api --method POST",
                          "git push", "git commit", 'sub.add_parser("dispatch")'):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
