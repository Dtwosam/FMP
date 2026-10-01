from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp065_evidence_contract import (
    EXPECTED_CELL_COUNT,
    EXPECTED_CELLS,
    compile_aggregate_evidence,
    compile_cell_evidence,
    validate_aggregate_evidence,
    validate_cell_evidence,
)
from fmp.discovery.exp065_pairwise_interaction_miner import (
    FeatureRankCalibration,
    InMemoryPairwiseInteractionResult,
    PairInteractionCalibration,
    PairwiseInteractionHypothesis,
    PairwiseInteractionMiningReport,
)
from fmp.discovery.exp065_pairwise_interaction_protocol import (
    DESIGN_YEARS,
    AnnualPairwiseInteractionStat,
    pair_hypothesis_fingerprint,
    pairwise_interaction_metrics,
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
) -> PairwiseInteractionHypothesis:
    annual = tuple(
        AnnualPairwiseInteractionStat(
            year=year,
            evaluable_support=400,
            selected_tail_support=100,
            signed_partial_interaction_slope_net_pips_0p5=0.5,
            selected_tail_mean_net_pips_0p5=0.6,
            selected_tail_incremental_residual_mean_net_pips_0p5=0.2,
            selected_tail_mean_net_pips_1p0=0.1,
        )
        for year in DESIGN_YEARS
    )
    metrics = pairwise_interaction_metrics(annual)
    partial_blocks = metrics[
        "two_year_block_signed_partial_slope_net_pips_0p5"
    ]
    raw_blocks = metrics["two_year_block_raw_tail_mean_net_pips_0p5"]
    incremental_blocks = metrics[
        "two_year_block_incremental_tail_mean_net_pips_0p5"
    ]
    assert isinstance(partial_blocks, dict)
    assert isinstance(raw_blocks, dict)
    assert isinstance(incremental_blocks, dict)

    feature_a = "return_1h"
    feature_b = "return_24h"
    direction = "LONG"
    polarity = "INCREASING"
    return PairwiseInteractionHypothesis(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon,
        feature_a=feature_a,
        feature_b=feature_b,
        direction=direction,
        polarity=polarity,
        fingerprint=pair_hypothesis_fingerprint(
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon,
            feature_a=feature_a,
            feature_b=feature_b,
            direction=direction,
            polarity=polarity,
        ),
        annual_stats=annual,
        total_selected_tail_support=int(
            metrics["total_selected_tail_support"]
        ),
        minimum_year_selected_tail_support=int(
            metrics["minimum_year_selected_tail_support"]
        ),
        positive_partial_slope_year_count=int(
            metrics["positive_partial_slope_year_count"]
        ),
        positive_raw_tail_mean_year_count=int(
            metrics["positive_raw_tail_mean_year_count"]
        ),
        positive_incremental_tail_mean_year_count=int(
            metrics["positive_incremental_tail_mean_year_count"]
        ),
        equal_year_signed_partial_slope_net_pips_0p5=float(
            metrics["equal_year_signed_partial_slope_net_pips_0p5"]
        ),
        equal_year_raw_tail_mean_net_pips_0p5=float(
            metrics["equal_year_raw_tail_mean_net_pips_0p5"]
        ),
        equal_year_incremental_tail_mean_net_pips_0p5=float(
            metrics["equal_year_incremental_tail_mean_net_pips_0p5"]
        ),
        equal_year_raw_tail_mean_net_pips_1p0=float(
            metrics["equal_year_raw_tail_mean_net_pips_1p0"]
        ),
        lower_half_signed_partial_slope_net_pips_0p5=float(
            metrics["lower_half_signed_partial_slope_net_pips_0p5"]
        ),
        lower_half_raw_tail_mean_net_pips_0p5=float(
            metrics["lower_half_raw_tail_mean_net_pips_0p5"]
        ),
        lower_half_incremental_tail_mean_net_pips_0p5=float(
            metrics["lower_half_incremental_tail_mean_net_pips_0p5"]
        ),
        two_year_block_signed_partial_slope_net_pips_0p5=tuple(
            (name, float(value)) for name, value in partial_blocks.items()
        ),
        minimum_two_year_block_signed_partial_slope_net_pips_0p5=float(
            metrics[
                "minimum_two_year_block_signed_partial_slope_net_pips_0p5"
            ]
        ),
        two_year_block_raw_tail_mean_net_pips_0p5=tuple(
            (name, float(value)) for name, value in raw_blocks.items()
        ),
        minimum_two_year_block_raw_tail_mean_net_pips_0p5=float(
            metrics["minimum_two_year_block_raw_tail_mean_net_pips_0p5"]
        ),
        two_year_block_incremental_tail_mean_net_pips_0p5=tuple(
            (name, float(value)) for name, value in incremental_blocks.items()
        ),
        minimum_two_year_block_incremental_tail_mean_net_pips_0p5=float(
            metrics[
                "minimum_two_year_block_incremental_tail_mean_net_pips_0p5"
            ]
        ),
    )


