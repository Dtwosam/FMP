from __future__ import annotations

import copy
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2023_runtime_authorization_install_preflight import (
    build_2023_runtime_authorization_install_preflight,
    validate_2023_runtime_authorization_install_preflight,
    validate_2023_runtime_authorization_install_preflight_sources,
)
from fmp.discovery.annual_pattern_catalogue_2023_runtime_authorization_plan import (
    build_2023_runtime_authorization_plan,
)


ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40


def _authorization() -> dict[str, object]:
    return {
        "decision": "DEC-603",
        "authorization_fingerprint_sha256": (
            "dc1f6dc96e4bdbf527ffba49be9df175310389737bd7c70ca945bd260baf3946"
        ),
        "annual_segment_label": "2023",
        "expected_run_number": 385,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37663157285,
        "runtime_authorization_installed": False,
        "runtime_gate_active": False,
        "dispatch_action_executed": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_386_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "protected_history_access_authorized": True,
        "protected_catalogue_segment": True,
        "governing_method_decision": "DEC-469",
        "governing_protocol_decision": "DEC-470",
        "protocol_full_collection_catalogue_use_authorized": True,
        "protocol_2023_2026_catalogue_use_authorized": True,
        "cross_year_comparison_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "source_preflight_workflow_run_id": 37678209687,
        "source_preflight_artifact_id": 11507656390,
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-605 requires installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2023RuntimeAuthorizationInstallPreflightTests(
    unittest.TestCase
):
    def _plan(self) -> dict[str, object]:
        authorization = _authorization()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2023_runtime_authorization_plan."
            "validate_2023_execution_authorization",
            return_value=authorization,
        ):
            return build_2023_runtime_authorization_plan(
                authorization,
                repository_root=ROOT,
            )

    def _build(
        self,
        authorization: dict[str, object] | None = None,
        plan: dict[str, object] | None = None,
        *,
        main_sha: str = HEAD,
    ) -> dict[str, object]:
        authorization = authorization or _authorization()
        plan = plan or self._plan()
        with patch(
            "fmp.discovery."
            "annual_pattern_catalogue_2023_runtime_authorization_install_preflight."
            "validate_2023_execution_authorization",
            return_value=authorization,
        ):
            return build_2023_runtime_authorization_install_preflight(
                authorization,
                plan,
                repository_root=ROOT,
                main_branch={"name": "main", "commit": {"sha": main_sha}},
                expected_head_sha=HEAD,
            )

    def test_sources_pin_dec603_dec604_and_dormant_targets(self) -> None:
        source = validate_2023_runtime_authorization_install_preflight_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            source["execution_authorization_source_blob_sha"],
            "2c4292abadbffb9dd87edaab67d9e32783facae7",
        )
        self.assertEqual(
            source["runtime_authorization_plan_source_blob_sha"],
            "fe5c18f8ffa5e3d698f91060ec8c28e0d0692318",
        )

    def test_preflight_is_read_only_and_exact_run385(self) -> None:
        value = self._build()
        self.assertIs(
            validate_2023_runtime_authorization_install_preflight(value),
            value,
        )
        self.assertEqual(value["decision"], "DEC-605")
        self.assertEqual(value["source_plan_workflow_run_id"], 37688619041)
        self.assertEqual(value["source_plan_artifact_id"], 11512058473)
        self.assertEqual(
            value["source_plan_artifact_digest"],
            "sha256:a43cd3c767082ae3c20587690e202f98da32c9824b0cda2f33d211ac19e21de8",
        )
        self.assertEqual(
            value["source_plan_canonical_sha256"],
            "9c5841d3842bc1c342c0e4032460c30ec66c33d0d144c47c4cf1a3523a7d1440",
        )
        self.assertEqual(value["expected_run_number"], 385)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37663157285)
        self.assertEqual(value["activation_mutation_file_count"], 2)
        self.assertEqual(
            value["expected_current_runtime_source_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        )
        self.assertEqual(
            value["target_gate_source_blob_sha"],
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
        )
        self.assertEqual(
            value["target_runtime_source_blob_sha"],
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        )
        self.assertTrue(
            value["source_authorization_protected_history_access_authorized"]
        )
        self.assertTrue(value["protected_catalogue_segment"])
        self.assertEqual(value["governing_method_decision"], "DEC-469")
        self.assertEqual(value["governing_protocol_decision"], "DEC-470")
        self.assertTrue(value["protocol_full_collection_catalogue_use_authorized"])
        self.assertTrue(value["protocol_2023_2026_catalogue_use_authorized"])
        self.assertEqual(
            value["next_gate"],
            (
                "EXACT_ANNUAL_PATTERN_CATALOGUE_2023_RUNTIME_"
                "AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC605"
            ),
        )
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

    def test_plan_mutation_authority_tamper_is_rejected(self) -> None:
        plan = copy.deepcopy(self._plan())
        plan["repository_mutation_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "repository_mutation_authorized mismatch",
        ):
            self._build(plan=plan)

    def test_missing_source_protected_authority_is_rejected(self) -> None:
        authorization = copy.deepcopy(_authorization())
        authorization["protected_history_access_authorized"] = False
        with self.assertRaisesRegex(
            ValueError,
            "protected-history authority missing",
        ):
            self._build(authorization=authorization)

    def test_wrong_main_head_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            self._build(main_sha="b" * 40)


if __name__ == "__main__":
    unittest.main()
