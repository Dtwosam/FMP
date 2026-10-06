from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery.annual_pattern_catalogue_2021_execution_authorization import (
    build_2021_execution_authorization,
    validate_2021_execution_authorization,
    validate_2021_execution_authorization_sources,
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
        "decision": "DEC-580",
        "expected_head_sha": "5b775915dc14c9f14aac34ac8dc98643a24841d8",
        "preflight_fingerprint_sha256": (
            "42582ae521d339a1a1df7b46fae7675fd5bce6cc98669bdbaa211d3bd864129e"
        ),
        "annual_segment_label": "2021",
        "prior_segment_label": "2020",
        "previous_annual_freeze_run_id": 37443770076,
        "expected_next_run_number": 383,
        "expected_next_run_attempt": 1,
        "preflight_read_only": True,
        "source_runtime_binding_fingerprint_sha256": (
            "ebde4b5ee78421cc2afb4c12c4ff2603b6d01f1990fbfe683aed11d00653a76c"
        ),
        "source_freeze_evidence_fingerprint_sha256": (
            "53cd4475b2e9f70252bc4962666ce421daf7795d3e78defbb38ec948448e1c3c"
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
    "DEC-581 requires the installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2021ExecutionAuthorizationTests(unittest.TestCase):
    def test_sources_pin_concrete_preflight_runtime_and_workflow(self) -> None:
        source = validate_2021_execution_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "981309374459ed6b99030f66d08ac5fc0e707dcc",
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            "4e124365430672fa63825b272001937c60151644",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_authorization_is_exact_run383_and_runtime_inactive(self) -> None:
        preflight = _preflight()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2021_execution_authorization."
            "validate_2020_execution_preflight",
            return_value=preflight,
        ):
            value = build_2021_execution_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
            )
        self.assertIs(validate_2021_execution_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-581")
        self.assertEqual(value["annual_segment_label"], "2021")
        self.assertEqual(value["prior_segment_label"], "2020")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37443770076)
        self.assertEqual(value["expected_run_number"], 383)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["source_preflight_workflow_run_id"], 37452889764)
        self.assertEqual(value["source_preflight_artifact_id"], 11407570779)
        self.assertEqual(
            value["source_preflight_artifact_digest"],
            "sha256:f408d6cdd389bb9f25e84d6aec110a502a0ac9d8a1098d92c8709aab879f6f62",
        )
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "42582ae521d339a1a1df7b46fae7675fd5bce6cc98669bdbaa211d3bd864129e",
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
        self.assertFalse(value["run_384_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_refingerprinted_runtime_activation_tamper_is_rejected(self) -> None:
        preflight = _preflight()
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2021_execution_authorization."
            "validate_2020_execution_preflight",
            return_value=preflight,
        ):
            value = build_2021_execution_authorization(
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
            validate_2021_execution_authorization(tampered)

    def test_wrong_run_number_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["expected_next_run_number"] = 384
        with patch(
            "fmp.discovery.annual_pattern_catalogue_2021_execution_authorization."
            "validate_2020_execution_preflight",
            return_value=preflight,
        ):
            with self.assertRaisesRegex(ValueError, "expected run number mismatch"):
                build_2021_execution_authorization(
                    preflight,
                    repository_root=REPOSITORY_ROOT,
                )

    def test_current_runtime_has_no_2021_route(self) -> None:
        runtime = (
            REPOSITORY_ROOT
            / "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('segment == "2021"', runtime)
        self.assertNotIn("require_2021_execution_authorized", runtime)


if __name__ == "__main__":
    unittest.main()
