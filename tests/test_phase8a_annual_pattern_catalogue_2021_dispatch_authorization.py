from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2021_dispatch_authorization import (
    build_2021_dispatch_authorization,
    validate_2021_dispatch_authorization,
    validate_2021_dispatch_authorization_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION_HEAD = "a" * 40

PREFLIGHT_JSON = r"""
{
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
}
"""


def _preflight() -> dict[str, object]:
    value = json.loads(PREFLIGHT_JSON)
    assert isinstance(value, dict)
    return value


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-587 requires installed 2021 runtime and active annual workflow",
)
class AnnualPatternCatalogue2021DispatchAuthorizationTests(unittest.TestCase):
    def test_sources_pin_dec586_and_installed_runtime(self) -> None:
        source = validate_2021_dispatch_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["dispatch_preflight_source_blob_sha"],
            "a2454464ad9445dfd3ac788797f1c7633b67e116",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        )

    def test_exact_preflight_yields_source_only_run383_authorization(self) -> None:
        value = build_2021_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        self.assertIs(validate_2021_dispatch_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-587")
        self.assertEqual(value["source_preflight_workflow_run_id"], 37501665304)
        self.assertEqual(value["source_preflight_artifact_id"], 11430072006)
        self.assertEqual(
            value["source_preflight_artifact_digest"],
            "sha256:e973c65ad1b72531e372a86cb028687733b8dfd9414fd901009c83d396621837",
        )
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "55a2c7cbeec4a0ae54b96f1a2687e79e929b79cc4e484b442a9729e62da8f84a",
        )
        self.assertEqual(value["authorization_head_sha"], AUTHORIZATION_HEAD)
        self.assertEqual(value["annual_segment_label"], "2021")
        self.assertEqual(value["prior_segment_label"], "2020")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37443770076)
        self.assertEqual(value["expected_run_number"], 383)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["authorization_contract_validated"])
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertTrue(value["source_only_authorization"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertFalse(value["run_384_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_source_preflight_dispatch_tamper_is_rejected(self) -> None:
        preflight = copy.deepcopy(_preflight())
        preflight["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "preflight fingerprint mismatch|annual_workflow_dispatch_authorized",
        ):
            build_2021_dispatch_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
                authorization_head_sha=AUTHORIZATION_HEAD,
            )

    def test_wrong_run_number_is_rejected(self) -> None:
        preflight = copy.deepcopy(_preflight())
        preflight["expected_run_number"] = 384
        with self.assertRaisesRegex(
            ValueError,
            "preflight fingerprint mismatch|expected_run_number mismatch|expected run number mismatch",
        ):
            build_2021_dispatch_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
                authorization_head_sha=AUTHORIZATION_HEAD,
            )

    def test_refingerprinted_later_run_authority_is_rejected(self) -> None:
        value = build_2021_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["run_384_or_later_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
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
            "run_384_or_later_authorized mismatch",
        ):
            validate_2021_dispatch_authorization(tampered)

    def test_cli_is_authorize_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2021_dispatch_authorization.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("authorize")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
