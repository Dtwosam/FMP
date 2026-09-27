from __future__ import annotations

from datetime import datetime, timedelta, timezone
import copy
import math
import unittest

import polars as pl

from fmp.discovery.nan_null_repair_adapter import (
    adapt_feature_frame,
    adapt_market_learning_cell,
    compile_cell_evidence,
    normalize_continuous_feature_value,
    validate_cell_evidence,
)
from fmp.discovery.nan_null_repair_protocol import (
    EXP062_EXPERIMENT_ID,
    exp062_repair_protocol_fingerprint,
)
from fmp.discovery.pattern_miner import (
    ConfirmationReport,
    DiscoveryReport,
    InMemoryDiscoveryResult,
    StateModel,
    ValidationReport,
)
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES
from fmp.market_learning.contracts import MARKET_FEATURE_SET_VERSION
from fmp.market_learning.outcomes import MARKET_OUTCOME_SET_VERSION
from fmp.market_learning.contracts import EVIDENCE_LABEL


PROCESSED_SHA = "a" * 64
FEATURE_MANIFEST_SHA = "b" * 64
OUTCOME_MANIFEST_SHA = "c" * 64
FEATURE_EVIDENCE_SHA = "d" * 64
OUTCOME_EVIDENCE_SHA = "e" * 64
CODE_COMMIT = "f" * 40


