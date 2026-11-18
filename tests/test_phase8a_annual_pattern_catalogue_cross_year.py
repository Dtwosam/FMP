from __future__ import annotations

import random
import time
import unittest
from pathlib import Path

from fmp.discovery.annual_pattern_catalogue_cross_year import (
    GATE_INOPERABLE_LT_9_SEGMENTS,
    AnnualSegmentProvenance,
    ValidatedAnnualPatternSubmission,
    build_synthetic_cross_year_report,
    canonical_cross_year_json,
    synthetic_cross_year_records,
    compare_cross_year_patterns,
    cross_year_report_sha256,
    render_cross_year_summary,
    run_synthetic_null_calibration,
    submissions_for_records,
    synthetic_annual_record,
    synthetic_segment_provenance,
)
from fmp.discovery.annual_pattern_catalogue_method import collection_segments
from fmp.discovery.annual_pattern_catalogue_miner import AnnualPatternRecord
from fmp.discovery.annual_pattern_catalogue_protocol import (
    ANNUAL_CATALOGUE_PROTOCOL_VERSION,
    DISCOVERY_SLIPPAGE_PIPS,
    MAX_CROSS_YEAR_SHORTLIST_GLOBAL,
    MAX_CROSS_YEAR_SHORTLIST_PER_CELL_FAMILY,
    MIN_ANNUAL_EVALUABLE_SUPPORT,
    STRESS_SLIPPAGE_PIPS,
    PatternDefinition,
    cross_year_gate_passes,
    enumerate_pattern_definitions,
    protocol_fingerprint,
    protocol_payload,
)
from fmp.discovery.pattern_protocol import DIRECTIONS, HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


def _labels() -> list[str]:
    return [segment.label for segment in collection_segments()]


def _pattern(index: int) -> PatternDefinition:
    return enumerate_pattern_definitions()[index]


def _record(
    index: int,
    label: str,
    *,
    support: int,
    base: float | None,
    stress: float | None,
    symbol: str = "EURUSD",
    timeframe: str = "5m",
    horizon_minutes: int = 60,
    direction: str = "LONG",
) -> AnnualPatternRecord:
    return synthetic_annual_record(
        pattern=_pattern(index),
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        direction=direction,
        annual_segment_label=label,
        support=support,
        mean_net_pips_0p5=base,
        mean_net_pips_1p0=stress,
    )


