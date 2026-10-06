from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2021_dispatch_authorization import (
    build_2021_dispatch_authorization,
)
from fmp.discovery.annual_pattern_catalogue_2021_dispatch_action_preflight import (
    build_2021_dispatch_action_preflight,
    validate_2021_dispatch_action_preflight,
    validate_2021_dispatch_action_preflight_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "e" * 40
AUTHORIZATION_HEAD = "80ea2e3a75397e098168fefa04851019d18c80f2"

PREFLIGHT_JSON = r"""\n{
  "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
  "annual_segment_label": "2021",
  "annual_workflow_dispatch_authorized": false,
  "annual_workflow_run_count": 8,
  "broker_mutation_authorized": false,
  "cross_year_result_production_authorized": false,
  "decision": "DEC-586",
  "demo_order_authorized": false,
  "dispatch_command_present": false,
  "expected_head_sha": "b62616de10cc4362ff4f372e44e73fcd2be91366",
  "expected_run_attempt": 1,
  "expected_run_number": 383,
  "failed_run_1_id": 37126711695,
  "failed_run_376_id": 37191637168,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_receipt_source_blob_sha": "b088a8483ea555b28107462e88b8c16ec72b66b8",
  "installed_gate_blob_sha": "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
  "installed_runtime_blob_sha": "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
  "live_order_authorized": false,
  "next_gate": "ANNUAL_PATTERN_CATALOGUE_2021_DISPATCH_AUTHORIZATION_BEFORE_RUN",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "preflight_fingerprint_sha256": "55a2c7cbeec4a0ae54b96f1a2687e79e929b79cc4e484b442a9729e62da8f84a",
  "preflight_read_only": true,
  "previous_annual_freeze_run_id": 37443770076,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "runtime_authorization_installed": true,
  "runtime_gate_active": true,
  "source_install_artifact_digest": "sha256:0eec90cdfdd9b4ab68fd4989e7114d3d40baf41fc7e5f1129bd6cac182f48d74",
  "source_install_artifact_id": 11427632507,
  "source_install_commit_sha": "4833c86f74af3febfc2592048916d9ce20aa051a",
  "source_install_receipt_decision": "DEC-585",
  "source_install_receipt_fingerprint_sha256": "6fcbfeb2d2f7a8154925ac7fb5d08d68050a0ea2f2bbf2b3612015fd08b422c5",
  "source_installer_workflow_head_sha": "3f128ce83dc8d88b3951d5e4b17312f3139d9100",
  "source_installer_workflow_run_id": 37496446082,
  "stage": "ANNUAL_CATALOGUE_2021_DISPATCH_PREFLIGHT_READY",
  "strategy_v1_synthesis_authorized": false,
  "successful_2015_run_id": 37198002653,
  "successful_2016_run_id": 37206992367,
  "successful_2017_run_id": 37227536041,
  "successful_2018_run_id": 37237817538,
  "successful_2019_run_id": 37310525635,
  "successful_2020_run_id": 37443770076,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2021-dispatch-preflight-v1"
}\n"""\n\n\ndef _preflight() -> dict[str, object]:
    value = json.loads(PREFLIGHT_JSON)
    assert isinstance(value, dict)
    return value


def _authorization() -> dict[str, object]:
    value = build_2021_dispatch_authorization(
        _preflight(),
        repository_root=REPOSITORY_ROOT,
        authorization_head_sha=AUTHORIZATION_HEAD,
    )
    assert value["authorization_fingerprint_sha256"] == (
        "d171f0c272166c277e3eae6dd37b7c8e6ff1166c0503a4bf5e0ff793226049b2"
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
            {
                **common,
                "id": 37310525635,
                "run_number": 381,
                "head_sha": "8bcee3a7a834743f08bd9ad73109bfc09609a2fe",
                "conclusion": "success",
            },
            {
                **common,
                "id": 37443770076,
                "run_number": 382,
                "head_sha": "681e81e021d4970a67b18370142d55b17ec68864",
                "conclusion": "success",
            },
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-588 requires the current installed 2021 runtime state",
)
class AnnualPatternCatalogue2021DispatchActionPreflightTests(unittest.TestCase):
    def test_sources_pin_concrete_authorization_and_runtime(self) -> None:
        source = validate_2021_dispatch_action_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["authorization_source_blob_sha"],
            "17a7b4de05f3d27bc96ecbc182347ac1fc7926af",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        )

    def test_exact_state_freezes_run383_parameters_read_only(self) -> None:
        value = build_2021_dispatch_action_preflight(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2021_dispatch_action_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-588")
        self.assertEqual(value["annual_workflow_run_count"], 7)
        self.assertEqual(value["annual_segment_label"], "2021")
        self.assertEqual(value["prior_segment_label"], "2020")
        self.assertEqual(value["successful_2020_run_id"], 37443770076)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37443770076)
        self.assertEqual(value["expected_run_number"], 383)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["dispatch_ref"], "main")
        self.assertEqual(value["dispatch_input_annual_segment_label"], "2021")
        self.assertEqual(
            value["dispatch_input_previous_annual_freeze_run_id"],
            "37443770076",
        )
        self.assertTrue(value["dispatch_parameters_frozen"])
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["run_384_or_later_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_unexpected_run383_is_rejected(self) -> None:
        runs = _runs()
        rows = list(runs["workflow_runs"])
        rows.append(
            {
                "id": 99999999999,
                "name": "phase8a-annual-pattern-catalogue",
                "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
                "run_number": 382,
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
            "exactly eight prior annual workflow runs",
        ):
            build_2021_dispatch_action_preflight(
                _authorization(),
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=HEAD,
            )

    def test_run382_head_drift_is_rejected(self) -> None:
        runs = _runs()
        rows = [dict(row) for row in runs["workflow_runs"]]
        rows[7]["head_sha"] = "d" * 40
        with self.assertRaisesRegex(
            ValueError,
            "annual run 382 head_sha mismatch",
        ):
            build_2021_dispatch_action_preflight(
                _authorization(),
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=HEAD,
            )

    def test_concrete_authorization_head_drift_is_rejected(self) -> None:
        authorization = copy.deepcopy(_authorization())
        authorization["authorization_head_sha"] = "f" * 40
        unsigned = dict(authorization)
        unsigned.pop("authorization_fingerprint_sha256", None)
        import hashlib
        authorization["authorization_fingerprint_sha256"] = hashlib.sha256(
            (
                json.dumps(
                    unsigned,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "source authorization head mismatch",
        ):
            build_2021_dispatch_action_preflight(
                authorization,
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2021_dispatch_action_preflight(
                _authorization(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "c" * 40}},
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2021_dispatch_action_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
