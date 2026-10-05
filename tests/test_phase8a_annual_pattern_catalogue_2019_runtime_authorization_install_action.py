from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2019_runtime_authorization_install_action import (
    compile_2019_runtime_authorization_install_action,
    validate_2019_runtime_authorization_install_action,
    validate_2019_runtime_authorization_install_action_sources,
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
        "decision": "DEC-559",
        "version": (
            "fmp-annual-catalogue-2019-runtime-authorization-install-preflight-v1"
        ),
        "execution_authorization_source_blob_sha": (
            "084fa62c7fd4855fc561038d991e1215df2ff73b"
        ),
        "runtime_authorization_plan_source_blob_sha": (
            "41e7adba8b5061028d8adc7ef93d1fc02424039e"
        ),
        "source_authorization_decision": "DEC-557",
        "source_authorization_fingerprint_sha256": (
            "c785127b20f57210e60ebd681d7b0e48a66f419fa8fbbbdd9cdd8fa560b464f9"
        ),
        "source_plan_decision": "DEC-558",
        "source_plan_workflow_run_id": 37294642532,
        "source_plan_workflow_head_sha": (
            "2e8d66e515b9f87023f78ae06c644bf804440501"
        ),
        "source_plan_artifact_id": 11337484835,
        "source_plan_artifact_digest": (
            "sha256:7ee0dbfd168a8a63664419cce85e41a65fde46f9e492dbee65868386d74975a8"
        ),
        "source_plan_canonical_sha256": (
            "5e35a860916137118e6a1ca9d751045373c59ad9e5e0ac373545b20740ccd074"
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_"
            "INSTALL_PREFLIGHT_READY"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": "bb1c7901d1b5859bec97a381716166e9024a6022",
        "annual_segment_label": "2019",
        "expected_run_number": 381,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37237817538,
        "expected_current_runtime_source_blob_sha": (
            "410180c34a9e3500bbbb42310a5253b993ac7785"
        ),
        "dormant_gate_template_path": (
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_2019_runtime_authorization.py.disabled"
        ),
        "dormant_gate_template_blob_sha": (
            "d87fe85a5b426fa92caf7d6cc165445590f4097c"
        ),
        "dormant_runtime_target_template_path": (
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2019_authorization.py.disabled"
        ),
        "dormant_runtime_target_template_blob_sha": (
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e"
        ),
        "target_gate_source_path": (
            "src/fmp/discovery/"
            "annual_pattern_catalogue_2019_runtime_authorization.py"
        ),
        "target_gate_source_blob_sha": (
            "d87fe85a5b426fa92caf7d6cc165445590f4097c"
        ),
        "target_runtime_source_path": (
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ),
        "target_runtime_source_blob_sha": (
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e"
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
            "EXACT_ANNUAL_PATTERN_CATALOGUE_2019_RUNTIME_"
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC559"
        ),
    }
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    assert value["preflight_fingerprint_sha256"] == (
        "1c585ad2a2a0bdf3a0fc811376d1fa5701b293b2fd888abca30ea5c13fcf3861"
    )
    return value


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-560 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2019RuntimeAuthorizationInstallActionTests(
    unittest.TestCase
):
    def test_sources_pin_exact_dec559(self) -> None:
        source = validate_2019_runtime_authorization_install_action_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["install_preflight_source_blob_sha"],
            "a3b087419f9b9dd8980139f5dc47db4de3f657fd",
        )

    def test_action_is_exact_two_file_mutation_and_non_dispatching(self) -> None:
        value = compile_2019_runtime_authorization_install_action(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            main_branch={"name": "main", "commit": {"sha": CURRENT_HEAD}},
            expected_head_sha=CURRENT_HEAD,
        )
        self.assertIs(
            validate_2019_runtime_authorization_install_action(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-560")
        self.assertEqual(value["source_preflight_workflow_run_id"], 37295798286)
        self.assertEqual(value["source_preflight_artifact_id"], 11338796649)
        self.assertEqual(value["expected_run_number"], 381)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37237817538)
        self.assertEqual(value["action_count"], 2)
        create, update = value["actions"]
        self.assertEqual(create["operation"], "create")
        self.assertEqual(
            create["target_path"],
            "src/fmp/discovery/"
            "annual_pattern_catalogue_2019_runtime_authorization.py",
        )
        self.assertTrue(create["expected_target_absent"])
        self.assertEqual(
            create["expected_result_blob_sha"],
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
        )
        self.assertEqual(update["operation"], "update")
        self.assertEqual(
            update["target_path"],
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        )
        self.assertEqual(
            update["expected_current_blob_sha"],
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        )
        self.assertEqual(
            update["expected_result_blob_sha"],
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
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
            compile_2019_runtime_authorization_install_action(
                _preflight(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                expected_head_sha=CURRENT_HEAD,
            )

    def test_refingerprinted_extra_action_is_rejected(self) -> None:
        value = compile_2019_runtime_authorization_install_action(
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
            validate_2019_runtime_authorization_install_action(tampered)

    def test_cli_is_compile_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/"
            "phase8a_annual_pattern_catalogue_2019_runtime_authorization_install_action.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("compile")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
