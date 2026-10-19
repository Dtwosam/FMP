"""DEC-1733: mutate source-only Phase 8A boundaries to test DEC-1732.

No source document or protected annual artifact is modified; all tampering
is isolated to per-test in-memory string and JSON dictionary copies.
"""
import copy
import unittest

import test_dec1732_phase8a_crossdocument_boundary_reconciliation as boundary


ATTRS = ("ledger", "state", "build", "owner", "economics", "handoff")


class Phase8ACrossDocumentMutationNegativeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        boundary.Phase8ACrossDocumentSourceOnlyBoundaryTests.setUpClass()
        cls.expected = {
            name: copy.deepcopy(
                getattr(boundary.Phase8ACrossDocumentSourceOnlyBoundaryTests,
                        name))
            for name in ATTRS
        }

    def _assert_crossdocument_guard_rejects(self, guard_name, mutate):
        case = boundary.Phase8ACrossDocumentSourceOnlyBoundaryTests(guard_name)
        for name in ATTRS:
            setattr(case, name, copy.deepcopy(self.expected[name]))
        before = {name: copy.deepcopy(getattr(case, name)) for name in ATTRS}
        mutate(case)
        self.assertNotEqual(
            {name: getattr(case, name) for name in ATTRS}, before)
        with self.assertRaises(AssertionError):
            getattr(case, guard_name)()
        for name in ATTRS:
            self.assertEqual(
                getattr(boundary.Phase8ACrossDocumentSourceOnlyBoundaryTests,
                        name),
                self.expected[name],
            )

    def test_detects_false_phase11_current_status(self):
        self._assert_crossdocument_guard_rejects(
            "test_current_state_labels_phase8a_not_live_trading",
            lambda c: setattr(c, "state", c.state.replace(
                "**Current phase:** Phase 8A",
                "**Current phase:** Phase 11", 1)))

    def test_detects_phase8b_before_research_phase8a(self):
        self._assert_crossdocument_guard_rejects(
            "test_phase_order_is_consistent_with_human_approval",
            lambda c: setattr(c, "build", c.build.replace(
                "### Phase 8A — Multi-pair, multi-strategy portfolio research",
                "### Phase 8C — Multi-pair, multi-strategy portfolio research",
                1)))

    def test_detects_removed_discovery_first_method(self):
        self._assert_crossdocument_guard_rejects(
            "test_annual_first_discovery_is_governing_not_rule_family",
            lambda c: setattr(c, "owner", c.owner.replace(
                "discovery-first **year-by-year annual pattern catalogue**",
                "rule-family-first **annual catalogue**", 1)))

    def test_detects_forged_2022_predecessor(self):
        self._assert_crossdocument_guard_rejects(
            "test_2022_historical_predecessor_is_not_a_current_attestation",
            lambda c: c.ledger["previous_annual_freeze"].__setitem__(
                "run_number", 385))

    def test_detects_swapped_run385_attempt_identity(self):
        self._assert_crossdocument_guard_rejects(
            "test_2023_one_shot_expected_identity_is_not_an_action",
            lambda c: c.ledger["yearly_catalogue_status"][8].__setitem__(
                "expected_attempt", 2))

    def test_detects_later_year_falsely_frozen(self):
        self._assert_crossdocument_guard_rejects(
            "test_later_years_remain_unapproved_in_all_documents",
            lambda c: c.ledger["yearly_catalogue_status"][9].__setitem__(
                "research_evidence", "HISTORICALLY_FROZEN"))

    def test_detects_old_main_falsely_admitted_as_current(self):
        self._assert_crossdocument_guard_rejects(
            "test_old_main_public_snapshot_is_not_current_authority",
            lambda c: c.ledger["main_branch_last_public_observation"].__setitem__(
                "is_current_at_action_time", True))

    def test_detects_risk_gate_wrongly_passed(self):
        self._assert_crossdocument_guard_rejects(
            "test_read_only_repository_permissions_are_not_an_admin_lock",
            lambda c: c.ledger.__setitem__("external_gate_status", "PASS"))

    def test_detects_forged_phase8a_economic_edge(self):
        self._assert_crossdocument_guard_rejects(
            "test_phase8a_economic_claims_are_not_phase7_profit",
            lambda c: c.ledger.__setitem__(
                "phase8a_economic_edge_proven", True))

    def test_detects_test_counts_falsely_declared_earnings(self):
        self._assert_crossdocument_guard_rejects(
            "test_source_only_ci_and_pr_count_are_not_revenue",
            lambda c: setattr(c, "economics", c.economics.replace(
                "Never count a PR, unittest method",
                "Count a PR, unittest method", 1)))

    def test_detects_forged_shadow_release(self):
        self._assert_crossdocument_guard_rejects(
            "test_prospective_shadow_and_demo_remain_separately_gated",
            lambda c: c.ledger["authority_flags"].__setitem__(
                "phase8b_authorized", True))

    def test_detects_forged_privileged_admin_witness(self):
        self._assert_crossdocument_guard_rejects(
            "test_independent_admin_and_runner_evidence_not_synthetic",
            lambda c: c.ledger.__setitem__(
                "live_administration_evidence_verified", True))

    def test_detects_forged_annual_dispatch_authorization(self):
        self._assert_crossdocument_guard_rejects(
            "test_year_order_cannot_authorize_run_by_document_agreement",
            lambda c: c.ledger["authority_flags"].__setitem__(
                "annual_workflow_dispatch_authorized", True))

    def test_pristine_documents_pass_thirteen_original_guards(self):
        case = boundary.Phase8ACrossDocumentSourceOnlyBoundaryTests(
            "test_current_state_labels_phase8a_not_live_trading")
        for name in ATTRS:
            setattr(case, name, copy.deepcopy(self.expected[name]))
        methods = [name for name in dir(case) if name.startswith("test_")]
        self.assertEqual(len(methods), 13)
        for name in methods:
            with self.subTest(guard=name):
                getattr(case, name)()
