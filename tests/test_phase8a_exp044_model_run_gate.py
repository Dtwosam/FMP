import unittest

from fmp.market_learning.model_run_gate import (
    EXPECTED_FEATURE_EVIDENCE_FINGERPRINT,
    EXPECTED_FEATURE_RUN_ID,
    EXPECTED_OUTCOME_EVIDENCE_ARTIFACT_ID,
    EXPECTED_OUTCOME_RUN_ID,
    EXPECTED_PROTOCOL_FINGERPRINT,
    EXPECTED_PROTOCOL_SOURCE_COMMIT,
    EXPECTED_READINESS_ARTIFACT_ID,
    build_model_run_source_gate,
)
from fmp.market_learning.operator import dispatch_command_for_next_report


def _execution_status() -> dict[str, object]:
    return {
        "stage": "MODEL_PROTOCOL_SOURCE_OPEN",
        "feature_run_id": EXPECTED_FEATURE_RUN_ID,
        "outcome_run_id": EXPECTED_OUTCOME_RUN_ID,
        "readiness_verified": True,
        "model_protocol_source_open_authorized": True,
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
    }


def _gate() -> dict[str, object]:
    return build_model_run_source_gate(
        execution_status=_execution_status(),
        protocol_fingerprint_value=EXPECTED_PROTOCOL_FINGERPRINT,
        feature_run_id=EXPECTED_FEATURE_RUN_ID,
        feature_evidence_fingerprint=EXPECTED_FEATURE_EVIDENCE_FINGERPRINT,
        outcome_run_id=EXPECTED_OUTCOME_RUN_ID,
        outcome_evidence_artifact_id=EXPECTED_OUTCOME_EVIDENCE_ARTIFACT_ID,
        readiness_artifact_id=EXPECTED_READINESS_ARTIFACT_ID,
    )


class Exp044ModelRunGateTests(unittest.TestCase):
    def test_exact_verified_chain_opens_source_only_model_run_work(self) -> None:
        result = _gate()
        self.assertEqual(result["stage"], "MODEL_PROTOCOL_FROZEN")
        self.assertIs(result["model_protocol_frozen"], True)
        self.assertIs(result["model_run_source_open_authorized"], True)
        self.assertEqual(result["model_protocol_fingerprint"], EXPECTED_PROTOCOL_FINGERPRINT)
        self.assertEqual(result["model_protocol_source_commit"], EXPECTED_PROTOCOL_SOURCE_COMMIT)
        for field in (
            "model_protocol_result_authorized",
            "model_fit_authorized",
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertIs(result[field], False)

    def test_protocol_fingerprint_drift_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_model_run_source_gate(
                execution_status=_execution_status(),
                protocol_fingerprint_value="0" * 64,
                feature_run_id=EXPECTED_FEATURE_RUN_ID,
                feature_evidence_fingerprint=EXPECTED_FEATURE_EVIDENCE_FINGERPRINT,
                outcome_run_id=EXPECTED_OUTCOME_RUN_ID,
                outcome_evidence_artifact_id=EXPECTED_OUTCOME_EVIDENCE_ARTIFACT_ID,
                readiness_artifact_id=EXPECTED_READINESS_ARTIFACT_ID,
            )

    def test_readiness_artifact_drift_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "readiness artifact mismatch"):
            build_model_run_source_gate(
                execution_status=_execution_status(),
                protocol_fingerprint_value=EXPECTED_PROTOCOL_FINGERPRINT,
                feature_run_id=EXPECTED_FEATURE_RUN_ID,
                feature_evidence_fingerprint=EXPECTED_FEATURE_EVIDENCE_FINGERPRINT,
                outcome_run_id=EXPECTED_OUTCOME_RUN_ID,
                outcome_evidence_artifact_id=EXPECTED_OUTCOME_EVIDENCE_ARTIFACT_ID,
                readiness_artifact_id=EXPECTED_READINESS_ARTIFACT_ID + 1,
            )

    def test_frozen_protocol_stage_is_not_dispatchable(self) -> None:
        result = _gate()
        report = {
            "read_only": True,
            "stage": result["stage"],
            "model_protocol_result_authorized": False,
            "model_fit_authorized": False,
            "promotion_authorized": False,
            "trading_authorized": False,
        }
        self.assertIsNone(dispatch_command_for_next_report(report))


if __name__ == "__main__":
    unittest.main()
