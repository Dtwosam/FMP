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
from fmp.discovery.annual_pattern_catalogue_2016_runtime_authorization_install_preflight import (
    build_2016_runtime_authorization_install_preflight,
    validate_2016_runtime_authorization_install_preflight,
    validate_2016_runtime_authorization_install_preflight_sources,
)


HEAD = "c" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


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


def _authorization() -> dict[str, object]:
    return build_2016_execution_authorization(
        _source_preflight(),
        repository_root=Path("."),
    )


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-506 requires the DEC-505 dormant activation plan",
)
@unittest.skipIf(
    Path(
        "src/fmp/discovery/"
        "annual_pattern_catalogue_2016_runtime_authorization.py"
    ).is_file(),
    "historical pre-install 2016 contract; installed state is covered by DEC-531/532",
)
class AnnualPatternCatalogue2016RuntimeAuthorizationInstallPreflightTests(
    unittest.TestCase
):
    def test_sources_pin_dec504_and_dec505(self) -> None:
        source = validate_2016_runtime_authorization_install_preflight_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "b60c03e7f2e18f62df04ec450a36aec5d9985cca",
        )
        self.assertEqual(
            source["runtime_authorization_plan_source_blob_sha"],
            "f74139508e84b2f81b9ca9337d03de528e01dd24",
        )

    def test_valid_concrete_authorization_yields_read_only_install_preflight(self) -> None:
        authorization = _authorization()
        value = build_2016_runtime_authorization_install_preflight(
            authorization,
            repository_root=Path("."),
            main_branch=_main(),
            expected_head_sha=HEAD,
        )
        self.assertIs(
            validate_2016_runtime_authorization_install_preflight(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-506")
        self.assertEqual(value["source_authorization_decision"], "DEC-504")
        self.assertEqual(value["annual_segment_label"], "2016")
        self.assertEqual(value["expected_run_number"], 378)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 424242)
        self.assertEqual(value["activation_mutation_file_count"], 2)
        self.assertTrue(value["authorization_contract_validated"])
        self.assertTrue(value["runtime_install_preflight_ready"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["repository_mutation_authorized"])
        self.assertFalse(value["runtime_authorization_installed"])
        self.assertFalse(value["runtime_gate_active"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_refingerprinted_active_authorization_is_rejected(self) -> None:
        authorization = _authorization()
        tampered = copy.deepcopy(authorization)
        tampered["runtime_gate_active"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "runtime_gate_active must remain false",
        ):
            build_2016_runtime_authorization_install_preflight(
                tampered,
                repository_root=Path("."),
                main_branch=_main(),
                expected_head_sha=HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2016_runtime_authorization_install_preflight(
                _authorization(),
                repository_root=Path("."),
                main_branch={
                    "name": "main",
                    "commit": {"sha": "d" * 40},
                },
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        script = Path(
            "scripts/"
            "phase8a_annual_pattern_catalogue_2016_runtime_authorization_install_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
