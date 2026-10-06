from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2021_runtime_authorization_install_action import (
    compile_2021_runtime_authorization_install_action,
    validate_2021_runtime_authorization_install_action,
    validate_2021_runtime_authorization_install_action_sources,
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
        "decision": "DEC-583",
        "version": (
            "fmp-annual-catalogue-2021-runtime-authorization-install-preflight-v1"
        ),
        "execution_authorization_source_blob_sha": (
            "3e086e82201ed0bea85226c115ae7a09e7d95983"
        ),
        "runtime_authorization_plan_source_blob_sha": (
            "de1643991d85cd63e5505401b871e3c02315e0e9"
        ),
        "source_authorization_decision": "DEC-581",
        "source_authorization_fingerprint_sha256": (
            "56226545935b649e24077b1e108e17b865a65bbdbee36fb73a9605d4f766d6d6"
        ),
        "source_plan_decision": "DEC-582",
        "source_plan_workflow_run_id": 37473293705,
        "source_plan_workflow_head_sha": (
            "2403d2770eca576e418f216196a0111fa7f07136"
        ),
        "source_plan_artifact_id": 11416884894,
        "source_plan_artifact_digest": (
            "sha256:cfc8580df9318eeebfdae9e446fa92603e5f2e408ec0066a05945845654743b0"
        ),
        "source_plan_canonical_sha256": (
            "ea0244c3ef60cfa21dc90567faeff680bca856afc68acc96e9e74c19fafd54f1"
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2021_RUNTIME_AUTHORIZATION_"
            "INSTALL_PREFLIGHT_READY"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": "0925e7d51d9c1d513cb737c6b9a00809bad61080",
        "annual_segment_label": "2021",
        "expected_run_number": 383,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37443770076,
        "expected_current_runtime_source_blob_sha": (
            "4e124365430672fa63825b272001937c60151644"
        ),
        "dormant_gate_template_path": (
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_2021_runtime_authorization.py.disabled"
        ),
        "dormant_gate_template_blob_sha": (
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9"
        ),
        "dormant_runtime_target_template_path": (
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2021_authorization.py.disabled"
        ),
        "dormant_runtime_target_template_blob_sha": (
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"
        ),
        "target_gate_source_path": (
            "src/fmp/discovery/"
            "annual_pattern_catalogue_2021_runtime_authorization.py"
        ),
        "target_gate_source_blob_sha": (
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9"
        ),
        "target_runtime_source_path": (
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ),
        "target_runtime_source_blob_sha": (
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"
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
            "EXACT_ANNUAL_PATTERN_CATALOGUE_2021_RUNTIME_"
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC583"
        ),
    }
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    assert value["preflight_fingerprint_sha256"] == (
        "54bb157ee055a5c625f1cb05094e7c4f8228f48766ccdfb163e4d2b07223d575"
    )
    return value


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-584 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2021RuntimeAuthorizationInstallActionTests(
    unittest.TestCase
):
    def test_sources_pin_exact_dec559(self) -> None:
        source = validate_2021_runtime_authorization_install_action_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["install_preflight_source_blob_sha"],
            "b8ba899634fe1b45ee7a50dc13da97440c3d45d0",
        )

    def test_action_is_exact_two_file_mutation_and_non_dispatching(self) -> None:
        value = compile_2021_runtime_authorization_install_action(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            main_branch={"name": "main", "commit": {"sha": CURRENT_HEAD}},
            expected_head_sha=CURRENT_HEAD,
        )
        self.assertIs(
            validate_2021_runtime_authorization_install_action(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-584")
        self.assertEqual(value["source_preflight_workflow_run_id"], 37486048003)
        self.assertEqual(value["source_preflight_artifact_id"], 11423396654)
        self.assertEqual(value["expected_run_number"], 383)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37443770076)
        self.assertEqual(value["action_count"], 2)
        create, update = value["actions"]
        self.assertEqual(create["operation"], "create")
        self.assertEqual(
            create["target_path"],
            "src/fmp/discovery/"
            "annual_pattern_catalogue_2021_runtime_authorization.py",
        )
        self.assertTrue(create["expected_target_absent"])
        self.assertEqual(
            create["expected_result_blob_sha"],
            "cac68c905bedf3105aa7e766eaa968c87bff6ce9",
        )
        self.assertEqual(update["operation"], "update")
        self.assertEqual(
            update["target_path"],
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        )
        self.assertEqual(
            update["expected_current_blob_sha"],
            "4e124365430672fa63825b272001937c60151644",
        )
        self.assertEqual(
            update["expected_result_blob_sha"],
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
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
            compile_2021_runtime_authorization_install_action(
                _preflight(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                expected_head_sha=CURRENT_HEAD,
            )

    def test_refingerprinted_extra_action_is_rejected(self) -> None:
        value = compile_2021_runtime_authorization_install_action(
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
            validate_2021_runtime_authorization_install_action(tampered)

    def test_cli_is_compile_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/"
            "phase8a_annual_pattern_catalogue_2021_runtime_authorization_install_action.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("compile")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
