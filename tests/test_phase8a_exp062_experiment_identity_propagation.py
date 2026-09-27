from __future__ import annotations

import unittest

from fmp.discovery.market_learning_adapter import (
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
from fmp.discovery.pattern_protocol import (
    EXPERIMENT_ID,
    pattern_fingerprint,
    protocol_fingerprint,
    protocol_payload,
)
from fmp.discovery.exp062_adapter_repair import EXP062_EXPERIMENT_ID


CODE_COMMIT = "a" * 40
PROCESSED_SHA = "b" * 64
FEATURE_MANIFEST_SHA = "c" * 64
OUTCOME_MANIFEST_SHA = "d" * 64
FEATURE_EVIDENCE_SHA = "e" * 64
OUTCOME_EVIDENCE_SHA = "f" * 64


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


def _compile(*, experiment_id: str = EXPERIMENT_ID) -> dict[str, object]:
    return compile_cell_evidence(
        _empty_result(),
        code_commit=CODE_COMMIT,
        processed_manifest_sha256=PROCESSED_SHA,
        feature_manifest_sha256=FEATURE_MANIFEST_SHA,
        outcome_manifest_sha256=OUTCOME_MANIFEST_SHA,
        feature_evidence_fingerprint=FEATURE_EVIDENCE_SHA,
        outcome_evidence_fingerprint=OUTCOME_EVIDENCE_SHA,
        experiment_id=experiment_id,
    )


class Exp062ExperimentIdentityPropagationTests(unittest.TestCase):
    def test_default_protocol_identity_remains_exp061_exactly(self) -> None:
        self.assertEqual(
            protocol_payload(),
            protocol_payload(experiment_id=EXPERIMENT_ID),
        )
        self.assertEqual(
            protocol_fingerprint(),
            protocol_fingerprint(experiment_id=EXPERIMENT_ID),
        )
        self.assertEqual(protocol_payload()["experiment_id"], EXPERIMENT_ID)

    def test_pattern_fingerprint_default_remains_exp061_and_exp062_differs(self) -> None:
        kwargs = {
            "symbol": "EURUSD",
            "timeframe": "15m",
            "horizon_minutes": 60,
            "direction": "LONG",
            "predicates": (("return_1h", "HIGH"),),
        }
        legacy = pattern_fingerprint(**kwargs)
        explicit_legacy = pattern_fingerprint(
            **kwargs,
            experiment_id=EXPERIMENT_ID,
        )
        repaired = pattern_fingerprint(
            **kwargs,
            experiment_id=EXP062_EXPERIMENT_ID,
        )
        self.assertEqual(legacy, explicit_legacy)
        self.assertNotEqual(legacy, repaired)
        self.assertEqual(
            repaired,
            pattern_fingerprint(
                **kwargs,
                experiment_id=EXP062_EXPERIMENT_ID,
            ),
        )

    def test_exp062_protocol_fingerprint_is_distinct_and_deterministic(self) -> None:
        legacy = protocol_fingerprint()
        repaired = protocol_fingerprint(
            experiment_id=EXP062_EXPERIMENT_ID
        )
        self.assertNotEqual(legacy, repaired)
        self.assertEqual(
            repaired,
            protocol_fingerprint(
                experiment_id=EXP062_EXPERIMENT_ID
            ),
        )
        payload = protocol_payload(
            experiment_id=EXP062_EXPERIMENT_ID
        )
        self.assertEqual(payload["experiment_id"], EXP062_EXPERIMENT_ID)

    def test_default_cell_evidence_equals_explicit_exp061(self) -> None:
        implicit = _compile()
        explicit = _compile(experiment_id=EXPERIMENT_ID)
        self.assertEqual(implicit, explicit)
        self.assertIs(validate_cell_evidence(implicit), implicit)

    def test_exp062_cell_evidence_is_distinct_and_validates_only_as_exp062(self) -> None:
        legacy = _compile()
        repaired = _compile(experiment_id=EXP062_EXPERIMENT_ID)
        self.assertNotEqual(legacy["evidence_fingerprint"], repaired["evidence_fingerprint"])
        self.assertEqual(repaired["experiment_id"], EXP062_EXPERIMENT_ID)
        self.assertEqual(
            repaired["protocol_fingerprint"],
            protocol_fingerprint(experiment_id=EXP062_EXPERIMENT_ID),
        )
        self.assertIs(
            validate_cell_evidence(
                repaired,
                expected_experiment_id=EXP062_EXPERIMENT_ID,
            ),
            repaired,
        )
        with self.assertRaisesRegex(ValueError, "experiment mismatch"):
            validate_cell_evidence(repaired)

    def test_empty_or_wrong_expected_identity_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-empty"):
            protocol_fingerprint(experiment_id="")

        repaired = _compile(experiment_id=EXP062_EXPERIMENT_ID)
        with self.assertRaisesRegex(ValueError, "experiment mismatch"):
            validate_cell_evidence(
                repaired,
                expected_experiment_id="EXP-OTHER",
            )


if __name__ == "__main__":
    unittest.main()
