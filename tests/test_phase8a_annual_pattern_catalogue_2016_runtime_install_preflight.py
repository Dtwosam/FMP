from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2016_runtime_install_preflight import (
    build_2016_runtime_install_preflight,
    validate_2016_runtime_install_preflight,
    validate_2016_runtime_install_preflight_sources,
)


HEAD = "d" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _authorization() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-504",
        "version": "fmp-annual-catalogue-2016-execution-authorization-v1",
        "execution_preflight_source_blob_sha": "00b0df00f15e1d983c799e8991a88e03e010d2e3",
        "runtime_source_blob_sha": "ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b",
        "active_workflow_blob_sha": "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        "source_preflight_decision": "DEC-503",
        "source_preflight_version": "fmp-annual-catalogue-2016-execution-preflight-v1",
        "source_preflight_canonical_sha256": "1" * 64,
        "stage": "ANNUAL_CATALOGUE_2016_EXECUTION_AUTHORIZED_RUNTIME_NOT_INSTALLED",
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_scope": "2016_run_3_attempt_1_only",
        "annual_segment_label": "2016",
        "prior_segment_label": "2015",
        "previous_annual_freeze_run_id": 424242,
        "expected_run_number": 3,
        "expected_run_attempt": 1,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "authorization_contract_validated": True,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
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
            "INSTALL_ANNUAL_PATTERN_CATALOGUE_2016_RUNTIME_AUTHORIZATION_"
            "AFTER_CONCRETE_PREFLIGHT"
        ),
    }
    value["authorization_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-505 requires the source-only 2016 authorization state",
)
class AnnualPatternCatalogue2016RuntimeInstallPreflightTests(unittest.TestCase):
    def test_sources_pin_authorization_runtime_and_workflow(self) -> None:
        source = validate_2016_runtime_install_preflight_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["authorization_source_blob_sha"],
            "19d95a11e3ae1684d28ab17020f78bea39003bc8",
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            "ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        )

    def test_plan_contains_exactly_one_locked_runtime_mutation(self) -> None:
        value = build_2016_runtime_install_preflight(
            _authorization(),
            repository_root=Path("."),
            main_branch=_main(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2016_runtime_install_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-505")
        self.assertEqual(value["planned_mutation_count"], 1)
        mutation = value["planned_mutations"][0]
        self.assertEqual(
            mutation["path"],
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        )
        self.assertEqual(mutation["operation"], "update")
        self.assertEqual(mutation["authorized_segment"], "2016")
        self.assertEqual(mutation["authorized_run_number"], 3)
        self.assertEqual(mutation["authorized_run_attempt"], 1)
        self.assertTrue(value["source_authorization_dispatch_authorized"])
        self.assertTrue(value["source_authorization_execution_authorized"])
        self.assertTrue(value["runtime_install_preflight_validated"])
        self.assertFalse(value["repository_mutation_authorized"])
        self.assertFalse(value["runtime_authorization_install_authorized"])
        self.assertFalse(value["runtime_authorization_installed"])
        self.assertFalse(value["runtime_gate_active"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertTrue(value["preflight_read_only"])

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2016_runtime_install_preflight(
                _authorization(),
                repository_root=Path("."),
                main_branch={"name": "main", "commit": {"sha": "e" * 40}},
                expected_head_sha=HEAD,
            )

    def test_live_mutation_authority_tamper_is_rejected(self) -> None:
        value = build_2016_runtime_install_preflight(
            _authorization(),
            repository_root=Path("."),
            main_branch=_main(),
            expected_head_sha=HEAD,
        )
        value["runtime_authorization_install_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "runtime_authorization_install_authorized must remain false",
        ):
            validate_2016_runtime_install_preflight(value)

    def test_cli_is_plan_only(self) -> None:
        script = Path(
            "scripts/phase8a_annual_pattern_catalogue_2016_runtime_install_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("install")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
