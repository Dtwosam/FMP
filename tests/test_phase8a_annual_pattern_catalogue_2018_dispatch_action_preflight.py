from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2018_dispatch_authorization import (
    build_2018_dispatch_authorization,
)
from fmp.discovery.annual_pattern_catalogue_2018_dispatch_action_preflight import (
    build_2018_dispatch_action_preflight,
    validate_2018_dispatch_action_preflight,
    validate_2018_dispatch_action_preflight_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "e" * 40
AUTHORIZATION_HEAD = "8a02d66cfd0aee43e105e9057a813c0dffcc6dde"

def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _preflight() -> dict[str, object]:
    value: dict[str, object] = {
        "active_workflow_blob_sha": (
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
        ),
        "annual_segment_label": "2018",
        "annual_workflow_dispatch_authorized": False,
        "annual_workflow_run_count": 5,
        "broker_mutation_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-551",
        "demo_order_authorized": False,
        "dispatch_command_present": False,
        "expected_head_sha": "35263ec4c59bae4733507c53b080f3ea07ff1325",
        "expected_run_attempt": 1,
        "expected_run_number": 380,
        "failed_run_1_id": 37126711695,
        "failed_run_376_id": 37191637168,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "install_receipt_source_blob_sha": (
            "a2a07003fdcef2a4202594286becc562ee6fc718"
        ),
        "installed_gate_blob_sha": (
            "cd50f50156cf74c34cd97d69d24291dc373b390f"
        ),
        "installed_runtime_blob_sha": (
            "410180c34a9e3500bbbb42310a5253b993ac7785"
        ),
        "live_order_authorized": False,
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2018_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "preflight_read_only": True,
        "previous_annual_freeze_run_id": 37227536041,
        "promotion_authorized": False,
        "real_money_authorized": False,
        "repository_full_name": "Dtwosam/FMP",
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "source_install_artifact_digest": (
            "sha256:8b9732b24a5ef6163d8ab54f34d058eecd9e1c4ce1a68c79a88306178933df2d"
        ),
        "source_install_artifact_id": 11314488545,
        "source_install_commit_sha": (
            "1fc73dfc1e102996cecd5b9ffcb75d3ab4fa3ade"
        ),
        "source_install_receipt_decision": "DEC-550",
        "source_install_receipt_fingerprint_sha256": (
            "5759024fded487649284109550a0d54d4a92332b963804e196b2cad15984dc27"
        ),
        "source_installer_workflow_head_sha": (
            "11048bd278bbf8f3697571aaff40c27656449a6c"
        ),
        "source_installer_workflow_run_id": 37233054691,
        "stage": "ANNUAL_CATALOGUE_2018_DISPATCH_PREFLIGHT_READY",
        "strategy_v1_synthesis_authorized": False,
        "successful_2015_run_id": 37198002653,
        "successful_2016_run_id": 37206992367,
        "successful_2017_run_id": 37227536041,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2018-dispatch-preflight-v1",
    }
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    assert (
        value["preflight_fingerprint_sha256"]
        == "f756088f404f77220b366eaffdfd36cfe805f9fcd91a274ef7c5a364994893c8"
    )
    return value


def _authorization() -> dict[str, object]:
    value = build_2018_dispatch_authorization(
        _preflight(),
        repository_root=REPOSITORY_ROOT,
        authorization_head_sha=AUTHORIZATION_HEAD,
    )
    assert value["authorization_fingerprint_sha256"] == (
        "eb0089103203b334c12800643f74cc838e8e9e140b4b7868f48ba74793d1d043"
    )
    return value


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
            {
                **common,
                "id": 37227536041,
                "run_number": 379,
                "head_sha": "7b4c1ef8573e280c067443b72f1534d9091d5b7f",
                "conclusion": "success",
            },
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-553 requires the current installed 2018 runtime state",
)
class AnnualPatternCatalogue2018DispatchActionPreflightTests(unittest.TestCase):
    def test_sources_pin_concrete_authorization_and_runtime(self) -> None:
        source = validate_2018_dispatch_action_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["authorization_source_blob_sha"],
            "8d4f59be7db640749aa3f5da7ba43f9e5466dd2f",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "cd50f50156cf74c34cd97d69d24291dc373b390f",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        )

    def test_exact_state_freezes_run380_parameters_read_only(self) -> None:
        value = build_2018_dispatch_action_preflight(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2018_dispatch_action_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-553")
        self.assertEqual(value["annual_workflow_run_count"], 5)
        self.assertEqual(value["annual_segment_label"], "2018")
        self.assertEqual(value["prior_segment_label"], "2017")
        self.assertEqual(value["successful_2017_run_id"], 37227536041)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37227536041)
        self.assertEqual(value["expected_run_number"], 380)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["dispatch_ref"], "main")
        self.assertEqual(value["dispatch_input_annual_segment_label"], "2018")
        self.assertEqual(
            value["dispatch_input_previous_annual_freeze_run_id"],
            "37227536041",
        )
        self.assertTrue(value["dispatch_parameters_frozen"])
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["run_381_or_later_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_unexpected_run380_is_rejected(self) -> None:
        runs = _runs()
        rows = list(runs["workflow_runs"])
        rows.append(
            {
                "id": 99999999999,
                "name": "phase8a-annual-pattern-catalogue",
                "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
                "run_number": 380,
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
            "exactly five prior annual workflow runs",
        ):
            build_2018_dispatch_action_preflight(
                _authorization(),
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=HEAD,
            )

    def test_run379_head_drift_is_rejected(self) -> None:
        runs = _runs()
        rows = [dict(row) for row in runs["workflow_runs"]]
        rows[4]["head_sha"] = "d" * 40
        with self.assertRaisesRegex(
            ValueError,
            "annual run 379 head_sha mismatch",
        ):
            build_2018_dispatch_action_preflight(
                _authorization(),
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=HEAD,
            )

    def test_concrete_authorization_head_drift_is_rejected(self) -> None:
        authorization = copy.deepcopy(_authorization())
        authorization["authorization_head_sha"] = "f" * 40
        with self.assertRaisesRegex(
            ValueError,
            "authorization fingerprint mismatch|source authorization head mismatch",
        ):
            build_2018_dispatch_action_preflight(
                authorization,
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2018_dispatch_action_preflight(
                _authorization(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "c" * 40}},
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2018_dispatch_action_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
