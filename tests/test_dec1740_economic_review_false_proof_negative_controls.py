"""DEC-1740: reject fabricated StrategyV1 readiness and unknown economics.

Adversarial mutations of an offline copied JSON requirement contract only.
These are not financial estimates and cannot authorize a workflow or broker.
"""
import copy
import json
import unittest

import test_dec1739_economic_evidence_before_shadow_contract as original


class UnprovenStrategyEconomicsNegativeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(
            original.PATH.read_text(encoding="utf-8"),
            object_pairs_hook=original._no_duplicates,
        )

    def _assert_review_guard_fails(self, method, mutate):
        altered = copy.deepcopy(self.original)
        mutate(altered)
        self.assertNotEqual(
            json.dumps(altered, sort_keys=True, separators=(",", ":")),
            json.dumps(self.original, sort_keys=True, separators=(",", ":")),
        )
        case = original.UnprovenPhase8AEconomicReviewContractTests(method)
        case.doc = altered
        with self.assertRaises(AssertionError):
            getattr(case, method)()
        self.assertEqual(
            original.PATH.read_text(encoding="utf-8"),
            json.dumps(self.original, indent=2) + "\n",
        )

    def test_rejects_invented_economic_measure_strategy_v1_net_return(self):
        self._assert_review_guard_fails(
            "test_all_strategy_v1_measurements_are_missing_not_zero",
            lambda d: d["reported_economic_measurements"].__setitem__(
                "strategy_v1_net_return", 0))

    def test_rejects_invented_economic_measure_strategy_v1_expected_value(self):
        self._assert_review_guard_fails(
            "test_all_strategy_v1_measurements_are_missing_not_zero",
            lambda d: d["reported_economic_measurements"].__setitem__(
                "strategy_v1_expected_value", 0))

    def test_rejects_invented_economic_measure_strategy_v1_drawdown(self):
        self._assert_review_guard_fails(
            "test_all_strategy_v1_measurements_are_missing_not_zero",
            lambda d: d["reported_economic_measurements"].__setitem__(
                "strategy_v1_drawdown", 0))

    def test_rejects_invented_economic_measure_strategy_v1_cost_sensitivity(self):
        self._assert_review_guard_fails(
            "test_all_strategy_v1_measurements_are_missing_not_zero",
            lambda d: d["reported_economic_measurements"].__setitem__(
                "strategy_v1_cost_sensitivity", 0))

    def test_rejects_invented_economic_measure_strategy_v1_out_of_sample_years(self):
        self._assert_review_guard_fails(
            "test_all_strategy_v1_measurements_are_missing_not_zero",
            lambda d: d["reported_economic_measurements"].__setitem__(
                "strategy_v1_out_of_sample_years", 0))

    def test_rejects_invented_economic_measure_strategy_v1_forward_shadow_return(self):
        self._assert_review_guard_fails(
            "test_all_strategy_v1_measurements_are_missing_not_zero",
            lambda d: d["reported_economic_measurements"].__setitem__(
                "strategy_v1_forward_shadow_return", 0))

    def test_rejects_forged_authorization_all_years_accepted(self):
        self._assert_review_guard_fails(
            "test_no_fabricated_approval_flags",
            lambda d: d.__setitem__("all_years_accepted", True))

    def test_rejects_forged_authorization_cross_year_comparison_authorized(self):
        self._assert_review_guard_fails(
            "test_no_fabricated_approval_flags",
            lambda d: d.__setitem__("cross_year_comparison_authorized", True))

    def test_rejects_forged_authorization_strategy_v1_frozen(self):
        self._assert_review_guard_fails(
            "test_no_fabricated_approval_flags",
            lambda d: d.__setitem__("strategy_v1_frozen", True))

    def test_rejects_forged_authorization_phase8b_shadow_approved(self):
        self._assert_review_guard_fails(
            "test_no_fabricated_approval_flags",
            lambda d: d.__setitem__("phase8b_shadow_approved", True))

    def test_rejects_forged_authorization_demo_approved(self):
        self._assert_review_guard_fails(
            "test_no_fabricated_approval_flags",
            lambda d: d.__setitem__("demo_approved", True))

    def test_rejects_forged_authorization_phase10_approved(self):
        self._assert_review_guard_fails(
            "test_no_fabricated_approval_flags",
            lambda d: d.__setitem__("phase10_approved", True))

    def test_rejects_forged_authorization_live_real_money_approved(self):
        self._assert_review_guard_fails(
            "test_no_fabricated_approval_flags",
            lambda d: d.__setitem__("live_real_money_approved", True))

    def test_rejects_forged_authorization_has_forward_profit_evidence(self):
        self._assert_review_guard_fails(
            "test_no_fabricated_approval_flags",
            lambda d: d.__setitem__("has_forward_profit_evidence", True))

    def test_rejects_boolean_one_as_attempt_number(self):
        self._assert_review_guard_fails(
            "test_annual_predecessor_and_next_one_shot_identity",
            lambda d: d["annual_series"].__setitem__("next_attempt", True))

    def test_rejects_false_fresh_inventory_claim(self):
        self._assert_review_guard_fails(
            "test_current_annual_provenance_missing_not_invented",
            lambda d: d["annual_series"].__setitem__(
                "independent_fresh_inventory_present", True))

    def test_rejects_nonempty_approved_execution_actions(self):
        self._assert_review_guard_fails(
            "test_action_fields_are_empty_and_not_signed",
            lambda d: d["allowed_execution_actions"].append("annual_run385"))

    def test_rejects_discovery_method_replacement(self):
        self._assert_review_guard_fails(
            "test_discovery_first_method_is_unmodified",
            lambda d: d.__setitem__("research_method",
                                    "OPTIMIZED_AFTER_SEEING_FUTURE_YEARS"))

    def test_unmodified_evidence_requirements_pass_twelve_guards(self):
        original.UnprovenPhase8AEconomicReviewContractTests.setUpClass()
        case = original.UnprovenPhase8AEconomicReviewContractTests(
            "test_contract_is_static_non_authorizing")
        case.doc = copy.deepcopy(self.original)
        case.source = original.PATH.read_text(encoding="utf-8")
        methods = [name for name in dir(case) if name.startswith("test_")]
        self.assertEqual(len(methods), 12)
        for name in methods:
            with self.subTest(guard=name):
                getattr(case, name)()
