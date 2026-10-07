from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_runtime_authorization_install_action import (
    compile_2023_runtime_authorization_install_action,
    validate_2023_runtime_authorization_install_action,
    validate_2023_runtime_authorization_install_action_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CURRENT_HEAD = "a" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _preflight() -> dict[str, object]:
    return {
        "activation_mutation_file_count": 2,
        "annual_segment_label": "2023",
        "annual_workflow_dispatch_authorized": False,
        "authorization_contract_validated": True,
        "broker_mutation_authorized": False,
        "cross_year_comparison_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-605",
        "demo_order_authorized": False,
        "dormant_gate_template_blob_sha": "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
        "dormant_gate_template_path": (
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_2023_runtime_authorization.py.disabled"
        ),
        "dormant_runtime_target_template_blob_sha": "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        "dormant_runtime_target_template_path": (
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2023_authorization.py.disabled"
        ),
        "execution_authorization_source_blob_sha": "2c4292abadbffb9dd87edaab67d9e32783facae7",
        "expected_current_runtime_source_blob_sha": "f2734c7ea32355b1024d1097812578b23fc4409d",
        "expected_head_sha": "81ffd195079d853d7bcd7a49ac34720d563f1a49",
        "expected_run_attempt": 1,
        "expected_run_number": 385,
        "governing_method_decision": "DEC-469",
        "governing_protocol_decision": "DEC-470",
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "live_order_authorized": False,
        "next_gate": (
            "EXACT_ANNUAL_PATTERN_CATALOGUE_2023_RUNTIME_"
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC605"
        ),
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "preflight_fingerprint_sha256": (
            "08d7d79adb7f1fabbe156851923adb4f1f907f2dacd54ddbd82e33063116de76"
        ),
        "preflight_read_only": True,
        "previous_annual_freeze_run_id": 37663157285,
        "promotion_authorized": False,
        "protected_catalogue_segment": True,
        "protected_history_access_authorized": False,
        "protocol_2023_2026_catalogue_use_authorized": True,
        "protocol_full_collection_catalogue_use_authorized": True,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "repository_full_name": "Dtwosam/FMP",
        "repository_mutation_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "run_386_or_later_authorized": False,
        "runtime_authorization_installed": False,
        "runtime_authorization_plan_source_blob_sha": "fe5c18f8ffa5e3d698f91060ec8c28e0d0692318",
        "runtime_gate_active": False,
        "runtime_install_preflight_ready": True,
        "runtime_plan_validated": True,
        "source_authorization_decision": "DEC-603",
        "source_authorization_fingerprint_sha256": (
            "dc1f6dc96e4bdbf527ffba49be9df175310389737bd7c70ca945bd260baf3946"
        ),
        "source_authorization_protected_history_access_authorized": True,
        "source_plan_artifact_digest": (
            "sha256:a43cd3c767082ae3c20587690e202f98da32c9824b0cda2f33d211ac19e21de8"
        ),
        "source_plan_artifact_id": 11512058473,
        "source_plan_canonical_sha256": (
            "9c5841d3842bc1c342c0e4032460c30ec66c33d0d144c47c4cf1a3523a7d1440"
        ),
        "source_plan_decision": "DEC-604",
        "source_plan_workflow_head_sha": "affbb533a320f639c8e4d1a955c2b1fd907b0d63",
        "source_plan_workflow_run_id": 37688619041,
        "stage": "ANNUAL_CATALOGUE_2023_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_READY",
        "strategy_v1_synthesis_authorized": False,
        "target_gate_source_blob_sha": "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
        "target_gate_source_path": (
            "src/fmp/discovery/"
            "annual_pattern_catalogue_2023_runtime_authorization.py"
        ),
        "target_runtime_source_blob_sha": "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        "target_runtime_source_path": "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2023-runtime-authorization-install-preflight-v1",
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-606 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2023RuntimeAuthorizationInstallActionTests(
    unittest.TestCase
):
    def test_fixture_is_exact_dec605(self) -> None:
        value = _preflight()
        unsigned = dict(value)
        fingerprint = unsigned.pop("preflight_fingerprint_sha256")
        self.assertEqual(
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
            fingerprint,
        )
        self.assertEqual(
            hashlib.sha256(_canonical_json(value)).hexdigest(),
            "85c8ac47a4e98d296b4423be1dd551286f82187dc5ec1f0c4c9eadf2fd316599",
        )

    def test_sources_pin_exact_dec605(self) -> None:
        source = validate_2023_runtime_authorization_install_action_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["install_preflight_source_blob_sha"],
            "614784849bca811cbd822cd2243eec19f26163d1",
        )

    def test_action_is_exact_two_file_mutation_and_non_dispatching(self) -> None:
        value = compile_2023_runtime_authorization_install_action(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            main_branch={"name": "main", "commit": {"sha": CURRENT_HEAD}},
            expected_head_sha=CURRENT_HEAD,
        )
        self.assertIs(
            validate_2023_runtime_authorization_install_action(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-606")
        self.assertEqual(value["source_preflight_workflow_run_id"], 37691460323)
        self.assertEqual(value["source_preflight_artifact_id"], 11513856300)
        self.assertEqual(
            value["source_preflight_artifact_digest"],
            "sha256:0cc56948730d68dc76f21fdc5d99dad97218640f3ddabd62b77062d1acb0e00b",
        )
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "08d7d79adb7f1fabbe156851923adb4f1f907f2dacd54ddbd82e33063116de76",
        )
        self.assertEqual(
            value["source_preflight_canonical_sha256"],
            "85c8ac47a4e98d296b4423be1dd551286f82187dc5ec1f0c4c9eadf2fd316599",
        )
        self.assertEqual(value["expected_run_number"], 385)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37663157285)
        self.assertTrue(
            value["source_authorization_protected_history_access_authorized"]
        )
        self.assertTrue(value["protected_catalogue_segment"])
        self.assertEqual(value["action_count"], 2)
        create, update = value["actions"]
        self.assertEqual(create["operation"], "create")
        self.assertEqual(
            create["target_path"],
            "src/fmp/discovery/"
            "annual_pattern_catalogue_2023_runtime_authorization.py",
        )
        self.assertTrue(create["expected_target_absent"])
        self.assertEqual(
            create["expected_result_blob_sha"],
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
        )
        self.assertEqual(update["operation"], "update")
        self.assertEqual(
            update["target_path"],
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        )
        self.assertEqual(
            update["expected_current_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        )
        self.assertEqual(
            update["expected_result_blob_sha"],
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        )
        self.assertTrue(value["repository_mutation_authorized"])
        for field in (
            "runtime_authorization_installed",
            "runtime_gate_active",
            "annual_workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "run_386_or_later_authorized",
            "next_segment_execution_authorized",
            "protected_history_access_authorized",
            "cross_year_comparison_authorized",
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
            compile_2023_runtime_authorization_install_action(
                _preflight(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                expected_head_sha=CURRENT_HEAD,
            )

    def test_refingerprinted_extra_action_is_rejected(self) -> None:
        value = compile_2023_runtime_authorization_install_action(
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
            validate_2023_runtime_authorization_install_action(tampered)

    def test_source_preflight_lock_tamper_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["run_386_or_later_authorized"] = True
        unsigned = dict(preflight)
        unsigned.pop("preflight_fingerprint_sha256", None)
        preflight["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaises(ValueError):
            compile_2023_runtime_authorization_install_action(
                preflight,
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": CURRENT_HEAD}},
                expected_head_sha=CURRENT_HEAD,
            )

    def test_cli_is_compile_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/"
            "phase8a_annual_pattern_catalogue_2023_runtime_authorization_install_action.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("compile")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
