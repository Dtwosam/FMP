from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2016_execution_authorization import (
    build_2016_execution_authorization,
)
from fmp.discovery.annual_pattern_catalogue_2016_runtime_authorization_install_action import (
    compile_2016_runtime_authorization_install_action,
    validate_2016_runtime_authorization_install_action,
    validate_2016_runtime_authorization_install_action_sources,
)
from fmp.discovery.annual_pattern_catalogue_2016_runtime_authorization_install_preflight import (
    build_2016_runtime_authorization_install_preflight,
)


HEAD = "c" * 40


def _source_preflight() -> dict[str, object]:
    return {
        "decision": "DEC-503",
        "version": "fmp-annual-catalogue-2016-execution-preflight-v1",
        "runtime_binding_source_blob_sha": "400e9715a6e3b2dab413ce2ecff0fbce8c46f6b0",
        "runtime_source_blob_sha": "f1fa50e7c862354931d919fe7da241de863f6834",
        "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        "annual_workflow_run_count": 3,
        "failed_first_run_id": 37126711695,
        "successful_2015_run_id": 424242,
        "successful_2015_run_number": 377,
        "successful_2015_run_attempt": 1,
        "successful_2015_run_head_sha": "b" * 40,
        "stage": (
            "ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": HEAD,
        "annual_segment_label": "2016",
        "prior_segment_required": True,
        "prior_segment_label": "2015",
        "previous_annual_freeze_run_id": 424242,
        "previous_runtime_binding_fingerprint": "1" * 64,
        "previous_runtime_freeze_fingerprint": "2" * 64,
        "previous_annual_freeze_evidence_fingerprint": "3" * 64,
        "expected_next_run_number": 378,
        "expected_next_run_attempt": 1,
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
        "preflight_read_only": True,
        "next_gate": "ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_AUTHORIZATION_BEFORE_RUN",
    }


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _install_preflight() -> dict[str, object]:
    authorization = build_2016_execution_authorization(
        _source_preflight(),
        repository_root=Path("."),
    )
    return build_2016_runtime_authorization_install_preflight(
        authorization,
        repository_root=Path("."),
        main_branch=_main(),
        expected_head_sha=HEAD,
    )


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-507 requires the DEC-506 install preflight state",
)
class AnnualPatternCatalogue2016RuntimeAuthorizationInstallActionTests(
    unittest.TestCase
):
    def test_sources_pin_exact_dec506(self) -> None:
        source = validate_2016_runtime_authorization_install_action_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["install_preflight_source_blob_sha"],
            "c52a88ff3159de35160c11061403172689433330",
        )

    def test_action_is_exact_two_file_mutation_and_non_dispatching(self) -> None:
        value = compile_2016_runtime_authorization_install_action(
            _install_preflight(),
            repository_root=Path("."),
            main_branch=_main(),
            expected_head_sha=HEAD,
        )
        self.assertIs(
            validate_2016_runtime_authorization_install_action(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-507")
        self.assertEqual(value["action_count"], 2)
        self.assertEqual(len(value["actions"]), 2)
        create, update = value["actions"]
        self.assertEqual(create["operation"], "create")
        self.assertEqual(
            create["target_path"],
            "src/fmp/discovery/annual_pattern_catalogue_2016_runtime_authorization.py",
        )
        self.assertTrue(create["expected_target_absent"])
        self.assertEqual(update["operation"], "update")
        self.assertEqual(
            update["target_path"],
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        )
        self.assertEqual(
            update["expected_current_blob_sha"],
            "f1fa50e7c862354931d919fe7da241de863f6834",
        )
        self.assertTrue(value["repository_mutation_authorized"])
        self.assertFalse(value["runtime_authorization_installed"])
        self.assertFalse(value["runtime_gate_active"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_main_drift_after_preflight_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "current main head mismatch"):
            compile_2016_runtime_authorization_install_action(
                _install_preflight(),
                repository_root=Path("."),
                main_branch={"name": "main", "commit": {"sha": "d" * 40}},
                expected_head_sha=HEAD,
            )

    def test_refingerprinted_extra_action_is_rejected(self) -> None:
        value = compile_2016_runtime_authorization_install_action(
            _install_preflight(),
            repository_root=Path("."),
            main_branch=_main(),
            expected_head_sha=HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["actions"] = list(tampered["actions"]) + [
            {
                "order": 3,
                "operation": "create",
                "target_path": "unexpected",
            }
        ]
        tampered["action_count"] = 3
        unsigned = dict(tampered)
        unsigned.pop("install_action_fingerprint_sha256", None)
        tampered["install_action_fingerprint_sha256"] = hashlib.sha256(
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
        with self.assertRaisesRegex(ValueError, "action count mismatch"):
            validate_2016_runtime_authorization_install_action(tampered)

    def test_cli_is_compile_only(self) -> None:
        script = Path(
            "scripts/"
            "phase8a_annual_pattern_catalogue_2016_runtime_authorization_install_action.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("compile")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
