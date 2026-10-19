"""DEC-1742: source-only annual readiness dependency graph validation.

Only local documentation is read. PASS means the *blocked* dependency
inventory is internally consistent, not that any stage is authorized.
"""
import json
from pathlib import Path
import unittest


PATH = (Path(__file__).resolve().parents[1] /
        "docs/dec1742-phase8a-blocked-dependency-graph.json")
ORDER = (
    "admin_exclusive_no_bypass_lock",
    "independent_approved_sha_workflow_runtime",
    "installed_three_job_preaccess_admission",
    "privileged_runner_os_isolation",
    "fresh_authoritative_annual_inventory",
    "separate_2023_run385_one_shot_decision",
    "accepted_2023_run385_freeze",
    "accepted_remaining_annual_freezes",
    "cross_year_pattern_economics",
    "strategy_v1_freeze",
    "prospective_order_impossible_shadow",
    "fixed_version_demo_review",
    "phase10_live_readiness_approval",
    "separate_phase11_real_money_approval",
)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate dependency member")
        result[key] = value
    return result


def _validate(graph):
    assert graph["schema"] == "fmp_dec1742_source_only_blocked_dependency_graph_v1"
    assert graph["decision"] == "DEC-1742"
    nodes = graph["nodes"]
    assert type(nodes) is list and len(nodes) == len(ORDER)
    ids = tuple(node["id"] for node in nodes)
    assert ids == ORDER
    assert len(ids) == len(set(ids))
    positions = {name: index for index, name in enumerate(ids)}
    for node in nodes:
        assert set(node) == {
            "id", "prerequisites", "status",
            "verified_current_evidence", "authorizes_execution",
        }
        assert type(node["prerequisites"]) is list
        assert len(node["prerequisites"]) == len(set(node["prerequisites"]))
        assert node["status"] == "BLOCKED"
        assert node["verified_current_evidence"] is False
        assert node["authorizes_execution"] is False
        for prerequisite in node["prerequisites"]:
            assert prerequisite in positions
            assert positions[prerequisite] < positions[node["id"]]
    return {node["id"]: set(node["prerequisites"]) for node in nodes}


class Phase8ABlockedDependencyGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(PATH.read_text(encoding="utf-8"),
                             object_pairs_hook=_unique_pairs)
        cls.dependencies = _validate(cls.doc)

    def test_exact_ordered_stages_and_no_forward_edges(self):
        self.assertEqual(tuple(self.dependencies), ORDER)

    def test_all_five_independent_external_witnesses_gate_one_shot(self):
        expected = set(ORDER[:5])
        self.assertEqual(self.dependencies[
            "separate_2023_run385_one_shot_decision"], expected)

    def test_no_annual_execution_without_distinct_one_shot_decision(self):
        self.assertEqual(self.dependencies["accepted_2023_run385_freeze"],
                         {"separate_2023_run385_one_shot_decision"})

    def test_later_years_require_accepted_2023_predecessor(self):
        self.assertEqual(self.dependencies["accepted_remaining_annual_freezes"],
                         {"accepted_2023_run385_freeze"})

    def test_cross_year_research_requires_every_annual_freeze(self):
        self.assertEqual(self.dependencies["cross_year_pattern_economics"],
                         {"accepted_remaining_annual_freezes"})

    def test_strategy_v1_requires_cross_year_economics(self):
        self.assertEqual(self.dependencies["strategy_v1_freeze"],
                         {"cross_year_pattern_economics"})

    def test_shadow_requires_frozen_strategy_and_remains_order_impossible(self):
        self.assertEqual(self.dependencies["prospective_order_impossible_shadow"],
                         {"strategy_v1_freeze"})
        self.assertIn("order_impossible", ORDER[10])

    def test_demo_and_phase10_and_phase11_have_distinct_predecessors(self):
        self.assertEqual(self.dependencies["fixed_version_demo_review"],
                         {"prospective_order_impossible_shadow"})
        self.assertEqual(self.dependencies["phase10_live_readiness_approval"],
                         {"fixed_version_demo_review"})
        self.assertEqual(self.dependencies["separate_phase11_real_money_approval"],
                         {"phase10_live_readiness_approval"})

    def test_all_stages_explicitly_blocked_never_fake_verified(self):
        for node in self.doc["nodes"]:
            with self.subTest(stage=node["id"]):
                self.assertEqual(node["status"], "BLOCKED")
                self.assertIs(node["verified_current_evidence"], False)
                self.assertIs(node["authorizes_execution"], False)

    def test_historical_year_and_unique_2023_attempt_not_authority(self):
        self.assertEqual(self.doc["last_frozen_historical_segment"], "2022")
        self.assertEqual(self.doc["next_protected_segment"], "2023")
        self.assertIs(type(self.doc["next_expected_run_number"]), int)
        self.assertIs(type(self.doc["next_expected_attempt"]), int)
        self.assertEqual(self.doc["next_expected_run_number"], 385)
        self.assertEqual(self.doc["next_expected_attempt"], 1)

    def test_no_economic_measurement_or_approved_action(self):
        self.assertIsNone(self.doc["live_strategy_v1_profit_evidence"])
        self.assertEqual(self.doc["already_authorized_actions"], [])
        self.assertIs(self.doc["external_authorization_established"], False)

    def test_source_only_document_not_a_runtime_command(self):
        raw = PATH.read_text(encoding="utf-8")
        self.assertIn("not validated security controls", raw)
        self.assertNotIn("gh workflow run ", raw)
        self.assertNotIn("gh api --method POST", raw)
