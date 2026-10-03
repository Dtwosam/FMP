from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_proof_workflow_run_freeze import (
    EXPECTED_RUN_REVIEW_BLOB_SHA,
    freeze_reviewed_proof_workflow_run,
    validate_proof_workflow_run_freeze,
    validate_proof_workflow_run_freeze_sources,
)
from fmp.discovery.annual_pattern_catalogue_proof_workflow_run_review import (
    review_proof_workflow_run,
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


def _review() -> dict[str, object]:
    preflight = build_workflow_install_preflight(
        repository_root=Path("."),
        main_branch=_main(),
        expected_head_sha=HEAD,
    )
    preflight_bytes = (
        json.dumps(preflight, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")
    return review_proof_workflow_run(
        repository_root=Path("."),
        main_branch=_main(),
        proof_run={
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
        },
        proof_job={
            "id": JOB_ID,
            "name": "annual-catalogue-install-preflight-proof",
            "run_id": RUN_ID,
            "status": "completed",
            "conclusion": "success",
        },
        artifact={
            "id": ARTIFACT_ID,
            "name": (
                "phase8a-annual-catalogue-workflow-install-preflight-" + HEAD
            ),
            "expired": False,
        },
        preflight_bytes=preflight_bytes,
        expected_proof_run_id=RUN_ID,
    )


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-489 requires the installed proof workflow",
)
class AnnualPatternCatalogueProofWorkflowRunFreezeTests(unittest.TestCase):
    def test_sources_pin_exact_dec488_reviewer(self) -> None:
        source = validate_proof_workflow_run_freeze_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["run_review_blob_sha"],
            EXPECTED_RUN_REVIEW_BLOB_SHA,
        )

    def test_valid_review_freezes_deterministically(self) -> None:
        value = freeze_reviewed_proof_workflow_run(
            _review(),
            repository_root=Path("."),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_proof_workflow_run_freeze(value), value)
        self.assertEqual(value["decision"], "DEC-489")
        self.assertEqual(value["proof_run_number"], 1)
        self.assertEqual(value["proof_run_attempt"], 1)
        self.assertTrue(value["runtime_review_validated"])
        self.assertTrue(value["runtime_evidence_frozen"])
        self.assertTrue(
            value["proof_workflow_dispatch_authorization_consumed"]
        )
        self.assertFalse(value["proof_workflow_dispatch_authorized"])
        self.assertFalse(value["annual_workflow_install_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertEqual(len(value["freeze_fingerprint_sha256"]), 64)

        second = freeze_reviewed_proof_workflow_run(
            _review(),
            repository_root=Path("."),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            value["freeze_fingerprint_sha256"],
            second["freeze_fingerprint_sha256"],
        )

    def test_review_head_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "reviewed main head mismatch"):
            freeze_reviewed_proof_workflow_run(
                _review(),
                repository_root=Path("."),
                expected_head_sha="b" * 40,
            )

    def test_refingerprinted_authority_tamper_is_rejected(self) -> None:
        value = freeze_reviewed_proof_workflow_run(
            _review(),
            repository_root=Path("."),
            expected_head_sha=HEAD,
        )
        tampered = copy.deepcopy(value)
        tampered["annual_workflow_install_authorized"] = True
        unsigned = dict(tampered)
        unsigned.pop("freeze_fingerprint_sha256", None)
        import hashlib

        tampered["freeze_fingerprint_sha256"] = hashlib.sha256(
            (
                json.dumps(
                    unsigned,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
        ).hexdigest()

        with self.assertRaisesRegex(
            ValueError,
            "annual_workflow_install_authorized mismatch",
        ):
            validate_proof_workflow_run_freeze(tampered)


if __name__ == "__main__":
    unittest.main()
