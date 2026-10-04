from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2017_dispatch_action_preflight import (
    build_2017_dispatch_action_preflight,
    validate_2017_dispatch_action_preflight,
    validate_2017_dispatch_action_preflight_sources,
)


HEAD = "e" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _authorization() -> dict[str, object]:
    return {
        "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        "annual_segment_label": "2017",
        "annual_workflow_dispatch_authorized": True,
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_contract_validated": True,
        "authorization_fingerprint_sha256": (
            "16d42cb2552df761b80e0b32a23de5378f143c004946cfe2c816f280b17d8e8e"
        ),
        "authorization_head_sha": "070b5ab9a9e6635ca26fa43f67ab71fdd49b3c1d",
        "authorization_scope": "2017_run_379_attempt_1_only",
        "broker_mutation_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-541",
        "demo_order_authorized": False,
        "dispatch_action_executed": False,
        "dispatch_command_present": False,
        "dispatch_preflight_source_blob_sha": (
            "0e048756a1a9ca5f8d45896c6ff212d386996ed0"
        ),
        "expected_run_attempt": 1,
        "expected_run_number": 379,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "installed_gate_blob_sha": "c1853eeec55ee98b3155a6054f07cf360793ba9b",
        "installed_runtime_blob_sha": "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
        "live_order_authorized": False,
        "next_gate": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_DISPATCH_ACTION_PREFLIGHT"
        ),
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "previous_annual_freeze_run_id": 37206992367,
        "prior_segment_label": "2016",
        "promotion_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "repository_full_name": "Dtwosam/FMP",
        "rerun_authorized": False,
        "retry_authorized": False,
        "run_380_or_later_authorized": False,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "source_only_authorization": True,
        "source_preflight_artifact_digest": (
            "sha256:a54675bd49ef6bb17d32f44b1d21a4adb10b541e3a248f583b05293505ef498d"
        ),
        "source_preflight_artifact_id": 11311031268,
        "source_preflight_canonical_sha256": (
            "40a2e1b66eabbf1f964600b487164d6e9c02a7de226396cfb15963c058a65592"
        ),
        "source_preflight_decision": "DEC-540",
        "source_preflight_fingerprint_sha256": (
            "7329cf4238c1aa8b608d7b4e41eaaaf643f78c3fb99f7ae399f6db303a75ffad"
        ),
        "source_preflight_version": (
            "fmp-annual-catalogue-2017-dispatch-preflight-v1"
        ),
        "source_preflight_workflow_head_sha": (
            "f7983f960ae141f15c83b3cc05f6d6030140c802"
        ),
        "source_preflight_workflow_run_id": 37223000759,
        "stage": "ANNUAL_CATALOGUE_2017_DISPATCH_AUTHORIZED_NOT_DISPATCHED",
        "strategy_v1_synthesis_authorized": False,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2017-dispatch-authorization-v1",
    }


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _runs() -> dict[str, object]:
    common = {
        "name": "phase8a-annual-pattern-catalogue",
        "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "run_attempt": 1,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "status": "completed",
    }
    return {
        "workflow_runs": [
            {
                **common,
                "id": 37126711695,
                "run_number": 1,
                "head_sha": "fd85a886d07234ad584dcca08692b37e6af54b2e",
                "conclusion": "failure",
            },
            {
                **common,
                "id": 37191637168,
                "run_number": 376,
                "head_sha": "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3",
                "conclusion": "failure",
            },
            {
                **common,
                "id": 37198002653,
                "run_number": 377,
                "head_sha": "a89db974be9a94481e7ed0990476bc661012f1e4",
                "conclusion": "success",
            },
            {
                **common,
                "id": 37206992367,
                "run_number": 378,
                "head_sha": "2524fde355349581c9440a172d0384c3cbce31ed",
                "conclusion": "success",
            },
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-542 requires the current installed 2017 runtime state",
)
class AnnualPatternCatalogue2017DispatchActionPreflightTests(unittest.TestCase):
    def test_sources_pin_concrete_authorization_and_runtime(self) -> None:
        source = validate_2017_dispatch_action_preflight_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["authorization_source_blob_sha"],
            "ba4a59867bba225bcdc683dde451151922074cdb",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
        )

    def test_exact_state_freezes_run379_parameters_read_only(self) -> None:
        value = build_2017_dispatch_action_preflight(
            _authorization(),
            repository_root=Path("."),
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2017_dispatch_action_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-542")
        self.assertEqual(value["annual_workflow_run_count"], 4)
        self.assertEqual(value["annual_segment_label"], "2017")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37206992367)
        self.assertEqual(value["expected_run_number"], 379)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["dispatch_ref"], "main")
        self.assertEqual(value["dispatch_input_annual_segment_label"], "2017")
        self.assertEqual(
            value["dispatch_input_previous_annual_freeze_run_id"],
            "37206992367",
        )
        self.assertTrue(value["dispatch_parameters_frozen"])
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["run_380_or_later_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_unexpected_run379_is_rejected(self) -> None:
        runs = _runs()
        rows = list(runs["workflow_runs"])
        rows.append(
            {
                "id": 99999999999,
                "name": "phase8a-annual-pattern-catalogue",
                "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
                "run_number": 379,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": HEAD,
                "status": "completed",
                "conclusion": "success",
            }
        )
        with self.assertRaisesRegex(
            ValueError,
            "exactly four prior annual workflow runs",
        ):
            build_2017_dispatch_action_preflight(
                _authorization(),
                repository_root=Path("."),
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=HEAD,
            )

    def test_run378_head_drift_is_rejected(self) -> None:
        runs = _runs()
        rows = [dict(row) for row in runs["workflow_runs"]]
        rows[3]["head_sha"] = "d" * 40
        with self.assertRaisesRegex(ValueError, "annual run 378 head_sha mismatch"):
            build_2017_dispatch_action_preflight(
                _authorization(),
                repository_root=Path("."),
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=HEAD,
            )

    def test_concrete_authorization_fingerprint_drift_is_rejected(self) -> None:
        authorization = copy.deepcopy(_authorization())
        authorization["authorization_head_sha"] = "f" * 40
        unsigned = dict(authorization)
        unsigned.pop("authorization_fingerprint_sha256", None)
        authorization["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "source authorization head mismatch",
        ):
            build_2017_dispatch_action_preflight(
                authorization,
                repository_root=Path("."),
                main_branch=_main(),
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2017_dispatch_action_preflight(
                _authorization(),
                repository_root=Path("."),
                main_branch={"name": "main", "commit": {"sha": "c" * 40}},
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        script = Path(
            "scripts/phase8a_annual_pattern_catalogue_2017_dispatch_action_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
