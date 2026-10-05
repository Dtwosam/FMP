from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2020_execution_authorization import (
    build_2020_execution_authorization,
    validate_2020_execution_authorization,
    validate_2020_execution_authorization_sources,
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
        "decision": "DEC-567",
        "expected_head_sha": "35115a69cae452d0afd922549fe41b4b8e404fd7",
        "preflight_fingerprint_sha256": (
            "bfccf190a7abad8464bafbf96a039305a8034f754fdc7cd05f5825c65398204f"
        ),
        "annual_segment_label": "2020",
        "prior_segment_label": "2019",
        "previous_annual_freeze_run_id": 37310525635,
        "expected_next_run_number": 382,
        "expected_next_run_attempt": 1,
        "preflight_read_only": True,
        "source_runtime_binding_fingerprint_sha256": (
            "a7063417dfb917f9b9019eb97c9a2803f50b4163ea524ea52c64b28a387720a2"
        ),
        "source_freeze_evidence_fingerprint_sha256": (
            "6935506f20d6d46054fabed5200ba6cec33ea4f10b00d839cc1cfc7f1b92b918"
        ),
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
    }


@unittest.skipIf(
    PREINSTALL_SNAPSHOT,
    "DEC-568 requires the installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2020ExecutionAuthorizationTests(unittest.TestCase):
    def test_sources_pin_concrete_preflight_runtime_and_workflow(self) -> None:
        source = validate_2020_execution_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "e045b3e82d2f16e870c77b5b107d8d46fcf96f85",
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_authorization_is_exact_run382_and_runtime_inactive(self) -> None:
        preflight = _preflight()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2020_execution_authorization."
            "validate_2020_execution_preflight",
            return_value=preflight,
        ):
            value = build_2020_execution_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
            )
        self.assertIs(validate_2020_execution_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-568")
        self.assertEqual(value["annual_segment_label"], "2020")
        self.assertEqual(value["prior_segment_label"], "2019")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37310525635)
        self.assertEqual(value["expected_run_number"], 382)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["source_preflight_workflow_run_id"], 37313687059)
        self.assertEqual(value["source_preflight_artifact_id"], 11346985812)
        self.assertEqual(
            value["source_preflight_artifact_digest"],
            "sha256:182be0b68d721e3267a84bab37c5a3bcb5c25b84b546ba9565c20b6c2ee1f1b0",
        )
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "bfccf190a7abad8464bafbf96a039305a8034f754fdc7cd05f5825c65398204f",
        )
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertTrue(value["authorization_contract_validated"])
        self.assertTrue(value["source_only_authorization"])
        self.assertFalse(value["runtime_authorization_installed"])
        self.assertFalse(value["runtime_gate_active"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertFalse(value["run_383_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_refingerprinted_runtime_activation_tamper_is_rejected(self) -> None:
        preflight = _preflight()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2020_execution_authorization."
            "validate_2020_execution_preflight",
            return_value=preflight,
        ):
            value = build_2020_execution_authorization(
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
            validate_2020_execution_authorization(tampered)

    def test_wrong_run_number_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["expected_next_run_number"] = 383
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2020_execution_authorization."
            "validate_2020_execution_preflight",
            return_value=preflight,
        ):
            with self.assertRaisesRegex(ValueError, "expected run number mismatch"):
                build_2020_execution_authorization(
                    preflight,
                    repository_root=REPOSITORY_ROOT,
                )

    def test_current_runtime_has_no_2020_route(self) -> None:
        runtime = (
            REPOSITORY_ROOT
            / "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('segment == "2020"', runtime)
        self.assertNotIn("require_2020_execution_authorized", runtime)


if __name__ == "__main__":
    unittest.main()
