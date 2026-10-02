from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.annual_pattern_catalogue_evidence import (
    DIRECTIONAL_RECORDS_PER_ANNUAL_CELL,
    ValidatedAnnualCellSummary,
)
from fmp.discovery.annual_pattern_catalogue_segment_evidence import (
    EXPECTED_CELLS_PER_SEGMENT,
    EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT,
    compile_annual_segment_freeze,
    segment_freeze_contract_payload,
    validate_annual_segment_freeze,
)
from fmp.discovery.pattern_protocol import HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


_CODE_COMMIT = "a" * 40


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _refingerprint(value: dict[str, object]) -> dict[str, object]:
    out = dict(value)
    out.pop("evidence_fingerprint", None)
    out["evidence_fingerprint"] = hashlib.sha256(_canonical(out)).hexdigest()
    return out


def _summary(
    segment: str,
    symbol: str,
    timeframe: str,
    horizon: int,
    *,
    code_commit: str = _CODE_COMMIT,
) -> ValidatedAnnualCellSummary:
    base = f"{segment}:{symbol}:{timeframe}:{horizon}"
    return ValidatedAnnualCellSummary(
        annual_segment_label=segment,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon,
        code_commit=code_commit,
        evidence_fingerprint=_sha("evidence:" + base),
        catalogue_payload_sha256=_sha("catalogue:" + base),
        processed_manifest_sha256=_sha("processed:" + symbol),
        feature_manifest_sha256=_sha("feature:" + symbol + ":" + timeframe),
        outcome_manifest_sha256=_sha("outcome:" + symbol + ":" + timeframe),
        feature_evidence_fingerprint=_sha("feature-evidence"),
        outcome_evidence_fingerprint=_sha("outcome-evidence"),
        directional_record_count=DIRECTIONAL_RECORDS_PER_ANNUAL_CELL,
        evaluable_record_count=10,
        zero_support_record_count=100,
        total_support=1000,
    )


def _segment_summaries(segment: str) -> list[ValidatedAnnualCellSummary]:
    return [
        _summary(segment, symbol, timeframe, horizon)
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
        for horizon in HORIZONS_MINUTES
    ]


class AnnualPatternCatalogueSegmentEvidenceTests(unittest.TestCase):
    def test_annual_freeze_is_exact_18_cell_89460_record_bundle(self) -> None:
        summaries = _segment_summaries("2015")
        evidence = compile_annual_segment_freeze(
            summaries,
            annual_segment_label="2015",
            code_commit=_CODE_COMMIT,
        )

        self.assertEqual(EXPECTED_CELLS_PER_SEGMENT, 18)
        self.assertEqual(EXPECTED_DIRECTIONAL_RECORDS_PER_SEGMENT, 89460)
        self.assertEqual(evidence["decision"], "DEC-477")
        self.assertEqual(evidence["annual_segment_label"], "2015")
        self.assertEqual(evidence["annual_cell_count"], 18)
        self.assertEqual(evidence["directional_record_count"], 89460)
        self.assertEqual(len(evidence["cells"]), 18)
        self.assertEqual(evidence["evaluable_record_count"], 180)
        self.assertEqual(evidence["zero_support_record_count"], 1800)
        self.assertEqual(evidence["total_support"], 18000)
        self.assertIs(
            validate_annual_segment_freeze(
                evidence,
                expected_summaries=summaries,
            ),
            evidence,
        )

    def test_input_order_is_canonicalized_to_frozen_cell_order(self) -> None:
        summaries = list(reversed(_segment_summaries("2015")))
        evidence = compile_annual_segment_freeze(
            summaries,
            annual_segment_label="2015",
            code_commit=_CODE_COMMIT,
        )

        identities = [
            (
                row["symbol"],
                row["timeframe"],
                row["horizon_minutes"],
            )
            for row in evidence["cells"]
        ]
        expected = [
            (symbol, timeframe, horizon)
            for symbol in SYMBOLS
            for timeframe in TIMEFRAMES
            for horizon in HORIZONS_MINUTES
        ]
        self.assertEqual(identities, expected)

    def test_missing_or_duplicate_cell_fails_closed(self) -> None:
        summaries = _segment_summaries("2015")

        with self.assertRaisesRegex(ValueError, "requires exactly 18 cells"):
            compile_annual_segment_freeze(
                summaries[:-1],
                annual_segment_label="2015",
                code_commit=_CODE_COMMIT,
            )

        duplicate = list(summaries)
        duplicate[-1] = duplicate[0]
        with self.assertRaisesRegex(ValueError, "duplicate annual cell"):
            compile_annual_segment_freeze(
                duplicate,
                annual_segment_label="2015",
                code_commit=_CODE_COMMIT,
            )

    def test_cross_year_cell_cannot_enter_annual_freeze(self) -> None:
        summaries = _segment_summaries("2015")
        summaries[-1] = _summary("2016", "USDJPY", "1h", 240)

        with self.assertRaisesRegex(ValueError, "cell universe mismatch"):
            compile_annual_segment_freeze(
                summaries,
                annual_segment_label="2015",
                code_commit=_CODE_COMMIT,
            )

    def test_mixed_code_commit_fails_closed(self) -> None:
        summaries = _segment_summaries("2015")
        summaries[-1] = _summary(
            "2015",
            "USDJPY",
            "1h",
            240,
            code_commit="b" * 40,
        )

        with self.assertRaisesRegex(ValueError, "code commit mismatch"):
            compile_annual_segment_freeze(
                summaries,
                annual_segment_label="2015",
                code_commit=_CODE_COMMIT,
            )

    def test_refingerprinted_total_tamper_still_fails_semantic_validation(self) -> None:
        evidence = compile_annual_segment_freeze(
            _segment_summaries("2015"),
            annual_segment_label="2015",
            code_commit=_CODE_COMMIT,
        )
        tampered = dict(evidence)
        tampered["directional_record_count"] = 1
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "directional_record_count mismatch",
        ):
            validate_annual_segment_freeze(tampered)

    def test_contract_keeps_next_year_cross_year_and_strategy_locked(self) -> None:
        payload = segment_freeze_contract_payload()

        self.assertEqual(payload["decision"], "DEC-477")
        self.assertEqual(payload["source_workflow_plan_decision"], "DEC-476")
        self.assertEqual(payload["cells_per_segment"], 18)
        self.assertEqual(payload["directional_records_per_segment"], 89460)
        self.assertTrue(payload["requires_validated_dec472_cell_summaries"])
        self.assertTrue(payload["annual_freeze_required_before_next_segment"])
        self.assertTrue(payload["annual_freeze_required_before_cross_year_comparison"])
        self.assertFalse(payload["next_segment_execution_authorized"])
        self.assertFalse(payload["cross_year_result_production_authorized"])
        self.assertFalse(payload["strategy_v1_synthesis_authorized"])
        self.assertFalse(payload["trading_authorized"])
        self.assertEqual(
            payload["next_gate"],
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_SOURCE",
        )


if __name__ == "__main__":
    unittest.main()
