from __future__ import annotations

from pathlib import Path
import unittest

from fmp.features.schema import FEATURE_VALUE_COLUMNS
from fmp.market_learning.model_protocol import (
    HIST_GRADIENT_BOOSTING_CONFIG,
    LOGISTIC_REGRESSION_CONFIG,
)
from fmp.market_learning.model_successor_protocol import (
    ALL_FAMILIES_UNAVAILABLE_STATUS,
    BASE_PROTOCOL_FINGERPRINT,
    FAMILY_FIT_ATTEMPTS,
    LOGISTIC_NONCONVERGENCE_POLICY,
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    NO_FINANCIAL_CHALLENGER_STATUS,
    PREDECESSOR_EXPERIMENT_ID,
    PREDECESSOR_FAILED_MODEL_HEAD_SHA,
    PREDECESSOR_FAILED_MODEL_RUN_ID,
    PREDECESSOR_FAILURE_REVIEW_DECISION,
    PRIOR_RESULT_INFORMED,
    PROMOTION_AUTHORIZED,
    SHADOW_AUTHORIZED,
    SUCCESSOR_EXPERIMENT_ID,
    SUCCESSOR_PROTOCOL_DECISION,
    SUCCESSOR_PROTOCOL_VERSION,
    TRADING_AUTHORIZED,
    UNTOUCHED_OOS,
    successor_protocol_fingerprint,
    successor_protocol_payload,
    validate_base_protocol_identity,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp045SuccessorModelProtocolTests(unittest.TestCase):
    def test_successor_identity_is_explicitly_post_result_informed(self) -> None:
        self.assertEqual(
            SUCCESSOR_EXPERIMENT_ID,
            "EXP-20260923-045",
        )
        self.assertEqual(
            SUCCESSOR_PROTOCOL_DECISION,
            "DEC-095",
        )
        self.assertEqual(
            SUCCESSOR_PROTOCOL_VERSION,
            "fmp-exp045-model-protocol-v1",
        )
        self.assertEqual(
            PREDECESSOR_EXPERIMENT_ID,
            "EXP-20260923-044",
        )
        self.assertEqual(
            PREDECESSOR_FAILURE_REVIEW_DECISION,
            "DEC-094",
        )
        self.assertEqual(
            PREDECESSOR_FAILED_MODEL_RUN_ID,
            35891605645,
        )
        self.assertEqual(
            PREDECESSOR_FAILED_MODEL_HEAD_SHA,
            "e97fa03d0e94fd505d0f926eb730e01a41947880",
        )
        self.assertTrue(PRIOR_RESULT_INFORMED)
        self.assertFalse(UNTOUCHED_OOS)

    def test_base_protocol_identity_remains_exact(self) -> None:
        validate_base_protocol_identity()
        self.assertEqual(
            BASE_PROTOCOL_FINGERPRINT,
            "1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605",
        )

    def test_universe_inputs_target_and_chronology_are_unchanged(self) -> None:
        payload = successor_protocol_payload()
        self.assertEqual(payload["universe"]["cell_count"], 18)
        self.assertEqual(
            payload["inputs"]["column_count"],
            48,
        )
        self.assertEqual(
            payload["inputs"]["columns"],
            list(FEATURE_VALUE_COLUMNS),
        )
        self.assertEqual(
            payload["target"]["column"],
            "best_direction_0p5",
        )
        self.assertEqual(
            payload["target"]["classes"],
            ["LONG", "SHORT", "NO_TRADE"],
        )
        self.assertFalse(
            payload["chronology"]["untouched_oos"],
        )
        self.assertTrue(
            payload["chronology"]["no_refit_after_fit"],
        )

    def test_estimator_configs_are_not_rescued_or_tuned(self) -> None:
        payload = successor_protocol_payload()
        self.assertEqual(
            payload["model_families"]["logistic_regression"],
            dict(LOGISTIC_REGRESSION_CONFIG),
        )
        self.assertEqual(
            payload["model_families"][
                "hist_gradient_boosting"
            ],
            dict(HIST_GRADIENT_BOOSTING_CONFIG),
        )
        self.assertEqual(
            payload["model_families"][
                "logistic_regression"
            ]["max_iter"],
            2000,
        )
        self.assertEqual(
            payload["model_families"][
                "logistic_regression"
            ]["solver"],
            "lbfgs",
        )
        self.assertEqual(FAMILY_FIT_ATTEMPTS, 1)

    def test_nonconvergence_policy_is_family_level_and_non_tuning(self) -> None:
        policy = dict(LOGISTIC_NONCONVERGENCE_POLICY)
        self.assertEqual(
            policy["family_status"],
            "FAILED_NON_CONVERGENCE",
        )
        self.assertEqual(
            policy["failure_reason"],
            "LBFGS_MAX_ITER_REACHED",
        )
        self.assertEqual(
            policy["variant_status"],
            "FAMILY_UNAVAILABLE",
        )
        self.assertFalse(policy["selection_gate_passed"])
        self.assertFalse(policy["retry_authorized"])
        self.assertFalse(policy["solver_fallback_authorized"])
        self.assertFalse(
            policy["max_iter_change_authorized"]
        )
        self.assertFalse(
            policy["preprocessing_change_authorized"]
        )
        self.assertTrue(
            policy[
                "cell_may_continue_with_other_frozen_family"
            ]
        )
        self.assertEqual(
            ALL_FAMILIES_UNAVAILABLE_STATUS,
            "NO_MODEL_FAMILY_AVAILABLE",
        )
        self.assertEqual(
            NO_FINANCIAL_CHALLENGER_STATUS,
            "NO_MODEL_CHALLENGER",
        )

    def test_persistence_policy_is_predeclared_before_any_exp045_result(self) -> None:
        persistence = successor_protocol_payload()[
            "evidence_persistence"
        ]
        self.assertTrue(
            persistence["pair_result_upload_always"]
        )
        self.assertTrue(
            persistence[
                "pair_result_include_hidden_files"
            ]
        )
        self.assertEqual(
            persistence["pair_result_missing_file_policy"],
            "WARN_AND_PRESERVE_JOB_FAILURE",
        )
        self.assertTrue(
            persistence["aggregate_include_hidden_files"]
        )
        self.assertTrue(
            persistence["aggregate_requires_all_cells"]
        )

    def test_all_authorization_locks_remain_false(self) -> None:
        self.assertFalse(MODEL_PROTOCOL_RESULT_AUTHORIZED)
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(PROMOTION_AUTHORIZED)
        self.assertFalse(SHADOW_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)
        authorization = successor_protocol_payload()[
            "authorization"
        ]
        self.assertTrue(
            all(value is False for value in authorization.values())
        )

    def test_protocol_fingerprint_is_deterministic(self) -> None:
        first = successor_protocol_fingerprint()
        second = successor_protocol_fingerprint()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_protocol_source_has_no_fit_or_dispatch_path(self) -> None:
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_protocol.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn(".fit(", source)
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertFalse(
            (
                ROOT
                / ".github/workflows/"
                "phase8a-exp045-model-training.yml"
            ).exists()
        )

    def test_dec095_documents_successor_boundary(self) -> None:
        decision = (
            ROOT / "docs/decision-log.md"
        ).read_text(encoding="utf-8")
        state = (
            ROOT / "docs/project-state.md"
        ).read_text(encoding="utf-8")
        self.assertIn("DEC-095", decision)
        self.assertIn("EXP-20260923-045", decision)
        self.assertIn(
            "EXP-045",
            state,
        )


if __name__ == "__main__":
    unittest.main()
