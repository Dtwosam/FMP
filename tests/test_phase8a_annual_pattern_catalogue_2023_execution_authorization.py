from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2023_execution_authorization import (
    build_2023_execution_authorization,
    validate_2023_execution_authorization,
    validate_2023_execution_authorization_sources,
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
        "annual_segment_label": "2023",
        "annual_workflow_dispatch_authorized": False,
        "annual_workflow_run_count": 10,
        "broker_mutation_authorized": False,
        "collection_segment_count": 12,
        "collection_terminal_segment_label": "2026_YTD_TO_2026_08_20",
        "cross_year_comparison_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-602",
        "demo_order_authorized": False,
        "expected_head_sha": "c9d61bdd982eac727ece651be754310d7871cfa7",
        "expected_next_run_attempt": 1,
        "expected_next_run_number": 385,
        "governing_method_decision": "DEC-469",
        "governing_protocol_decision": "DEC-470",
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "live_order_authorized": False,
        "method_source_blob_sha": "d7486296c2e953d6b4e7602c753c5529ccf5eef2",
        "next_gate": "ANNUAL_PATTERN_CATALOGUE_2023_EXECUTION_AUTHORIZATION_BEFORE_RUN",
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "preflight_fingerprint_sha256": (
            "dc63a0265b9e2b00625431b3d48c9625ed077047bc505caac04c692890198db4"
        ),
        "preflight_read_only": True,
        "previous_annual_freeze_run_id": 37663157285,
        "prior_segment_label": "2022",
        "prior_segment_required": True,
        "promotion_authorized": False,
        "protected_catalogue_segment": True,
        "protected_history_access_authorized": False,
        "protocol_2023_2026_catalogue_use_authorized": True,
        "protocol_2023_2026_remains_untouched_oos_for_strategy_v1": False,
        "protocol_full_collection_catalogue_use_authorized": True,
        "protocol_source_blob_sha": "5ddd987cc480e6e31c0cd45328eba16cf690dee9",
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "repository_full_name": "Dtwosam/FMP",
        "rerun_authorized": False,
        "retry_authorized": False,
        "run_386_or_later_authorized": False,
        "runtime_binding_source_blob_sha": "7048781474ce74b8bbed0fd380f8edf4ec51491d",
        "source_final_required_annual_segment_bound_claim": True,
        "source_next_gate_claim": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_CROSS_YEAR_COMPARISON_PREFLIGHT"
        ),
        "source_runtime_binding_artifact_digest": (
            "sha256:45e4436ce5536c7df7ed8a3af99d9dc911025ec441a554de627d4adf8de1f755"
        ),
        "source_runtime_binding_artifact_id": 11504596272,
        "source_runtime_binding_canonical_sha256": (
            "7e36345fc0ca8592e5f5ede41b9afcfdc9becff72d2415b7e6741ed2352923ac"
        ),
        "source_runtime_binding_decision": "DEC-601",
        "source_runtime_binding_fingerprint_sha256": (
            "926832634d5836b158d780e21886692e762709104a6d0048c54a75c77ad2f352"
        ),
        "source_runtime_binding_workflow_head_sha": (
            "a08512973deb127f16e199c6ecd2876e0fc8d8e0"
        ),
        "source_runtime_binding_workflow_run_id": 37670106681,
        "source_terminal_successor_claim_superseded_by_dec469_dec470": True,
        "stage": (
            "ANNUAL_CATALOGUE_2023_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "strategy_v1_synthesis_authorized": False,
        "successful_2021_run_id": 37531960014,
        "successful_2021_run_number": 383,
        "successful_2022_run_attempt": 1,
        "successful_2022_run_head_sha": (
            "dd79687adc4ec179c56f91939cb600e6746fab5d"
        ),
        "successful_2022_run_id": 37663157285,
        "successful_2022_run_number": 384,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2023-execution-preflight-v1",
    }


@unittest.skipIf(
    PREINSTALL_SNAPSHOT,
    "DEC-603 requires the installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2023ExecutionAuthorizationTests(unittest.TestCase):
    def test_sources_pin_preflight_runtime_and_workflow(self) -> None:
        source = validate_2023_execution_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "d7e0823bc0d7513b6d7ee27a02fb5b519bc4818b",
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            "f2734c7ea32355b1024d1097812578b23fc4409d",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_authorization_is_exact_protected_run385_and_runtime_inactive(self) -> None:
        preflight = _preflight()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2023_execution_authorization."
            "validate_2023_execution_preflight",
            return_value=preflight,
        ):
            value = build_2023_execution_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
            )
        self.assertIs(validate_2023_execution_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-603")
        self.assertEqual(value["annual_segment_label"], "2023")
        self.assertEqual(value["prior_segment_label"], "2022")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37663157285)
        self.assertEqual(value["expected_run_number"], 385)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["source_preflight_workflow_run_id"], 37678209687)
        self.assertEqual(value["source_preflight_artifact_id"], 11507656390)
        self.assertEqual(
            value["source_preflight_artifact_digest"],
            "sha256:519c9e963df4def2011fab65c49ca909b3f7a24aacb5b09a1b8582d51cc6a8a5",
        )
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "dc63a0265b9e2b00625431b3d48c9625ed077047bc505caac04c692890198db4",
        )
        self.assertEqual(
            value["source_preflight_canonical_sha256"],
            "4ed1e69320a4e66dd11454f35f39abbca43f14c74f8d6b52de672257a1ba658e",
        )
        self.assertTrue(value["protected_catalogue_segment"])
        self.assertTrue(value["protocol_full_collection_catalogue_use_authorized"])
        self.assertTrue(value["protocol_2023_2026_catalogue_use_authorized"])
        self.assertFalse(
            value["protocol_2023_2026_remains_untouched_oos_for_strategy_v1"]
        )
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertTrue(value["protected_history_access_authorized"])
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
            "run_386_or_later_authorized",
            "next_segment_execution_authorized",
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

    def test_refingerprinted_protected_access_removal_is_rejected(self) -> None:
        preflight = _preflight()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2023_execution_authorization."
            "validate_2023_execution_preflight",
            return_value=preflight,
        ):
            value = build_2023_execution_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
            )
        tampered = copy.deepcopy(value)
        tampered["protected_history_access_authorized"] = False
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "protected_history_access_authorized mismatch",
        ):
            validate_2023_execution_authorization(tampered)

    def test_refingerprinted_run386_authority_is_rejected(self) -> None:
        preflight = _preflight()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2023_execution_authorization."
            "validate_2023_execution_preflight",
            return_value=preflight,
        ):
            value = build_2023_execution_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
            )
        tampered = copy.deepcopy(value)
        tampered["run_386_or_later_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "run_386_or_later_authorized mismatch",
        ):
            validate_2023_execution_authorization(tampered)

    def test_current_runtime_has_no_2023_route_or_gate(self) -> None:
        runtime = (
            REPOSITORY_ROOT
            / "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('segment == "2023"', runtime)
        self.assertNotIn("require_2023_execution_authorized", runtime)
        self.assertFalse(
            (
                REPOSITORY_ROOT
                / "src/fmp/discovery/"
                "annual_pattern_catalogue_2023_runtime_authorization.py"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
