from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_proof_workflow_run_review import (
    EXPECTED_DISPATCH_AUTHORIZATION_BLOB_SHA,
    EXPECTED_PROOF_CONTRACT_BLOB_SHA,
    PROOF_JOB_NAME,
    review_proof_workflow_run,
    validate_proof_workflow_run_review,
    validate_proof_workflow_run_review_sources,
)
from fmp.discovery.annual_pattern_catalogue_workflow_install_preflight import (
    build_workflow_install_preflight,
)


HEAD = "a" * 40
RUN_ID = 50000000001
JOB_ID = 50000000002
ARTIFACT_ID = 50000000003


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _run() -> dict[str, object]:
    return {
        "id": RUN_ID,
        "name": "phase8a-annual-catalogue-workflow-install-preflight-proof",
        "path": (
            ".github/workflows/"
            "phase8a-annual-catalogue-workflow-install-preflight-proof.yml"
        ),
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _job() -> dict[str, object]:
    return {
        "id": JOB_ID,
        "name": PROOF_JOB_NAME,
        "run_id": RUN_ID,
        "status": "completed",
        "conclusion": "success",
    }


def _artifact() -> dict[str, object]:
    return {
        "id": ARTIFACT_ID,
        "name": (
            "phase8a-annual-catalogue-workflow-install-preflight-" + HEAD
        ),
        "expired": False,
    }


def _preflight_bytes() -> bytes:
    value = build_workflow_install_preflight(
        repository_root=Path("."),
        main_branch=_main(),
        expected_head_sha=HEAD,
    )
    return (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-488 requires the installed proof workflow",
)
class AnnualPatternCatalogueProofWorkflowRunReviewTests(unittest.TestCase):
    def test_sources_pin_authorization_proof_contract_and_active_workflow(self) -> None:
        source = validate_proof_workflow_run_review_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dispatch_authorization"],
            EXPECTED_DISPATCH_AUTHORIZATION_BLOB_SHA,
        )
        self.assertEqual(
            source["proof_contract"],
            EXPECTED_PROOF_CONTRACT_BLOB_SHA,
        )
        self.assertEqual(
            source["active_proof_workflow"],
            "0d6c93e2af04501f9ac2589fd24d6672b2b41910",
        )

    def test_successful_first_run_and_artifact_review(self) -> None:
        value = review_proof_workflow_run(
            repository_root=Path("."),
            main_branch=_main(),
            proof_run=_run(),
            proof_job=_job(),
            artifact=_artifact(),
            preflight_bytes=_preflight_bytes(),
            expected_proof_run_id=RUN_ID,
        )
        self.assertIs(validate_proof_workflow_run_review(value), value)
        self.assertEqual(value["decision"], "DEC-488")
        self.assertEqual(value["proof_run_number"], 1)
        self.assertEqual(value["proof_run_attempt"], 1)
        self.assertEqual(value["proof_run_conclusion"], "success")
        self.assertEqual(value["proof_job_conclusion"], "success")
        self.assertFalse(value["artifact_expired"])
        self.assertTrue(value["review_only"])
        self.assertTrue(value["proof_workflow_first_run_reviewed"])
        self.assertTrue(
            value["proof_workflow_dispatch_authorization_consumed"]
        )
        self.assertFalse(value["proof_workflow_dispatch_authorized"])
        self.assertFalse(value["annual_workflow_install_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_wrong_run_number_is_rejected(self) -> None:
        run = _run()
        run["run_number"] = 2
        with self.assertRaisesRegex(ValueError, "run_number mismatch"):
            review_proof_workflow_run(
                repository_root=Path("."),
                main_branch=_main(),
                proof_run=run,
                proof_job=_job(),
                artifact=_artifact(),
                preflight_bytes=_preflight_bytes(),
                expected_proof_run_id=RUN_ID,
            )

    def test_failed_job_is_rejected(self) -> None:
        job = _job()
        job["conclusion"] = "failure"
        with self.assertRaisesRegex(ValueError, "job conclusion mismatch"):
            review_proof_workflow_run(
                repository_root=Path("."),
                main_branch=_main(),
                proof_run=_run(),
                proof_job=job,
                artifact=_artifact(),
                preflight_bytes=_preflight_bytes(),
                expected_proof_run_id=RUN_ID,
            )

    def test_wrong_artifact_name_is_rejected(self) -> None:
        artifact = _artifact()
        artifact["name"] = "wrong"
        with self.assertRaisesRegex(ValueError, "artifact name mismatch"):
            review_proof_workflow_run(
                repository_root=Path("."),
                main_branch=_main(),
                proof_run=_run(),
                proof_job=_job(),
                artifact=artifact,
                preflight_bytes=_preflight_bytes(),
                expected_proof_run_id=RUN_ID,
            )

    def test_tampered_preflight_is_rejected(self) -> None:
        preflight = json.loads(_preflight_bytes().decode("utf-8"))
        tampered = copy.deepcopy(preflight)
        tampered["annual_workflow_install_authorized"] = True
        payload = (
            json.dumps(tampered, sort_keys=True, indent=2, allow_nan=False) + "\n"
        ).encode("utf-8")
        with self.assertRaisesRegex(ValueError, "preflight fingerprint mismatch"):
            review_proof_workflow_run(
                repository_root=Path("."),
                main_branch=_main(),
                proof_run=_run(),
                proof_job=_job(),
                artifact=_artifact(),
                preflight_bytes=payload,
                expected_proof_run_id=RUN_ID,
            )


if __name__ == "__main__":
    unittest.main()
