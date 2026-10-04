from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2017_dispatch_authorization import (
    build_2017_dispatch_authorization,
    validate_2017_dispatch_authorization,
    validate_2017_dispatch_authorization_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION_HEAD = "a" * 40


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
        "annual_segment_label": "2017",
        "annual_workflow_dispatch_authorized": False,
        "annual_workflow_run_count": 4,
        "broker_mutation_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-540",
        "demo_order_authorized": False,
        "dispatch_command_present": False,
        "expected_head_sha": "f7983f960ae141f15c83b3cc05f6d6030140c802",
        "expected_run_attempt": 1,
        "expected_run_number": 379,
        "failed_run_1_id": 37126711695,
        "failed_run_376_id": 37191637168,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "install_receipt_source_blob_sha": (
            "c3662046efc7daf2c00637066aa78c885b85fa8e"
        ),
        "installed_gate_blob_sha": (
            "c1853eeec55ee98b3155a6054f07cf360793ba9b"
        ),
        "installed_runtime_blob_sha": (
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"
        ),
        "live_order_authorized": False,
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2017_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "preflight_read_only": True,
        "previous_annual_freeze_run_id": 37206992367,
        "promotion_authorized": False,
        "real_money_authorized": False,
        "repository_full_name": "Dtwosam/FMP",
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "source_install_artifact_digest": (
            "sha256:6672b0642a763424541d971d84b273f8c2fde5089fcd736e6152fe8dc9a7e32e"
        ),
        "source_install_artifact_id": 11309927463,
        "source_install_commit_sha": (
            "dcdf7210b0039077efa3a23c65c2ed8fa41e2427"
        ),
        "source_install_receipt_decision": "DEC-539",
        "source_install_receipt_fingerprint_sha256": (
            "42b20ce4123a8d42e79942dc5d7768ab5397ba63ed45823650e9cdad414af68d"
        ),
        "source_installer_workflow_head_sha": (
            "9c3e2e6042b5a00109ee1f07ad6fd24c9ac33308"
        ),
        "source_installer_workflow_run_id": 37219929487,
        "stage": "ANNUAL_CATALOGUE_2017_DISPATCH_PREFLIGHT_READY",
        "strategy_v1_synthesis_authorized": False,
        "successful_2015_run_id": 37198002653,
        "successful_2016_run_id": 37206992367,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2017-dispatch-preflight-v1",
    }
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    assert (
        value["preflight_fingerprint_sha256"]
        == "7329cf4238c1aa8b608d7b4e41eaaaf643f78c3fb99f7ae399f6db303a75ffad"
    )
    return value


class AnnualPatternCatalogue2017DispatchAuthorizationTests(unittest.TestCase):
    def test_sources_pin_dec540_and_installed_runtime(self) -> None:
        source = validate_2017_dispatch_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["dispatch_preflight_source_blob_sha"],
            "0e048756a1a9ca5f8d45896c6ff212d386996ed0",
        )
        self.assertEqual(
            source["installed_gate_blob_sha"],
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
        )
        self.assertEqual(
            source["installed_runtime_blob_sha"],
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
        )

    def test_exact_preflight_yields_source_only_run379_authorization(self) -> None:
        value = build_2017_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        self.assertIs(validate_2017_dispatch_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-541")
        self.assertEqual(value["source_preflight_workflow_run_id"], 37223000759)
        self.assertEqual(value["source_preflight_artifact_id"], 11311031268)
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "7329cf4238c1aa8b608d7b4e41eaaaf643f78c3fb99f7ae399f6db303a75ffad",
        )
        self.assertEqual(value["authorization_head_sha"], AUTHORIZATION_HEAD)
        self.assertEqual(value["annual_segment_label"], "2017")
        self.assertEqual(value["prior_segment_label"], "2016")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37206992367)
        self.assertEqual(value["expected_run_number"], 379)
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
        self.assertFalse(value["run_380_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_source_preflight_dispatch_tamper_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["annual_workflow_dispatch_authorized"] = True
        unsigned = dict(preflight)
        unsigned.pop("preflight_fingerprint_sha256", None)
        preflight["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "preflight fingerprint mismatch|annual_workflow_dispatch_authorized",
        ):
            build_2017_dispatch_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
                authorization_head_sha=AUTHORIZATION_HEAD,
            )

    def test_wrong_run_number_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["expected_run_number"] = 380
        unsigned = dict(preflight)
        unsigned.pop("preflight_fingerprint_sha256", None)
        preflight["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "preflight fingerprint mismatch|expected run number",
        ):
            build_2017_dispatch_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
                authorization_head_sha=AUTHORIZATION_HEAD,
            )

    def test_refingerprinted_later_run_authority_is_rejected(self) -> None:
        value = build_2017_dispatch_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            authorization_head_sha=AUTHORIZATION_HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["run_380_or_later_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "run_380_or_later_authorized mismatch",
        ):
            validate_2017_dispatch_authorization(tampered)

    def test_cli_is_authorize_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2017_dispatch_authorization.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("authorize")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
