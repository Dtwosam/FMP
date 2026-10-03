from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_proof_workflow_runtime_evidence_binding import (
    EXPECTED_BINDING_FINGERPRINT_SHA256,
    build_runtime_evidence_binding,
    validate_runtime_evidence_binding,
    validate_runtime_evidence_binding_sources,
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-490 binds the installed proof-workflow runtime evidence",
)
class AnnualPatternCatalogueProofWorkflowRuntimeEvidenceBindingTests(
    unittest.TestCase
):
    def test_sources_pin_exact_review_freeze_contract_and_workflow(self) -> None:
        source = validate_runtime_evidence_binding_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["source_freeze_blob_sha"],
            "f323deaca43fe50b21150d4dda79081227adb072",
        )
        self.assertEqual(
            source["source_review_blob_sha"],
            "ec92323d910785d342028c5896528fa1dcf1cc96",
        )
        self.assertEqual(
            source["source_proof_contract_blob_sha"],
            "fb9ea8d4a17734ee91225d48012a0a5b0088d415",
        )
        self.assertEqual(
            source["active_proof_workflow_blob_sha"],
            "0d6c93e2af04501f9ac2589fd24d6672b2b41910",
        )

    def test_concrete_runtime_evidence_is_exact_and_consumed(self) -> None:
        value = build_runtime_evidence_binding(repository_root=Path("."))
        self.assertIs(validate_runtime_evidence_binding(value), value)
        self.assertEqual(value["decision"], "DEC-490")
        self.assertEqual(
            value["main_head_sha"],
            "6ee059cb451e7c6d2235b7744542dc194acc014e",
        )
        self.assertEqual(value["proof_run_id"], 37120635769)
        self.assertEqual(value["proof_run_number"], 1)
        self.assertEqual(value["proof_run_attempt"], 1)
        self.assertEqual(value["proof_run_event"], "workflow_dispatch")
        self.assertEqual(value["proof_run_conclusion"], "success")
        self.assertEqual(value["proof_job_id"], 111195887975)
        self.assertEqual(value["proof_job_conclusion"], "success")
        self.assertEqual(value["artifact_id"], 11273008137)
        self.assertEqual(value["artifact_size_in_bytes"], 1370)
        self.assertEqual(
            value["artifact_digest"],
            (
                "sha256:"
                "3b242f14e89950eb828c614bf1b021dd51d9fc43b9045c2efccc6a1f7bcd8e32"
            ),
        )
        self.assertEqual(
            value["preflight_raw_sha256"],
            "70f6aaaca16fbb5de9e481e135cd8ec85d6dc7c6df524fcf328e23fd0d8de3d3",
        )
        self.assertEqual(
            value["preflight_canonical_sha256"],
            "f151fcbd487b40be35b54356f7b3002ba416812ec4ece2ea4bd7868cf5c0a163",
        )
        self.assertEqual(
            value["repository_hosted_proof_fingerprint"],
            "4ad886232c6af5566c8ac5581c153274b8328c7cd41d508ba93dcf343fdf8578",
        )
        self.assertEqual(
            value["runtime_freeze_fingerprint_sha256"],
            "99397d1593f724bcc6024c5d0a2f4abf2b230273bf7ffb0edcc0b88562cd58fb",
        )
        self.assertEqual(
            value["binding_fingerprint_sha256"],
            EXPECTED_BINDING_FINGERPRINT_SHA256,
        )
        self.assertTrue(value["proof_workflow_dispatch_authorization_consumed"])
        self.assertTrue(value["runtime_review_validated"])
        self.assertTrue(value["runtime_evidence_frozen"])
        self.assertTrue(value["runtime_evidence_bound"])

    def test_downstream_authority_remains_locked(self) -> None:
        value = build_runtime_evidence_binding(repository_root=Path("."))
        for field in (
            "repository_mutation_authorized",
            "proof_workflow_dispatch_authorized",
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
            self.assertFalse(value[field], field)
        self.assertEqual(
            value["next_gate"],
            (
                "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_"
                "INSTALL_AUTHORIZATION_BEFORE_MUTATION"
            ),
        )


if __name__ == "__main__":
    unittest.main()
