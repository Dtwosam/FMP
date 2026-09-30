from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp063_evidence_contract import (
    EXPECTED_CELL_COUNT,
    EXPECTED_CELLS,
    compile_aggregate_evidence,
    compile_cell_evidence,
    validate_aggregate_evidence,
    validate_cell_evidence,
)
from fmp.discovery.exp063_persistence_miner import (
    InMemoryPersistenceResult,
    PersistenceMiningReport,
    PersistencePatternHypothesis,
)
from fmp.discovery.exp063_persistence_protocol import (
    DESIGN_YEARS,
    AnnualPersistenceStat,
    pattern_fingerprint,
    persistence_metrics,
)
from fmp.discovery.pattern_miner import StateModel
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
) -> PersistencePatternHypothesis:
    annual = tuple(
        AnnualPersistenceStat(
            year=year,
            support=100,
            total_net_pips_0p5=100.0,
            total_net_pips_1p0=40.0,
        )
        for year in DESIGN_YEARS
    )
    metrics = persistence_metrics(annual)
    blocks = metrics["two_year_block_mean_net_pips_0p5"]
    assert isinstance(blocks, dict)
    predicates = (("return_1h", "HIGH"),)
    return PersistencePatternHypothesis(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon,
        direction="LONG",
        predicates=predicates,
        fingerprint=pattern_fingerprint(
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon,
            direction="LONG",
            predicates=predicates,
        ),
        annual_stats=annual,
        total_support=int(metrics["total_support"]),
        minimum_year_support=int(metrics["minimum_year_support"]),
        aggregate_mean_net_pips_0p5=float(
            metrics["aggregate_mean_net_pips_0p5"]
        ),
        aggregate_mean_net_pips_1p0=float(
            metrics["aggregate_mean_net_pips_1p0"]
        ),
        positive_year_count=int(metrics["positive_year_count"]),
        worst_annual_mean_net_pips_0p5=float(
            metrics["worst_annual_mean_net_pips_0p5"]
        ),
        lower_half_annual_mean_net_pips_0p5=float(
            metrics["lower_half_annual_mean_net_pips_0p5"]
        ),
        two_year_block_mean_net_pips_0p5=tuple(
            (name, float(value)) for name, value in blocks.items()
        ),
        minimum_two_year_block_mean_net_pips_0p5=float(
            metrics["minimum_two_year_block_mean_net_pips_0p5"]
        ),
    )


def _result(
    symbol: str,
    timeframe: str,
    horizon: int,
) -> InMemoryPersistenceResult:
    candidate = _candidate(symbol, timeframe, horizon)
    return InMemoryPersistenceResult(
        state_model=StateModel(
            symbol=symbol,
            timeframe=timeframe,
            cutpoints=(("return_1h", 99.0, 199.0),),
        ),
        report=PersistenceMiningReport(
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon,
            active_continuous_features=("return_1h",),
            enumerated_pattern_count=23,
            directional_hypothesis_count=46,
            qualifying_directional_hypothesis_count=1,
            deduplicated_directional_hypothesis_count=1,
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


class Exp063EvidenceContractTests(unittest.TestCase):
    def test_cell_evidence_is_deterministic_and_self_validating(self) -> None:
        first = _cell_evidence("EURUSD", "15m", 60)
        second = _cell_evidence("EURUSD", "15m", 60)

        self.assertEqual(first, second)
        self.assertEqual(len(first["evidence_fingerprint"]), 64)
        self.assertIs(validate_cell_evidence(first), first)
        self.assertEqual(
            first["persistence"]["output_kind"],
            "RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED",
        )
        self.assertFalse(first["reserved_robustness_opened"])

    def test_refingerprinted_metric_tamper_fails_semantic_validation(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        persistence = dict(value["persistence"])
        shortlist = [dict(persistence["shortlist"][0])]
        shortlist[0]["positive_year_count"] = 7
        persistence["shortlist"] = shortlist
        tampered = dict(value)
        tampered["persistence"] = persistence
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "positive_year_count mismatch",
        ):
            validate_cell_evidence(tampered)

    def test_refingerprinted_frozen_inventory_tamper_fails_closed(self) -> None:
        value = _cell_evidence("EURUSD", "15m", 60)
        persistence = dict(value["persistence"])
        persistence["frozen_pattern_fingerprints"] = []
        tampered = dict(value)
        tampered["persistence"] = persistence
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
        self.assertEqual(aggregate["persistence_shortlist_count"], 18)
        self.assertEqual(aggregate["persistence_frozen_count"], 18)
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
