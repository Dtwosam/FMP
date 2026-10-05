from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2019_dispatch_authorization import (
    build_2019_dispatch_authorization,
    validate_2019_dispatch_authorization,
    validate_2019_dispatch_authorization_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION_HEAD = "a" * 40

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


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-563 requires installed 2019 runtime and active annual workflow",
)
class AnnualPatternCatalogue2019DispatchAuthorizationTests(unittest.TestCase):
    def test_sources_pin_dec562_and_installed_runtime(self) -> None:
        source = validate_2019_dispatch_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["dispatch_preflight_source_blob_sha"],
            "4d1313ac3f79638e252c9d0e4f87844d387d73bc",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        )

    def test_exact_preflight_yields_source_only_run381_authorization(self) -> None:
        value = build_2019_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        self.assertIs(validate_2019_dispatch_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-563")
        self.assertEqual(value["source_preflight_workflow_run_id"], 37305622078)
        self.assertEqual(value["source_preflight_artifact_id"], 11344155034)
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "b02c7c68f682f9706e3f9e4a6e4ade7826e1abb47d01330f543279221063fe45",
        )
        self.assertEqual(value["authorization_head_sha"], AUTHORIZATION_HEAD)
        self.assertEqual(value["annual_segment_label"], "2019")
        self.assertEqual(value["prior_segment_label"], "2018")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37237817538)
        self.assertEqual(value["expected_run_number"], 381)
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
        self.assertFalse(value["run_382_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_source_preflight_dispatch_tamper_is_rejected(self) -> None:
        preflight = copy.deepcopy(_preflight())
        preflight["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "preflight fingerprint mismatch|annual_workflow_dispatch_authorized",
        ):
            build_2019_dispatch_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
                authorization_head_sha=AUTHORIZATION_HEAD,
            )

    def test_wrong_run_number_is_rejected(self) -> None:
        preflight = copy.deepcopy(_preflight())
        preflight["expected_run_number"] = 382
        with self.assertRaisesRegex(
            ValueError,
            "preflight fingerprint mismatch|expected_run_number mismatch|expected run number mismatch",
        ):
            build_2019_dispatch_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
                authorization_head_sha=AUTHORIZATION_HEAD,
            )

    def test_refingerprinted_later_run_authority_is_rejected(self) -> None:
        value = build_2019_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["run_382_or_later_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        import hashlib
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
            "run_382_or_later_authorized mismatch",
        ):
            validate_2019_dispatch_authorization(tampered)

    def test_cli_is_authorize_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2019_dispatch_authorization.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("authorize")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
