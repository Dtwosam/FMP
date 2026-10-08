from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_dispatch_immutability_audit import (
    audit_2023_dispatch_main_immutability,
)
from fmp.discovery.annual_pattern_catalogue_2023_main_lock_readiness import (
    build_2023_main_lock_readiness,
    validate_2023_main_lock_readiness,
)
from test_phase8a_annual_pattern_catalogue_2023_dispatch_immutability_audit import (
    _annual, _dec610,
)

ROOT = Path(__file__).resolve().parents[1]
DEC611_HEAD = "329e467a924ec00956505355f6cc1da7a589207c"
CURRENT_MAIN = "b" * 40


def _upstream() -> dict[str, object]:
    return audit_2023_dispatch_main_immutability(
        _dec610(),
        repository_root=ROOT,
        main_branch={"name": "main", "commit": {"sha": DEC611_HEAD}, "protected": False},
        annual_workflow_runs=_annual(),
        expected_head_sha=DEC611_HEAD,
    )


def _branch(*, protected: bool = False) -> dict[str, object]:
    return {
        "name": "main",
        "commit": {"sha": CURRENT_MAIN},
        "protected": protected,
    }


def _protection() -> dict[str, object]:
    return {
        "lock_branch": {"enabled": True},
        "enforce_admins": {"enabled": True},
        "allow_fork_syncing": {"enabled": False},
        "allow_force_pushes": {"enabled": False},
        "allow_deletions": {"enabled": False},
    }


def _assess(
    *,
    branch: object = None,
    protection: object = None,
    effective_rules: object = None,
    rulesets: object = None,
    runs: object = None,
    upstream: object = None,
) -> dict[str, object]:
    return build_2023_main_lock_readiness(
        dec611_audit=_upstream() if upstream is None else upstream,
        repository_root=ROOT,
        main_branch=_branch() if branch is None else branch,
        annual_workflow_runs=_annual() if runs is None else runs,
        branch_protection=protection,
        effective_branch_rules=effective_rules,
        inherited_rulesets=rulesets,
        expected_head_sha=CURRENT_MAIN,
    )


