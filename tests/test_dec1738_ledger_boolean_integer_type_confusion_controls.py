"""DEC-1738: typed 0/False and 1/True confusion in Phase8A refusals.

Exercises the repaired DEC-1729 mutation harness and real DEC-1728 guards.
These offline tests cannot authenticate or grant GitHub/trading authority.
"""
import json
import unittest

import test_dec1729_phase8a_ledger_mutation_negative_controls as mutations


class LedgerTypedBooleanIntegerConfusionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mutations.Phase8ALedgerAdversarialMutationTests.setUpClass()

    def setUp(self):
        self.guard = mutations.Phase8ALedgerAdversarialMutationTests(
            "test_denies_boolean_attempt_one_type_confusion")

    def _require_existing_guard_refuses(self, guard_name, alter):
        self.guard._expect_refusal(guard_name, alter)

    def test_integer_zero_cannot_spoof_false_annual_workflow_dispatch_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("annual_workflow_dispatch_authorized", 0))

    def test_integer_zero_cannot_spoof_false_protected_history_access_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("protected_history_access_authorized", 0))

    def test_integer_zero_cannot_spoof_false_run385_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("run385_authorized", 0))

    def test_integer_zero_cannot_spoof_false_run385_executed(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("run385_executed", 0))

    def test_integer_zero_cannot_spoof_false_retry_or_rerun_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("retry_or_rerun_authorized", 0))

    def test_integer_zero_cannot_spoof_false_later_years_research_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("later_years_research_authorized", 0))

    def test_integer_zero_cannot_spoof_false_cross_year_synthesis_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("cross_year_synthesis_authorized", 0))

    def test_integer_zero_cannot_spoof_false_strategy_promotion_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("strategy_promotion_authorized", 0))

    def test_integer_zero_cannot_spoof_false_phase8b_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("phase8b_authorized", 0))

    def test_integer_zero_cannot_spoof_false_broker_mutation_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("broker_mutation_authorized", 0))

    def test_integer_zero_cannot_spoof_false_demo_orders_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("demo_orders_authorized", 0))

    def test_integer_zero_cannot_spoof_false_real_money_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("real_money_authorized", 0))

    def test_integer_zero_cannot_spoof_false_live_orders_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("live_orders_authorized", 0))

    def test_integer_zero_cannot_spoof_false_trading_authorized(self):
        self._require_existing_guard_refuses(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda d: d["authority_flags"].__setitem__("trading_authorized", 0))

    def test_integer_zero_cannot_spoof_blocked_year_2023(self):
        self._require_existing_guard_refuses(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda d: d["yearly_catalogue_status"][8].__setitem__(
                "promotion_eligible", 0))

    def test_integer_zero_cannot_spoof_blocked_year_2024(self):
        self._require_existing_guard_refuses(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda d: d["yearly_catalogue_status"][9].__setitem__(
                "promotion_eligible", 0))

    def test_integer_zero_cannot_spoof_blocked_year_2025(self):
        self._require_existing_guard_refuses(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda d: d["yearly_catalogue_status"][10].__setitem__(
                "promotion_eligible", 0))

    def test_integer_zero_cannot_spoof_blocked_year_2026_ytd(self):
        self._require_existing_guard_refuses(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda d: d["yearly_catalogue_status"][11].__setitem__(
                "promotion_eligible", 0))

    def test_integer_zero_cannot_spoof_main_observation_protected(self):
        self._require_existing_guard_refuses(
            "test_observed_branch_does_not_masquerade_as_current_admin_proof",
            lambda d: d["main_branch_last_public_observation"].__setitem__(
                "protected", 0))

    def test_integer_zero_cannot_spoof_main_observation_is_current_at_action_time(self):
        self._require_existing_guard_refuses(
            "test_observed_branch_does_not_masquerade_as_current_admin_proof",
            lambda d: d["main_branch_last_public_observation"].__setitem__(
                "is_current_at_action_time", 0))

    def test_integer_zero_cannot_spoof_main_observation_proves_exclusive_no_bypass_lock(self):
        self._require_existing_guard_refuses(
            "test_observed_branch_does_not_masquerade_as_current_admin_proof",
            lambda d: d["main_branch_last_public_observation"].__setitem__(
                "proves_exclusive_no_bypass_lock", 0))

    def test_integer_zero_cannot_spoof_economic_status_phase8a_strategy_v1_frozen(self):
        self._require_existing_guard_refuses(
            "test_economic_status_and_action_list_are_strictly_denied",
            lambda d: d.__setitem__("phase8a_strategy_v1_frozen", 0))

    def test_integer_zero_cannot_spoof_economic_status_phase8a_economic_edge_proven(self):
        self._require_existing_guard_refuses(
            "test_economic_status_and_action_list_are_strictly_denied",
            lambda d: d.__setitem__("phase8a_economic_edge_proven", 0))

    def test_integer_zero_cannot_spoof_economic_status_fresh_prospective_shadow_accepted(self):
        self._require_existing_guard_refuses(
            "test_economic_status_and_action_list_are_strictly_denied",
            lambda d: d.__setitem__("fresh_prospective_shadow_accepted", 0))

    def test_integer_zero_cannot_spoof_economic_status_demo_trading_approved(self):
        self._require_existing_guard_refuses(
            "test_economic_status_and_action_list_are_strictly_denied",
            lambda d: d.__setitem__("demo_trading_approved", 0))

    def test_integer_zero_cannot_spoof_economic_status_live_trading_approved(self):
        self._require_existing_guard_refuses(
            "test_economic_status_and_action_list_are_strictly_denied",
            lambda d: d.__setitem__("live_trading_approved", 0))

    def test_integer_zero_cannot_spoof_economic_status_live_administration_evidence_verified(self):
        self._require_existing_guard_refuses(
            "test_economic_status_and_action_list_are_strictly_denied",
            lambda d: d.__setitem__("live_administration_evidence_verified", 0))

    def test_integer_zero_cannot_spoof_economic_status_live_annual_run_385_inventory_verified(self):
        self._require_existing_guard_refuses(
            "test_economic_status_and_action_list_are_strictly_denied",
            lambda d: d.__setitem__("live_annual_run_385_inventory_verified", 0))

    def test_boolean_true_cannot_masquerade_as_attempt_one(self):
        self._require_existing_guard_refuses(
            "test_2023_one_shot_is_strict_integer_not_boolean",
            lambda d: d["yearly_catalogue_status"][8].__setitem__(
                "expected_attempt", True))

    def test_canonical_json_distinguishes_all_bool_integer_aliases(self):
        aliases = ((False, 0), (True, 1))
        for boolean, integer in aliases:
            with self.subTest(boolean=boolean, integer=integer):
                self.assertEqual(boolean, integer)
                self.assertIsNot(type(boolean), type(integer))
                self.assertNotEqual(
                    json.dumps({"value": boolean}, sort_keys=True),
                    json.dumps({"value": integer}, sort_keys=True),
                )
