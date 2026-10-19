"""DEC-1729: adversarial checks of the actual DEC-1728 ledger assertions.

Manipulates deep-copied, source-only JSON, not protected annual evidence.
"""
from __future__ import annotations

import copy
import json
import unittest

import test_dec1728_annual_readiness_ledger_strict_inventory as strict


class Phase8ALedgerAdversarialMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(strict.PATH.read_text(encoding="utf-8"),
                                  object_pairs_hook=strict._no_duplicate_keys)

    def _expect_refusal(self, guard, mutate):
        self.assertIn(guard, {
            "test_exact_top_level_field_inventory",
            "test_exact_authority_name_inventory_and_bool_types",
            "test_historical_rows_have_no_extra_claims_or_statuses",
            "test_later_rows_preserve_exact_blocked_reasons",
            "test_2023_one_shot_is_strict_integer_not_boolean",
            "test_prior_freeze_inventory_is_only_historical",
            "test_observed_branch_does_not_masquerade_as_current_admin_proof",
            "test_economic_status_and_action_list_are_strictly_denied",
        })
        before = copy.deepcopy(self.original)
        modified = copy.deepcopy(before)
        mutate(modified)
        # Python considers True == 1: compare strict JSON scalar types so
        # the adversarial Boolean-for-integer mutation reaches the real guard.
        self.assertNotEqual(
            json.dumps(modified, sort_keys=True, separators=(",", ":")),
            json.dumps(before, sort_keys=True, separators=(",", ":")),
        )
        case = strict.Phase8AReadinessLedgerStrictInventoryTests(guard)
        case.data = modified
        with self.assertRaises(AssertionError):
            getattr(case, guard)()
        self.assertEqual(self.original, before)

    def test_denies_forged_annual_workflow_dispatch_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "annual_workflow_dispatch_authorized", True))

    def test_denies_forged_protected_history_access_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "protected_history_access_authorized", True))

    def test_denies_forged_run385_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "run385_authorized", True))

    def test_denies_forged_run385_executed(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "run385_executed", True))

    def test_denies_forged_retry_or_rerun_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "retry_or_rerun_authorized", True))

    def test_denies_forged_later_years_research_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "later_years_research_authorized", True))

    def test_denies_forged_cross_year_synthesis_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "cross_year_synthesis_authorized", True))

    def test_denies_forged_strategy_promotion_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "strategy_promotion_authorized", True))

    def test_denies_forged_phase8b_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "phase8b_authorized", True))

    def test_denies_forged_broker_mutation_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "broker_mutation_authorized", True))

    def test_denies_forged_demo_orders_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "demo_orders_authorized", True))

    def test_denies_forged_real_money_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "real_money_authorized", True))

    def test_denies_forged_live_orders_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "live_orders_authorized", True))

    def test_denies_forged_trading_authorized(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "trading_authorized", True))

    def test_denies_extra_authorization_flag(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].__setitem__(
                "unstated_admin_approval", True))

    def test_denies_missing_authorization_flag(self):
        self._expect_refusal(
            "test_exact_authority_name_inventory_and_bool_types",
            lambda document: document["authority_flags"].pop(
                "annual_workflow_dispatch_authorized"))

    def test_denies_nonempty_authorized_actions(self):
        self._expect_refusal(
            "test_economic_status_and_action_list_are_strictly_denied",
            lambda document: document["authorized_actions"].append(
                "annual_2023_dispatch"))

    def test_denies_nonsensical_authorized_actions_boolean(self):
        self._expect_refusal(
            "test_economic_status_and_action_list_are_strictly_denied",
            lambda document: document.__setitem__("authorized_actions", False))

    def test_denies_extra_root_member(self):
        self._expect_refusal(
            "test_exact_top_level_field_inventory",
            lambda document: document.__setitem__("safety_override", True))

    def test_denies_missing_root_member(self):
        self._expect_refusal(
            "test_exact_top_level_field_inventory",
            lambda document: document.pop("external_gate_status"))

    def test_denies_prior_freeze_provenance_upgrade(self):
        self._expect_refusal(
            "test_prior_freeze_inventory_is_only_historical",
            lambda document: document["previous_annual_freeze"].__setitem__(
                "source_provenance", "NOW_LIVE_APPROVED"))

    def test_denies_old_main_claimed_protected(self):
        self._expect_refusal(
            "test_observed_branch_does_not_masquerade_as_current_admin_proof",
            lambda document: document["main_branch_last_public_observation"].__setitem__(
                "protected", True))

    def test_denies_old_main_claimed_current(self):
        self._expect_refusal(
            "test_observed_branch_does_not_masquerade_as_current_admin_proof",
            lambda document: document["main_branch_last_public_observation"].__setitem__(
                "is_current_at_action_time", True))

    def test_denies_false_frozen_2023(self):
        self._expect_refusal(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda document: document["yearly_catalogue_status"][8].__setitem__(
                "research_evidence", "HISTORICALLY_FROZEN"))

    def test_denies_promotion_eligible_2023(self):
        self._expect_refusal(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda document: document["yearly_catalogue_status"][8].__setitem__(
                "promotion_eligible", True))

    def test_denies_false_frozen_2024(self):
        self._expect_refusal(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda document: document["yearly_catalogue_status"][9].__setitem__(
                "research_evidence", "HISTORICALLY_FROZEN"))

    def test_denies_promotion_eligible_2024(self):
        self._expect_refusal(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda document: document["yearly_catalogue_status"][9].__setitem__(
                "promotion_eligible", True))

    def test_denies_false_frozen_2025(self):
        self._expect_refusal(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda document: document["yearly_catalogue_status"][10].__setitem__(
                "research_evidence", "HISTORICALLY_FROZEN"))

    def test_denies_promotion_eligible_2025(self):
        self._expect_refusal(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda document: document["yearly_catalogue_status"][10].__setitem__(
                "promotion_eligible", True))

    def test_denies_false_frozen_2026_ytd(self):
        self._expect_refusal(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda document: document["yearly_catalogue_status"][11].__setitem__(
                "research_evidence", "HISTORICALLY_FROZEN"))

    def test_denies_promotion_eligible_2026_ytd(self):
        self._expect_refusal(
            "test_later_rows_preserve_exact_blocked_reasons",
            lambda document: document["yearly_catalogue_status"][11].__setitem__(
                "promotion_eligible", True))

    def test_denies_wrong_run385_identity(self):
        self._expect_refusal(
            "test_2023_one_shot_is_strict_integer_not_boolean",
            lambda document: document["yearly_catalogue_status"][8].__setitem__(
                "expected_run_number", 386))

    def test_denies_boolean_attempt_one_type_confusion(self):
        self._expect_refusal(
            "test_2023_one_shot_is_strict_integer_not_boolean",
            lambda document: document["yearly_catalogue_status"][8].__setitem__(
                "expected_attempt", True))

    def test_rejects_duplicate_decoded_member_names(self):
        with self.assertRaises(ValueError):
            json.loads(
                '{"run385_authorized":false,'
                '"run385\\u005fauthorized":true}',
                object_pairs_hook=strict._no_duplicate_keys)

    def test_unmodified_control_passes_all_eight_real_guards(self):
        strict.Phase8AReadinessLedgerStrictInventoryTests.setUpClass()
        case = strict.Phase8AReadinessLedgerStrictInventoryTests(
            "test_exact_top_level_field_inventory")
        case.data = copy.deepcopy(self.original)
        for method in (
            "test_exact_top_level_field_inventory",
            "test_exact_authority_name_inventory_and_bool_types",
            "test_historical_rows_have_no_extra_claims_or_statuses",
            "test_later_rows_preserve_exact_blocked_reasons",
            "test_2023_one_shot_is_strict_integer_not_boolean",
            "test_prior_freeze_inventory_is_only_historical",
            "test_observed_branch_does_not_masquerade_as_current_admin_proof",
            "test_economic_status_and_action_list_are_strictly_denied",
        ):
            with self.subTest(guard=method):
                getattr(case, method)()
