"""DEC-1749: mutation-test existing four-source Phase8A safety consistency.

No protected data read, annual dispatch, broker call or live authorization.
All mutation targets are in-memory copies; each expected failure is observed in
the *existing* DEC-1748 guard, not an artificial replacement validator.
"""
import copy
import json
import unittest

import test_dec1748_preregistration_four_source_reconciliation as joined


class FourSourceAdversarialReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        joined.PreregistrationFourSourceBoundaryConsistencyTests.setUpClass()
        cls.pristine = copy.deepcopy(
            joined.PreregistrationFourSourceBoundaryConsistencyTests.sources)

    def _must_reject(self, change, guard_method):
        changed = copy.deepcopy(self.pristine)
        annual = changed["annual"]
        economic = changed["economic"]
        graph = changed["dependency"]
        packet = changed["preregistration"]
        before = json.dumps(changed, sort_keys=True, separators=(",", ":"))
        exec_change = change
        # Explicit mutation functions below only touch isolated JSON copies.
        exec_change(annual, economic, graph, packet)
        after = json.dumps(changed, sort_keys=True, separators=(",", ":"))
        self.assertNotEqual(before, after, "a no-op mutation is not a test")
        case = joined.PreregistrationFourSourceBoundaryConsistencyTests(
            guard_method)
        case.sources = changed
        case.annual = annual
        case.economic = economic
        case.graph = graph
        case.packet = packet
        case.nodes = {item["id"]: item for item in graph["nodes"]}
        with self.assertRaises(AssertionError):
            getattr(case, guard_method)()
        self.assertEqual(
            joined.PreregistrationFourSourceBoundaryConsistencyTests.sources,
            self.pristine, "fixture must never be mutated")

    def test_reject_wrong_2023_identity(self):
        def change(annual, economic, graph, packet):
            packet['next_one_shot_segment'] = '2024'
        self._must_reject(change, "test_2023_run385_attempt1_identity_agrees_across_four_documents")

    def test_reject_wrong_expected_run(self):
        def change(annual, economic, graph, packet):
            annual['yearly_catalogue_status'][8]['expected_run_number'] = 386
        self._must_reject(change, "test_2023_run385_attempt1_identity_agrees_across_four_documents")

    def test_reject_wrong_graph_attempt(self):
        def change(annual, economic, graph, packet):
            graph['next_expected_attempt'] = 2
        self._must_reject(change, "test_2023_run385_attempt1_identity_agrees_across_four_documents")

    def test_reject_bool_packet_run(self):
        def change(annual, economic, graph, packet):
            packet['next_run_number'] = True
        self._must_reject(change, "test_run385_and_attempt_numbers_are_real_integers_not_booleans")

    def test_reject_float_economic_attempt(self):
        def change(annual, economic, graph, packet):
            economic['annual_series']['next_attempt'] = 1.0
        self._must_reject(change, "test_run385_and_attempt_numbers_are_real_integers_not_booleans")

    def test_reject_bool_annual_attempt(self):
        def change(annual, economic, graph, packet):
            annual['yearly_catalogue_status'][8]['expected_attempt'] = True
        self._must_reject(change, "test_run385_and_attempt_numbers_are_real_integers_not_booleans")

    def test_reject_wrong_historical_predecessor(self):
        def change(annual, economic, graph, packet):
            annual['previous_annual_freeze']['run_number'] = 383
        self._must_reject(change, "test_historical_2022_run384_predecessor_consistent")

    def test_reject_invented_historical_end(self):
        def change(annual, economic, graph, packet):
            graph['last_frozen_historical_segment'] = '2023'
        self._must_reject(change, "test_historical_2022_run384_predecessor_consistent")

    def test_reject_removed_research_year(self):
        def change(annual, economic, graph, packet):
            annual['yearly_catalogue_status'].pop(9)
        self._must_reject(change, "test_exact_2015_to_partial_2026_catalogue_inventory")

    def test_reject_swapped_year_order(self):
        def change(annual, economic, graph, packet):
            annual['yearly_catalogue_status'][8], annual['yearly_catalogue_status'][9] = annual['yearly_catalogue_status'][9], annual['yearly_catalogue_status'][8]
        self._must_reject(change, "test_exact_2015_to_partial_2026_catalogue_inventory")

    def test_reject_made_2025_historically_frozen(self):
        def change(annual, economic, graph, packet):
            annual['yearly_catalogue_status'][10]['research_evidence'] = 'HISTORICALLY_FROZEN'
        self._must_reject(change, "test_unfinished_years_are_blocked_not_auto_selected")

    def test_reject_made_2024_eligible(self):
        def change(annual, economic, graph, packet):
            annual['yearly_catalogue_status'][9]['promotion_eligible'] = True
        self._must_reject(change, "test_unfinished_years_are_blocked_not_auto_selected")

    def test_reject_omitted_prereg_gate(self):
        def change(annual, economic, graph, packet):
            packet['gates'].pop(0)
        self._must_reject(change, "test_unfilled_preregistration_has_exact_research_category_order")

    def test_reject_reordered_prereg_gates(self):
        def change(annual, economic, graph, packet):
            packet['gates'].reverse()
        self._must_reject(change, "test_unfilled_preregistration_has_exact_research_category_order")

    def test_reject_forged_signoff(self):
        def change(annual, economic, graph, packet):
            packet['gates'][14]['signoff'] = 'independent-risk-accepted'
        self._must_reject(change, "test_all_preregistration_categories_have_no_evidence_or_signoff")

    def test_reject_forged_evidence_ref(self):
        def change(annual, economic, graph, packet):
            packet['gates'][4]['evidence_ref'] = 'fabricated://evidence'
        self._must_reject(change, "test_all_preregistration_categories_have_no_evidence_or_signoff")

    def test_reject_forged_prereg_status(self):
        def change(annual, economic, graph, packet):
            packet['gates'][9]['status'] = 'PASS'
        self._must_reject(change, "test_all_preregistration_categories_have_no_evidence_or_signoff")

    def test_reject_missing_cost_sensitivity_requirement(self):
        def change(annual, economic, graph, packet):
            economic['required_evidence_groups']['after_cost_economics'].remove('slippage_sensitivity')
        self._must_reject(change, "test_ten_preregistered_risks_have_matching_economic_evidence_requirements")

    def test_reject_missing_holdout_requirement(self):
        def change(annual, economic, graph, packet):
            economic['required_evidence_groups']['annual_catalogue_and_selection'].remove('unseen_years_not_touched_as_future_final_test')
        self._must_reject(change, "test_ten_preregistered_risks_have_matching_economic_evidence_requirements")

    def test_reject_forged_admin_verification(self):
        def change(annual, economic, graph, packet):
            annual['live_administration_evidence_verified'] = True
        self._must_reject(change, "test_external_administrator_and_fresh_inventory_remain_unproven")

    def test_reject_forged_inventory_verification(self):
        def change(annual, economic, graph, packet):
            economic['annual_series']['independent_fresh_inventory_present'] = True
        self._must_reject(change, "test_external_administrator_and_fresh_inventory_remain_unproven")

    def test_reject_invented_live_authority(self):
        def change(annual, economic, graph, packet):
            annual['authority_flags']['real_money_authorized'] = True
        self._must_reject(change, "test_eighteen_claimed_outcomes_cannot_override_false_authority")

    def test_reject_numeric_false_alias(self):
        def change(annual, economic, graph, packet):
            annual['authority_flags']['run385_authorized'] = 0
        self._must_reject(change, "test_eighteen_claimed_outcomes_cannot_override_false_authority")

    def test_reject_forged_shadow_permission(self):
        def change(annual, economic, graph, packet):
            packet['prospective_shadow_authorized'] = True
        self._must_reject(change, "test_eighteen_claimed_outcomes_cannot_override_false_authority")

    def test_reject_numeric_zero_profit(self):
        def change(annual, economic, graph, packet):
            economic['reported_economic_measurements']['strategy_v1_net_return'] = 0
        self._must_reject(change, "test_no_economic_result_is_zero_filled_or_reused")

    def test_reject_invented_candidate(self):
        def change(annual, economic, graph, packet):
            packet['candidate_strategy_identity'] = 'synthetic-strategy'
        self._must_reject(change, "test_no_economic_result_is_zero_filled_or_reused")

    def test_reject_invented_strategy_profit(self):
        def change(annual, economic, graph, packet):
            graph['live_strategy_v1_profit_evidence'] = 0.20
        self._must_reject(change, "test_no_economic_result_is_zero_filled_or_reused")

    def test_reject_dag_pass_forgery(self):
        def change(annual, economic, graph, packet):
            graph['nodes'][6]['status'] = 'PASS'
        self._must_reject(change, "test_source_only_dependency_graph_fails_closed_for_every_stage")

    def test_reject_dag_evidence_forgery(self):
        def change(annual, economic, graph, packet):
            graph['nodes'][0]['verified_current_evidence'] = True
        self._must_reject(change, "test_source_only_dependency_graph_fails_closed_for_every_stage")

    def test_reject_removed_admin_prerequisite(self):
        def change(annual, economic, graph, packet):
            graph['nodes'][5]['prerequisites'].remove('admin_exclusive_no_bypass_lock')
        self._must_reject(change, "test_run385_requires_five_independent_witnesses_before_one_shot")

    def test_reject_removed_2023_one_shot_dependency(self):
        def change(annual, economic, graph, packet):
            graph['nodes'][6]['prerequisites'] = []
        self._must_reject(change, "test_run385_requires_five_independent_witnesses_before_one_shot")

    def test_reject_skipped_cross_year_step(self):
        def change(annual, economic, graph, packet):
            graph['nodes'][9]['prerequisites'] = ['accepted_remaining_annual_freezes']
        self._must_reject(change, "test_annual_evidence_precedes_cross_year_analysis_and_strategy_v1")

    def test_reject_premature_cross_year(self):
        def change(annual, economic, graph, packet):
            economic['cross_year_comparison_authorized'] = True
        self._must_reject(change, "test_annual_evidence_precedes_cross_year_analysis_and_strategy_v1")

    def test_reject_shadow_before_strategy(self):
        def change(annual, economic, graph, packet):
            graph['nodes'][10]['prerequisites'] = []
        self._must_reject(change, "test_shadow_after_strategy_is_order_impossible_and_separately_blocked")

    def test_reject_fake_demo_approval(self):
        def change(annual, economic, graph, packet):
            economic['demo_approved'] = True
        self._must_reject(change, "test_all_real_money_and_demo_flags_still_false_everywhere")

    def test_reject_skip_phase10(self):
        def change(annual, economic, graph, packet):
            graph['nodes'][13]['prerequisites'] = ['fixed_version_demo_review']
        self._must_reject(change, "test_demo_phase10_and_phase11_are_three_separate_dependencies")

    def test_reject_incorrect_historical_return(self):
        def change(annual, economic, graph, packet):
            packet['known_historical_context']['reported_phase7_net_return_pct_by_slippage_pips']['1.0'] = '99'
        self._must_reject(change, "test_phase7_benchmark_not_a_phase8a_return_or_forward_forecast")

    def test_reject_false_forward_forecast(self):
        def change(annual, economic, graph, packet):
            packet['known_historical_context']['live_return_forecast'] = '+5%'
        self._must_reject(change, "test_phase7_benchmark_not_a_phase8a_return_or_forward_forecast")

    def test_reject_post_hoc_threshold_permission(self):
        def change(annual, economic, graph, packet):
            packet['predefined_thresholds_documented'] = True
        self._must_reject(change, "test_no_retrospective_pass_thresholds_or_invented_selection")

    def test_reject_removed_rejection_outcome(self):
        def change(annual, economic, graph, packet):
            packet['possible_dispositions'].remove('REJECT')
        self._must_reject(change, "test_no_retrospective_pass_thresholds_or_invented_selection")

    def test_reject_approved_live_action(self):
        def change(annual, economic, graph, packet):
            packet['allowed_actions'].append('broker_place_order')
        self._must_reject(change, "test_all_four_sources_have_zero_authorized_actions")

    def test_reject_approved_annual_action(self):
        def change(annual, economic, graph, packet):
            annual['authorized_actions'].append('gh workflow run annual-catalogue')
        self._must_reject(change, "test_all_four_sources_have_zero_authorized_actions")

    def test_reject_numeric_demo_permission(self):
        def change(annual, economic, graph, packet):
            packet['demo_order_authorized'] = 0
        self._must_reject(change, "test_all_real_money_and_demo_flags_still_false_everywhere")

    def test_pristine_controls_all_twenty_three_methods(self):
        methods = sorted(
            name for name in dir(
                joined.PreregistrationFourSourceBoundaryConsistencyTests)
            if name.startswith("test_"))
        self.assertEqual(len(methods), 23)
        for name in methods:
            with self.subTest(method=name):
                case = joined.PreregistrationFourSourceBoundaryConsistencyTests(
                    name)
                case.sources = copy.deepcopy(self.pristine)
                case.annual = case.sources["annual"]
                case.economic = case.sources["economic"]
                case.graph = case.sources["dependency"]
                case.packet = case.sources["preregistration"]
                case.nodes = {node["id"]: node for node in
                              case.graph["nodes"]}
                getattr(case, name)()
