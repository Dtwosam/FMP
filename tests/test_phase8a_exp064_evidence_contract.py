from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp064_continuous_stability_miner import (
    ContinuousStabilityHypothesis,
    ContinuousStabilityMiningReport,
    FeatureRankCalibration,
    InMemoryContinuousStabilityResult,
)
from fmp.discovery.exp064_continuous_stability_protocol import (
    DESIGN_YEARS,
    AnnualContinuousEffectStat,
    continuous_stability_metrics,
    effect_hypothesis_fingerprint,
)
from fmp.discovery.exp064_evidence_contract import (
    EXPECTED_CELL_COUNT,
    EXPECTED_CELLS,
    compile_aggregate_evidence,
    compile_cell_evidence,
    validate_aggregate_evidence,
    validate_cell_evidence,
)
from fmp.market_learning.evidence import EXPECTED_SOURCE_MANIFEST_SHA256


_CODE_COMMIT = "a" * 40
_FEATURE_EVIDENCE = "b" * 64
_OUTCOME_EVIDENCE = "c" * 64


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _refingerprint(value: dict[str, object]) -> dict[str, object]:
    out = dict(value)
    out.pop("evidence_fingerprint", None)
    out["evidence_fingerprint"] = hashlib.sha256(_canonical(out)).hexdigest()
    return out


