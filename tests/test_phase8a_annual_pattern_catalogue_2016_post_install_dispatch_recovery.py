from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery import annual_pattern_catalogue_2016_post_install_dispatch_recovery as recovery_module
from fmp.discovery import annual_pattern_catalogue_2016_post_install_runtime_repair as repair_module
from fmp.discovery.annual_pattern_catalogue_2016_post_install_dispatch_recovery import (
    build_2016_post_install_dispatch_recovery,
    validate_2016_post_install_dispatch_recovery,
)
from fmp.discovery.annual_pattern_catalogue_2016_post_install_runtime_repair import (
    build_2016_post_install_runtime_repair,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PREINSTALL_SNAPSHOT = os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1"
HEAD = "a" * 40
RUN377_HEAD = "a89db974be9a94481e7ed0990476bc661012f1e4"


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _artifact(artifact_id: int, name: str, digest: str) -> dict[str, object]:
    return {
        "id": artifact_id,
        "name": name,
        "digest": f"sha256:{digest}",
        "size_in_bytes": 123,
    }


def _binding() -> dict[str, object]:
    jobs = {f"cell-{i}": 1000 + i for i in range(18)}
    artifacts = {
        f"cell-{i}": _artifact(2000 + i, f"cell-{i}", "d" * 64)
        for i in range(18)
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
        "run_id": 37198002653,
        "run_number": 377,
        "run_attempt": 1,
        "run_status": "completed",
        "run_conclusion": "success",
        "run_head_sha": RUN377_HEAD,
        "preflight_job_id": 9001,
        "freeze_job_id": 9002,
        "cell_job_ids": jobs,
        "preflight_artifact": _artifact(3001, "preflight", "e" * 64),
        "freeze_artifact": _artifact(3002, "freeze", "f" * 64),
        "cell_artifacts": artifacts,
        "freeze_artifact_zip_sha256": "f" * 64,
        "freeze_evidence_canonical_sha256": "1" * 64,
        "freeze_evidence_fingerprint": "2" * 64,
        "annual_cell_count": 18,
        "directional_record_count": 89460,
        "evaluable_record_count": 1,
        "zero_support_record_count": 2,
        "total_support": 3,
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


def _install_receipt() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-508",
        "version": "fmp-annual-catalogue-2016-runtime-authorization-install-receipt-v1",
        "install_action_source_blob_sha": "0545f0474bdead4e479c07b9af889db842bf00dd",
        "source_action_decision": "DEC-507",
        "source_action_fingerprint_sha256": "5" * 64,
        "stage": "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALLED_DISPATCH_LOCKED",
        "repository_full_name": "Dtwosam/FMP",
        "install_commit_sha": "525386dd68955e9f02909f9692987968ab15e516",
        "annual_segment_label": "2016",
        "expected_run_number": 378,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37198002653,
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


def _repair() -> dict[str, object]:
    run = {
        "id": 37205170186,
        "name": "phase8a-annual-catalogue-2016-runtime-install-executor",
        "path": ".github/workflows/phase8a-annual-catalogue-2016-runtime-install-executor.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": "481e3127415e0b676c590a6edf7e30c0bc10760f",
        "run_number": 2,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }
    jobs = {
        "jobs": [{
            "id": 1,
            "name": "install-runtime-authorization",
            "status": "completed",
            "conclusion": "failure",
            "steps": [
                {"name": "Apply exact two-file runtime authorization install", "conclusion": "success"},
                {"name": "Commit exact DEC-518 install", "conclusion": "success"},
                {"name": "Push only the exact install commit to main", "conclusion": "success"},
                {"name": "Build concrete DEC-508 install receipt", "conclusion": "failure"},
            ],
        }]
    }
    historical_sources = {
        "active_gate_blob_sha": repair_module.EXPECTED_ACTIVE_GATE_BLOB_SHA,
        "runtime_blob_sha": repair_module.EXPECTED_RUNTIME_BLOB_SHA,
        "active_workflow_blob_sha": (
            repair_module.EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA
        ),
    }
    with patch.object(
        repair_module,
        "validate_2016_post_install_runtime_repair_sources",
        return_value=historical_sources,
    ):
        return build_2016_post_install_runtime_repair(
            repository_root=REPOSITORY_ROOT,
            installer_run=run,
            installer_jobs=jobs,
            repair_head_sha=HEAD,
        )


def _runs() -> dict[str, object]:
    return {"workflow_runs": [
        {
            "id": 37126711695, "run_number": 1, "run_attempt": 1,
            "event": "workflow_dispatch", "head_branch": "main",
            "head_sha": "fd85a886d07234ad584dcca08692b37e6af54b2e",
            "status": "completed", "conclusion": "failure",
        },
        {
            "id": 37191637168, "run_number": 376, "run_attempt": 1,
            "event": "workflow_dispatch", "head_branch": "main",
            "head_sha": "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3",
            "status": "completed", "conclusion": "failure",
        },
        {
            "id": 37198002653, "run_number": 377, "run_attempt": 1,
            "event": "workflow_dispatch", "head_branch": "main",
            "head_sha": RUN377_HEAD, "status": "completed", "conclusion": "success",
        },
    ]}


@unittest.skipIf(
    PREINSTALL_SNAPSHOT,
    "post-install dispatch recovery requires active annual runtime state",
)
class AnnualCatalogue2016PostInstallDispatchRecoveryTests(unittest.TestCase):
    def _historical_sources(self) -> dict[str, str]:
        return {
            "repair_source_blob_sha": recovery_module.EXPECTED_REPAIR_SOURCE_BLOB_SHA,
            "install_receipt_source_blob_sha": (
                recovery_module.EXPECTED_INSTALL_RECEIPT_SOURCE_BLOB_SHA
            ),
            "runtime_binding_source_blob_sha": (
                recovery_module.EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA
            ),
            "active_gate_blob_sha": recovery_module.EXPECTED_ACTIVE_GATE_BLOB_SHA,
            "runtime_blob_sha": recovery_module.EXPECTED_RUNTIME_BLOB_SHA,
            "active_workflow_blob_sha": (
                recovery_module.EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA
            ),
        }

    def test_sources_keep_historical_repair_runtime_pins(self) -> None:
        self.assertEqual(
            recovery_module.EXPECTED_REPAIR_SOURCE_BLOB_SHA,
            "fce9214787b487f9dacf083adec39a4507958d92",
        )
        self.assertEqual(
            recovery_module.EXPECTED_ACTIVE_GATE_BLOB_SHA,
            "5b034fba697c3de0c0f8b6140d6f84771f1ae54b",
        )
        self.assertEqual(
            recovery_module.EXPECTED_RUNTIME_BLOB_SHA,
            "b564f5a26fdef146fc6080962e7c4762b0b5949a",
        )

    def test_exact_repaired_state_authorizes_only_fresh_run378(self) -> None:
        with patch.object(
            recovery_module,
            "validate_2016_post_install_dispatch_recovery_sources",
            return_value=self._historical_sources(),
        ):
            value = build_2016_post_install_dispatch_recovery(
                repository_root=REPOSITORY_ROOT,
                repair_receipt=_repair(),
                install_receipt=_install_receipt(),
                runtime_binding=_binding(),
                main_branch={"name": "main", "commit": {"sha": HEAD}},
                annual_workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )
        self.assertIs(validate_2016_post_install_dispatch_recovery(value), value)
        self.assertEqual(value["decision"], "DEC-532")
        self.assertEqual(value["expected_run_number"], 378)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertTrue(value["annual_workflow_dispatch_authorized"])
        self.assertTrue(value["runtime_import_cycle_repaired"])
        self.assertFalse(value["dispatch_action_executed"])
        self.assertFalse(value["run_379_or_later_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_existing_run378_is_rejected(self) -> None:
        runs = _runs()
        rows = runs["workflow_runs"]
        assert isinstance(rows, list)
        rows.append({
            "id": 99, "run_number": 378, "run_attempt": 1,
            "event": "workflow_dispatch", "head_branch": "main",
            "head_sha": HEAD, "status": "completed", "conclusion": "success",
        })
        with patch.object(
            recovery_module,
            "validate_2016_post_install_dispatch_recovery_sources",
            return_value=self._historical_sources(),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "exactly three prior annual",
            ):
                build_2016_post_install_dispatch_recovery(
                    repository_root=REPOSITORY_ROOT,
                    repair_receipt=_repair(),
                    install_receipt=_install_receipt(),
                    runtime_binding=_binding(),
                    main_branch={"name": "main", "commit": {"sha": HEAD}},
                    annual_workflow_runs=runs,
                    expected_head_sha=HEAD,
                )


if __name__ == "__main__":
    unittest.main()
