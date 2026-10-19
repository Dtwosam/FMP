"""DEC-1747: adversarial regression tests for the *existing* DEC-1746 guards.

These tests mutate copies of the nonauthorizing, unevaluated research
preregistration packet, never broker interfaces or protected annual inputs.
"""
import copy
import json
import unittest

import test_dec1746_economic_preregistration_strict_source_guards as guard


class StrategyV1PreregistrationForgeryNegativeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(
            guard.PACKET.read_text(encoding="utf-8"),
            object_pairs_hook=guard._strict_pairs,
        )
        cls.original_prose = guard.EXPLANATION.read_text(encoding="utf-8")

    def _refused(self, edit, existing_guard, edit_prose=None):
        changed = copy.deepcopy(self.original)
        edit(changed)
        prose = self.original_prose
        if edit_prose is not None:
            prose = edit_prose(prose)
        canonical = lambda d: json.dumps(
            d, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        self.assertNotEqual(
            (canonical(changed), prose),
            (canonical(self.original), self.original_prose),
            "Every adversarial case must contain a real mutation",
        )
        case = guard.EconomicPreregistrationSourceIntegrityTests(existing_guard)
        case.doc = changed
        case.prose = prose
        case.raw = canonical(changed)
        with self.assertRaises(AssertionError):
            getattr(case, existing_guard)()
        self.assertEqual(
            self.original,
            json.loads(guard.PACKET.read_text(encoding="utf-8"),
                       object_pairs_hook=guard._strict_pairs),
            "Mutation must not alter the actual preregistration packet",
        )

    def test_forged_pass_category_rejected(self):
        self._refused(
            lambda d: d["gates"][0].__setitem__("status", "PASS"),
            "test_all_evidence_groups_still_not_evaluated_or_signed")

    def test_forged_evidence_reference_rejected(self):
        self._refused(
            lambda d: d["gates"][4].__setitem__("evidence_ref", "fake://passed"),
            "test_all_evidence_groups_still_not_evaluated_or_signed")

    def test_forged_independent_signoff_rejected(self):
        self._refused(
            lambda d: d["gates"][8].__setitem__("signoff", "APPROVED"),
            "test_all_evidence_groups_still_not_evaluated_or_signed")

    def test_removed_risk_category_rejected(self):
        self._refused(
            lambda d: d["gates"].pop(9),
            "test_exact_fifteen_required_evidence_categories")

    def test_duplicated_category_rejected(self):
        self._refused(
            lambda d: d["gates"].append(copy.deepcopy(d["gates"][0])),
            "test_exact_fifteen_required_evidence_categories")

    def test_swapped_review_order_rejected(self):
        self._refused(
            lambda d: d["gates"].reverse(),
            "test_exact_fifteen_required_evidence_categories")

    def test_extra_shadow_approval_field_rejected(self):
        self._refused(
            lambda d: d["gates"][13].__setitem__("is_approved", True),
            "test_all_evidence_groups_still_not_evaluated_or_signed")

    def test_empty_required_evidence_rejected(self):
        self._refused(
            lambda d: d["gates"][7].__setitem__("required_evidence", ""),
            "test_all_evidence_groups_still_not_evaluated_or_signed")

    def test_forged_annual_complete_flag_rejected(self):
        self._refused(
            lambda d: d.__setitem__("annual_catalogues_complete", True),
            "test_all_unreviewed_stages_use_strict_false_not_numeric_zero")

    def test_numeric_zero_as_false_flag_rejected(self):
        self._refused(
            lambda d: d.__setitem__("live_trading_authorized", 0),
            "test_all_unreviewed_stages_use_strict_false_not_numeric_zero")

    def test_integer_one_as_authority_rejected(self):
        self._refused(
            lambda d: d.__setitem__("demo_order_authorized", 1),
            "test_all_unreviewed_stages_use_strict_false_not_numeric_zero")

    def test_boolean_attempt_one_alias_rejected(self):
        self._refused(
            lambda d: d.__setitem__("attempt_number", True),
            "test_human_run385_identity_strict_integer_and_not_authorized")

    def test_floating_run_number_rejected(self):
        self._refused(
            lambda d: d.__setitem__("next_run_number", 385.0),
            "test_human_run385_identity_strict_integer_and_not_authorized")

    def test_second_protected_attempt_rejected(self):
        self._refused(
            lambda d: d.__setitem__("attempt_number", 2),
            "test_human_run385_identity_strict_integer_and_not_authorized")

    def test_skipped_2023_year_rejected(self):
        self._refused(
            lambda d: d.__setitem__("next_one_shot_segment", "2024"),
            "test_human_run385_identity_strict_integer_and_not_authorized")

    def test_cross_year_shortcut_method_rejected(self):
        self._refused(
            lambda d: d.__setitem__("method", "OPTIMIZE_STRATEGY_FIRST"),
            "test_year_by_year_governing_method_not_strategy_family_shortcut")

    def test_invented_strategy_identity_rejected(self):
        self._refused(
            lambda d: d.__setitem__("candidate_strategy_identity", "strategy_v1"),
            "test_candidate_rule_and_return_numbers_are_missing_not_fabricated")

    def test_numeric_profit_measurement_rejected(self):
        self._refused(
            lambda d: d.__setitem__("profitability_measurements", {"net_return": 0}),
            "test_candidate_rule_and_return_numbers_are_missing_not_fabricated")

    def test_string_profit_claim_rejected(self):
        self._refused(
            lambda d: d.__setitem__("profitability_measurements", "+18%"),
            "test_candidate_rule_and_return_numbers_are_missing_not_fabricated")

    def test_phase7_relabel_as_strategy_evidence_rejected(self):
        self._refused(
            lambda d: d["known_historical_context"].__setitem__(
                "not_phase8a_strategy_v1_results", False),
            "test_historical_phase7_benchmark_is_not_strategy_v1_evidence")

    def test_forged_historical_return_rejected(self):
        self._refused(
            lambda d: d["known_historical_context"][
                "reported_phase7_net_return_pct_by_slippage_pips"
            ].__setitem__("1.0", "99.000000"),
            "test_historical_phase7_benchmark_is_not_strategy_v1_evidence")

    def test_historical_benchmark_promoted_to_live_forecast_rejected(self):
        self._refused(
            lambda d: d["known_historical_context"].__setitem__(
                "live_return_forecast", "2%"),
            "test_historical_phase7_benchmark_is_not_strategy_v1_evidence")

    def test_unregistered_thresholds_claimed_rejected(self):
        self._refused(
            lambda d: d.__setitem__("predefined_thresholds_documented", True),
            "test_thresholds_not_chosen_after_candidate_data_review")

    def test_retroactive_threshold_rationale_rejected(self):
        self._refused(
            lambda d: d.__setitem__(
                "rationale", "Choose favorable pass thresholds after results"),
            "test_thresholds_not_chosen_after_candidate_data_review")

    def test_forged_current_pass_disposition_rejected(self):
        self._refused(
            lambda d: d.__setitem__("current_disposition", "APPROVED_FOR_LIVE"),
            "test_rejection_is_still_possible_and_no_pass_disposition")

    def test_removed_reject_outcome_rejected(self):
        self._refused(
            lambda d: d["possible_dispositions"].remove("REJECT"),
            "test_rejection_is_still_possible_and_no_pass_disposition")

    def test_unapproved_live_disposition_added_rejected(self):
        self._refused(
            lambda d: d["possible_dispositions"].append("APPROVED_FOR_LIVE"),
            "test_rejection_is_still_possible_and_no_pass_disposition")

    def test_broker_action_added_rejected(self):
        self._refused(
            lambda d: d["allowed_actions"].append("broker_place_order"),
            "test_no_any_authorized_execution_actions_or_signed_orders")

    def test_executable_order_command_inside_packet_rejected(self):
        self._refused(
            lambda d: d.__setitem__("caveat", "No approval; place_order("),
            "test_packet_has_no_dispatch_or_broker_execution_commands")

    def test_workflow_dispatch_command_inside_packet_rejected(self):
        self._refused(
            lambda d: d.__setitem__("caveat", "gh workflow run protected-annual"),
            "test_packet_has_no_dispatch_or_broker_execution_commands")

    def test_removed_nonauthorization_caveat_rejected(self):
        self._refused(
            lambda d: d.__setitem__("caveat", "This is approved"),
            "test_packet_has_no_dispatch_or_broker_execution_commands")

    def test_pristine_holdout_wording_erasure_rejected(self):
        self._refused(
            lambda d: None,
            "test_multiple_testing_and_holdout_contamination_are_required",
            lambda s: s.replace("pristine final holdout", "used holdout"))

    def test_multiple_comparisons_erasure_rejected(self):
        self._refused(
            lambda d: None,
            "test_multiple_testing_and_holdout_contamination_are_required",
            lambda s: s.replace("multiple comparisons", "single comparison"))

    def test_nested_duplicate_json_members_refused_by_actual_decoder(self):
        with self.assertRaisesRegex(ValueError, "duplicate preregistration member"):
            json.loads(
                '{"gates":[{"id":"time_safe_signal_and_execution",'
                '"id":"fake_pass"}]}',
                object_pairs_hook=guard._strict_pairs,
            )

    def test_pristine_control_still_passes_all_fifteen_source_guards(self):
        guard.EconomicPreregistrationSourceIntegrityTests.setUpClass()
        methods = sorted(
            name for name in dir(
                guard.EconomicPreregistrationSourceIntegrityTests
            ) if name.startswith("test_")
        )
        self.assertEqual(len(methods), 15)
        for method in methods:
            with self.subTest(guard=method):
                case = guard.EconomicPreregistrationSourceIntegrityTests(method)
                case.doc = copy.deepcopy(self.original)
                case.prose = self.original_prose
                case.raw = guard.PACKET.read_text(encoding="utf-8")
                getattr(case, method)()
