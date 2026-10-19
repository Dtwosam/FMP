"""DEC-1743: detect bypass attempts on the source-only Phase8A DAG.

All mutations use isolated deep copies of a nonauthorizing JSON document.
They cannot change a GitHub gate, annual runner, market state or broker.
"""
import copy
import json
import unittest

import test_dec1742_blocked_dependency_graph as graph


class Phase8ADependencyBypassMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(
            graph.PATH.read_text(encoding="utf-8"),
            object_pairs_hook=graph._unique_pairs,
        )

    def _mutate(self, change):
        mutated = copy.deepcopy(self.original)
        change(mutated)
        self.assertNotEqual(
            json.dumps(mutated, sort_keys=True, separators=(",", ":")),
            json.dumps(self.original, sort_keys=True, separators=(",", ":")),
        )
        return mutated

    def _expect_shape_rejects(self, change):
        mutated = self._mutate(change)
        with self.assertRaises(AssertionError):
            graph._validate(mutated)
        self.assertEqual(
            self.original,
            json.loads(graph.PATH.read_text(encoding="utf-8"),
                       object_pairs_hook=graph._unique_pairs),
        )

    def _expect_existing_stage_guard_rejects(self, change, method):
        mutated = self._mutate(change)
        predecessors = graph._validate(mutated)
        case = graph.Phase8ABlockedDependencyGraphTests(method)
        case.doc = mutated
        case.dependencies = predecessors
        with self.assertRaises(AssertionError):
            getattr(case, method)()
        self.assertEqual(
            self.original,
            json.loads(graph.PATH.read_text(encoding="utf-8"),
                       object_pairs_hook=graph._unique_pairs),
        )

    def test_rejects_forged_completed_stage(self):
        self._expect_shape_rejects(
            lambda d: d["nodes"][5].__setitem__("status", "PASS"))

    def test_rejects_forged_independent_witness(self):
        self._expect_shape_rejects(
            lambda d: d["nodes"][0].__setitem__(
                "verified_current_evidence", True))

    def test_rejects_forged_authorized_execution(self):
        self._expect_shape_rejects(
            lambda d: d["nodes"][6].__setitem__(
                "authorizes_execution", True))

    def test_rejects_dag_forward_edge_before_approval(self):
        self._expect_shape_rejects(
            lambda d: d["nodes"][0]["prerequisites"].append(
                "separate_phase11_real_money_approval"))

    def test_rejects_duplicate_prerequisite(self):
        self._expect_shape_rejects(
            lambda d: d["nodes"][5]["prerequisites"].append(
                "admin_exclusive_no_bypass_lock"))

    def test_rejects_missing_external_witness(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d["nodes"][5].__setitem__(
                "prerequisites", []),
            "test_all_five_independent_external_witnesses_gate_one_shot")

    def test_rejects_run385_without_one_shot(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d["nodes"][6].__setitem__(
                "prerequisites", []),
            "test_no_annual_execution_without_distinct_one_shot_decision")

    def test_rejects_later_years_without_2023(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d["nodes"][7].__setitem__(
                "prerequisites", []),
            "test_later_years_require_accepted_2023_predecessor")

    def test_rejects_cross_year_without_annual(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d["nodes"][8].__setitem__(
                "prerequisites", []),
            "test_cross_year_research_requires_every_annual_freeze")

    def test_rejects_strategy_without_cross_year(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d["nodes"][9].__setitem__(
                "prerequisites", []),
            "test_strategy_v1_requires_cross_year_economics")

    def test_rejects_shadow_without_strategy(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d["nodes"][10].__setitem__(
                "prerequisites", []),
            "test_shadow_requires_frozen_strategy_and_remains_order_impossible")

    def test_rejects_demo_without_shadow(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d["nodes"][11].__setitem__(
                "prerequisites", []),
            "test_demo_and_phase10_and_phase11_have_distinct_predecessors")

    def test_rejects_phase10_without_demo(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d["nodes"][12].__setitem__(
                "prerequisites", []),
            "test_demo_and_phase10_and_phase11_have_distinct_predecessors")

    def test_rejects_phase11_without_phase10(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d["nodes"][13].__setitem__(
                "prerequisites", []),
            "test_demo_and_phase10_and_phase11_have_distinct_predecessors")

    def test_rejects_boolean_run_attempt_alias(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d.__setitem__("next_expected_attempt", True),
            "test_historical_year_and_unique_2023_attempt_not_authority")

    def test_rejects_broker_action_in_empty_actions(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d["already_authorized_actions"].append(
                "broker_place_order"),
            "test_no_economic_measurement_or_approved_action")

    def test_rejects_invented_live_profit_measurement(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d.__setitem__("live_strategy_v1_profit_evidence", 0),
            "test_no_economic_measurement_or_approved_action")

    def test_rejects_fabricated_external_authority(self):
        self._expect_existing_stage_guard_rejects(
            lambda d: d.__setitem__("external_authorization_established",
                                    True),
            "test_no_economic_measurement_or_approved_action")

    def test_original_dependency_graph_passes_all_twelve_guards(self):
        graph.Phase8ABlockedDependencyGraphTests.setUpClass()
        case = graph.Phase8ABlockedDependencyGraphTests(
            "test_exact_ordered_stages_and_no_forward_edges")
        case.doc = copy.deepcopy(self.original)
        case.dependencies = graph._validate(case.doc)
        methods = [name for name in dir(case) if name.startswith("test_")]
        self.assertEqual(len(methods), 12)
        for method in methods:
            with self.subTest(guard=method):
                getattr(case, method)()
