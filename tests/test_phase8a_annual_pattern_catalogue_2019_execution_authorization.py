from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2019_execution_authorization import (
    build_2019_execution_authorization,
    validate_2019_execution_authorization,
    validate_2019_execution_authorization_sources,
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
        "decision": "DEC-556",
        "expected_head_sha": "9fa3446b389cbbe1c8429968032ae573198e78b2",
        "preflight_fingerprint_sha256": (
            "3d311b8d8d387aca00f079bdab6b0531cf17aefc36913165cfb5eb265ad50421"
        ),
        "annual_segment_label": "2019",
        "prior_segment_label": "2018",
        "previous_annual_freeze_run_id": 37237817538,
        "expected_next_run_number": 381,
        "expected_next_run_attempt": 1,
        "preflight_read_only": True,
        "previous_runtime_binding_fingerprint_sha256": (
            "09950f6bfb577c4abe17a2466e466a08585fbcd05359ad5fa6c4bad16cce5fda"
        ),
        "previous_annual_freeze_evidence_fingerprint_sha256": (
            "355a1e5ca9282300a7a38e24dd3009ebe8470d1f029e62c38860bf710ac80559"
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
    "DEC-557 requires the installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2019ExecutionAuthorizationTests(unittest.TestCase):
    def test_sources_pin_concrete_preflight_runtime_and_workflow(self) -> None:
        source = validate_2019_execution_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "a813a8db59927eaf9108e010a5db84f6c6dafa27",
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            "410180c34a9e3500bbbb42310a5253b993ac7785",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_authorization_is_exact_run381_and_runtime_inactive(self) -> None:
        preflight = _preflight()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2019_execution_authorization."
            "validate_2019_execution_preflight",
            return_value=preflight,
        ):
            value = build_2019_execution_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
            )
        self.assertIs(validate_2019_execution_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-557")
        self.assertEqual(value["annual_segment_label"], "2019")
        self.assertEqual(value["prior_segment_label"], "2018")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37237817538)
        self.assertEqual(value["expected_run_number"], 381)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["source_preflight_workflow_run_id"], 37240728378)
        self.assertEqual(value["source_preflight_artifact_id"], 11317461212)
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "3d311b8d8d387aca00f079bdab6b0531cf17aefc36913165cfb5eb265ad50421",
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
        self.assertFalse(value["run_382_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_refingerprinted_runtime_activation_tamper_is_rejected(self) -> None:
        preflight = _preflight()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2019_execution_authorization."
            "validate_2019_execution_preflight",
            return_value=preflight,
        ):
            value = build_2019_execution_authorization(
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
            validate_2019_execution_authorization(tampered)

    def test_wrong_run_number_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["expected_next_run_number"] = 382
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2019_execution_authorization."
            "validate_2019_execution_preflight",
            return_value=preflight,
        ):
            with self.assertRaisesRegex(ValueError, "expected run number mismatch"):
                build_2019_execution_authorization(
                    preflight,
                    repository_root=REPOSITORY_ROOT,
                )

    def test_current_runtime_has_no_2019_route(self) -> None:
        runtime = (
            REPOSITORY_ROOT
            / "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('segment == "2019"', runtime)
        self.assertNotIn("require_2019_execution_authorized", runtime)


if __name__ == "__main__":
    unittest.main()
