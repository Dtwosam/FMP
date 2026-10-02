from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import unittest

from fmp.discovery.annual_pattern_catalogue_evidence import (
    DIRECTIONAL_RECORDS_PER_ANNUAL_CELL,
    EXPECTED_ANNUAL_CELL_COUNT,
    EXPECTED_ANNUAL_CELL_IDENTITIES,
    EXPECTED_TOTAL_DIRECTIONAL_RECORDS,
    ValidatedAnnualCellSummary,
    compile_aggregate_evidence,
    compile_cell_evidence,
    evidence_contract_payload,
    validate_aggregate_evidence,
    validate_cell_evidence,
    validated_cell_summary,
)
from fmp.discovery.annual_pattern_catalogue_miner import mine_annual_catalogue_cell
from fmp.discovery.pattern_miner import FeatureObservation, OutcomeObservation
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES


_CODE_COMMIT = "a" * 40
_SESSION_FLAGS = (
    "is_london_new_york_overlap",
    "is_london_session",
    "is_new_york_session",
    "is_asia_session",
)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _feature(observation_id: str, available: datetime) -> FeatureObservation:
    values: dict[str, object] = {name: 0.0 for name in CONTINUOUS_FEATURES}
    values.update({name: False for name in _SESSION_FLAGS})
    return FeatureObservation(
        observation_id=observation_id,
        symbol="EURUSD",
        timeframe="5m",
        available_at_utc=available,
        values=values,
    )


def _outcome(observation_id: str, available: datetime) -> OutcomeObservation:
    return OutcomeObservation(
        observation_id=observation_id,
        symbol="EURUSD",
        timeframe="5m",
        available_at_utc=available,
        exit_timestamp_utc=available + timedelta(minutes=60),
        horizon_minutes=60,
        long_net_pips_0p5=1.0,
        short_net_pips_0p5=-1.0,
        long_net_pips_1p0=0.5,
        short_net_pips_1p0=-1.5,
    )


def _cell() -> tuple[dict[str, object], bytes]:
    available = datetime(2015, 1, 2, tzinfo=timezone.utc)
    result = mine_annual_catalogue_cell(
        (_feature("x", available),),
        (_outcome("x", available),),
        symbol="EURUSD",
        timeframe="5m",
        horizon_minutes=60,
        annual_segment_label="2015",
    )
    return compile_cell_evidence(
        result,
        code_commit=_CODE_COMMIT,
        processed_manifest_sha256=_sha("processed"),
        feature_manifest_sha256=_sha("feature"),
        outcome_manifest_sha256=_sha("outcome"),
        feature_evidence_fingerprint=_sha("feature-evidence"),
        outcome_evidence_fingerprint=_sha("outcome-evidence"),
    )


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


