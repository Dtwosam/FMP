from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2016_dispatch_action_preflight import (
    build_2016_dispatch_action_preflight,
    validate_2016_dispatch_action_preflight,
    validate_2016_dispatch_action_preflight_sources,
)


HEAD = "e" * 40
RUN2_HEAD = "b" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _authorization() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-510",
        "version": "fmp-annual-catalogue-2016-dispatch-authorization-v1",
        "dispatch_preflight_source_blob_sha": "ab15723683f0fa37f5cc4511168cf264f47063c0",
        "active_workflow_blob_sha": "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        "source_preflight_decision": "DEC-509",
        "source_preflight_version": "fmp-annual-catalogue-2016-dispatch-preflight-v1",
        "source_preflight_fingerprint_sha256": "1" * 64,
        "stage": "ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZED_NOT_DISPATCHED",
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_scope": "2016_run_3_attempt_1_only",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": HEAD,
        "install_commit_sha": HEAD,
        "annual_segment_label": "2016",
        "prior_segment_label": "2015",
        "previous_annual_freeze_run_id": 424242,
        "successful_2015_run_id": 424242,
        "successful_2015_run_head_sha": RUN2_HEAD,
        "expected_run_number": 3,
        "expected_run_attempt": 1,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "authorization_contract_validated": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_action_executed": False,
        "dispatch_command_present": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "fourth_or_later_run_authorized": False,
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
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT"
        ),
    }
    value["authorization_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _runs() -> dict[str, object]:
    return {
        "workflow_runs": [
            {
                "id": 37126711695,
                "run_number": 1,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": "fd85a886d07234ad584dcca08692b37e6af54b2e",
                "status": "completed",
                "conclusion": "failure",
            },
            {
                "id": 424242,
                "run_number": 2,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": RUN2_HEAD,
                "status": "completed",
                "conclusion": "success",
            },
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-511 requires the DEC-510 source state",
)
class AnnualPatternCatalogue2016DispatchActionPreflightTests(unittest.TestCase):
    def test_sources_pin_authorization_and_active_workflow(self) -> None:
        source = validate_2016_dispatch_action_preflight_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["authorization_source_blob_sha"],
            "8de76c1d3a576d365a3d99f15336868165123dd0",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "f7e65ee95f472918e390bceedd7cf2f38bbf7e92",
        )

    def test_exact_state_yields_read_only_frozen_dispatch_parameters(self) -> None:
        value = build_2016_dispatch_action_preflight(
            _authorization(),
            repository_root=Path("."),
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2016_dispatch_action_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-511")
        self.assertEqual(value["annual_segment_label"], "2016")
        self.assertEqual(value["expected_run_number"], 3)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["dispatch_ref"], "main")
        self.assertEqual(value["dispatch_input_annual_segment_label"], "2016")
        self.assertEqual(
            value["dispatch_input_previous_annual_freeze_run_id"],
            "424242",
        )
        self.assertEqual(value["successful_2015_run_head_sha"], RUN2_HEAD)
        self.assertTrue(value["dispatch_parameters_frozen"])
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["historical_artifact_read_authorized"])
        self.assertTrue(value["historical_catalogue_execution_authorized"])
        self.assertTrue(value["historical_result_production_authorized"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["fourth_or_later_run_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_third_prior_workflow_run_is_rejected(self) -> None:
        rows = list(_runs()["workflow_runs"])
        rows.append(
            {
                "id": 525252,
                "run_number": 3,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": HEAD,
                "status": "completed",
                "conclusion": "success",
            }
        )
        with self.assertRaisesRegex(
            ValueError,
            "exactly two prior annual-catalogue workflow runs",
        ):
            build_2016_dispatch_action_preflight(
                _authorization(),
                repository_root=Path("."),
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=HEAD,
            )

    def test_predecessor_head_drift_is_rejected(self) -> None:
        runs = _runs()
        rows = [dict(row) for row in runs["workflow_runs"]]
        rows[1]["head_sha"] = "c" * 40
        with self.assertRaisesRegex(
            ValueError,
            "successful 2015 run head_sha mismatch",
        ):
            build_2016_dispatch_action_preflight(
                _authorization(),
                repository_root=Path("."),
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=HEAD,
            )

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_2016_dispatch_action_preflight(
                _authorization(),
                repository_root=Path("."),
                main_branch={"name": "main", "commit": {"sha": "d" * 40}},
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_refingerprinted_dispatch_execution_tamper_is_rejected(self) -> None:
        value = build_2016_dispatch_action_preflight(
            _authorization(),
            repository_root=Path("."),
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["dispatch_action_executed"] = True
        unsigned = dict(tampered)
        unsigned.pop("preflight_fingerprint_sha256", None)
        tampered["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "dispatch_action_executed mismatch",
        ):
            validate_2016_dispatch_action_preflight(tampered)

    def test_cli_is_plan_only(self) -> None:
        script = Path(
            "scripts/phase8a_annual_pattern_catalogue_2016_dispatch_action_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