def _result(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> InMemoryPairwiseInteractionResult:
    candidate = _candidate(symbol, timeframe, horizon)
    feature_a = FeatureRankCalibration(
        feature_name="return_1h",
        values=tuple(float(index) for index in range(600)),
    )
    feature_b = FeatureRankCalibration(
        feature_name="return_24h",
        values=tuple(float(index * 2) for index in range(600)),
    )
    pair = PairInteractionCalibration(
        feature_a="return_1h",
        feature_b="return_24h",
        values=tuple((index - 300) / 600.0 for index in range(600)),
    )
    return InMemoryPairwiseInteractionResult(
        feature_calibrations=(feature_a, feature_b),
        pair_calibrations=(pair,),
        report=PairwiseInteractionMiningReport(
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon,
            active_continuous_features=("return_1h", "return_24h"),
            active_feature_pairs=(("return_1h", "return_24h"),),
            hypothesis_count=760,
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


class Exp065EvidenceContractTests(unittest.TestCase):
    def test_cell_evidence_is_deterministic_and_self_validating(self) -> None:
        first = _cell_evidence("EURUSD", "15m", 60)
        second = _cell_evidence("EURUSD", "15m", 60)

        self.assertEqual(first, second)
        self.assertEqual(len(first["evidence_fingerprint"]), 64)
        self.assertIs(validate_cell_evidence(first), first)
        section = first["pairwise_interaction"]
        self.assertEqual(section["hypothesis_count"], 760)
        self.assertEqual(section["evaluable_hypothesis_count"], 4)
        self.assertEqual(
            section["output_kind"],
            "RETROSPECTIVE_PAIRWISE_INTERACTION_HYPOTHESIS_NOT_VALIDATED",
        )
        self.assertEqual(
            section["active_feature_pairs"],
            [["return_1h", "return_24h"]],
        )
        self.assertEqual(
            len(first["pair_interaction_calibrations"]),
            1,
        )
        self.assertFalse(first["reserved_robustness_opened"])

    def test_refingerprinted_nominal_search_shrinkage_fails_closed(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        section = dict(value["pairwise_interaction"])
        section["hypothesis_count"] = 4
        tampered = dict(value)
        tampered["pairwise_interaction"] = section
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "nominal hypothesis count mismatch",
        ):
            validate_cell_evidence(tampered)

    def test_refingerprinted_incremental_metric_tamper_fails_semantics(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        section = dict(value["pairwise_interaction"])
        shortlist = [dict(section["shortlist"][0])]
        shortlist[0]["positive_incremental_tail_mean_year_count"] = 7
        section["shortlist"] = shortlist
        tampered = dict(value)
        tampered["pairwise_interaction"] = section
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "positive_incremental_tail_mean_year_count mismatch",
        ):
            validate_cell_evidence(tampered)

    def test_refingerprinted_annual_incrementality_tamper_fails_gate(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        section = dict(value["pairwise_interaction"])
        shortlist = [dict(section["shortlist"][0])]
        annual = [dict(row) for row in shortlist[0]["annual_stats"]]
        annual[0][
            "selected_tail_incremental_residual_mean_net_pips_0p5"
        ] = -10.0
        shortlist[0]["annual_stats"] = annual
        section["shortlist"] = shortlist
        tampered = dict(value)
        tampered["pairwise_interaction"] = section
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "fails pairwise-interaction gate",
        ):
            validate_cell_evidence(tampered)

    def test_refingerprinted_pair_calibration_weakening_fails_closed(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        calibrations = [
            dict(value["pair_interaction_calibrations"][0])
        ]
        calibrations[0]["distinct_value_count"] = 1
        tampered = dict(value)
        tampered["pair_interaction_calibrations"] = calibrations
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "pair calibration distinct count outside protocol",
        ):
            validate_cell_evidence(tampered)

    def test_refingerprinted_frozen_inventory_tamper_fails_closed(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        section = dict(value["pairwise_interaction"])
        section["frozen_hypothesis_fingerprints"] = []
        tampered = dict(value)
        tampered["pairwise_interaction"] = section
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
            aggregate["pairwise_interaction_shortlist_count"],
            18,
        )
        self.assertEqual(
            aggregate["pairwise_interaction_frozen_count"],
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

    def test_refingerprinted_aggregate_evaluable_count_tamper_fails_closed(
        self,
    ) -> None:
        cells = [
            _cell_evidence(symbol, timeframe, horizon)
            for symbol, timeframe, horizon in EXPECTED_CELLS
        ]
        aggregate = compile_aggregate_evidence(
            cells,
            code_commit=_CODE_COMMIT,
        )
        rows = [dict(row) for row in aggregate["cells"]]
        rows[0]["evaluable_hypothesis_count"] = 5
        tampered = dict(aggregate)
        tampered["cells"] = rows
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "evaluable count exceeds active pair search",
        ):
            validate_aggregate_evidence(tampered)

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
