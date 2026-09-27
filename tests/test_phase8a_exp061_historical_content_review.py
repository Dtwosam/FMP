from __future__ import annotations

import copy
import hashlib
import json
import unittest

from fmp.discovery.historical_result_content_review import (
    review_historical_result_content,
)
from fmp.discovery.market_learning_adapter import compile_cell_evidence
from fmp.discovery.pattern_miner import (
    ConfirmationReport,
    DiscoveryReport,
    InMemoryDiscoveryResult,
    StateModel,
    ValidationReport,
)
from fmp.discovery.run_contract import (
    EXPECTED_CELLS,
    compile_aggregate_evidence,
)
from fmp.market_learning.evidence import EXPECTED_SOURCE_MANIFEST_SHA256


HEAD = "a" * 40
FEATURE_EVIDENCE_FINGERPRINT = "b" * 64
OUTCOME_EVIDENCE_FINGERPRINT = "c" * 64


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _empty_result(
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


def _cell(symbol: str, timeframe: str, horizon: int) -> dict[str, object]:
    return compile_cell_evidence(
        _empty_result(symbol, timeframe, horizon),
        code_commit=HEAD,
        processed_manifest_sha256=EXPECTED_SOURCE_MANIFEST_SHA256[symbol],
        feature_manifest_sha256=_sha(f"feature:{symbol}:{timeframe}"),
        outcome_manifest_sha256=_sha(f"outcome:{symbol}:{timeframe}"),
        feature_evidence_fingerprint=FEATURE_EVIDENCE_FINGERPRINT,
        outcome_evidence_fingerprint=OUTCOME_EVIDENCE_FINGERPRINT,
    )


def _cells() -> list[dict[str, object]]:
    return [
        _cell(symbol, timeframe, horizon)
        for symbol, timeframe, horizon in EXPECTED_CELLS
    ]


class Exp061HistoricalContentReviewTests(unittest.TestCase):
    def test_exact_cells_and_recomputed_aggregate_validate(self) -> None:
        cells = _cells()
        aggregate = compile_aggregate_evidence(cells, code_commit=HEAD)
        report = review_historical_result_content(
            list(reversed(cells)),
            aggregate,
            expected_head_sha=HEAD,
        )
        self.assertEqual(report["verified_cell_count"], 18)
        self.assertTrue(report["aggregate_recomputed_exactly"])
        self.assertEqual(report["discovery_shortlist_count"], 0)
        self.assertEqual(report["confirmation_frozen_count"], 0)
        self.assertEqual(report["validation_accepted_count"], 0)
        self.assertEqual(
            report["content_classification"],
            "HISTORICAL_CONTENT_VALID_NO_VALIDATED_PATTERNS",
        )
        self.assertTrue(report["historical_result_content_validated"])
        self.assertFalse(report["historical_result_accepted"])
        self.assertFalse(report["pattern_hypotheses_accepted"])
        self.assertTrue(report["reviewed_result_decision_required"])

    def test_missing_or_duplicate_cell_fails_closed(self) -> None:
        cells = _cells()
        aggregate = compile_aggregate_evidence(cells, code_commit=HEAD)
        with self.assertRaisesRegex(ValueError, "exactly 18"):
            review_historical_result_content(
                cells[:-1],
                aggregate,
                expected_head_sha=HEAD,
            )

        duplicated = list(cells)
        duplicated[-1] = duplicated[0]
        with self.assertRaisesRegex(ValueError, "duplicate cell evidence"):
            review_historical_result_content(
                duplicated,
                aggregate,
                expected_head_sha=HEAD,
            )

    def test_cell_commit_drift_is_rejected(self) -> None:
        cells = _cells()
        aggregate = compile_aggregate_evidence(cells, code_commit=HEAD)
        forged = copy.deepcopy(cells)
        forged[0]["code_commit"] = "d" * 40
        unsigned = dict(forged[0])
        unsigned.pop("evidence_fingerprint", None)
        forged[0]["evidence_fingerprint"] = hashlib.sha256(
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

        with self.assertRaisesRegex(ValueError, "cell code commit mismatch"):
            review_historical_result_content(
                forged,
                aggregate,
                expected_head_sha=HEAD,
            )

    def test_aggregate_commit_drift_is_rejected(self) -> None:
        cells = _cells()
        aggregate = compile_aggregate_evidence(cells, code_commit=HEAD)
        forged = copy.deepcopy(aggregate)
        forged["code_commit"] = "d" * 40
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

        with self.assertRaisesRegex(ValueError, "aggregate code commit mismatch"):
            review_historical_result_content(
                cells,
                forged,
                expected_head_sha=HEAD,
            )

    def test_recomputed_aggregate_must_match_exactly(self) -> None:
        cells = _cells()
        aggregate = compile_aggregate_evidence(cells, code_commit=HEAD)
        forged = copy.deepcopy(aggregate)
        forged["evidence_label"] = "RETROSPECTIVE_ALREADY_SEEN"
        forged["untouched_oos"] = False
        forged["candidate_compilation_authorized"] = False
        forged["reserved_robustness_opened"] = False
        forged["discovery_shortlist_count"] = 1
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

        with self.assertRaises(ValueError):
            review_historical_result_content(
                cells,
                forged,
                expected_head_sha=HEAD,
            )

    def test_all_downstream_authorities_remain_false(self) -> None:
        cells = _cells()
        aggregate = compile_aggregate_evidence(cells, code_commit=HEAD)
        report = review_historical_result_content(
            cells,
            aggregate,
            expected_head_sha=HEAD,
        )
        for field in (
            "historical_result_accepted",
            "pattern_hypotheses_accepted",
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
            self.assertFalse(report[field], field)


if __name__ == "__main__":
    unittest.main()
