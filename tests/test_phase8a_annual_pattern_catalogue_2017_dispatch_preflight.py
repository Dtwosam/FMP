from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2017_dispatch_preflight import (
    build_2017_dispatch_preflight,
    validate_2017_dispatch_preflight,
    validate_2017_dispatch_preflight_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40


def _fingerprint(value: dict[str, object]) -> str:
    return hashlib.sha256(
        (
            json.dumps(
                value,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    ).hexdigest()


def _install_receipt() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-539",
        "version": "fmp-annual-catalogue-2017-runtime-authorization-install-receipt-v1",
        "install_action_source_blob_sha": (
            "b6fd22c5eca66ca373d0479e63af51cd39068ed9"
        ),
        "source_action_decision": "DEC-538",
        "source_action_workflow_run_id": 37219170862,
        "source_action_workflow_head_sha": (
            "7dfcf6cacca63719ac40a88858c69895fc68670b"
        ),
        "source_action_artifact_id": 11310165235,
        "source_action_artifact_digest": (
            "sha256:e210042872cbe191f4383fcba4a6ac9305fbdeb96acaed32d46e034acff1681d"
        ),
        "source_action_fingerprint_sha256": "1" * 64,
        "stage": "ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_INSTALLED",
        "repository_full_name": "Dtwosam/FMP",
        "install_commit_sha": "dcdf7210b0039077efa3a23c65c2ed8fa41e2427",
        "annual_segment_label": "2017",
        "expected_run_number": 379,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37206992367,
        "changed_files": [
            (
                "src/fmp/discovery/"
                "annual_pattern_catalogue_2017_runtime_authorization.py"
            ),
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        ],
        "installed_gate_blob_sha": (
            "c1853eeec55ee98b3155a6054f07cf360793ba9b"
        ),
        "installed_runtime_blob_sha": (
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"
        ),
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "install_action_consumed": True,
        "annual_workflow_dispatch_authorized": False,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "next_segment_execution_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_DISPATCH_PREFLIGHT",
    }
    value["install_receipt_fingerprint_sha256"] = _fingerprint(value)
    return value


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _run(
    *,
    run_id: int,
    number: int,
    head_sha: str,
    conclusion: str,
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": "phase8a-annual-pattern-catalogue",
        "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "run_number": number,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": conclusion,
    }


def _annual_runs() -> dict[str, object]:
    return {
        "workflow_runs": [
            _run(
                run_id=37206992367,
                number=378,
                head_sha="2524fde355349581c9440a172d0384c3cbce31ed",
                conclusion="success",
            ),
            _run(
                run_id=37198002653,
                number=377,
                head_sha="a89db974be9a94481e7ed0990476bc661012f1e4",
                conclusion="success",
            ),
            _run(
                run_id=37191637168,
                number=376,
                head_sha="4c14fa7db6eb812b89ecb79201f7e298fa9c04f3",
                conclusion="failure",
            ),
            _run(
                run_id=37126711695,
                number=1,
                head_sha="fd85a886d07234ad584dcca08692b37e6af54b2e",
                conclusion="failure",
            ),
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-540 requires the installed annual workflow and 2017 runtime state",
)
class AnnualPatternCatalogue2017DispatchPreflightTests(unittest.TestCase):
    def test_sources_pin_installed_runtime_and_dec539_receipt(self) -> None:
        value = validate_2017_dispatch_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            value["install_receipt_source_blob_sha"],
            "c3662046efc7daf2c00637066aa78c885b85fa8e",
        )
        self.assertEqual(
            value["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            value["installed_gate_blob_sha"],
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
        )
        self.assertEqual(
            value["installed_runtime_blob_sha"],
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
        )

    def test_preflight_freezes_run379_without_authorizing_dispatch(self) -> None:
        value = build_2017_dispatch_preflight(
            _install_receipt(),
            repository_root=REPOSITORY_ROOT,
            main_branch=_main(),
            annual_workflow_runs=_annual_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2017_dispatch_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-540")
        self.assertEqual(value["expected_run_number"], 379)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37206992367)
        self.assertEqual(value["annual_workflow_run_count"], 4)
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_run379_already_present_fails_closed(self) -> None:
        runs = _annual_runs()
        rows = runs["workflow_runs"]
        assert isinstance(rows, list)
        rows.insert(
            0,
            _run(
                run_id=999999,
                number=379,
                head_sha="d" * 40,
                conclusion="failure",
            ),
        )
        with self.assertRaisesRegex(ValueError, "exactly four prior"):
            build_2017_dispatch_preflight(
                _install_receipt(),
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs=runs,
                expected_head_sha=HEAD,
            )

    def test_install_receipt_authority_tampering_fails_closed(self) -> None:
        receipt = copy.deepcopy(_install_receipt())
        receipt["annual_workflow_dispatch_authorized"] = True
        unsigned = dict(receipt)
        unsigned.pop("install_receipt_fingerprint_sha256", None)
        receipt["install_receipt_fingerprint_sha256"] = _fingerprint(unsigned)
        with self.assertRaisesRegex(
            ValueError,
            "annual_workflow_dispatch_authorized mismatch",
        ):
            build_2017_dispatch_preflight(
                receipt,
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs=_annual_runs(),
                expected_head_sha=HEAD,
            )

    def test_main_drift_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "current main head mismatch"):
            build_2017_dispatch_preflight(
                _install_receipt(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "c" * 40}},
                annual_workflow_runs=_annual_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        text = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2017_dispatch_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn('subparsers.add_parser("dispatch")', text)


if __name__ == "__main__":
    unittest.main()
