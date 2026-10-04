from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2016_dispatch_preflight import (
    build_2016_dispatch_preflight,
    validate_2016_dispatch_preflight,
    validate_2016_dispatch_preflight_sources,
)


MAIN_HEAD = "e" * 40
RUN377_HEAD = "b" * 40


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _artifact(artifact_id: int, name: str, digest_hex: str) -> dict[str, object]:
    return {
        "id": artifact_id,
        "name": name,
        "digest": f"sha256:{digest_hex}",
        "size_in_bytes": 123,
    }


def _binding() -> dict[str, object]:
    cell_job_ids = {
        f"annual-cell-2015-cell-{index:02d}": 1000 + index
        for index in range(18)
    }
    cell_artifacts = {
        f"phase8a-annual-catalogue-cell-2015-cell-{index:02d}-{RUN377_HEAD}": _artifact(
            2000 + index,
            f"phase8a-annual-catalogue-cell-2015-cell-{index:02d}-{RUN377_HEAD}",
            "d" * 64,
        )
        for index in range(18)
    }
    value: dict[str, object] = {
        "decision": "DEC-502",
        "version": "fmp-annual-catalogue-2015-runtime-evidence-binding-v1",
        "run_freeze_source_blob_sha": "97cfd73d5693046f05104342cb74867d5dc471cc",
        "run_review_source_blob_sha": "d6935a7b31b028b955f182cf81bc2c123a321852",
        "active_workflow_blob_sha": "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        "source_freeze_decision": "DEC-501",
        "source_freeze_version": "fmp-annual-catalogue-2015-replacement-run-freeze-v1",
        "stage": "ANNUAL_CATALOGUE_2015_CONCRETE_RUNTIME_EVIDENCE_BOUND",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2015",
        "run_id": 424242,
        "run_number": 377,
        "run_attempt": 1,
        "run_status": "completed",
        "run_conclusion": "success",
        "run_head_sha": RUN377_HEAD,
        "preflight_job_id": 9001,
        "freeze_job_id": 9002,
        "cell_job_ids": cell_job_ids,
        "preflight_artifact": _artifact(
            3001,
            f"phase8a-annual-catalogue-preflight-2015-{RUN377_HEAD}",
            "e" * 64,
        ),
        "freeze_artifact": _artifact(
            3002,
            f"phase8a-annual-catalogue-freeze-2015-{RUN377_HEAD}",
            "f" * 64,
        ),
        "cell_artifacts": cell_artifacts,
        "freeze_artifact_zip_sha256": "f" * 64,
        "freeze_evidence_canonical_sha256": "1" * 64,
        "freeze_evidence_fingerprint": "2" * 64,
        "annual_cell_count": 18,
        "directional_record_count": 89460,
        "evaluable_record_count": 123,
        "zero_support_record_count": 456,
        "total_support": 789,
        "review_fingerprint_sha256": "3" * 64,
        "runtime_freeze_fingerprint_sha256": "4" * 64,
        "replacement_authorization_consumed": True,
        "runtime_review_validated": True,
        "runtime_evidence_frozen": True,
        "runtime_evidence_bound": True,
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
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_PREFLIGHT",
    }
    value["binding_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


def _receipt(
    *,
    previous_run_id: int = 424242,
    install_commit_sha: str = MAIN_HEAD,
) -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-508",
        "version": "fmp-annual-catalogue-2016-runtime-authorization-install-receipt-v1",
        "install_action_source_blob_sha": "0545f0474bdead4e479c07b9af889db842bf00dd",
        "source_action_decision": "DEC-507",
        "source_action_fingerprint_sha256": "5" * 64,
        "stage": "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALLED_DISPATCH_LOCKED",
        "repository_full_name": "Dtwosam/FMP",
        "install_commit_sha": install_commit_sha,
        "annual_segment_label": "2016",
        "expected_run_number": 378,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": previous_run_id,
        "changed_file_count": 2,
        "changed_files": [
            "src/fmp/discovery/annual_pattern_catalogue_2016_runtime_authorization.py",
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        ],
        "installed_gate_source_path": (
            "src/fmp/discovery/annual_pattern_catalogue_2016_runtime_authorization.py"
        ),
        "installed_gate_source_blob_sha": "4bb008eedc2ca0676cf25dd3cfcebba5eac0eaff",
        "installed_runtime_source_path": (
            "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
        ),
        "installed_runtime_source_blob_sha": "b564f5a26fdef146fc6080962e7c4762b0b5949a",
        "install_action_consumed": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
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
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_PREFLIGHT",
    }
    value["receipt_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    return value


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": MAIN_HEAD}}


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
                "id": 37191637168,
                "run_number": 376,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3",
                "status": "completed",
                "conclusion": "failure",
            },
            {
                "id": 424242,
                "run_number": 377,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": RUN377_HEAD,
                "status": "completed",
                "conclusion": "success",
            },
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-509 requires the future DEC-508 source state",
)
class AnnualPatternCatalogue2016DispatchPreflightTests(unittest.TestCase):
    def test_sources_pin_receipt_binding_and_workflow(self) -> None:
        source = validate_2016_dispatch_preflight_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["install_receipt_source_blob_sha"],
            "3a5614af2393378ed664c4802806147d79ccd8c7",
        )
        self.assertEqual(
            source["runtime_binding_source_blob_sha"],
            "400e9715a6e3b2dab413ce2ecff0fbce8c46f6b0",
        )
        self.assertEqual(
            source["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_exact_installed_state_yields_read_only_dispatch_preflight(self) -> None:
        value = build_2016_dispatch_preflight(
            repository_root=Path("."),
            install_receipt=_receipt(),
            runtime_binding=_binding(),
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=MAIN_HEAD,
        )
        self.assertIs(validate_2016_dispatch_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-509")
        self.assertEqual(value["annual_segment_label"], "2016")
        self.assertEqual(value["previous_annual_freeze_run_id"], 424242)
        self.assertEqual(value["annual_workflow_run_count"], 3)
        self.assertEqual(value["successful_2015_run_number"], 377)
        self.assertEqual(value["expected_run_number"], 378)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["install_commit_sha"], MAIN_HEAD)
        self.assertTrue(value["install_action_consumed"])
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_artifact_read_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["historical_result_production_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["strategy_v1_synthesis_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertTrue(value["preflight_read_only"])

    def test_fourth_workflow_run_is_rejected(self) -> None:
        rows = list(_runs()["workflow_runs"])
        rows.append(
            {
                "id": 525252,
                "run_number": 378,
                "run_attempt": 1,
                "event": "workflow_dispatch",
                "head_branch": "main",
                "head_sha": MAIN_HEAD,
                "status": "completed",
                "conclusion": "success",
            }
        )
        with self.assertRaisesRegex(
            ValueError,
            "exactly three prior annual-catalogue workflow runs",
        ):
            build_2016_dispatch_preflight(
                repository_root=Path("."),
                install_receipt=_receipt(),
                runtime_binding=_binding(),
                main_branch=_main(),
                annual_workflow_runs={"workflow_runs": rows},
                expected_head_sha=MAIN_HEAD,
            )

    def test_install_receipt_must_bind_current_main(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "install receipt/main head mismatch",
        ):
            build_2016_dispatch_preflight(
                repository_root=Path("."),
                install_receipt=_receipt(install_commit_sha="d" * 40),
                runtime_binding=_binding(),
                main_branch=_main(),
                annual_workflow_runs=_runs(),
                expected_head_sha=MAIN_HEAD,
            )

    def test_install_receipt_must_bind_same_2015_freeze(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "install receipt predecessor mismatch",
        ):
            build_2016_dispatch_preflight(
                repository_root=Path("."),
                install_receipt=_receipt(previous_run_id=999999),
                runtime_binding=_binding(),
                main_branch=_main(),
                annual_workflow_runs=_runs(),
                expected_head_sha=MAIN_HEAD,
            )

    def test_refingerprinted_dispatch_authority_tamper_is_rejected(self) -> None:
        value = build_2016_dispatch_preflight(
            repository_root=Path("."),
            install_receipt=_receipt(),
            runtime_binding=_binding(),
            main_branch=_main(),
            annual_workflow_runs=_runs(),
            expected_head_sha=MAIN_HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["annual_workflow_dispatch_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("preflight_fingerprint_sha256", None)
        tampered["preflight_fingerprint_sha256"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError,
            "annual_workflow_dispatch_authorized mismatch",
        ):
            validate_2016_dispatch_preflight(tampered)

    def test_cli_is_plan_only(self) -> None:
        script = Path(
            "scripts/phase8a_annual_pattern_catalogue_2016_dispatch_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', script)
        self.assertNotIn('subparsers.add_parser("dispatch")', script)
        self.assertNotIn('subparsers.add_parser("run")', script)
        self.assertNotIn('subparsers.add_parser("execute")', script)
        self.assertNotIn("gh workflow run ", script)


if __name__ == "__main__":
    unittest.main()
