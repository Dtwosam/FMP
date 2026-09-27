from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch
import unittest

import polars as pl

from fmp.discovery.exp062_adapter_probe import (
    EXPECTED_CELLS,
    compile_exp062_adapter_probe,
    probe_exp062_adapter_cell,
    validate_exp062_adapter_probe_cell,
)
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES


HEAD = "a" * 40


def _frame(*, nonfinite: bool) -> pl.DataFrame:
    row = {name: 1.0 for name in CONTINUOUS_FEATURES}
    if nonfinite:
        row["realized_vol_8h"] = float("nan")
        row["realized_vol_24h"] = float("inf")
    return pl.DataFrame([row])


def _loaded(*, nonfinite: bool = True) -> SimpleNamespace:
    return SimpleNamespace(
        feature_frame=_frame(nonfinite=nonfinite),
        outcome_frame=pl.DataFrame([{"x": 1}, {"x": 2}]),
        processed_manifest_sha256="1" * 64,
        feature_manifest_sha256="2" * 64,
        outcome_manifest_sha256="3" * 64,
        feature_evidence_fingerprint="4" * 64,
        outcome_evidence_fingerprint="5" * 64,
        selected_feature_artifacts=tuple(f"f-{i}" for i in range(96)),
        selected_outcome_artifacts=tuple(f"o-{i}" for i in range(96)),
    )


def _adapted() -> SimpleNamespace:
    return SimpleNamespace(
        feature_observations=(object(),),
        outcome_observations=(object(), object()),
    )


def _cell(symbol: str, timeframe: str, *, nonfinite: int = 2) -> dict[str, object]:
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
        "feature_row_count": 10,
        "outcome_row_count": 20,
        "adapted_feature_observation_count": 10,
        "adapted_outcome_observation_count": 20,
        "processed_manifest_sha256": "1" * 64,
        "feature_manifest_sha256": "2" * 64,
        "outcome_manifest_sha256": "3" * 64,
        "feature_evidence_fingerprint": "4" * 64,
        "outcome_evidence_fingerprint": "5" * 64,
        "selected_feature_partition_count": 96,
        "selected_outcome_partition_count": 96,
        "raw_nonfinite_by_feature": {
            name: nonfinite if name == "realized_vol_8h" else 0
            for name in CONTINUOUS_FEATURES
        },
        "raw_nonfinite_value_count": nonfinite,
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


class Exp062AdapterProbeTests(unittest.TestCase):
    def test_cell_probe_counts_real_nonfinite_values_and_adapts_all_rows(self) -> None:
        with (
            patch(
                "fmp.discovery.exp062_adapter_probe.load_verified_exp061_cell_from_indexes",
                return_value=_loaded(nonfinite=True),
            ),
            patch(
                "fmp.discovery.exp062_adapter_probe.adapt_market_learning_cell",
                return_value=_adapted(),
            ),
        ):
            report = probe_exp062_adapter_cell(
                feature_root=".",
                outcome_root=".",
                feature_evidence_path="feature.json",
                outcome_evidence_path="outcome.json",
                symbol="EURUSD",
                timeframe="15m",
                code_commit=HEAD,
            )

        self.assertIs(validate_exp062_adapter_probe_cell(report), report)
        self.assertEqual(report["raw_nonfinite_value_count"], 2)
        self.assertEqual(
            report["raw_nonfinite_by_feature"]["realized_vol_8h"],
            1,
        )
        self.assertEqual(
            report["raw_nonfinite_by_feature"]["realized_vol_24h"],
            1,
        )
        self.assertTrue(report["adapter_probe_success"])
        self.assertFalse(report["historical_discovery_execution_authorized"])
        self.assertFalse(report["candidate_compilation_authorized"])

    def test_cell_probe_rejects_partition_or_row_parity_drift(self) -> None:
        loaded = _loaded()
        loaded.selected_feature_artifacts = ("one",)
        with (
            patch(
                "fmp.discovery.exp062_adapter_probe.load_verified_exp061_cell_from_indexes",
                return_value=loaded,
            ),
            patch(
                "fmp.discovery.exp062_adapter_probe.adapt_market_learning_cell",
                return_value=_adapted(),
            ),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "feature partition count mismatch",
            ):
                probe_exp062_adapter_cell(
                    feature_root=".",
                    outcome_root=".",
                    feature_evidence_path="feature.json",
                    outcome_evidence_path="outcome.json",
                    symbol="EURUSD",
                    timeframe="15m",
                    code_commit=HEAD,
                )

    def test_aggregate_requires_exact_nine_unique_cells(self) -> None:
        cells = [_cell(symbol, timeframe) for symbol, timeframe in EXPECTED_CELLS]
        report = compile_exp062_adapter_probe(cells, code_commit=HEAD)
        self.assertEqual(report["cell_count"], 9)
        self.assertTrue(report["all_nine_real_data_adapter_probes_successful"])
        self.assertGreater(report["total_raw_nonfinite_value_count"], 0)
        self.assertFalse(report["historical_discovery_execution_authorized"])
        self.assertFalse(report["discovery_result_authorized"])
        self.assertFalse(report["trading_authorized"])

        duplicate = list(cells)
        duplicate[-1] = dict(duplicate[0])
        with self.assertRaisesRegex(ValueError, "cell inventory mismatch"):
            compile_exp062_adapter_probe(duplicate, code_commit=HEAD)

    def test_aggregate_requires_real_defect_case_to_be_observed(self) -> None:
        cells = [
            _cell(symbol, timeframe, nonfinite=0)
            for symbol, timeframe in EXPECTED_CELLS
        ]
        with self.assertRaisesRegex(
            ValueError,
            "must encounter the repaired nonfinite case",
        ):
            compile_exp062_adapter_probe(cells, code_commit=HEAD)

    def test_validator_rejects_any_execution_or_trading_authority(self) -> None:
        value = _cell("EURUSD", "5m")
        value["historical_discovery_execution_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_discovery_execution_authorized must remain false",
        ):
            validate_exp062_adapter_probe_cell(value)


if __name__ == "__main__":
    unittest.main()
