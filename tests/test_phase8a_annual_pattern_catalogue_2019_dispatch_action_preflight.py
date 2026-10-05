from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2019_dispatch_authorization import (
    build_2019_dispatch_authorization,
)
from fmp.discovery.annual_pattern_catalogue_2019_dispatch_action_preflight import (
    build_2019_dispatch_action_preflight,
    validate_2019_dispatch_action_preflight,
    validate_2019_dispatch_action_preflight_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "e" * 40
AUTHORIZATION_HEAD = "c9b93843c2b853fc23d78cdbcebdbf51a3cc390e"

PREFLIGHT_JSON = r"""
{
  "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
  "annual_segment_label": "2019",
  "annual_workflow_dispatch_authorized": false,
  "annual_workflow_run_count": 6,
  "broker_mutation_authorized": false,
  "cross_year_result_production_authorized": false,
  "decision": "DEC-562",
  "demo_order_authorized": false,
  "dispatch_command_present": false,
  "expected_head_sha": "236fc332c3d0fb0ad52a25038e764cd0f4e5d49f",
  "expected_run_attempt": 1,
  "expected_run_number": 381,
  "failed_run_1_id": 37126711695,
  "failed_run_376_id": 37191637168,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_receipt_source_blob_sha": "5befb123f9d3f01cd4457c992c454c662a9f5b7d",
  "installed_gate_blob_sha": "d87fe85a5b426fa92caf7d6cc165445590f4097c",
  "installed_runtime_blob_sha": "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
  "live_order_authorized": false,
  "next_gate": "ANNUAL_PATTERN_CATALOGUE_2019_DISPATCH_AUTHORIZATION_BEFORE_RUN",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "preflight_fingerprint_sha256": "b02c7c68f682f9706e3f9e4a6e4ade7826e1abb47d01330f543279221063fe45",
  "preflight_read_only": true,
  "previous_annual_freeze_run_id": 37237817538,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "runtime_authorization_installed": true,
  "runtime_gate_active": true,
  "source_install_artifact_digest": "sha256:9739dda98fe654435c9e58053b934cfba4f1cf8747ab79dcd7dcbe9e27e6492b",
  "source_install_artifact_id": 11342593171,
  "source_install_commit_sha": "ea3d63b5181fc592039c0c26d6decb358e43f7cc",
  "source_install_receipt_decision": "DEC-561",
  "source_install_receipt_fingerprint_sha256": "098d2d24fbce40943ccff16a9ae1374e77facc0804365fedbb15eb128b3ca7be",
  "source_installer_workflow_head_sha": "0e23f87b5990961bcfe8d4e6998fef20282f6626",
  "source_installer_workflow_run_id": 37304310188,
  "stage": "ANNUAL_CATALOGUE_2019_DISPATCH_PREFLIGHT_READY",
  "strategy_v1_synthesis_authorized": false,
  "successful_2015_run_id": 37198002653,
  "successful_2016_run_id": 37206992367,
  "successful_2017_run_id": 37227536041,
  "successful_2018_run_id": 37237817538,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2019-dispatch-preflight-v1"
}
"""


def _preflight() -> dict[str, object]:
    value = json.loads(PREFLIGHT_JSON)
    assert isinstance(value, dict)
    return value


def _authorization() -> dict[str, object]:
    value = build_2019_dispatch_authorization(
        _preflight(),
        repository_root=REPOSITORY_ROOT,
        authorization_head_sha=AUTHORIZATION_HEAD,
    )
    assert value["authorization_fingerprint_sha256"] == (
        "fd554fbfd2ca556b0e4a6e65ddb00ec805809eda70d80a1e1a401edfeb71fcf8"
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
            {
                **common,
                "id": 37237817538,
                "run_number": 380,
                "head_sha": "30971a996f514670a6f836d8e45cf80137197a4f",
                "conclusion": "success",
            },
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-564 requires the current installed 2019 runtime state",
)
class AnnualPatternCatalogue2019DispatchActionPreflightTests(unittest.TestCase):
    def test_sources_pin_concrete_authorization_and_runtime(self) -> None:
        source = validate_2019_dispatch_action_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["authorization_source_blob_sha"],
            "aa614fd67367a53be2889651a701b63f1ef2a7c9",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        )

    def test_exact_state_freezes_run381_parameters_read_only(self) -> None:
        value = build_2019_dispatch_action_preflight(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2019_dispatch_action_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-564")
        self.assertEqual(value["annual_workflow_run_count"], 6)
        self.assertEqual(value["annual_segment_label"], "2019")
        self.assertEqual(value["prior_segment_label"], "2018")
        self.assertEqual(value["successful_2018_run_id"], 37237817538)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37237817538)
        self.assertEqual(value["expected_run_number"], 381)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["dispatch_ref"], "main")
        self.assertEqual(value["dispatch_input_annual_segment_label"], "2019")
        self.assertEqual(
            value["dispatch_input_previous_annual_freeze_run_id"],
            "37237817538",
        )
        self.assertTrue(value["dispatch_parameters_frozen"])
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["run_382_or_later_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_unexpected_run381_is_rejected(self) -> None:
        runs = _runs()
        rows = list(runs["workflow_runs"])
        rows.append(
            {
                "id": 99999999999,
                "name": "phase8a-annual-pattern-catalogue",
                "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
                "run_number": 381,
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
            "exactly six prior annual workflow runs",
        ):
            build_2019_dispatch_action_preflight(
                _authorization(),
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=HEAD,
            )

    def test_run380_head_drift_is_rejected(self) -> None:
        runs = _runs()
        rows = [dict(row) for row in runs["workflow_runs"]]
        rows[5]["head_sha"] = "d" * 40
        with self.assertRaisesRegex(
            ValueError,
            "annual run 380 head_sha mismatch",
        ):
            build_2019_dispatch_action_preflight(
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
            build_2019_dispatch_action_preflight(
                authorization,
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2019_dispatch_action_preflight(
                _authorization(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "c" * 40}},
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2019_dispatch_action_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
