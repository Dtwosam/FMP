from __future__ import annotations

import copy
from pathlib import Path
import unittest

from fmp.discovery.nan_null_repair_adapter import compile_cell_evidence
from fmp.discovery.nan_null_repair_run_contract import (
    EXPECTED_ARTIFACT_COUNT,
    EXPECTED_CELL_COUNT,
    EXPECTED_CELLS,
    EXPECTED_JOB_COUNT,
    compile_aggregate_evidence,
    expected_artifact_names,
    expected_job_names,
    run_contract_payload,
    validate_aggregate_evidence,
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


def _cells() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for symbol, timeframe, horizon in EXPECTED_CELLS:
        feature_manifest = (
            f"{symbol}-{timeframe}-feature".encode("utf-8").hex()[:64]
        ).ljust(64, "0")
        outcome_manifest = (
            f"{symbol}-{timeframe}-outcome".encode("utf-8").hex()[:64]
        ).ljust(64, "0")
        out.append(
            compile_cell_evidence(
                _result(symbol, timeframe, horizon),
                code_commit=CODE_COMMIT,
                processed_manifest_sha256=EXPECTED_SOURCE_MANIFEST_SHA256[
                    symbol
                ],
                feature_manifest_sha256=feature_manifest,
                outcome_manifest_sha256=outcome_manifest,
                feature_evidence_fingerprint=FEATURE_EVIDENCE_SHA,
                outcome_evidence_fingerprint=OUTCOME_EVIDENCE_SHA,
            )
        )
    return out


class Exp062RunContractTests(unittest.TestCase):
    def test_sources_bind_exact_repair_stack_and_keep_execution_locked(self) -> None:
        report = validate_exp062_run_contract_sources(
            repository_root=Path("."),
        )
        self.assertEqual(report["decision"], "DEC-294")
        self.assertEqual(report["experiment_id"], "EXP-20260927-062")
        self.assertEqual(
            report["source_blobs"]["dec292_repair_protocol"],
            "1d26da24134c825e2f405224316e1dd3136a38fb",
        )
        self.assertEqual(
            report["source_blobs"]["dec293_repaired_adapter"],
            "53f85d99bad42decb673e9fa2ff0f771150e17db",
        )
        self.assertFalse(report["workflow_source_authorized"])
        self.assertFalse(report["workflow_dispatch_authorized"])
        self.assertFalse(report["historical_discovery_execution_authorized"])
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_contract_has_exact_twenty_jobs_and_artifacts_with_exp062_names(self) -> None:
        value = run_contract_payload(code_commit=CODE_COMMIT)
        self.assertEqual(value["decision"], "DEC-294")
        self.assertEqual(value["experiment_id"], "EXP-20260927-062")
        self.assertEqual(len(expected_job_names()), EXPECTED_JOB_COUNT)
        self.assertEqual(
            len(expected_artifact_names(code_commit=CODE_COMMIT)),
            EXPECTED_ARTIFACT_COUNT,
        )
        self.assertEqual(EXPECTED_CELL_COUNT, 18)
        self.assertEqual(expected_job_names()[0], "exp062-preflight")
        self.assertEqual(expected_job_names()[-1], "exp062-aggregate")
        self.assertTrue(
            all(
                name.startswith("exp062-")
                for name in expected_job_names()
            )
        )
        self.assertTrue(
            all(
                name.startswith("phase8a-exp062-")
                for name in expected_artifact_names(
                    code_commit=CODE_COMMIT
                )
            )
        )

    def test_contract_keeps_every_execution_and_downstream_path_locked(self) -> None:
        auth = run_contract_payload(
            code_commit=CODE_COMMIT
        )["authorizations"]
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

    def test_aggregate_wraps_exact_exp061_semantics_and_revalidates(self) -> None:
        cells = _cells()
        value = compile_aggregate_evidence(
            cells,
            code_commit=CODE_COMMIT,
        )
        self.assertIs(validate_aggregate_evidence(value), value)
        self.assertEqual(value["experiment_id"], "EXP-20260927-062")
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
        self.assertTrue(value["nan_to_null_adapter_repair_applied"])
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

    def test_aggregate_requires_exact_eighteen_cells(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "exactly 18 cell evidence objects",
        ):
            compile_aggregate_evidence(
                _cells()[:-1],
                code_commit=CODE_COMMIT,
            )

    def test_aggregate_rejects_commit_mismatch(self) -> None:
        cells = _cells()
        cells[0] = dict(cells[0])
        cells[0]["code_commit"] = "a" * 40
        with self.assertRaises(ValueError):
            compile_aggregate_evidence(
                cells,
                code_commit=CODE_COMMIT,
            )

    def test_outer_aggregate_tamper_is_detected(self) -> None:
        value = compile_aggregate_evidence(
            _cells(),
            code_commit=CODE_COMMIT,
        )
        tampered = copy.deepcopy(value)
        tampered["nan_to_null_adapter_repair_applied"] = False
        with self.assertRaisesRegex(
            ValueError,
            "fingerprint mismatch",
        ):
            validate_aggregate_evidence(tampered)

    def test_exp062_cell_fingerprint_inventory_is_exact_and_unique(self) -> None:
        value = compile_aggregate_evidence(
            _cells(),
            code_commit=CODE_COMMIT,
        )
        rows = value["exp062_cell_evidence_fingerprints"]
        self.assertEqual(len(rows), 18)
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

    def test_aggregate_keeps_reserved_and_trading_locks_closed(self) -> None:
        value = compile_aggregate_evidence(
            _cells(),
            code_commit=CODE_COMMIT,
        )
        for field in (
            "reserved_robustness_opened",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(value[field], field)


if __name__ == "__main__":
    unittest.main()
