from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2018_execution_authorization import (
    build_2018_execution_authorization,
    validate_2018_execution_authorization,
    validate_2018_execution_authorization_sources,
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
        "annual_segment_label": "2018",
        "annual_workflow_dispatch_authorized": False,
        "annual_workflow_run_count": 5,
        "broker_mutation_authorized": False,
        "cross_year_result_production_authorized": False,
        "decision": "DEC-545",
        "demo_order_authorized": False,
        "expected_head_sha": "24fa329cbcf88192cdc19e63173edd55b3aa7eb5",
        "expected_next_run_attempt": 1,
        "expected_next_run_number": 380,
        "failed_first_run_id": 37126711695,
        "failed_run376_id": 37191637168,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "live_order_authorized": False,
        "next_gate": "ANNUAL_PATTERN_CATALOGUE_2018_EXECUTION_AUTHORIZATION_BEFORE_RUN",
        "next_segment_execution_authorized": False,
        "phase8b_authorized": False,
        "preflight_fingerprint_sha256": "55b9378a78f54a99a9055da1ac0294e73c5e02434fc4ad17d38acea7ac5c6315",
        "preflight_read_only": True,
        "previous_annual_freeze_evidence_fingerprint_sha256": "ed579f80f947f9a04731b4a20e675c98e2101884c874fa385df5999ef419ff8b",
        "previous_annual_freeze_run_id": 37227536041,
        "previous_runtime_binding_fingerprint_sha256": "a454e3eef8a51260cc07f9103a7de0208f5408a18686bb1249ad05e349edd9ae",
        "prior_segment_label": "2017",
        "prior_segment_required": True,
        "promotion_authorized": False,
        "real_money_authorized": False,
        "repository_full_name": "Dtwosam/FMP",
        "runtime_binding_source_blob_sha": "67e45260a79be451d7484dfcef1fc36c4df12bf0",
        "source_runtime_binding_artifact_digest": "sha256:f48dd73bbae1587bf8c6e97408295ab94761ab4536c7124532ef5b6f55c2d1d1",
        "source_runtime_binding_artifact_id": 11313481023,
        "source_runtime_binding_decision": "DEC-544",
        "source_runtime_binding_fingerprint_sha256": "a454e3eef8a51260cc07f9103a7de0208f5408a18686bb1249ad05e349edd9ae",
        "source_runtime_binding_recovery_head_sha": "8169c07142fee231cf0fbe539954b876e2f0e240",
        "source_runtime_binding_recovery_workflow_run_id": 37228767187,
        "source_runtime_binding_version": "fmp-annual-catalogue-2017-run379-evidence-review-v1",
        "stage": "ANNUAL_CATALOGUE_2018_EXECUTION_PREFLIGHT_PREDECESSOR_BOUND_AUTHORIZATION_LOCKED",
        "strategy_v1_synthesis_authorized": False,
        "successful_2015_run_attempt": 1,
        "successful_2015_run_head_sha": "a89db974be9a94481e7ed0990476bc661012f1e4",
        "successful_2015_run_id": 37198002653,
        "successful_2015_run_number": 377,
        "successful_2016_run_attempt": 1,
        "successful_2016_run_head_sha": "2524fde355349581c9440a172d0384c3cbce31ed",
        "successful_2016_run_id": 37206992367,
        "successful_2016_run_number": 378,
        "successful_2017_run_attempt": 1,
        "successful_2017_run_head_sha": "7b4c1ef8573e280c067443b72f1534d9091d5b7f",
        "successful_2017_run_id": 37227536041,
        "successful_2017_run_number": 379,
        "trading_authorized": False,
        "version": "fmp-annual-catalogue-2018-execution-preflight-v1",
    }


@unittest.skipIf(
    PREINSTALL_SNAPSHOT,
    "DEC-546 requires the installed annual workflow/runtime state",
)
class AnnualPatternCatalogue2018ExecutionAuthorizationTests(unittest.TestCase):
    def test_sources_pin_concrete_preflight_runtime_and_workflow(self) -> None:
        source = validate_2018_execution_authorization_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            source["execution_preflight_source_blob_sha"],
            "ed71113733ae0034d81914d4c0ab37efb5c4ce6e",
        )
        self.assertEqual(
            source["runtime_source_blob_sha"],
            "e9cbc76dc9e6866e80088d223498fbcc3b870fd1",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_authorization_is_exact_run380_and_runtime_inactive(self) -> None:
        value = build_2018_execution_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
        )
        self.assertIs(validate_2018_execution_authorization(value), value)
        self.assertEqual(value["decision"], "DEC-546")
        self.assertEqual(value["annual_segment_label"], "2018")
        self.assertEqual(value["prior_segment_label"], "2017")
        self.assertEqual(value["previous_annual_freeze_run_id"], 37227536041)
        self.assertEqual(value["expected_run_number"], 380)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["source_preflight_workflow_run_id"], 37229319220)
        self.assertEqual(value["source_preflight_artifact_id"], 11313083318)
        self.assertEqual(
            value["source_preflight_fingerprint_sha256"],
            "55b9378a78f54a99a9055da1ac0294e73c5e02434fc4ad17d38acea7ac5c6315",
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
        self.assertFalse(value["run_381_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_refingerprinted_runtime_activation_tamper_is_rejected(self) -> None:
        value = build_2018_execution_authorization(
            _preflight(),
            repository_root=REPOSITORY_ROOT,
        )
        tampered = copy.deepcopy(value)
        tampered["runtime_gate_active"] = True
        unsigned = dict(tampered)
        unsigned.pop("authorization_fingerprint_sha256", None)
        tampered["authorization_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "runtime_gate_active mismatch",
        ):
            validate_2018_execution_authorization(tampered)

    def test_wrong_run_number_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["expected_next_run_number"] = 381
        unsigned = dict(preflight)
        unsigned.pop("preflight_fingerprint_sha256", None)
        preflight["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "DEC-545 expected_next_run_number mismatch|"
            "source preflight fingerprint mismatch|expected run number mismatch",
        ):
            build_2018_execution_authorization(
                preflight,
                repository_root=REPOSITORY_ROOT,
            )

    def test_current_runtime_has_no_2018_route(self) -> None:
        runtime = (
            REPOSITORY_ROOT
            / "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('segment == "2018"', runtime)
        self.assertNotIn("require_2018_execution_authorized", runtime)


if __name__ == "__main__":
    unittest.main()