def _candidate(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> ContinuousStabilityHypothesis:
    annual = tuple(
        AnnualContinuousEffectStat(
            year=year,
            evaluable_support=400,
            selected_tail_support=100,
            signed_rank_slope_net_pips_0p5=1.0,
            selected_tail_mean_net_pips_0p5=1.0,
            selected_tail_mean_net_pips_1p0=0.5,
        )
        for year in DESIGN_YEARS
    )
    metrics = continuous_stability_metrics(annual)
    slope_blocks = metrics[
        "two_year_block_signed_rank_slope_net_pips_0p5"
    ]
    tail_blocks = metrics[
        "two_year_block_selected_tail_mean_net_pips_0p5"
    ]
    assert isinstance(slope_blocks, dict)
    assert isinstance(tail_blocks, dict)
    return ContinuousStabilityHypothesis(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon,
        feature_name="return_1h",
        direction="LONG",
        polarity="INCREASING",
        fingerprint=effect_hypothesis_fingerprint(
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon,
            feature_name="return_1h",
            direction="LONG",
            polarity="INCREASING",
        ),
        annual_stats=annual,
        total_selected_tail_support=int(
            metrics["total_selected_tail_support"]
        ),
        minimum_year_selected_tail_support=int(
            metrics["minimum_year_selected_tail_support"]
        ),
        positive_slope_year_count=int(
            metrics["positive_slope_year_count"]
        ),
        positive_tail_mean_year_count=int(
            metrics["positive_tail_mean_year_count"]
        ),
        equal_year_signed_rank_slope_net_pips_0p5=float(
            metrics["equal_year_signed_rank_slope_net_pips_0p5"]
        ),
        lower_half_annual_signed_rank_slope_net_pips_0p5=float(
            metrics[
                "lower_half_annual_signed_rank_slope_net_pips_0p5"
            ]
        ),
        equal_year_selected_tail_mean_net_pips_0p5=float(
            metrics["equal_year_selected_tail_mean_net_pips_0p5"]
        ),
        equal_year_selected_tail_mean_net_pips_1p0=float(
            metrics["equal_year_selected_tail_mean_net_pips_1p0"]
        ),
        lower_half_annual_selected_tail_mean_net_pips_0p5=float(
            metrics[
                "lower_half_annual_selected_tail_mean_net_pips_0p5"
            ]
        ),
        two_year_block_signed_rank_slope_net_pips_0p5=tuple(
            (name, float(value)) for name, value in slope_blocks.items()
        ),
        minimum_two_year_block_signed_rank_slope_net_pips_0p5=float(
            metrics[
                "minimum_two_year_block_signed_rank_slope_net_pips_0p5"
            ]
        ),
        two_year_block_selected_tail_mean_net_pips_0p5=tuple(
            (name, float(value)) for name, value in tail_blocks.items()
        ),
        minimum_two_year_block_selected_tail_mean_net_pips_0p5=float(
            metrics[
                "minimum_two_year_block_selected_tail_mean_net_pips_0p5"
            ]
        ),
    )


def _result(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> InMemoryContinuousStabilityResult:
    candidate = _candidate(symbol, timeframe, horizon)
    calibration = FeatureRankCalibration(
        feature_name="return_1h",
        values=tuple(float(index) for index in range(600)),
    )
    return InMemoryContinuousStabilityResult(
        calibrations=(calibration,),
        report=ContinuousStabilityMiningReport(
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon,
            active_continuous_features=("return_1h",),
            hypothesis_count=80,
            evaluable_hypothesis_count=4,
            qualifying_hypothesis_count=1,
            deduplicated_hypothesis_count=1,
            shortlist=(candidate,),
            frozen=(candidate,),
        ),
    )


def _cell_evidence(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> dict[str, object]:
    return compile_cell_evidence(
        _result(symbol, timeframe, horizon),
        code_commit=_CODE_COMMIT,
        processed_manifest_sha256=EXPECTED_SOURCE_MANIFEST_SHA256[symbol],
        feature_manifest_sha256=_sha(f"feature:{symbol}:{timeframe}"),
        outcome_manifest_sha256=_sha(f"outcome:{symbol}:{timeframe}"),
        feature_evidence_fingerprint=_FEATURE_EVIDENCE,
        outcome_evidence_fingerprint=_OUTCOME_EVIDENCE,
    )


class Exp064EvidenceContractTests(unittest.TestCase):
    def test_cell_evidence_is_deterministic_and_self_validating(self) -> None:
        first = _cell_evidence("EURUSD", "15m", 60)
        second = _cell_evidence("EURUSD", "15m", 60)

        self.assertEqual(first, second)
        self.assertEqual(len(first["evidence_fingerprint"]), 64)
        self.assertIs(validate_cell_evidence(first), first)
        self.assertEqual(
            first["continuous_stability"]["output_kind"],
            "RETROSPECTIVE_CONTINUOUS_STABILITY_HYPOTHESIS_NOT_VALIDATED",
        )
        calibration = first["rank_calibrations"][0]
        self.assertEqual(calibration["feature_name"], "return_1h")
        self.assertEqual(calibration["value_count"], 600)
        self.assertEqual(calibration["distinct_value_count"], 600)
        self.assertEqual(calibration["minimum"], 0.0)
        self.assertEqual(calibration["maximum"], 599.0)
        self.assertEqual(len(calibration["values_sha256"]), 64)
        self.assertFalse(first["reserved_robustness_opened"])

    def test_refingerprinted_metric_tamper_fails_semantic_validation(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        section = dict(value["continuous_stability"])
        shortlist = [dict(section["shortlist"][0])]
        shortlist[0]["positive_slope_year_count"] = 7
        section["shortlist"] = shortlist
        tampered = dict(value)
        tampered["continuous_stability"] = section
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "positive_slope_year_count mismatch",
        ):
            validate_cell_evidence(tampered)

    def test_refingerprinted_annual_stat_tamper_fails_gate_or_metrics(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        section = dict(value["continuous_stability"])
        shortlist = [dict(section["shortlist"][0])]
        annual = [dict(row) for row in shortlist[0]["annual_stats"]]
        annual[0]["selected_tail_mean_net_pips_0p5"] = -10.0
        shortlist[0]["annual_stats"] = annual
        section["shortlist"] = shortlist
        tampered = dict(value)
        tampered["continuous_stability"] = section
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "fails continuous-stability gate",
        ):
            validate_cell_evidence(tampered)

    def test_refingerprinted_calibration_contract_tamper_fails_closed(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        calibrations = [dict(value["rank_calibrations"][0])]
        calibrations[0]["distinct_value_count"] = 1
        tampered = dict(value)
        tampered["rank_calibrations"] = calibrations
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "distinct count outside protocol",
        ):
            validate_cell_evidence(tampered)

    def test_refingerprinted_frozen_inventory_tamper_fails_closed(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        section = dict(value["continuous_stability"])
        section["frozen_hypothesis_fingerprints"] = []
        tampered = dict(value)
        tampered["continuous_stability"] = section
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "frozen fingerprint inventory mismatch",
        ):
            validate_cell_evidence(tampered)

    def test_exact_18_cell_aggregate_compiles_and_validates(self) -> None:
        cells = [
            _cell_evidence(symbol, timeframe, horizon)
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ]
        aggregate = compile_aggregate_evidence(
            cells,
            code_commit=_CODE_COMMIT,
        )

        self.assertEqual(EXPECTED_CELL_COUNT, 18)
        self.assertEqual(aggregate["verified_cell_count"], 18)
        self.assertEqual(
            aggregate["continuous_stability_shortlist_count"],
            18,
        )
        self.assertEqual(
            aggregate["continuous_stability_frozen_count"],
            18,
        )
        self.assertEqual(
            [
                (
                    row["symbol"],
                    row["timeframe"],
                    row["horizon_minutes"],
                )
                for row in aggregate["cells"]
            ],
            list(sorted(EXPECTED_CELLS)),
        )
        self.assertIs(validate_aggregate_evidence(aggregate), aggregate)
        self.assertFalse(aggregate["historical_execution_authorized"])
        self.assertFalse(aggregate["reserved_robustness_access_authorized"])
        self.assertFalse(aggregate["candidate_compilation_authorized"])
        self.assertFalse(aggregate["phase8b_authorized"])
        self.assertFalse(aggregate["trading_authorized"])

    def test_aggregate_requires_exact_cell_inventory(self) -> None:
        cells = [
            _cell_evidence(symbol, timeframe, horizon)
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ]

        with self.assertRaisesRegex(
            ValueError,
            "requires exactly 18 cells",
        ):
            compile_aggregate_evidence(
                cells[:-1],
                code_commit=_CODE_COMMIT,
            )

        duplicated = list(cells)
        duplicated[-1] = cells[0]
        with self.assertRaisesRegex(ValueError, "duplicate cell"):
            compile_aggregate_evidence(
                duplicated,
                code_commit=_CODE_COMMIT,
            )

    def test_cross_horizon_manifest_drift_fails_closed(self) -> None:
        cells = [
            _cell_evidence(symbol, timeframe, horizon)
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ]
        index = EXPECTED_CELLS.index(("EURUSD", "15m", 240))
        changed = dict(cells[index])
        changed["feature_manifest_sha256"] = "d" * 64
        cells[index] = _refingerprint(changed)

        with self.assertRaisesRegex(
            ValueError,
            "manifest identity differs across horizons",
        ):
            compile_aggregate_evidence(
                cells,
                code_commit=_CODE_COMMIT,
            )

    def test_refingerprinted_authority_tamper_fails_closed(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        tampered = dict(value)
        tampered["candidate_compilation_authorized"] = True
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "candidate_compilation_authorized must remain false",
        ):
            validate_cell_evidence(tampered)


if __name__ == "__main__":
    unittest.main()