def _feature_row(
    *,
    available: datetime,
    nan_field: str | None = None,
    inf_field: str | None = None,
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
    for index, name in enumerate(CONTINUOUS_FEATURES):
        row[name] = float(index + 1)
    if nan_field is not None:
        row[nan_field] = float("nan")
    if inf_field is not None:
        row[inf_field] = float("inf")
    return row


def _outcome_row(*, available: datetime) -> dict[str, object]:
    return {
        "symbol": "EURUSD",
        "timeframe": "15m",
        "bar_start_utc": available - timedelta(minutes=15),
        "available_at_utc": available,
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "processed_manifest_sha256": PROCESSED_SHA,
        "exit_timestamp_utc": available + timedelta(minutes=60),
        "horizon_minutes": 60,
        "long_net_pips_0p5": 1.0,
        "short_net_pips_0p5": -1.0,
        "long_net_pips_1p0": 0.4,
        "short_net_pips_1p0": -1.6,
        "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
        "evidence_label": EVIDENCE_LABEL,
    }


def _empty_result() -> InMemoryDiscoveryResult:
    model = StateModel(symbol="EURUSD", timeframe="15m", cutpoints=())
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


class Exp062NanNullRepairAdapterTests(unittest.TestCase):
    def test_normalizer_changes_only_float_nan(self) -> None:
        self.assertIsNone(normalize_continuous_feature_value(float("nan")))
        for value in (0.0, 1.5, -2.0, 7, None, True, float("inf"), float("-inf")):
            with self.subTest(value=value):
                out = normalize_continuous_feature_value(value)
                if isinstance(value, float) and math.isinf(value):
                    self.assertTrue(math.isinf(out))
                else:
                    self.assertEqual(out, value)

    def test_feature_adapter_converts_nan_to_none_and_preserves_identity(self) -> None:
        available = datetime(2020, 6, 1, 12, 15, tzinfo=timezone.utc)
        frame = pl.DataFrame(
            [_feature_row(available=available, nan_field="realized_vol_8h")]
        )
        observations, processed = adapt_feature_frame(
            frame,
            symbol="EURUSD",
            timeframe="15m",
        )
        self.assertEqual(processed, PROCESSED_SHA)
        self.assertEqual(len(observations), 1)
        obs = observations[0]
        self.assertIsNone(obs.values["realized_vol_8h"])
        self.assertEqual(obs.values["realized_vol_1h"], float(CONTINUOUS_FEATURES.index("realized_vol_1h") + 1))
        self.assertTrue(obs.values["is_london_session"])
        self.assertFalse(obs.values["is_asia_session"])

    def test_feature_adapter_still_rejects_positive_and_negative_infinity(self) -> None:
        available = datetime(2020, 6, 1, 12, 15, tzinfo=timezone.utc)
        for bad in (float("inf"), float("-inf")):
            row = _feature_row(available=available)
            row["realized_vol_1h"] = bad
            frame = pl.DataFrame([row])
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(
                    ValueError,
                    "realized_vol_1h must be finite or null",
                ):
                    adapt_feature_frame(
                        frame,
                        symbol="EURUSD",
                        timeframe="15m",
                    )

    def test_repaired_cell_adapts_nan_and_keeps_feature_outcome_identity(self) -> None:
        available = datetime(2020, 6, 1, 12, 15, tzinfo=timezone.utc)
        adapted = adapt_market_learning_cell(
            feature_frame=pl.DataFrame(
                [_feature_row(available=available, nan_field="realized_vol_1h")]
            ),
            outcome_frame=pl.DataFrame([_outcome_row(available=available)]),
            symbol="EURUSD",
            timeframe="15m",
        )
        self.assertEqual(
            adapted.feature_observations[0].observation_id,
            adapted.outcome_observations[0].observation_id,
        )
        self.assertIsNone(
            adapted.feature_observations[0].values["realized_vol_1h"]
        )

    def test_exp062_cell_evidence_wraps_and_revalidates_predecessor_semantics(self) -> None:
        evidence = compile_cell_evidence(
            _empty_result(),
            code_commit=CODE_COMMIT,
            processed_manifest_sha256=PROCESSED_SHA,
            feature_manifest_sha256=FEATURE_MANIFEST_SHA,
            outcome_manifest_sha256=OUTCOME_MANIFEST_SHA,
            feature_evidence_fingerprint=FEATURE_EVIDENCE_SHA,
            outcome_evidence_fingerprint=OUTCOME_EVIDENCE_SHA,
        )
        self.assertIs(validate_cell_evidence(evidence), evidence)
        self.assertEqual(evidence["experiment_id"], EXP062_EXPERIMENT_ID)
        self.assertEqual(
            evidence["protocol_fingerprint"],
            exp062_repair_protocol_fingerprint(),
        )
        self.assertEqual(
            evidence["semantic_predecessor_experiment_id"],
            "EXP-20260927-061",
        )
        self.assertTrue(evidence["nan_to_null_adapter_repair_applied"])
        self.assertFalse(
            evidence["positive_negative_infinity_normalization_authorized"]
        )
        self.assertEqual(
            evidence,
            compile_cell_evidence(
                _empty_result(),
                code_commit=CODE_COMMIT,
                processed_manifest_sha256=PROCESSED_SHA,
                feature_manifest_sha256=FEATURE_MANIFEST_SHA,
                outcome_manifest_sha256=OUTCOME_MANIFEST_SHA,
                feature_evidence_fingerprint=FEATURE_EVIDENCE_SHA,
                outcome_evidence_fingerprint=OUTCOME_EVIDENCE_SHA,
            ),
        )

        tampered = copy.deepcopy(evidence)
        tampered["nan_to_null_adapter_repair_applied"] = False
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            validate_cell_evidence(tampered)

    def test_reserved_and_trading_locks_remain_false_in_wrapped_evidence(self) -> None:
        evidence = compile_cell_evidence(
            _empty_result(),
            code_commit=CODE_COMMIT,
            processed_manifest_sha256=PROCESSED_SHA,
            feature_manifest_sha256=FEATURE_MANIFEST_SHA,
            outcome_manifest_sha256=OUTCOME_MANIFEST_SHA,
            feature_evidence_fingerprint=FEATURE_EVIDENCE_SHA,
            outcome_evidence_fingerprint=OUTCOME_EVIDENCE_SHA,
        )
        for field in (
            "reserved_robustness_opened",
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


if __name__ == "__main__":
    unittest.main()
