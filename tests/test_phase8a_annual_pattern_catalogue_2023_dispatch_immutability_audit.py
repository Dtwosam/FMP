from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_dispatch_authorization import (
    build_2023_dispatch_authorization,
)
from fmp.discovery.annual_pattern_catalogue_2023_dispatch_action_preflight import (
    build_2023_dispatch_action_preflight,
)
from fmp.discovery.annual_pattern_catalogue_2023_dispatch_immutability_audit import (
    DEC610_HEAD_SHA,
    audit_2023_dispatch_main_immutability,
    validate_2023_dispatch_main_immutability_audit,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/phase8a_dec608_2023_dispatch_preflight.json"
HEAD = "f" * 40
RUNS = {
    1: (37126711695, "fd85a886d07234ad584dcca08692b37e6af54b2e", "failure"),
    376: (37191637168, "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3", "failure"),
    377: (37198002653, "a89db974be9a94481e7ed0990476bc661012f1e4", "success"),
    378: (37206992367, "2524fde355349581c9440a172d0384c3cbce31ed", "success"),
    379: (37227536041, "7b4c1ef8573e280c067443b72f1534d9091d5b7f", "success"),
    380: (37237817538, "30971a996f514670a6f836d8e45cf80137197a4f", "success"),
    381: (37310525635, "8bcee3a7a834743f08bd9ad73109bfc09609a2fe", "success"),
    382: (37443770076, "681e81e021d4970a67b18370142d55b17ec68864", "success"),
    383: (37531960014, "a1e194907c273a2fcdddfb4c24d64a96cfd8d263", "success"),
    384: (37663157285, "dd79687adc4ec179c56f91939cb600e6746fab5d", "success"),
}


def _annual() -> dict[str, object]:
    return {
        "workflow_runs": [
            {
                "id": run_id, "run_number": number, "run_attempt": 1,
                "name": "phase8a-annual-pattern-catalogue",
                "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
                "event": "workflow_dispatch", "head_branch": "main",
                "head_sha": sha, "status": "completed", "conclusion": result,
            }
            for number, (run_id, sha, result) in RUNS.items()
        ]
    }


def _dec610() -> dict[str, object]:
    dec608 = json.loads(FIXTURE.read_text(encoding="utf-8"))
    dec609 = build_2023_dispatch_authorization(
        dec608, repository_root=ROOT,
        authorization_head_sha="7d40ccaf79270162dd96a8a1e7024dd94c3a72b7",
    )
    result = build_2023_dispatch_action_preflight(
        dec609,
        repository_root=ROOT,
        main_branch={"name": "main", "commit": {"sha": DEC610_HEAD_SHA}},
        annual_workflow_runs=_annual(),
        expected_head_sha=DEC610_HEAD_SHA,
    )
    return result


def _audit(*, protected: bool = False, main: object = None,
           annual: object = None) -> dict[str, object]:
    branch = (
        {"name": "main", "commit": {"sha": HEAD}, "protected": protected}
        if main is None else main
    )
    return audit_2023_dispatch_main_immutability(
        _dec610(), repository_root=ROOT,
        main_branch=branch,
        annual_workflow_runs=_annual() if annual is None else annual,
        expected_head_sha=HEAD,
    )


def _fingerprint(value: dict[str, object]) -> str:
    unsigned = dict(value)
    unsigned.pop("audit_fingerprint_sha256", None)
    canon = (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    return hashlib.sha256(canon).hexdigest()


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-611 audit requires DEC-607-installed protected 2023 runtime",
)
class AnnualCatalogue2023MainImmutabilityAuditTests(unittest.TestCase):
    def test_dec610_source_fingerprint_is_exact(self) -> None:
        dec610 = _dec610()
        canon = (json.dumps(dec610, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
        self.assertEqual(
            hashlib.sha256(canon).hexdigest(),
            "176cadda04eac41454d401bbabeeadc91e701307bbdd94054890ae89bf65689e",
        )
        self.assertEqual(
            dec610["preflight_fingerprint_sha256"],
            "07f391338fe3d20c5e823f72a14cecdf454aec87a6e7638bdd8774f3c9b4b063",
        )

    def test_unprotected_main_blocks_every_dispatch(self) -> None:
        value = _audit(protected=False)
        self.assertIs(validate_2023_dispatch_main_immutability_audit(value), value)
        self.assertEqual(value["decision"], "DEC-611")
        self.assertEqual(value["expected_run_number"], 385)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37663157285)
        self.assertEqual(value["block_reason"], "UNPROTECTED_MUTABLE_MAIN_REF")
        self.assertFalse(value["main_branch_protected_reported"])
        self.assertTrue(value["dispatch_blocked"])
        self.assertTrue(value["audit_read_only"])
        for field in (
            "main_exclusive_lock_proven", "dispatch_atomic_to_vetted_sha",
            "annual_workflow_dispatch_authorized", "dispatch_action_executed",
            "protected_history_access_authorized", "rerun_authorized",
            "retry_authorized", "run_386_or_later_authorized",
            "cross_year_comparison_authorized", "strategy_v1_synthesis_authorized",
            "broker_mutation_authorized", "live_order_authorized",
            "real_money_authorized", "trading_authorized",
        ):
            self.assertIs(value[field], False, field)

    def test_protected_flag_alone_does_not_unlock(self) -> None:
        value = _audit(protected=True)
        self.assertEqual(value["block_reason"], "EXCLUSIVE_MAIN_LOCK_NOT_PROVEN")
        self.assertTrue(value["main_branch_protected_reported"])
        self.assertTrue(value["dispatch_blocked"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["main_exclusive_lock_proven"])

    def test_head_drift_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "current main head mismatch"):
            _audit(main={"name": "main", "commit": {"sha": "b" * 40}, "protected": False})

    def test_run385_consumed_rejected(self) -> None:
        inventory = _annual()
        rows = inventory["workflow_runs"]
        self.assertIsInstance(rows, list)
        rows.append({**rows[-1], "run_number": 385, "id": 99999})
        with self.assertRaises(ValueError):
            _audit(annual=inventory)

    def test_fingerprint_cannot_upgrade_authority(self) -> None:
        for field in (
            "annual_workflow_dispatch_authorized", "dispatch_action_executed",
            "main_exclusive_lock_proven", "dispatch_atomic_to_vetted_sha",
            "protected_history_access_authorized", "trading_authorized",
        ):
            with self.subTest(field=field):
                tampered = copy.deepcopy(_audit())
                tampered[field] = True
                tampered["audit_fingerprint_sha256"] = _fingerprint(tampered)
                with self.assertRaisesRegex(ValueError, f"{field} mismatch"):
                    validate_2023_dispatch_main_immutability_audit(tampered)

    def test_unauthorized_field_rejected(self) -> None:
        tampered = _audit()
        tampered["execution_granted"] = True
        tampered["audit_fingerprint_sha256"] = _fingerprint(tampered)
        with self.assertRaisesRegex(ValueError, "unauthorized field set"):
            validate_2023_dispatch_main_immutability_audit(tampered)

    def test_cli_is_audit_only(self) -> None:
        script = (
            ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_dispatch_immutability_audit.py"
        ).read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("audit")', script)
        for forbidden in ("gh workflow run ", 'sub.add_parser("dispatch")',
                          "git push", "git commit", "actions: write"):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
