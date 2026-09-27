from __future__ import annotations

import copy
from pathlib import Path
import unittest

from fmp.discovery.exp062_run_contract import (
    EXPECTED_ARTIFACT_COUNT,
    EXPECTED_CELL_COUNT,
    EXPECTED_CELLS,
    EXPECTED_JOB_COUNT,
    EXP062_EXPERIMENT_ID,
    compile_aggregate_evidence,
    compile_cell_evidence,
    expected_artifact_names,
    expected_job_names,
    run_contract_payload,
    validate_aggregate_evidence,
    validate_cell_evidence,
    validate_exp062_run_contract_sources,
)
from fmp.discovery.pattern_miner import (
    ConfirmationReport,
    DiscoveryReport,
    InMemoryDiscoveryResult,
    StateModel,
    ValidationReport,
)
from fmp.market_learning.evidence import EXPECTED_SOURCE_MANIFEST_SHA256


CODE_COMMIT = "f" * 40
FEATURE_EVIDENCE_SHA = "d" * 64
OUTCOME_EVIDENCE_SHA = "e" * 64


def _result(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> InMemoryDiscoveryResult:
    return InMemoryDiscoveryResult(
        state_model=StateModel(
            symbol=symbol,
            timeframe=timeframe,
            cutpoints=(),
        ),
        discovery=DiscoveryReport(
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon,
            active_continuous_features=(),
            enumerated_pattern_count=5,
            directional_hypothesis_count=10,
            qualifying_directional_hypothesis_count=0,
            deduplicated_directional_hypothesis_count=0,
            shortlist=(),
        ),
        confirmation=ConfirmationReport(evaluations=(), frozen=()),
        validation=ValidationReport(evaluations=(), validated=()),
    )


def _cell(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> dict[str, object]:
    feature_manifest = (
        f"{symbol}-{timeframe}-feature".encode("utf-8").hex()[:64]
    ).ljust(64, "0")
    outcome_manifest = (
        f"{symbol}-{timeframe}-outcome".encode("utf-8").hex()[:64]
    ).ljust(64, "0")
    return compile_cell_evidence(
        _result(symbol, timeframe, horizon),
        code_commit=CODE_COMMIT,
        processed_manifest_sha256=EXPECTED_SOURCE_MANIFEST_SHA256[symbol],
        feature_manifest_sha256=feature_manifest,
        outcome_manifest_sha256=outcome_manifest,
        feature_evidence_fingerprint=FEATURE_EVIDENCE_SHA,
        outcome_evidence_fingerprint=OUTCOME_EVIDENCE_SHA,
    )


def _cells() -> list[dict[str, object]]:
    return [
        _cell(symbol, timeframe, horizon)
        for symbol, timeframe, horizon in EXPECTED_CELLS
    ]


class Exp062RunEvidenceContractTests(unittest.TestCase):
    def test_sources_bind_verified_repair_and_frozen_predecessors(self) -> None:
        report = validate_exp062_run_contract_sources(
            repository_root=Path("."),
        )
        self.assertEqual(report["decision"], "DEC-298")
        self.assertEqual(report["experiment_id"], EXP062_EXPERIMENT_ID)
        self.assertEqual(
            report["source_blobs"]["dec297_verified_repair_proof"],
            "18b7dde7eadf0f051a09fda04e648650bb270eb7",
        )
        self.assertEqual(
            report["source_blobs"]["dec293_repaired_adapter"],
            "491ba8c92cb6e6e4c715bfb1ecb934b6949e1596",
        )
        self.assertEqual(
            report["source_blobs"]["exp061_cell_adapter"],
            "978a33554fad7e9d78b002778c4896be0af3333a",
        )
        for field in (
            "workflow_source_authorized",
            "workflow_dispatch_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "trading_authorized",
        ):
            self.assertFalse(report[field], field)

    def test_contract_has_distinct_exp062_twenty_job_artifact_identity(self) -> None:
        value = run_contract_payload(code_commit=CODE_COMMIT)
        self.assertEqual(value["decision"], "DEC-298")
        self.assertEqual(value["experiment_id"], "EXP-20260927-062")
        self.assertEqual(EXPECTED_CELL_COUNT, 18)
        self.assertEqual(len(expected_job_names()), EXPECTED_JOB_COUNT)
        self.assertEqual(
            len(expected_artifact_names(code_commit=CODE_COMMIT)),
            EXPECTED_ARTIFACT_COUNT,
        )
        self.assertEqual(expected_job_names()[0], "exp062-preflight")
        self.assertEqual(expected_job_names()[-1], "exp062-aggregate")
        self.assertTrue(
            all(name.startswith("exp062-") for name in expected_job_names())
        )
        self.assertTrue(
            all(
                name.startswith("phase8a-exp062-")
                for name in expected_artifact_names(code_commit=CODE_COMMIT)
            )
        )
        auth = value["authorizations"]
        for field in (
            "workflow_source_authorized",
            "workflow_dispatch_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(auth[field], field)

    def test_cell_evidence_wraps_exact_predecessor_semantics(self) -> None:
        value = _cell("EURUSD", "5m", 60)
        self.assertIs(validate_cell_evidence(value), value)
        self.assertEqual(value["experiment_id"], EXP062_EXPERIMENT_ID)
        self.assertEqual(
            value["evidence_protocol"],
            "fmp-exp062-cell-evidence-v1",
        )
        self.assertEqual(value["repair_decision"], "DEC-293")
        self.assertEqual(value["repair_proof_decision"], "DEC-297")
        self.assertEqual(
            value["semantic_predecessor_experiment_id"],
            "EXP-20260927-061",
        )
        self.assertTrue(value["nonfinite_to_null_repair_applied"])
        self.assertEqual(
            value,
            _cell("EURUSD", "5m", 60),
        )

    def test_cell_outer_tamper_is_detected(self) -> None:
        value = _cell("EURUSD", "5m", 60)
        tampered = copy.deepcopy(value)
        tampered["nonfinite_to_null_repair_applied"] = False
        with self.assertRaisesRegex(
            ValueError,
            "cell evidence fingerprint mismatch",
        ):
            validate_cell_evidence(tampered)

    def test_aggregate_round_trips_all_eighteen_cells(self) -> None:
        cells = _cells()
        value = compile_aggregate_evidence(
            cells,
            code_commit=CODE_COMMIT,
        )
        self.assertIs(validate_aggregate_evidence(value), value)
        self.assertEqual(value["experiment_id"], EXP062_EXPERIMENT_ID)
        self.assertEqual(
            value["evidence_protocol"],
            "fmp-exp062-aggregate-evidence-v1",
        )
        self.assertEqual(
            value["run_contract_version"],
            "fmp-exp062-run-contract-v1",
        )
        self.assertEqual(value["verified_cell_count"], 18)
        self.assertEqual(value["discovery_shortlist_count"], 0)
        self.assertEqual(value["confirmation_frozen_count"], 0)
        self.assertEqual(value["validation_accepted_count"], 0)
        self.assertTrue(value["nonfinite_to_null_repair_applied"])
        self.assertEqual(
            len(value["exp062_cell_evidence_fingerprints"]),
            18,
        )
        self.assertEqual(
            value,
            compile_aggregate_evidence(
                cells,
                code_commit=CODE_COMMIT,
            ),
        )

    def test_aggregate_requires_exact_cells_and_single_commit(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly 18 cells"):
            compile_aggregate_evidence(
                _cells()[:-1],
                code_commit=CODE_COMMIT,
            )

        cells = _cells()
        cells[0] = dict(cells[0])
        cells[0]["code_commit"] = "a" * 40
        cells[0].pop("evidence_fingerprint")
        with self.assertRaises(ValueError):
            compile_aggregate_evidence(
                cells,
                code_commit=CODE_COMMIT,
            )

    def test_aggregate_outer_tamper_is_detected(self) -> None:
        value = compile_aggregate_evidence(
            _cells(),
            code_commit=CODE_COMMIT,
        )
        tampered = copy.deepcopy(value)
        tampered["candidate_compilation_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "aggregate evidence fingerprint mismatch",
        ):
            validate_aggregate_evidence(tampered)

    def test_exp062_outer_cell_fingerprints_are_exact_and_unique(self) -> None:
        value = compile_aggregate_evidence(
            _cells(),
            code_commit=CODE_COMMIT,
        )
        rows = value["exp062_cell_evidence_fingerprints"]
        identities = [
            (
                row["symbol"],
                row["timeframe"],
                row["horizon_minutes"],
            )
            for row in rows
        ]
        self.assertEqual(identities, sorted(EXPECTED_CELLS))
        fingerprints = [row["evidence_fingerprint"] for row in rows]
        self.assertEqual(len(fingerprints), len(set(fingerprints)))


if __name__ == "__main__":
    unittest.main()
