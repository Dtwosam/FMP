from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_workflow_install_preflight import (
    build_workflow_install_preflight,
)
from fmp.discovery.annual_pattern_catalogue_workflow_install_preflight_proof import (
    EXPECTED_PREFLIGHT_SOURCE_BLOB_SHA,
    PROOF_WORKFLOW_NAME,
    PROOF_WORKFLOW_PATH,
    compile_repository_hosted_preflight_proof,
    validate_proof_sources,
    validate_repository_hosted_preflight_proof,
)


HEAD = "a" * 40
RUN_ID = 515151


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _preflight() -> dict[str, object]:
    return build_workflow_install_preflight(
        repository_root=Path("."),
        main_branch=_main(),
        expected_head_sha=HEAD,
    )


def _run(
    *,
    run_id: int = RUN_ID,
    head_sha: str = HEAD,
    conclusion: str = "success",
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": PROOF_WORKFLOW_NAME,
        "path": PROOF_WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": conclusion,
    }


def _fingerprint(value: object) -> str:
    return hashlib.sha256(
        (
            json.dumps(
                value,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    ).hexdigest()


class AnnualPatternCatalogueWorkflowInstallPreflightProofTests(
    unittest.TestCase
):
    def test_proof_source_binds_exact_dec480_preflight_source(self) -> None:
        value = validate_proof_sources(repository_root=Path("."))

        self.assertEqual(
            value["preflight_source_blob_sha"],
            EXPECTED_PREFLIGHT_SOURCE_BLOB_SHA,
        )

    def test_successful_repository_hosted_read_only_proof_is_frozen(self) -> None:
        preflight = _preflight()
        proof = compile_repository_hosted_preflight_proof(
            repository_root=Path("."),
            preflight=preflight,
            main_branch=_main(),
            proof_run=_run(),
            expected_proof_run_id=RUN_ID,
        )

        self.assertIs(
            validate_repository_hosted_preflight_proof(proof),
            proof,
        )
        self.assertEqual(proof["decision"], "DEC-481")
        self.assertEqual(proof["main_head_sha"], HEAD)
        self.assertEqual(proof["proof_run_id"], RUN_ID)
        self.assertEqual(proof["proof_run_event"], "workflow_dispatch")
        self.assertEqual(proof["proof_run_head_branch"], "main")
        self.assertEqual(proof["proof_run_head_sha"], HEAD)
        self.assertEqual(proof["proof_run_status"], "completed")
        self.assertEqual(proof["proof_run_conclusion"], "success")
        self.assertEqual(
            proof["preflight_fingerprint"],
            preflight["preflight_fingerprint"],
        )
        self.assertEqual(
            proof["install_action_fingerprint"],
            preflight["install_action_fingerprint"],
        )
        self.assertTrue(proof["repository_hosted_read_only_proof"])
        self.assertTrue(proof["preflight_validated"])

    def test_proof_run_must_be_exact_successful_main_dispatch(self) -> None:
        preflight = _preflight()

        bad = _run(conclusion="failure")
        with self.assertRaisesRegex(ValueError, "proof run conclusion mismatch"):
            compile_repository_hosted_preflight_proof(
                repository_root=Path("."),
                preflight=preflight,
                main_branch=_main(),
                proof_run=bad,
                expected_proof_run_id=RUN_ID,
            )

        bad = _run(head_sha="b" * 40)
        with self.assertRaisesRegex(ValueError, "proof run head_sha mismatch"):
            compile_repository_hosted_preflight_proof(
                repository_root=Path("."),
                preflight=preflight,
                main_branch=_main(),
                proof_run=bad,
                expected_proof_run_id=RUN_ID,
            )

    def test_preflight_main_head_drift_fails_closed(self) -> None:
        preflight = _preflight()
        with self.assertRaisesRegex(ValueError, "preflight/main head mismatch"):
            compile_repository_hosted_preflight_proof(
                repository_root=Path("."),
                preflight=preflight,
                main_branch={"name": "main", "commit": {"sha": "b" * 40}},
                proof_run=_run(),
                expected_proof_run_id=RUN_ID,
            )

    def test_refingerprinted_authority_escalation_fails_semantically(self) -> None:
        proof = compile_repository_hosted_preflight_proof(
            repository_root=Path("."),
            preflight=_preflight(),
            main_branch=_main(),
            proof_run=_run(),
            expected_proof_run_id=RUN_ID,
        )
        tampered = dict(proof)
        tampered["annual_workflow_install_authorized"] = True
        tampered.pop("proof_fingerprint", None)
        tampered["proof_fingerprint"] = _fingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "annual_workflow_install_authorized mismatch",
        ):
            validate_repository_hosted_preflight_proof(tampered)

    def test_refingerprinted_run_provenance_tamper_fails_semantically(self) -> None:
        proof = compile_repository_hosted_preflight_proof(
            repository_root=Path("."),
            preflight=_preflight(),
            main_branch=_main(),
            proof_run=_run(),
            expected_proof_run_id=RUN_ID,
        )

        tampered = dict(proof)
        tampered["proof_run_conclusion"] = "failure"
        tampered.pop("proof_fingerprint", None)
        tampered["proof_fingerprint"] = _fingerprint(tampered)
        with self.assertRaisesRegex(ValueError, "proof_run_conclusion mismatch"):
            validate_repository_hosted_preflight_proof(tampered)

        tampered = dict(proof)
        tampered["proof_run_head_sha"] = "b" * 40
        tampered.pop("proof_fingerprint", None)
        tampered["proof_fingerprint"] = _fingerprint(tampered)
        with self.assertRaisesRegex(ValueError, "proof run head/main mismatch"):
            validate_repository_hosted_preflight_proof(tampered)

    def test_all_mutation_execution_and_trading_authority_remains_false(self) -> None:
        proof = compile_repository_hosted_preflight_proof(
            repository_root=Path("."),
            preflight=_preflight(),
            main_branch=_main(),
            proof_run=_run(),
            expected_proof_run_id=RUN_ID,
        )

        for field in (
            "repository_mutation_authorized",
            "annual_workflow_install_authorized",
            "annual_workflow_installed",
            "annual_workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "next_segment_execution_authorized",
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
            self.assertFalse(proof[field], field)
        self.assertEqual(
            proof["next_gate"],
            (
                "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_"
                "WORKFLOW_INSTALL_PREFLIGHT_PROOF_WORKFLOW_SOURCE"
            ),
        )


if __name__ == "__main__":
    unittest.main()
