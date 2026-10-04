from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2017_runtime_authorization_install_preflight import (
    build_2017_runtime_authorization_install_preflight,
    validate_2017_runtime_authorization_install_preflight,
    validate_2017_runtime_authorization_install_preflight_sources,
)
from fmp.discovery.annual_pattern_catalogue_2017_runtime_authorization_plan import (
    build_2017_runtime_authorization_plan,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _authorization() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-535",
        "version": "fmp-annual-catalogue-2017-execution-authorization-v1",
        "execution_preflight_source_blob_sha": (
            "7e6e6a54d4111a44a68218e551c379fa342d3e27"
        ),
        "runtime_source_blob_sha": (
            "b564f5a26fdef146fc6080962e7c4762b0b5949a"
        ),
        "active_workflow_blob_sha": (
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
        ),
        "source_preflight_decision": "DEC-534",
        "source_preflight_version": (
            "fmp-annual-catalogue-2017-execution-preflight-v2"
        ),
        "source_preflight_workflow_run_id": 37210041270,
        "source_preflight_workflow_head_sha": (
            "23231c82360da824e3b9eedbd4e2a5edcffd0d45"
        ),
        "source_preflight_artifact_id": 11306121033,
        "source_preflight_artifact_digest": (
            "sha256:531c468e36ac80f6c0c24620c14b78d2b2faad869d53be098efe7a2b31425e04"
        ),
        "source_preflight_fingerprint_sha256": "1" * 64,
        "source_preflight_canonical_sha256": "2" * 64,
        "stage": (
            "ANNUAL_CATALOGUE_2017_EXECUTION_AUTHORIZED_"
            "RUNTIME_NOT_INSTALLED"
        ),
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_scope": "2017_run_379_attempt_1_only",
        "annual_segment_label": "2017",
        "prior_segment_label": "2016",
        "previous_annual_freeze_run_id": 37206992367,
        "previous_runtime_binding_fingerprint_sha256": "3" * 64,
        "previous_annual_freeze_evidence_fingerprint_sha256": "4" * 64,
        "expected_run_number": 379,
        "expected_run_attempt": 1,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "authorization_contract_validated": True,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_380_or_later_authorized": False,
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
        "source_only_authorization": True,
        "next_gate": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_RUNTIME_AUTHORIZATION_PLAN"
        ),
    }
    value["authorization_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-537 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2017RuntimeAuthorizationInstallPreflightTests(
    unittest.TestCase
):
    def _plan(self) -> dict[str, object]:
        return build_2017_runtime_authorization_plan(
            _authorization(),
            repository_root=REPOSITORY_ROOT,
        )

    def test_sources_pin_dec535_dec536_and_dormant_targets(self) -> None:
        source = validate_2017_runtime_authorization_install_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "ef70a0aec215943a2d992a484fd95feb390c6e07",
        )
        self.assertEqual(
            source["runtime_authorization_plan_source_blob_sha"],
            "441b411cdae5b541226d3c0ef88b6cf687ce70da",
        )

    def test_preflight_is_read_only_and_exact_run379(self) -> None:
        value = build_2017_runtime_authorization_install_preflight(
            _authorization(),
            self._plan(),
            repository_root=REPOSITORY_ROOT,
            main_branch={"name": "main", "commit": {"sha": HEAD}},
            expected_head_sha=HEAD,
        )
        self.assertIs(
            validate_2017_runtime_authorization_install_preflight(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-537")
        self.assertEqual(value["source_plan_workflow_run_id"], 37215086807)
        self.assertEqual(value["source_plan_artifact_id"], 11307494750)
        self.assertEqual(
            value["source_plan_artifact_digest"],
            "sha256:80395e51c57ca26788ef4291d7cdf1e6e3e79ef6cf92893e9d37d14dd8bc2adc",
        )
        self.assertEqual(value["expected_run_number"], 379)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37206992367)
        self.assertEqual(value["activation_mutation_file_count"], 2)
        self.assertTrue(value["authorization_contract_validated"])
        self.assertTrue(value["runtime_plan_validated"])
        self.assertTrue(value["runtime_install_preflight_ready"])
        self.assertTrue(value["preflight_read_only"])
        for field in (
            "repository_mutation_authorized",
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

    def test_plan_mutation_authority_tamper_is_rejected(self) -> None:
        plan = copy.deepcopy(self._plan())
        plan["repository_mutation_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "repository_mutation_authorized mismatch",
        ):
            build_2017_runtime_authorization_install_preflight(
                _authorization(),
                plan,
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": HEAD}},
                expected_head_sha=HEAD,
            )

    def test_wrong_main_head_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2017_runtime_authorization_install_preflight(
                _authorization(),
                self._plan(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
