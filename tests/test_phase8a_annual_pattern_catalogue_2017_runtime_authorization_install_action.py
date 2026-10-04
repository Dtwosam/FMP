from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2017_runtime_authorization_install_action import (
    compile_2017_runtime_authorization_install_action,
    validate_2017_runtime_authorization_install_action,
    validate_2017_runtime_authorization_install_action_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CURRENT_HEAD = "a" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _preflight() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-537",
        "version": (
            "fmp-annual-catalogue-2017-runtime-authorization-install-preflight-v1"
        ),
        "execution_authorization_source_blob_sha": (
            "ef70a0aec215943a2d992a484fd95feb390c6e07"
        ),
        "runtime_authorization_plan_source_blob_sha": (
            "441b411cdae5b541226d3c0ef88b6cf687ce70da"
        ),
        "source_authorization_decision": "DEC-535",
        "source_authorization_fingerprint_sha256": "1" * 64,
        "source_plan_decision": "DEC-536",
        "source_plan_workflow_run_id": 37215086807,
        "source_plan_workflow_head_sha": (
            "585feb304ab11ac2fead24eac05233960ba80e0e"
        ),
        "source_plan_artifact_id": 11307494750,
        "source_plan_artifact_digest": (
            "sha256:80395e51c57ca26788ef4291d7cdf1e6e3e79ef6cf92893e9d37d14dd8bc2adc"
        ),
        "source_plan_canonical_sha256": "2" * 64,
        "stage": (
            "ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_"
            "INSTALL_PREFLIGHT_READY"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": (
            "f8a8de09adc4b64b84b2129eacbc38d0eb00e645"
        ),
        "annual_segment_label": "2017",
        "expected_run_number": 379,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37206992367,
        "expected_current_runtime_source_blob_sha": (
            "b564f5a26fdef146fc6080962e7c4762b0b5949a"
        ),
        "dormant_gate_template_path": (
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_2017_runtime_authorization.py.disabled"
        ),
        "dormant_gate_template_blob_sha": (
            "c1853eeec55ee98b3155a6054f07cf360793ba9b"
        ),
        "dormant_runtime_target_template_path": (
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2017_authorization.py.disabled"
        ),
        "dormant_runtime_target_template_blob_sha": (
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"
        ),
        "target_gate_source_path": (
            "src/fmp/discovery/"
            "annual_pattern_catalogue_2017_runtime_authorization.py"
        ),
        "target_gate_source_blob_sha": (
            "c1853eeec55ee98b3155a6054f07cf360793ba9b"
        ),
        "target_runtime_source_path": (
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ),
        "target_runtime_source_blob_sha": (
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"
        ),
        "activation_mutation_file_count": 2,
        "authorization_contract_validated": True,
        "runtime_plan_validated": True,
        "runtime_install_preflight_ready": True,
        "preflight_read_only": True,
        "repository_mutation_authorized": False,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
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
        "next_gate": (
            "EXACT_ANNUAL_PATTERN_CATALOGUE_2017_RUNTIME_"
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC537"
        ),
    }
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-538 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2017RuntimeAuthorizationInstallActionTests(
    unittest.TestCase
):
    def test_sources_pin_exact_dec537(self) -> None:
        source = validate_2017_runtime_authorization_install_action_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["install_preflight_source_blob_sha"],
            "446fb95265ee222aa40ffa3f11ef869a1ede8090",
        )

    def test_action_is_exact_two_file_mutation_and_non_dispatching(self) -> None:
        value = compile_2017_runtime_authorization_install_action(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            main_branch={"name": "main", "commit": {"sha": CURRENT_HEAD}},
            expected_head_sha=CURRENT_HEAD,
        )
        self.assertIs(
            validate_2017_runtime_authorization_install_action(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-538")
        self.assertEqual(value["source_preflight_workflow_run_id"], 37215789401)
        self.assertEqual(value["source_preflight_artifact_id"], 11308490990)
        self.assertEqual(value["expected_run_number"], 379)
        self.assertEqual(value["action_count"], 2)
        create, update = value["actions"]
        self.assertEqual(create["operation"], "create")
        self.assertEqual(
            create["target_path"],
            "src/fmp/discovery/"
            "annual_pattern_catalogue_2017_runtime_authorization.py",
        )
        self.assertTrue(create["expected_target_absent"])
        self.assertEqual(
            create["expected_result_blob_sha"],
            "c1853eeec55ee98b3155a6054f07cf360793ba9b",
        )
        self.assertEqual(update["operation"], "update")
        self.assertEqual(
            update["target_path"],
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        )
        self.assertEqual(
            update["expected_current_blob_sha"],
            "b564f5a26fdef146fc6080962e7c4762b0b5949a",
        )
        self.assertEqual(
            update["expected_result_blob_sha"],
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
        )
        self.assertTrue(value["repository_mutation_authorized"])
        for field in (
            "runtime_authorization_installed",
            "runtime_gate_active",
            "annual_workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "next_segment_execution_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(value[field], field)

    def test_current_main_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "current main head mismatch"):
            compile_2017_runtime_authorization_install_action(
                _preflight(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                expected_head_sha=CURRENT_HEAD,
            )

    def test_refingerprinted_extra_action_is_rejected(self) -> None:
        value = compile_2017_runtime_authorization_install_action(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            main_branch={"name": "main", "commit": {"sha": CURRENT_HEAD}},
            expected_head_sha=CURRENT_HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["actions"] = list(tampered["actions"]) + [
            {"order": 3, "operation": "create", "target_path": "unexpected"}
        ]
        tampered["action_count"] = 3
        unsigned = dict(tampered)
        unsigned.pop("install_action_fingerprint_sha256", None)
        tampered["install_action_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "action_count mismatch"):
            validate_2017_runtime_authorization_install_action(tampered)

    def test_cli_is_compile_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/"
            "phase8a_annual_pattern_catalogue_2017_runtime_authorization_install_action.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("compile")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
