from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2022_execution_authorization import (
    build_2022_execution_authorization,
    validate_2022_execution_authorization,
    validate_2022_execution_authorization_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PREINSTALL_SNAPSHOT = os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1"


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _preflight() -> dict[str, object]:
    return {
        "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        "annual_segment_label": "2022",
        "annual_workflow_dispatch_authorized": False,
        "annual_workflow_run_count": 9,
        "broker_mutation_authorized": False,
        "collection_segment_count": 12,
        "collection_terminal_segment_label": "2026_YTD_TO_2026_08_20",
        "cross_year_comparison_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-591",
        "demo_order_authorized": False,
        "expected_head_sha": "ed7589b1e63591c6508271ff75dcfc7a63893421",
        "expected_next_run_attempt": 1,
        "expected_next_run_number": 384,
        "governing_method_decision": "DEC-469",
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "live_order_authorized": False,
        "method_source_blob_sha": "d7486296c2e953d6b4e7602c753c5529ccf5eef2",
        "next_gate": "ANNUAL_PATTERN_CATALOGUE_2022_EXECUTION_AUTHORIZATION_BEFORE_RUN",
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "preflight_fingerprint_sha256": (
            "4dcd96a91c673559f0aecbb0e8cf61c437fb49e0f1831ebb9fc40d4428a1bdda"
        ),
        "preflight_read_only": True,
        "previous_annual_freeze_run_id": 37531960014,
        "prior_segment_label": "2021",
        "prior_segment_required": True,
        "promotion_authorized": False,
        "protected_history_access_authorized": False,
        "real_money_authorized": False,
        "repository_full_name": "Dtwosam/FMP",
        "runtime_binding_source_blob_sha": "542ace21e77c2bbdf5fec5312556c58d9e641da7",
        "source_final_required_annual_segment_bound_claim": True,
        "source_next_gate_claim": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_CROSS_YEAR_COMPARISON_PREFLIGHT"
        ),
        "source_runtime_binding_artifact_digest": (
            "sha256:3b4ac4827390c2262b35bf38e28a0b82140b792c7e2f9eb2575122ecd1e37eda"
        ),
        "source_runtime_binding_artifact_id": 11446806853,
        "source_runtime_binding_canonical_sha256": (
            "7ea6ac7ec5a780bbd41fad754d3dce212d2d6e2e198ffe88cf9d85381133c683"
        ),
        "source_runtime_binding_decision": "DEC-590",
        "source_runtime_binding_fingerprint_sha256": (
            "09aa36f87de239f692c90ae8aa5f41f6a3d5dd3015445979195a9dd9e9df2dfc"
        ),
        "source_runtime_binding_workflow_head_sha": (
            "2798003636d1858da38c564adbb70227cbb41e76"
        ),
        "source_runtime_binding_workflow_run_id": 37536632065,
        "source_terminal_successor_claim_superseded_by_dec469": True,
        "stage": (
            "ANNUAL_CATALOGUE_2022_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "strategy_v1_synthesis_authorized": False,
        "successful_2020_run_id": 37443770076,
        "successful_2020_run_number": 382,
        "successful_2021_run_attempt": 1,
        "successful_2021_run_head_sha": (
            "a1e194907c273a2fcdddfb4c24d64a96cfd8d263"
        ),
        "successful_2021_run_id": 37531960014,
        "successful_2021_run_number": 383,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2022-execution-preflight-v1",
    }


@unittest.skipIf(
    PREINSTALL_SNAPSHOT,
    "DEC-592 requires the installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2022ExecutionAuthorizationTests(unittest.TestCase):
    def test_sources_pin_preflight_runtime_and_workflow(self) -> None:
        source = validate_2022_execution_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "a52661d8abd910856bc5260898a7f21cc4958f94",
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            "d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_authorization_is_exact_run384_and_runtime_inactive(self) -> None:
        preflight = _preflight()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2022_execution_authorization."
            "validate_2022_execution_preflight",
            return_value=preflight,
        ):
            value = build_2022_execution_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
            )
        self.assertIs(validate_2022_execution_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-592")
        self.assertEqual(value["annual_segment_label"], "2022")
        self.assertEqual(value["prior_segment_label"], "2021")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37531960014)
        self.assertEqual(value["expected_run_number"], 384)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["source_preflight_workflow_run_id"], 37603215074)
        self.assertEqual(value["source_preflight_artifact_id"], 11474170578)
        self.assertEqual(
            value["source_preflight_artifact_digest"],
            "sha256:cc129455cda4fe6ec8835f436abc3ef39f009d073a4dc2efac859313f753cd50",
        )
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "4dcd96a91c673559f0aecbb0e8cf61c437fb49e0f1831ebb9fc40d4428a1bdda",
        )
        self.assertEqual(
            value["source_preflight_canonical_sha256"],
            "c8a481c2040ad6d61e74c1624c6b040b968854da25304e0c4ee6877451480b60",
        )
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertTrue(value["authorization_contract_validated"])
        self.assertTrue(value["source_only_authorization"])
        for field in (
            "runtime_authorization_installed",
            "runtime_gate_active",
            "dispatch_command_present",
            "dispatch_action_executed",
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

    def test_refingerprinted_runtime_activation_tamper_is_rejected(self) -> None:
        preflight = _preflight()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2022_execution_authorization."
            "validate_2022_execution_preflight",
            return_value=preflight,
        ):
            value = build_2022_execution_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
            )
        tampered = copy.deepcopy(value)
        tampered["runtime_gate_active"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "runtime_gate_active mismatch"):
            validate_2022_execution_authorization(tampered)

    def test_tampered_run_number_is_rejected_by_canonical_binding(self) -> None:
        preflight = _preflight()
        preflight["expected_next_run_number"] = 385
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2022_execution_authorization."
            "validate_2022_execution_preflight",
            return_value=preflight,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "source preflight canonical hash mismatch",
            ):
                build_2022_execution_authorization(
                    preflight,
                    repository_root=REPOSITORY_ROOT,
                )

    def test_current_runtime_has_no_2022_route_or_gate(self) -> None:
        runtime = (
            REPOSITORY_ROOT
            / "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('segment == "2022"', runtime)
        self.assertNotIn("require_2022_execution_authorized", runtime)
        self.assertFalse(
            (
                REPOSITORY_ROOT
                / "src/fmp/discovery/"
                "annual_pattern_catalogue_2022_runtime_authorization.py"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
