from __future__ import annotations

import copy
import unittest

from fmp.discovery.exp062_adapter_probe import (
    EXPECTED_CELLS,
    compile_exp062_adapter_probe,
)
from fmp.discovery.exp062_adapter_proof_content_review import (
    EXP062_ADAPTER_PROOF_CONTENT_REVIEW_DECISION,
    review_exp062_adapter_proof_content,
)
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES


HEAD = "a" * 40


def _terminal() -> dict[str, object]:
    return {
        "decision": "DEC-295",
        "version": "fmp-exp062-adapter-proof-review-contract-v1",
        "stage": "EXP062_ADAPTER_PROOF_SUCCESS_COMPLETE_REVIEW_REQUIRED",
        "proof_run_id": 41000000000,
        "proof_run_head_sha": HEAD,
        "proof_run_conclusion": "success",
        "proof_run_attempt": 1,
        "proof_success_complete": True,
        "materialized_job_count": 10,
        "artifact_count": 10,
        "expected_success_job_count": 10,
        "expected_success_artifact_count": 10,
        "aggregate_content_review_required": True,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def _cell(symbol: str, timeframe: str, index: int) -> dict[str, object]:
    counts = {name: 0 for name in CONTINUOUS_FEATURES}
    if index % 2 == 0:
        counts["realized_vol_8h"] = index + 1
    total = sum(counts.values())
    return {
        "decision": "DEC-294",
        "version": "fmp-exp062-real-data-adapter-probe-v1",
        "experiment_id": "EXP-20260927-062",
        "repair_decision": "DEC-293",
        "repair_version": "fmp-exp062-nonfinite-feature-normalization-v1",
        "predecessor_failure_decision": "DEC-292",
        "code_commit": HEAD,
        "symbol": symbol,
        "timeframe": timeframe,
        "feature_row_count": 100 + index,
        "outcome_row_count": 200 + index,
        "adapted_feature_observation_count": 100 + index,
        "adapted_outcome_observation_count": 200 + index,
        "processed_manifest_sha256": "1" * 64,
        "feature_manifest_sha256": "2" * 64,
        "outcome_manifest_sha256": "3" * 64,
        "feature_evidence_fingerprint": "4" * 64,
        "outcome_evidence_fingerprint": "5" * 64,
        "selected_feature_partition_count": 96,
        "selected_outcome_partition_count": 96,
        "raw_nonfinite_by_feature": counts,
        "raw_nonfinite_value_count": total,
        "adapter_probe_success": True,
        "historical_source_probe_authorized": True,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def _cells() -> list[dict[str, object]]:
    return [
        _cell(symbol, timeframe, index)
        for index, (symbol, timeframe) in enumerate(EXPECTED_CELLS)
    ]


class Exp062AdapterProofContentReviewTests(unittest.TestCase):
    def test_exact_proof_content_verifies_repair_without_authority(self) -> None:
        cells = _cells()
        aggregate = compile_exp062_adapter_probe(cells, code_commit=HEAD)
        report = review_exp062_adapter_proof_content(
            terminal_review=_terminal(),
            cell_probes=cells,
            aggregate_proof=aggregate,
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            report["decision"],
            EXP062_ADAPTER_PROOF_CONTENT_REVIEW_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "EXP062_ADAPTER_REPAIR_REAL_DATA_PROOF_VERIFIED",
        )
        self.assertEqual(report["verified_cell_probe_count"], 9)
        self.assertTrue(report["aggregate_proof_verified"])
        self.assertGreater(report["total_raw_nonfinite_value_count"], 0)
        self.assertGreater(report["cells_with_raw_nonfinite_values"], 0)
        self.assertEqual(
            sum(report["raw_nonfinite_by_feature"].values()),
            report["total_raw_nonfinite_value_count"],
        )
        self.assertFalse(report["historical_discovery_execution_authorized"])
        self.assertFalse(report["discovery_result_authorized"])
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_requires_exact_nine_cell_inventory(self) -> None:
        cells = _cells()
        aggregate = compile_exp062_adapter_probe(cells, code_commit=HEAD)
        with self.assertRaisesRegex(ValueError, "exactly nine cell probes"):
            review_exp062_adapter_proof_content(
                terminal_review=_terminal(),
                cell_probes=cells[:-1],
                aggregate_proof=aggregate,
                expected_head_sha=HEAD,
            )

    def test_commit_drift_is_rejected(self) -> None:
        cells = _cells()
        cells[0]["code_commit"] = "b" * 40
        aggregate = compile_exp062_adapter_probe(_cells(), code_commit=HEAD)
        with self.assertRaisesRegex(ValueError, "cell probe commit mismatch"):
            review_exp062_adapter_proof_content(
                terminal_review=_terminal(),
                cell_probes=cells,
                aggregate_proof=aggregate,
                expected_head_sha=HEAD,
            )

    def test_aggregate_must_match_deterministic_recompilation(self) -> None:
        cells = _cells()
        aggregate = compile_exp062_adapter_probe(cells, code_commit=HEAD)
        tampered = copy.deepcopy(aggregate)
        tampered["total_feature_row_count"] += 1
        with self.assertRaisesRegex(
            ValueError,
            "deterministic recompilation",
        ):
            review_exp062_adapter_proof_content(
                terminal_review=_terminal(),
                cell_probes=cells,
                aggregate_proof=tampered,
                expected_head_sha=HEAD,
            )

    def test_terminal_review_must_be_complete_success(self) -> None:
        cells = _cells()
        aggregate = compile_exp062_adapter_probe(cells, code_commit=HEAD)
        terminal = _terminal()
        terminal["proof_success_complete"] = False
        with self.assertRaisesRegex(
            ValueError,
            "proof_success_complete mismatch",
        ):
            review_exp062_adapter_proof_content(
                terminal_review=terminal,
                cell_probes=cells,
                aggregate_proof=aggregate,
                expected_head_sha=HEAD,
            )

    def test_zero_real_nonfinite_case_cannot_be_reclassified_as_proof(self) -> None:
        cells = _cells()
        for cell in cells:
            cell["raw_nonfinite_by_feature"] = {
                name: 0 for name in CONTINUOUS_FEATURES
            }
            cell["raw_nonfinite_value_count"] = 0
        with self.assertRaisesRegex(
            ValueError,
            "must encounter the repaired nonfinite case",
        ):
            aggregate = compile_exp062_adapter_probe(cells, code_commit=HEAD)
            review_exp062_adapter_proof_content(
                terminal_review=_terminal(),
                cell_probes=cells,
                aggregate_proof=aggregate,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
