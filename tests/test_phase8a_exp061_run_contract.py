from __future__ import annotations

import copy
import hashlib
import json
import unittest

from fmp.discovery.market_learning_adapter import compile_cell_evidence
from fmp.discovery.pattern_miner import (
    ConfirmationReport,
    DiscoveryReport,
    InMemoryDiscoveryResult,
    StateModel,
    ValidationReport,
)
from fmp.discovery.run_contract import (
    EXPECTED_ARTIFACT_COUNT,
    EXPECTED_CELL_COUNT,
    EXPECTED_CELLS,
    EXPECTED_JOB_COUNT,
    RERUN_AUTHORIZED,
    REPLACEMENT_RUN_AUTHORIZED,
    RETRY_AUTHORIZED,
    WORKFLOW_DISPATCH_AUTHORIZED,
    compile_aggregate_evidence,
    expected_artifact_names,
    expected_job_names,
    run_contract_payload,
    validate_aggregate_evidence,
)
from fmp.market_learning.evidence import EXPECTED_SOURCE_MANIFEST_SHA256


CODE_COMMIT = "a" * 40
FEATURE_EVIDENCE_FINGERPRINT = "b" * 64
OUTCOME_EVIDENCE_FINGERPRINT = "c" * 64


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _empty_result(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> InMemoryDiscoveryResult:
    model = StateModel(
        symbol=symbol,
        timeframe=timeframe,
        cutpoints=(),
    )
    discovery = DiscoveryReport(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon,
        active_continuous_features=(),
        enumerated_pattern_count=5,
        directional_hypothesis_count=10,
        qualifying_directional_hypothesis_count=0,
        deduplicated_directional_hypothesis_count=0,
        shortlist=(),
    )
    return InMemoryDiscoveryResult(
        state_model=model,
        discovery=discovery,
        confirmation=ConfirmationReport(evaluations=(), frozen=()),
        validation=ValidationReport(evaluations=(), validated=()),
    )


def _cell_evidence(
    symbol: str,
    timeframe: str,
    horizon: int,
    *,
    feature_manifest_sha: str | None = None,
    processed_sha: str | None = None,
) -> dict[str, object]:
    return compile_cell_evidence(
        _empty_result(symbol, timeframe, horizon),
        code_commit=CODE_COMMIT,
        processed_manifest_sha256=(
            processed_sha or EXPECTED_SOURCE_MANIFEST_SHA256[symbol]
        ),
        feature_manifest_sha256=(
            feature_manifest_sha
            or _sha(f"feature:{symbol}:{timeframe}")
        ),
        outcome_manifest_sha256=_sha(f"outcome:{symbol}:{timeframe}"),
        feature_evidence_fingerprint=FEATURE_EVIDENCE_FINGERPRINT,
        outcome_evidence_fingerprint=OUTCOME_EVIDENCE_FINGERPRINT,
    )


def _all_cells() -> list[dict[str, object]]:
    return [
        _cell_evidence(symbol, timeframe, horizon)
        for symbol, timeframe, horizon in EXPECTED_CELLS
    ]


class Exp061RunContractTests(unittest.TestCase):
    def test_run_contract_freezes_exact_unambiguous_inventory(self) -> None:
        payload = run_contract_payload(code_commit=CODE_COMMIT)
        self.assertEqual(EXPECTED_CELL_COUNT, 18)
        self.assertEqual(len(payload["cells"]), 18)
        self.assertEqual(EXPECTED_JOB_COUNT, 20)
        self.assertEqual(EXPECTED_ARTIFACT_COUNT, 20)

        jobs = expected_job_names()
        artifacts = expected_artifact_names(code_commit=CODE_COMMIT)
        self.assertEqual(len(jobs), 20)
        self.assertEqual(len(set(jobs)), 20)
        self.assertEqual(len(artifacts), 20)
        self.assertEqual(len(set(artifacts)), 20)
        self.assertEqual(jobs[0], "exp061-preflight")
        self.assertEqual(jobs[-1], "exp061-aggregate")
        self.assertTrue(
            all("(" not in name and "," not in name for name in jobs)
        )

        self.assertEqual(payload["workflow"]["event"], "workflow_dispatch")
        self.assertEqual(payload["workflow"]["branch"], "main")
        self.assertEqual(payload["workflow"]["run_attempt"], 1)
        self.assertFalse(payload["authorizations"]["workflow_source_authorized"])
        self.assertFalse(payload["authorizations"]["workflow_dispatch_authorized"])
        self.assertFalse(
            payload["authorizations"]["historical_discovery_execution_authorized"]
        )
        self.assertTrue(
            payload["non_success_shape"]["slot_consumed_if_later_authorized"]
        )
        self.assertFalse(payload["non_success_shape"]["rerun_authorized"])
        self.assertFalse(payload["non_success_shape"]["retry_authorized"])
        self.assertFalse(payload["non_success_shape"]["replacement_run_authorized"])

    def test_aggregate_compiles_exact_eighteen_cells_deterministically(self) -> None:
        cells = _all_cells()
        first = compile_aggregate_evidence(
            cells,
            code_commit=CODE_COMMIT,
        )
        second = compile_aggregate_evidence(
            list(reversed(cells)),
            code_commit=CODE_COMMIT,
        )
        self.assertEqual(first, second)
        self.assertIs(validate_aggregate_evidence(first), first)
        self.assertEqual(first["verified_cell_count"], 18)
        self.assertEqual(first["discovery_shortlist_count"], 0)
        self.assertEqual(first["confirmation_frozen_count"], 0)
        self.assertEqual(first["validation_accepted_count"], 0)
        self.assertFalse(first["reserved_robustness_opened"])

        for field in (
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(first[field], field)

    def test_aggregate_rejects_missing_cell(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly 18"):
            compile_aggregate_evidence(
                _all_cells()[:-1],
                code_commit=CODE_COMMIT,
            )

    def test_aggregate_rejects_phase2_source_identity_drift(self) -> None:
        cells = _all_cells()
        symbol, timeframe, horizon = EXPECTED_CELLS[0]
        cells[0] = _cell_evidence(
            symbol,
            timeframe,
            horizon,
            processed_sha="d" * 64,
        )
        with self.assertRaisesRegex(ValueError, "Phase 2 source identity mismatch"):
            compile_aggregate_evidence(
                cells,
                code_commit=CODE_COMMIT,
            )

    def test_aggregate_rejects_manifest_drift_across_horizons(self) -> None:
        cells = _all_cells()
        symbol, timeframe, horizon = EXPECTED_CELLS[1]
        cells[1] = _cell_evidence(
            symbol,
            timeframe,
            horizon,
            feature_manifest_sha="e" * 64,
        )
        with self.assertRaisesRegex(ValueError, "differs across horizons"):
            compile_aggregate_evidence(
                cells,
                code_commit=CODE_COMMIT,
            )

    def test_re_fingerprinted_aggregate_semantic_forgery_is_rejected(self) -> None:
        evidence = compile_aggregate_evidence(
            _all_cells(),
            code_commit=CODE_COMMIT,
        )
        forged = copy.deepcopy(evidence)
        forged["verified_cell_count"] = 17
        unsigned = dict(forged)
        unsigned.pop("evidence_fingerprint", None)
        forged["evidence_fingerprint"] = hashlib.sha256(
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

        with self.assertRaisesRegex(ValueError, "verified cell count mismatch"):
            validate_aggregate_evidence(forged)

    def test_all_execution_retry_and_trading_authorities_remain_false(self) -> None:
        self.assertFalse(WORKFLOW_DISPATCH_AUTHORIZED)
        self.assertFalse(RERUN_AUTHORIZED)
        self.assertFalse(RETRY_AUTHORIZED)
        self.assertFalse(REPLACEMENT_RUN_AUTHORIZED)


if __name__ == "__main__":
    unittest.main()