class AnnualPatternCatalogueCrossYearTests(unittest.TestCase):
    def test_synthetic_report_preserves_identity_and_hand_calculations(self) -> None:
        report = build_synthetic_cross_year_report()
        self.assertEqual(report["pattern_count"], 7)
        self.assertEqual(report["identical_source_commit_required"], False)
        self.assertGreater(report["distinct_source_commit_count"], 1)
        self.assertFalse(report["historical_market_artifacts_read"])
        self.assertFalse(report["strategy_v1_synthesized"])
        self.assertEqual(report["patterns_removed_as_near_duplicates"], 0)
        self.assertEqual(report["near_duplicate"]["status"], "UNAVAILABLE")
        self.assertIsNone(report["near_duplicate"]["substitute"])
        self.assertEqual(
            report["statistical_evidence"]["p_values"],
            "UNAVAILABLE_NOT_COMPUTED",
        )
        self.assertFalse(
            report["statistical_evidence"]["statistical_significance_claimed"]
        )
        self.assertFalse(report["cost_model"]["spread_double_charged"])
        self.assertEqual(report["cost_model"]["additional_spread_pips"], 0.0)
        self.assertEqual(
            report["cost_model"]["base_slippage_pips_per_fill"],
            DISCOVERY_SLIPPAGE_PIPS,
        )
        self.assertEqual(
            report["cost_model"]["stress_slippage_pips_per_fill"],
            STRESS_SLIPPAGE_PIPS,
        )
        self.assertEqual(
            report["rank_fields_applied"],
            list(protocol_payload()["cross_year_comparison"]["rank_fields"]),
        )

        by_fingerprint = {
            row["canonical_pattern_fingerprint"]: row for row in report["patterns"]
        }
        definitions = enumerate_pattern_definitions()
        passer = by_fingerprint[
            _record(0, "2015", support=100, base=0.5, stress=0.25).canonical_pattern_fingerprint
        ]
        self.assertEqual(passer["canonical_pattern_fingerprint"], _fingerprint(0))
        self.assertEqual(passer["summary"]["evaluable_segments"], 9)
        self.assertEqual(passer["summary"]["pooled_mean_net_pips_0p5"], 0.5)
        self.assertEqual(passer["summary"]["pooled_mean_net_pips_1p0"], 0.25)
        self.assertEqual(passer["summary"]["median_annual_mean_net_pips_0p5"], 0.5)
        self.assertEqual(
            passer["summary"]["worst_evaluable_annual_mean_net_pips_0p5"],
            0.5,
        )
        self.assertEqual(passer["summary"]["sign_flips"], 0)
        self.assertEqual(passer["summary"]["gate_status"], "PASS")
        self.assertTrue(passer["summary"]["gate_passes"])
        self.assertFalse(passer["summary"]["gate_pass_is_statistical_significance"])
        self.assertEqual(passer["summary"]["shortlist_status"], "SHORTLISTED")
        self.assertEqual(passer["summary"]["support_concentration_max_year_share"], 1.0 / 9.0)
        self.assertEqual(passer["summary"]["support_hhi"], 1.0 / 9.0)
        self.assertEqual(passer["panel"][0]["annual_record_id"], _record(0, "2015", support=100, base=0.5, stress=0.25).annual_record_id)
        self.assertNotEqual(
            passer["panel"][0]["code_commit"],
            passer["panel"][1]["code_commit"],
        )

        eight = by_fingerprint[_fingerprint(1)]
        self.assertEqual(eight["summary"]["evaluable_segments"], 8)
        self.assertEqual(eight["summary"]["gate_status"], GATE_INOPERABLE_LT_9_SEGMENTS)
        self.assertFalse(eight["summary"]["gate_passes"])
        self.assertEqual(eight["summary"]["pooled_mean_net_pips_0p5"], 0.5)
        self.assertEqual(eight["panel"][8]["evidence_status"], "MISSING_RECORD")

        negative = by_fingerprint[_fingerprint(2)]
        self.assertEqual(negative["summary"]["effect_label"], "NEGATIVE")
        self.assertEqual(negative["summary"]["gate_status"], "FAIL")
        self.assertEqual(negative["summary"]["pooled_mean_net_pips_0p5"], -0.5)
        self.assertEqual(negative["summary"]["base_positive_segments"], 0)
        self.assertIn(negative["canonical_pattern_fingerprint"], [
            row["canonical_pattern_fingerprint"] for row in report["patterns"]
        ])

        flips = by_fingerprint[_fingerprint(3)]
        self.assertEqual(
            flips["summary"]["sign_sequence"],
            [
                "POSITIVE",
                "POSITIVE",
                "NON_POSITIVE",
                "POSITIVE",
                "POSITIVE",
                "POSITIVE",
                "POSITIVE",
                "NON_POSITIVE",
                "POSITIVE",
                "POSITIVE",
                "POSITIVE",
                "POSITIVE",
            ],
        )
        self.assertEqual(flips["summary"]["sign_flips"], 4)
        self.assertEqual(flips["summary"]["failure_years"], ["2017", "2022"])
        self.assertAlmostEqual(flips["summary"]["pooled_mean_net_pips_0p5"], 0.375)
        self.assertAlmostEqual(flips["summary"]["pooled_mean_net_pips_1p0"], 0.1875)
        self.assertEqual(flips["summary"]["median_annual_mean_net_pips_0p5"], 0.5)
        self.assertEqual(
            flips["summary"]["worst_evaluable_annual_mean_net_pips_0p5"],
            -0.25,
        )
        self.assertEqual(flips["summary"]["base_positive_segments"], 10)
        self.assertFalse(flips["summary"]["gate_passes"])
        self.assertEqual(flips["summary"]["gate_status"], "FAIL")
        relaxed = dict(flips["summary"]["gate_inputs"])
        relaxed["sign_flips"] = 3
        self.assertTrue(cross_year_gate_passes(**relaxed))
        self.assertFalse(cross_year_gate_passes(**flips["summary"]["gate_inputs"]))

        low = by_fingerprint[_fingerprint(4)]
        self.assertEqual(low["summary"]["evaluable_segments"], 0)
        self.assertEqual(low["summary"]["total_support"], 40 * 12)
        self.assertEqual(low["summary"]["total_evaluable_support"], 0)
        self.assertIsNone(low["summary"]["pooled_mean_net_pips_0p5"])
        self.assertEqual(low["summary"]["gate_status"], GATE_INOPERABLE_LT_9_SEGMENTS)
        self.assertEqual(low["panel"][0]["evidence_status"], "INSUFFICIENT_SUPPORT")
        self.assertLess(low["panel"][0]["support"], MIN_ANNUAL_EVALUABLE_SUPPORT)

        uneven = by_fingerprint[_fingerprint(5)]
        self.assertAlmostEqual(uneven["summary"]["pooled_mean_net_pips_0p5"], 7.0 / 3.0)
        self.assertAlmostEqual(uneven["summary"]["pooled_mean_net_pips_1p0"], 4.0 / 3.0)
        self.assertEqual(uneven["summary"]["median_annual_mean_net_pips_0p5"], 2.0)
        self.assertEqual(
            uneven["summary"]["worst_evaluable_annual_segment"],
            "2015",
        )
        self.assertEqual(uneven["summary"]["support_concentration_max_year_share"], 0.5)
        self.assertEqual(uneven["summary"]["support_concentration_max_year"], "2017")
        self.assertAlmostEqual(uneven["summary"]["support_hhi"], 7.0 / 18.0)
        self.assertAlmostEqual(
            uneven["summary"]["absolute_effect_concentration_max_year_share"],
            9.0 / 14.0,
        )
        self.assertEqual(uneven["summary"]["gate_status"], GATE_INOPERABLE_LT_9_SEGMENTS)

        absent = by_fingerprint[_fingerprint(6)]
        self.assertEqual(absent["panel"][0]["evidence_status"], "ZERO_SUPPORT")
        self.assertEqual(absent["panel"][1]["evidence_status"], "MISSING_RECORD")
        self.assertEqual(absent["summary"]["effect_label"], "NOT_EVALUABLE")
        self.assertEqual(report["preserved_non_passing_count"], 6)
        self.assertEqual(report["negative_effect_count"], 1)
        self.assertEqual(report["shortlist"], [passer["canonical_pattern_fingerprint"]])
        self.assertEqual(definitions[0].family, passer["family"])

    def test_gate_inputs_match_the_frozen_function_for_every_pattern(self) -> None:
        report = build_synthetic_cross_year_report()
        for pattern in report["patterns"]:
            inputs = pattern["summary"]["gate_inputs"]
            self.assertEqual(
                pattern["summary"]["gate_passes"],
                cross_year_gate_passes(**inputs),
            )

    def test_eight_segments_are_inoperable_and_do_not_relax_the_gate(self) -> None:
        labels = _labels()[:8]
        records = [
            _record(0, label, support=200, base=2.0, stress=1.0) for label in labels
        ]
        report = compare_cross_year_patterns(submissions_for_records(records))
        pattern = report["patterns"][0]
        self.assertEqual(pattern["summary"]["evaluable_segments"], 8)
        self.assertEqual(pattern["summary"]["gate_status"], GATE_INOPERABLE_LT_9_SEGMENTS)
        self.assertFalse(pattern["summary"]["gate_passes"])
        self.assertFalse(
            cross_year_gate_passes(**pattern["summary"]["gate_inputs"])
        )
        self.assertEqual(pattern["summary"]["segment_not_supplied"], 4)
        self.assertIn(GATE_INOPERABLE_LT_9_SEGMENTS, render_cross_year_summary(report))
        self.assertEqual(report["gate"]["minimum_evaluable_segments"], 9)
        self.assertFalse(report["gate"]["thresholds_modified"])

    def test_low_support_years_do_not_enter_the_pooled_mean(self) -> None:
        labels = _labels()
        records = [
            _record(0, label, support=100, base=0.5, stress=0.25)
            for label in labels[:9]
        ]
        records.append(_record(0, labels[9], support=74, base=100.0, stress=99.0))
        report = compare_cross_year_patterns(submissions_for_records(records))
        summary = report["patterns"][0]["summary"]
        self.assertEqual(summary["evaluable_segments"], 9)
        self.assertEqual(summary["pooled_mean_net_pips_0p5"], 0.5)
        self.assertEqual(summary["base_positive_segments"], 9)
        self.assertEqual(summary["total_evaluable_support"], 900)
        self.assertEqual(summary["total_support"], 974)
        self.assertEqual(summary["sign_flips"], 0)
        self.assertTrue(summary["gate_passes"])

    def test_duplicate_record_and_duplicate_segment_are_rejected(self) -> None:
        record = _record(0, "2015", support=100, base=0.5, stress=0.25)
        with self.assertRaisesRegex(ValueError, "duplicate annual pattern record"):
            compare_cross_year_patterns(
                submissions_for_records([record, record])
            )
        submission = submissions_for_records([record])[0]
        with self.assertRaisesRegex(ValueError, "duplicate annual segment"):
            compare_cross_year_patterns([submission, submission])

    def test_tampered_fingerprint_and_incompatible_protocol_fail(self) -> None:
        record = _record(0, "2015", support=100, base=0.5, stress=0.25)
        tampered = AnnualPatternRecord(
            annual_record_id=record.annual_record_id,
            canonical_pattern_fingerprint="ab" * 32,
            annual_segment_label=record.annual_segment_label,
            symbol=record.symbol,
            timeframe=record.timeframe,
            horizon_minutes=record.horizon_minutes,
            direction=record.direction,
            family=record.family,
            dimensions=record.dimensions,
            states=record.states,
            lag_minutes=record.lag_minutes,
            event_fingerprint=record.event_fingerprint,
            statistics=record.statistics,
        )
        with self.assertRaisesRegex(ValueError, "canonical pattern fingerprint mismatch"):
            compare_cross_year_patterns(submissions_for_records([tampered]))

        bad = AnnualSegmentProvenance(
            annual_segment_label="2015",
            protocol_version=ANNUAL_CATALOGUE_PROTOCOL_VERSION,
            protocol_fingerprint="cd" * 32,
            code_commit="a" * 40,
            evidence_fingerprint="ef" * 32,
        )
        with self.assertRaisesRegex(ValueError, "incompatible annual catalogue protocol"):
            compare_cross_year_patterns(
                [
                    ValidatedAnnualPatternSubmission(
                        provenance=bad,
                        records=(record,),
                    )
                ]
            )

    def test_different_source_commits_are_accepted(self) -> None:
        labels = _labels()[:2]
        records = [
            _record(0, label, support=80, base=0.2, stress=0.05) for label in labels
        ]
        report = compare_cross_year_patterns(
            submissions_for_records(
                records,
                code_commit_for_segment={
                    labels[0]: "1" * 40,
                    labels[1]: "2" * 40,
                },
            )
        )
        panel = report["patterns"][0]["panel"]
        self.assertEqual(panel[0]["code_commit"], "1" * 40)
        self.assertEqual(panel[1]["code_commit"], "2" * 40)
        self.assertEqual(report["distinct_source_commit_count"], 2)
        self.assertFalse(report["identical_source_commit_required"])

    def test_ranking_is_deterministic_and_caps_each_cell_family(self) -> None:
        labels = _labels()[:9]
        records = []
        singles = [
            pattern
            for pattern in enumerate_pattern_definitions()
            if pattern.family == "SNAPSHOT_SINGLE"
        ][:6]
        pair = next(
            pattern
            for pattern in enumerate_pattern_definitions()
            if pattern.family == "SNAPSHOT_PAIR"
        )
        chosen = list(singles) + [pair]
        for pattern in chosen:
            for label in labels:
                records.append(
                    synthetic_annual_record(
                        pattern=pattern,
                        symbol="EURUSD",
                        timeframe="5m",
                        horizon_minutes=60,
                        direction="LONG",
                        annual_segment_label=label,
                        support=100,
                        mean_net_pips_0p5=0.5,
                        mean_net_pips_1p0=0.25,
                    )
                )
        report = compare_cross_year_patterns(submissions_for_records(records))
        self.assertEqual(report["gate_pass_count"], 7)
        single_rows = [
            row for row in report["patterns"] if row["family"] == "SNAPSHOT_SINGLE"
        ]
        single_rows.sort(key=lambda row: row["canonical_pattern_fingerprint"])
        shortlisted = [
            row["canonical_pattern_fingerprint"]
            for row in single_rows
            if row["summary"]["shortlist_status"] == "SHORTLISTED"
        ]
        capped = [
            row["canonical_pattern_fingerprint"]
            for row in single_rows
            if row["summary"]["shortlist_status"] == "CAPPED"
        ]
        self.assertEqual(shortlisted, [row["canonical_pattern_fingerprint"] for row in single_rows[:5]])
        self.assertEqual(capped, [single_rows[-1]["canonical_pattern_fingerprint"]])
        pair_row = next(row for row in report["patterns"] if row["family"] == "SNAPSHOT_PAIR")
        self.assertEqual(pair_row["summary"]["shortlist_status"], "SHORTLISTED")
        self.assertLessEqual(report["shortlist_count"], MAX_CROSS_YEAR_SHORTLIST_GLOBAL)
        self.assertEqual(
            report["shortlist_limits"]["per_cell_family"],
            MAX_CROSS_YEAR_SHORTLIST_PER_CELL_FAMILY,
        )
        self.assertEqual(report["shortlist"], sorted(report["shortlist"]))

    def test_higher_pooled_mean_ranks_ahead_when_earlier_keys_tie(self) -> None:
        labels = _labels()[:9]
        low = []
        high = []
        for index, label in enumerate(labels):
            low_base = 1.0 if index == 8 else 0.4
            high_base = 0.4
            low.append(_record(0, label, support=100, base=low_base, stress=0.2))
            high.append(_record(1, label, support=100, base=high_base, stress=0.2))
        # Give the second pattern one larger year while keeping the worst year
        # and the median tied with the first.
        high[-1] = _record(1, labels[8], support=100, base=1.5, stress=0.2)
        low[-1] = _record(0, labels[8], support=100, base=1.0, stress=0.2)
        report = compare_cross_year_patterns(submissions_for_records(low + high))
        self.assertEqual(report["shortlist"][0], _fingerprint(1))
        self.assertEqual(report["shortlist"][1], _fingerprint(0))

    def test_shuffled_inputs_and_repeated_runs_share_one_hash(self) -> None:
        report = build_synthetic_cross_year_report()
        again = build_synthetic_cross_year_report()
        self.assertEqual(canonical_cross_year_json(report), canonical_cross_year_json(again))
        self.assertEqual(cross_year_report_sha256(report), cross_year_report_sha256(again))

        records = list(synthetic_cross_year_records())
        shuffled = list(records)
        random.Random(7).shuffle(shuffled)
        grouped = {}
        for record in shuffled:
            grouped.setdefault(record.annual_segment_label, []).append(record)
        submissions = []
        for label in _labels():
            rows = grouped.get(label)
            if not rows:
                continue
            random.Random(3).shuffle(rows)
            submissions.append(
                ValidatedAnnualPatternSubmission(
                    provenance=synthetic_segment_provenance(
                        label,
                        code_commit=format(_labels().index(label) + 1, "040x"),
                    ),
                    records=tuple(rows),
                )
            )
        random.Random(5).shuffle(submissions)
        shuffled_report = compare_cross_year_patterns(submissions)
        self.assertEqual(
            cross_year_report_sha256(report),
            cross_year_report_sha256(shuffled_report),
        )

    def test_summary_states_the_unavailable_evidence(self) -> None:
        text = render_cross_year_summary(build_synthetic_cross_year_report())
        self.assertIn("UNAVAILABLE", text)
        self.assertIn("not a claim of statistical significance", text)
        self.assertIn("Spread double-charged: False", text)
        self.assertIn(GATE_INOPERABLE_LT_9_SEGMENTS, text)
        self.assertIn("Historical market artifacts read: False", text)

    def test_null_calibration_does_not_tune_or_claim_significance(self) -> None:
        report = run_synthetic_null_calibration()
        repeat = run_synthetic_null_calibration()
        self.assertEqual(report, repeat)
        self.assertFalse(report["gate_thresholds_modified_after_simulation"])
        self.assertFalse(report["statistical_significance_claimed"])
        self.assertFalse(report["market_artifacts_read"])
        self.assertEqual(report["gate_constants"]["minimum_evaluable_segments"], 9)
        self.assertEqual(
            report["cost_assumptions"]["spread_round_trip_pips"],
            0.8,
        )
        self.assertTrue(report["cost_assumptions"]["spread_charged_once"])
        self.assertFalse(report["cost_assumptions"]["spread_is_measured_from_history"])
        by_name = {row["name"]: row for row in report["scenarios"]}
        for name in (
            "zero_gross_no_noise",
            "positive_gross_negative_after_cost",
            "independent_zero_gross_sigma_0.25",
            "independent_zero_gross_sigma_1.0",
            "independent_zero_gross_sigma_3.0",
            "correlated_zero_gross_sigma_1.0",
            "correlated_zero_gross_sigma_3.0",
        ):
            self.assertEqual(by_name[name]["false_pass_count"], 0, name)
            self.assertFalse(by_name[name]["spread_double_charged"])
            self.assertEqual(by_name[name]["near_duplicate_status"], "UNAVAILABLE")
        self.assertEqual(by_name["strong_planted_no_noise"]["planted_recovery_rate"], 1.0)
        self.assertEqual(by_name["strong_planted_sigma_0_25"]["planted_recovery_rate"], 1.0)
        self.assertEqual(report["strong_planted_recovery_rate"], 1.0)
        self.assertEqual(report["null_and_negative_false_pass_count"], 0)
        self.assertEqual(by_name["sign_reversals"]["false_pass_count"], 0)
        self.assertGreater(by_name["sign_reversals"]["gate_fail_count"], 0)
        self.assertEqual(by_name["low_support"]["gate_pass_count"], 0)
        self.assertEqual(
            by_name["low_support"]["gate_inoperable_count"],
            by_name["low_support"]["pattern_count"],
        )
        self.assertEqual(by_name["eight_segment_planted"]["gate_pass_count"], 0)
        self.assertEqual(
            by_name["eight_segment_planted"]["gate_inoperable_count"],
            by_name["eight_segment_planted"]["pattern_count"],
        )

    def test_bounded_performance_uses_catalogue_dimensions_without_market_files(self) -> None:
        labels = _labels()
        definitions = enumerate_pattern_definitions()
        by_family = {family: [] for family in ("SNAPSHOT_SINGLE", "SNAPSHOT_PAIR", "SAME_DIMENSION_TRANSITION")}
        for pattern in definitions:
            if len(by_family[pattern.family]) < 4:
                by_family[pattern.family].append(pattern)
        chosen = [pattern for rows in by_family.values() for pattern in rows]
        self.assertEqual(len(SYMBOLS) * len(TIMEFRAMES) * len(HORIZONS_MINUTES), 18)
        records = []
        for symbol in SYMBOLS:
            for timeframe in TIMEFRAMES:
                for horizon in HORIZONS_MINUTES:
                    for pattern in chosen:
                        for direction in DIRECTIONS:
                            for label in labels:
                                records.append(
                                    synthetic_annual_record(
                                        pattern=pattern,
                                        symbol=symbol,
                                        timeframe=timeframe,
                                        horizon_minutes=horizon,
                                        direction=direction,
                                        annual_segment_label=label,
                                        support=80,
                                        mean_net_pips_0p5=-0.2,
                                        mean_net_pips_1p0=-1.2,
                                    )
                                )
        started = time.perf_counter()
        report = compare_cross_year_patterns(submissions_for_records(records))
        elapsed = time.perf_counter() - started
        self.assertEqual(
            report["pattern_count"],
            18 * len(chosen) * len(DIRECTIONS),
        )
        self.assertEqual(len(report["supplied_segments"]), 12)
        self.assertEqual(report["gate_pass_count"], 0)
        self.assertFalse(report["historical_market_artifacts_read"])
        self.assertLess(elapsed, 15.0)
        self.assertGreater(report["negative_effect_count"], 0)

    def test_engine_source_does_not_open_artifacts_or_disabled_workflows(self) -> None:
        source = Path(
            "src/fmp/discovery/annual_pattern_catalogue_cross_year.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("open(", source)
        self.assertNotIn("373883560", source)
        self.assertNotIn("357842915", source)
        self.assertNotIn("DEC-629", source)
        self.assertNotIn("DEC-630", source)
        self.assertNotIn("workflow_dispatch", source)

    def test_invalid_commit_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "code_commit"):
            synthetic_segment_provenance("2015", code_commit="not-a-commit")
        self.assertEqual(len(protocol_fingerprint()), 64)


def _fingerprint(index: int) -> str:
    return _record(
        index,
        "2015",
        support=100,
        base=0.5,
        stress=0.25,
    ).canonical_pattern_fingerprint


if __name__ == "__main__":
    unittest.main()