def _summary(
    identity: tuple[str, str, str, int],
) -> ValidatedAnnualCellSummary:
    segment, symbol, timeframe, horizon = identity
    base = f"{segment}:{symbol}:{timeframe}:{horizon}"
    return ValidatedAnnualCellSummary(
        annual_segment_label=segment,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon,
        code_commit=_CODE_COMMIT,
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


class AnnualPatternCatalogueEvidenceTests(unittest.TestCase):
    def test_cell_evidence_serializes_all_records_and_self_validates(self) -> None:
        evidence, payload = _cell()

        self.assertEqual(evidence["experiment_id"], "EXP-20261002-067")
        self.assertEqual(
            evidence["miner_merge_sha"],
            "3926daa8b64ca18c69d5a95a7b31b960dddde27b",
        )
        self.assertEqual(evidence["directional_record_count"], 4970)
        self.assertEqual(len(payload), evidence["catalogue_payload_size_bytes"])
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            evidence["catalogue_payload_sha256"],
        )
        self.assertIs(validate_cell_evidence(evidence, payload), evidence)
        summary = validated_cell_summary(evidence, payload)
        self.assertEqual(summary.annual_segment_label, "2015")
        self.assertEqual(summary.directional_record_count, 4970)

    def test_refingerprinted_record_metric_tamper_fails_semantic_validation(self) -> None:
        evidence, payload = _cell()
        decoded = json.loads(payload)
        off_long = next(
            row
            for row in decoded["records"]
            if row["family"] == "SNAPSHOT_SINGLE"
            and row["dimensions"] == ["session_state"]
            and row["states"] == ["OFF_SESSION"]
            and row["direction"] == "LONG"
        )
        off_long["statistics"]["support"] = 75
        tampered_payload = _canonical(decoded)
        tampered = dict(evidence)
        tampered["catalogue_payload_sha256"] = hashlib.sha256(
            tampered_payload
        ).hexdigest()
        tampered["catalogue_payload_size_bytes"] = len(tampered_payload)
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "evaluable/support relation mismatch",
        ):
            validate_cell_evidence(tampered, tampered_payload)

    def test_refingerprinted_identity_tamper_fails_semantic_validation(self) -> None:
        evidence, payload = _cell()
        decoded = json.loads(payload)
        decoded["records"][0]["canonical_pattern_fingerprint"] = "f" * 64
        tampered_payload = _canonical(decoded)
        tampered = dict(evidence)
        tampered["catalogue_payload_sha256"] = hashlib.sha256(
            tampered_payload
        ).hexdigest()
        tampered["catalogue_payload_size_bytes"] = len(tampered_payload)
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "canonical pattern fingerprint mismatch",
        ):
            validate_cell_evidence(tampered, tampered_payload)

    def test_aggregate_requires_exact_12_by_18_matrix(self) -> None:
        summaries = [_summary(identity) for identity in EXPECTED_ANNUAL_CELL_IDENTITIES]
        aggregate = compile_aggregate_evidence(
            summaries,
            code_commit=_CODE_COMMIT,
        )

        self.assertEqual(EXPECTED_ANNUAL_CELL_COUNT, 216)
        self.assertEqual(EXPECTED_TOTAL_DIRECTIONAL_RECORDS, 1073520)
        self.assertEqual(aggregate["experiment_id"], "EXP-20261002-067")
        self.assertEqual(
            aggregate["miner_merge_sha"],
            "3926daa8b64ca18c69d5a95a7b31b960dddde27b",
        )
        self.assertEqual(aggregate["annual_segment_count"], 12)
        self.assertEqual(aggregate["annual_cell_count"], 216)
        self.assertEqual(aggregate["directional_record_count"], 1073520)
        self.assertEqual(len(aggregate["segment_summaries"]), 12)
        self.assertTrue(
            all(row["annual_cell_count"] == 18 for row in aggregate["segment_summaries"])
        )
        self.assertIs(
            validate_aggregate_evidence(
                aggregate,
                expected_summaries=summaries,
            ),
            aggregate,
        )

    def test_aggregate_missing_or_duplicate_cell_fails_closed(self) -> None:
        summaries = [_summary(identity) for identity in EXPECTED_ANNUAL_CELL_IDENTITIES]
        with self.assertRaisesRegex(ValueError, "requires exactly 216 annual cells"):
            compile_aggregate_evidence(
                summaries[:-1],
                code_commit=_CODE_COMMIT,
            )

        duplicate = list(summaries)
        duplicate[-1] = duplicate[0]
        with self.assertRaisesRegex(ValueError, "duplicate annual cell"):
            compile_aggregate_evidence(
                duplicate,
                code_commit=_CODE_COMMIT,
            )

    def test_refingerprinted_aggregate_total_tamper_fails_closed(self) -> None:
        summaries = [_summary(identity) for identity in EXPECTED_ANNUAL_CELL_IDENTITIES]
        aggregate = compile_aggregate_evidence(
            summaries,
            code_commit=_CODE_COMMIT,
        )
        tampered = dict(aggregate)
        tampered["directional_record_count"] = 1
        tampered = _refingerprint(tampered)

        with self.assertRaisesRegex(
            ValueError,
            "directional_record_count mismatch",
        ):
            validate_aggregate_evidence(tampered)

    def test_authority_locks_remain_false(self) -> None:
        contract = evidence_contract_payload()

        self.assertEqual(
            contract["next_gate"],
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_FULL_HISTORY_LOADER",
        )
        for field in (
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(contract[field], field)


if __name__ == "__main__":
    unittest.main()
