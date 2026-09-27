from __future__ import annotations

from datetime import datetime, timedelta, timezone
import copy
import unittest

import polars as pl

from fmp.discovery.market_learning_adapter import (
    adapt_feature_frame,
    adapt_market_learning_cell,
    adapt_outcome_frame,
    compile_cell_evidence,
    validate_cell_evidence,
)
from fmp.discovery.pattern_miner import (
    ConfirmationReport,
    DiscoveryReport,
    InMemoryDiscoveryResult,
    StateModel,
    ValidationReport,
)
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES
from fmp.market_learning.contracts import (
    EVIDENCE_LABEL,
    MARKET_FEATURE_SET_VERSION,
)
from fmp.market_learning.outcomes import MARKET_OUTCOME_SET_VERSION


PROCESSED_SHA = "a" * 64
FEATURE_EVIDENCE_SHA = "b" * 64
OUTCOME_EVIDENCE_SHA = "c" * 64
CODE_COMMIT = "d" * 40


def _feature_row(
    *,
    available: datetime,
    signal: float = 1.0,
) -> dict[str, object]:
    row: dict[str, object] = {
        "symbol": "EURUSD",
        "timeframe": "15m",
        "bar_start_utc": available - timedelta(minutes=15),
        "available_at_utc": available,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "processed_manifest_sha256": PROCESSED_SHA,
        "is_london_new_york_overlap": False,
        "is_london_session": True,
        "is_new_york_session": False,
        "is_asia_session": False,
    }
    for name in CONTINUOUS_FEATURES:
        row[name] = 1.0
    row["return_1h"] = signal
    return row


def _outcome_row(
    *,
    available: datetime,
    horizon: int = 60,
) -> dict[str, object]:
    return {
        "symbol": "EURUSD",
        "timeframe": "15m",
        "bar_start_utc": available - timedelta(minutes=15),
        "available_at_utc": available,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "processed_manifest_sha256": PROCESSED_SHA,
        "exit_timestamp_utc": available + timedelta(minutes=horizon),
        "horizon_minutes": horizon,
        "long_net_pips_0p5": 1.0,
        "short_net_pips_0p5": -1.0,
        "long_net_pips_1p0": 0.4,
        "short_net_pips_1p0": -1.6,
        "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
        "evidence_label": EVIDENCE_LABEL,
    }


def _empty_result() -> InMemoryDiscoveryResult:
    model = StateModel(
        symbol="EURUSD",
        timeframe="15m",
        cutpoints=(),
    )
    discovery = DiscoveryReport(
        symbol="EURUSD",
        timeframe="15m",
        horizon_minutes=60,
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


class Exp061MarketLearningAdapterTests(unittest.TestCase):
    def test_exact_frames_adapt_to_matching_immutable_observations(self) -> None:
        available = datetime(2020, 6, 1, 12, 15, tzinfo=timezone.utc)
        feature_frame = pl.DataFrame([_feature_row(available=available)])
        outcome_frame = pl.DataFrame([_outcome_row(available=available)])

        adapted = adapt_market_learning_cell(
            feature_frame=feature_frame,
            outcome_frame=outcome_frame,
            symbol="EURUSD",
            timeframe="15m",
        )

        self.assertEqual(adapted.processed_manifest_sha256, PROCESSED_SHA)
        self.assertEqual(len(adapted.feature_observations), 1)
        self.assertEqual(len(adapted.outcome_observations), 1)
        self.assertEqual(
            adapted.feature_observations[0].observation_id,
            adapted.outcome_observations[0].observation_id,
        )
        self.assertEqual(
            adapted.outcome_observations[0].exit_timestamp_utc,
            available + timedelta(minutes=60),
        )

    def test_feature_adapter_rejects_reserved_2023_rows(self) -> None:
        available = datetime(2023, 1, 1, 0, 15, tzinfo=timezone.utc)
        frame = pl.DataFrame([_feature_row(available=available)])
        with self.assertRaisesRegex(ValueError, "outside 2015-2022 input range"):
            adapt_feature_frame(
                frame,
                symbol="EURUSD",
                timeframe="15m",
            )

    def test_outcome_adapter_rejects_target_crossing_into_reserved_2023(self) -> None:
        available = datetime(2022, 12, 31, 23, 0, tzinfo=timezone.utc)
        frame = pl.DataFrame([_outcome_row(available=available, horizon=60)])
        with self.assertRaisesRegex(ValueError, "refuses any target"):
            adapt_outcome_frame(
                frame,
                symbol="EURUSD",
                timeframe="15m",
                expected_processed_manifest_sha256=PROCESSED_SHA,
            )

    def test_feature_outcome_source_identity_mismatch_fails_closed(self) -> None:
        available = datetime(2020, 6, 1, 12, 15, tzinfo=timezone.utc)
        feature_frame = pl.DataFrame([_feature_row(available=available)])
        outcome = _outcome_row(available=available)
        outcome["processed_manifest_sha256"] = "e" * 64
        outcome_frame = pl.DataFrame([outcome])

        with self.assertRaisesRegex(ValueError, "processed-manifest identity mismatch"):
            adapt_market_learning_cell(
                feature_frame=feature_frame,
                outcome_frame=outcome_frame,
                symbol="EURUSD",
                timeframe="15m",
            )

    def test_cell_evidence_is_deterministic_and_tamper_detecting(self) -> None:
        evidence = compile_cell_evidence(
            _empty_result(),
            code_commit=CODE_COMMIT,
            processed_manifest_sha256=PROCESSED_SHA,
            feature_evidence_fingerprint=FEATURE_EVIDENCE_SHA,
            outcome_evidence_fingerprint=OUTCOME_EVIDENCE_SHA,
        )
        self.assertEqual(
            evidence,
            compile_cell_evidence(
                _empty_result(),
                code_commit=CODE_COMMIT,
                processed_manifest_sha256=PROCESSED_SHA,
                feature_evidence_fingerprint=FEATURE_EVIDENCE_SHA,
                outcome_evidence_fingerprint=OUTCOME_EVIDENCE_SHA,
            ),
        )
        self.assertIs(validate_cell_evidence(evidence), evidence)
        self.assertFalse(evidence["reserved_robustness_opened"])

        for field in (
            "historical_source_access_authorized",
            "historical_discovery_execution_authorized",
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
            self.assertFalse(evidence[field], field)

        tampered = copy.deepcopy(evidence)
        tampered["reserved_robustness_opened"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            validate_cell_evidence(tampered)


if __name__ == "__main__":
    unittest.main()