def _refingerprint(value: dict[str, object]) -> dict[str, object]:
    unsigned = dict(value)
    unsigned.pop("readiness_fingerprint_sha256", None)
    value["readiness_fingerprint_sha256"] = hashlib.sha256(
        (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    ).hexdigest()
    return value


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-612 requires installed 2023 protected runtime",
)
class AnnualCatalogue2023MainLockReadinessTests(unittest.TestCase):
    def test_concrete_dec611_fingerprint_and_canonical_binding(self) -> None:
        u = _upstream()
        canon = (json.dumps(u, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
        self.assertEqual(
            hashlib.sha256(canon).hexdigest(),
            "5de4c3b87b64795c14f84211c838c9d9e1400c4c32b06d46946cb10a00e3a026",
        )
        self.assertEqual(
            u["audit_fingerprint_sha256"],
            "f1842fd06bdba200be7ab521ed2735a9429df4836408a18297888d9c3d6416a5",
        )

    def test_unprotected_main_is_blocked(self) -> None:
        result = _assess()
        self.assertIs(validate_2023_main_lock_readiness(result), result)
        self.assertEqual(result["block_reason"], "MAIN_UNPROTECTED")
        self.assertEqual(result["source_dec611_workflow_run_id"], 37778086874)
        self.assertEqual(result["source_dec611_artifact_id"], 11550716769)
        self.assertEqual(result["expected_run_number"], 385)
        self.assertEqual(result["annual_workflow_run_count"], 10)
        self.assertFalse(result["lock_configuration_candidate"])
        self.assertTrue(result["dispatch_blocked"])
        self.assertTrue(result["read_only"])
        self.assertFalse(result["dispatch_action_executed"])
        self.assertFalse(result["trading_authorized"])

    def test_protected_flag_without_complete_details_stays_blocked(self) -> None:
        result = _assess(branch=_branch(protected=True))
        self.assertEqual(result["block_reason"], "INSUFFICIENT_LOCK_CONFIGURATION_OR_VISIBILITY")
        self.assertFalse(result["lock_configuration_candidate"])
        self.assertTrue(result["dispatch_blocked"])

    def test_complete_lock_snapshot_is_only_a_candidate_not_authority(self) -> None:
        result = _assess(
            branch=_branch(protected=True),
            protection=_protection(),
            effective_rules=[{"type": "update"}],
            rulesets=[],
        )
        self.assertTrue(result["lock_configuration_candidate"])
        self.assertEqual(result["block_reason"], "LOCK_SNAPSHOT_REQUIRES_EXCLUSIVE_WINDOW_REVIEW")
        self.assertFalse(result["main_exclusive_lock_proven"])
        self.assertFalse(result["dispatch_atomic_to_vetted_sha"])
        self.assertFalse(result["annual_workflow_dispatch_authorized"])
        self.assertFalse(result["dispatch_action_executed"])
        self.assertTrue(result["dispatch_blocked"])

    def test_bypass_actor_and_unknown_rulesets_fail_closed(self) -> None:
        for rows in (
            None,
            [{"name": "org", "enforcement": "active"}],
            [{"name": "org", "enforcement": "active", "bypass_actors": [{"actor_id": 1}]}],
        ):
            with self.subTest(rows=rows):
                result = _assess(
                    branch=_branch(protected=True), protection=_protection(),
                    effective_rules=[{"type": "update"}], rulesets=rows,
                )
                self.assertFalse(result["no_reported_bypass_actors"])
                self.assertFalse(result["lock_configuration_candidate"])
                self.assertTrue(result["dispatch_blocked"])

    def test_missing_effective_rules_and_each_missing_protection_lock_fail(self) -> None:
        for field in (
            "lock_branch", "enforce_admins", "allow_fork_syncing",
            "allow_force_pushes", "allow_deletions",
        ):
            with self.subTest(field=field):
                protection = _protection()
                del protection[field]
                result = _assess(
                    branch=_branch(protected=True), protection=protection,
                    effective_rules=[{"type": "update"}], rulesets=[],
                )
                self.assertFalse(result["lock_configuration_candidate"])
        result = _assess(
            branch=_branch(protected=True),
            protection=_protection(),
            rulesets=[],
        )
        self.assertFalse(result["effective_branch_rules_visible"])

    def test_main_drift_and_consumed_slot_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "current main SHA mismatch"):
            _assess(branch={"name": "main", "commit": {"sha": "c" * 40}, "protected": False})
        runs = _annual()
        rows = runs["workflow_runs"]
        self.assertIsInstance(rows, list)
        rows.append({**rows[-1], "id": 9000, "run_number": 385})
        with self.assertRaises(ValueError):
            _assess(runs=runs)

    def test_dec611_source_tampering_is_rejected(self) -> None:
        source = _upstream()
        source["trading_authorized"] = True
        unsigned = dict(source)
        unsigned.pop("audit_fingerprint_sha256")
        source["audit_fingerprint_sha256"] = hashlib.sha256(
            (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
        ).hexdigest()
        with self.assertRaises(ValueError):
            _assess(upstream=source)

    def test_refingerprinted_authority_escalation_is_rejected(self) -> None:
        for field in (
            "annual_workflow_dispatch_authorized", "main_exclusive_lock_proven",
            "dispatch_action_executed", "trading_authorized", "dispatch_blocked",
        ):
            with self.subTest(field=field):
                v = copy.deepcopy(_assess())
                v[field] = field != "dispatch_blocked"
                _refingerprint(v)
                with self.assertRaisesRegex(ValueError, f"{field} mismatch"):
                    validate_2023_main_lock_readiness(v)

    def test_candidate_inconsistency_and_extra_field_rejected(self) -> None:
        v = _assess()
        v["lock_configuration_candidate"] = True
        with self.assertRaisesRegex(ValueError, "lock candidate inconsistent"):
            validate_2023_main_lock_readiness(_refingerprint(v))
        v = _assess()
        v["secret_order_permission"] = True
        with self.assertRaisesRegex(ValueError, "unauthorized fields"):
            validate_2023_main_lock_readiness(_refingerprint(v))

    def test_cli_is_read_only(self) -> None:
        script = (
            ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_main_lock_readiness.py"
        ).read_text()
        self.assertIn('sub.add_parser("assess")', script)
        for forbidden in ("gh workflow run ", "git push", "git commit",
                          'sub.add_parser("dispatch")', "actions: write"):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
