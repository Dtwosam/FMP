from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2022_runtime_authorization_install_action import (
    compile_2022_runtime_authorization_install_action,
    validate_2022_runtime_authorization_install_action,
    validate_2022_runtime_authorization_install_action_sources,
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
        "activation_mutation_file_count": 2,
        "annual_segment_label": "2022",
        "annual_workflow_dispatch_authorized": False,
        "authorization_contract_validated": True,
        "broker_mutation_authorized": False,
        "cross_year_comparison_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-594",
        "demo_order_authorized": False,
        "dormant_gate_template_blob_sha": (
            "ecb21dc7106e7bd43447f4135c3a696251a75e05"
        ),
        "dormant_gate_template_path": (
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_2022_runtime_authorization.py.disabled"
        ),
        "dormant_runtime_target_template_blob_sha": (
            "f2734c7ea32355b1024d1097812578b23fc4409d"
        ),
        "dormant_runtime_target_template_path": (
            "docs/superpowers/templates/"
            "annual_pattern_catalogue_runtime_with_2022_authorization.py.disabled"
        ),
        "execution_authorization_source_blob_sha": (
            "e68e9f1ee41ca89f0ae3d7758d59b4ce8c5823bb"
        ),
        "expected_current_runtime_source_blob_sha": (
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6"
        ),
        "expected_head_sha": "ae0949d54a55d2a71a7cd78f153c391be0c6ff23",
        "expected_run_attempt": 1,
        "expected_run_number": 384,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "live_order_authorized": False,
        "next_gate": (
            "EXACT_ANNUAL_PATTERN_CATALOGUE_2022_RUNTIME_"
            "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC594"
        ),
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "preflight_read_only": True,
        "previous_annual_freeze_run_id": 37531960014,
        "promotion_authorized": False,
        "protected_history_access_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "repository_full_name": "Dtwosam/FMP",
        "repository_mutation_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "run_385_or_later_authorized": False,
        "runtime_authorization_installed": False,
        "runtime_authorization_plan_source_blob_sha": (
            "d7710ab16dde2eea6b0d93dc6387c6cc489b30d7"
        ),
        "runtime_gate_active": False,
        "runtime_install_preflight_ready": True,
        "runtime_plan_validated": True,
        "source_authorization_decision": "DEC-592",
        "source_authorization_fingerprint_sha256": (
            "5365ca95855d97df7ad28ff7d4e6f5c2ec51183899da7f88048d78b5d381bf54"
        ),
        "source_plan_artifact_digest": (
            "sha256:ff974250ff9a09069e77f8c61e96649c9318e83dfcccab74e8dfd3dd07fed420"
        ),
        "source_plan_artifact_id": 11477773270,
        "source_plan_canonical_sha256": (
            "2ed8681de71e27f9767f75a9e47861044c81c3886639195e412495613acd09fd"
        ),
        "source_plan_decision": "DEC-593",
        "source_plan_workflow_head_sha": (
            "9d53e2f11746ccff7e525a1df1d10427fdfdd2be"
        ),
        "source_plan_workflow_run_id": 37611869958,
        "stage": "ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_READY",
        "strategy_v1_synthesis_authorized": False,
        "target_gate_source_blob_sha": (
            "ecb21dc7106e7bd43447f4135c3a696251a75e05"
        ),
        "target_gate_source_path": (
            "src/fmp/discovery/"
            "annual_pattern_catalogue_2022_runtime_authorization.py"
        ),
        "target_runtime_source_blob_sha": (
            "f2734c7ea32355b1024d1097812578b23fc4409d"
        ),
        "target_runtime_source_path": (
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ),
        "trading_authorized": False,
        "version": (
            "fmp-annual-catalogue-2022-runtime-authorization-install-preflight-v1"
        ),
    }
    value["preflight_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    assert value["preflight_fingerprint_sha256"] == (
        "56c3ff244ed7ad47a07ab64efbea68e41acb61cfdba24303f2d265a2e690b08c"
    )
    assert hashlib.sha256(_canonical_json(value)).hexdigest() == (
        "6927206445b32ea2cd8a1e78b0511f70e9815a9204d771712c5976a5d79af4e4"
    )
    return value


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-595 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2022RuntimeAuthorizationInstallActionTests(
    unittest.TestCase
):
    def test_sources_pin_exact_dec594(self) -> None:
        source = validate_2022_runtime_authorization_install_action_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["install_preflight_source_blob_sha"],
            "8d1fce9c947fd7a579a6ab581d605293a02329a3",
        )

    def test_action_is_exact_two_file_mutation_and_non_dispatching(self) -> None:
        value = compile_2022_runtime_authorization_install_action(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
            main_branch={"name": "main", "commit": {"sha": CURRENT_HEAD}},
            expected_head_sha=CURRENT_HEAD,
        )
        self.assertIs(
            validate_2022_runtime_authorization_install_action(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-595")
        self.assertEqual(value["source_preflight_workflow_run_id"], 37616348059)
        self.assertEqual(value["source_preflight_artifact_id"], 11480120937)
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "56c3ff244ed7ad47a07ab64efbea68e41acb61cfdba24303f2d265a2e690b08c",
        )
        self.assertEqual(
            value["source_preflight_canonical_sha256"],
            "6927206445b32ea2cd8a1e78b0511f70e9815a9204d771712c5976a5d79af4e4",
        )
        self.assertEqual(value["expected_run_number"], 384)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37531960014)
        self.assertEqual(value["action_count"], 2)
        create, update = value["actions"]
        self.assertEqual(create["operation"], "create")
        self.assertEqual(
            create["target_path"],
            "src/fmp/discovery/"
            "annual_pattern_catalogue_2022_runtime_authorization.py",
        )
        self.assertTrue(create["expected_target_absent"])
        self.assertEqual(
            create["expected_result_blob_sha"],
            "ecb21dc7106e7bd43447f4135c3a696251a75e05",
        )
        self.assertEqual(update["operation"], "update")
        self.assertEqual(
            update["target_path"],
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        )
        self.assertEqual(
            update["expected_current_blob_sha"],
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        )
        self.assertEqual(
            update["expected_result_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
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
            "run_385_or_later_authorized",
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
            compile_2022_runtime_authorization_install_action(
                _preflight(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                expected_head_sha=CURRENT_HEAD,
            )

    def test_refingerprinted_extra_action_is_rejected(self) -> None:
        value = compile_2022_runtime_authorization_install_action(
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
            validate_2022_runtime_authorization_install_action(tampered)

    def test_source_preflight_lock_tamper_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["run_385_or_later_authorized"] = True
        unsigned = dict(preflight)
        unsigned.pop("preflight_fingerprint_sha256", None)
        preflight["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaises(ValueError):
            compile_2022_runtime_authorization_install_action(
                preflight,
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": CURRENT_HEAD}},
                expected_head_sha=CURRENT_HEAD,
            )

    def test_cli_is_compile_only(self) -> None:
        script = (
            REPOSITORY_ROOT
            / "scripts/"
            "phase8a_annual_pattern_catalogue_2022_runtime_authorization_install_action.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("compile")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
