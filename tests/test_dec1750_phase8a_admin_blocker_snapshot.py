"""DEC-1750: record existing unprotected-main blocker without granting authority.

Only static JSON is inspected. No network, admin, workflow, protected
market-data, or broker interactions are performed by this test.
"""
import json
from pathlib import Path
import unittest

PACKET = Path(__file__).resolve().parents[1] / "docs" / (
    "dec1750-phase8a-admin-blocker-evidence-snapshot.json")
PROOF_IDS = (
    "effective_github_admin_and_inherited_ruleset_inventory",
    "exclusive_continuous_ref_lock_and_no_bypass",
    "independent_reviewed_source_sha_workflow_identity",
    "installed_three_job_precheckout_preinstall_preaccess_enforcement",
    "privileged_runner_os_isolation_and_publisher_witness",
    "frozen_dec609_dec610_provenance_reauthentication",
    "fresh_complete_authoritative_one_shot_annual_run_inventory",
    "separate_2023_run385_attempt1_human_execution_decision",
)
DOWNSTREAM = (
    "annual_2023", "remaining_annual_years", "cross_year_economics",
    "strategy_v1", "prospective_shadow", "demo", "phase10",
    "phase11_real_money",
)


def _unique_pairs(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError("duplicate snapshot object key")
        seen[key] = value
    return seen


class AdminBlockerSourceOnlySnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = PACKET.read_text(encoding="utf-8")
        cls.doc = json.loads(cls.raw, object_pairs_hook=_unique_pairs)

    def test_packet_identity_and_nonauthorizing_kind(self):
        self.assertEqual(self.doc["schema"],
                         "fmp_dec1750_phase8a_external_authority_blocker_snapshot_v1")
        self.assertEqual(self.doc["decision"], "DEC-1750")
        self.assertEqual(self.doc["kind"],
                         "READ_ONLY_SOURCE_DOCUMENTATION_NOT_INDEPENDENT_ATTESTATION")

    def test_observation_date_is_explicit_and_not_a_future_witness(self):
        self.assertEqual(self.doc["observed_date_utc"], "2026-10-19")
        self.assertIs(self.doc["public_observation"]["observation_current_at_future_action_time"], False)

    def test_main_ref_and_sha_match_the_read_only_snapshot(self):
        public = self.doc["public_observation"]
        self.assertEqual(public["main_ref"], "refs/heads/main")
        self.assertEqual(public["observed_main_sha"],
                         "53e203133bbc141b2f48c7b8b8241d56b35166a3")

    def test_main_is_not_protected_in_this_capture(self):
        public = self.doc["public_observation"]
        self.assertIs(type(public["main_branch_protected"]), bool)
        self.assertIs(public["main_branch_protected"], False)

    def test_zero_observed_repo_rulesets_is_not_all_inherited_rulesets_proven(self):
        public = self.doc["public_observation"]
        self.assertIs(type(public["repo_rulesets_count"]), int)
        self.assertEqual(public["repo_rulesets_count"], 0)
        self.assertIs(public["inherited_org_ruleset_scope_verified"], False)

    def test_no_effective_independent_administrator_scope_attested(self):
        public = self.doc["public_observation"]
        self.assertIs(public["independent_admin_scope_verified"], False)
        self.assertIs(public["proof_of_effective_exclusive_lock"], False)

    def test_historical_2022_run384_not_credential_for_a_future_run(self):
        history = self.doc["historical_provenance"]
        self.assertEqual(history["historical_freeze_segment"], "2022")
        self.assertIs(type(history["historical_freeze_run"]), int)
        self.assertEqual(history["historical_freeze_run"], 384)
        self.assertEqual(history["historical_freeze_run_id"], 37663157285)
        self.assertIs(history["independently_reauthenticated_for_future_dispatch"], False)

    def test_next_year_exact_one_shot_integer_identity(self):
        action = self.doc["next_protected_action"]
        self.assertEqual(action["segment"], "2023")
        self.assertIs(type(action["run_number"]), int)
        self.assertIs(type(action["attempt_number"]), int)
        self.assertEqual((action["run_number"], action["attempt_number"]), (385, 1))

    def test_fresh_inventory_and_one_shot_consumption_are_unverified(self):
        action = self.doc["next_protected_action"]
        self.assertIs(action["run_inventory_currently_independently_verified"], False)
        self.assertIs(action["run_385_unconsumed_currently_independently_proven"], False)

    def test_dispatch_or_retry_are_not_authorized(self):
        action = self.doc["next_protected_action"]
        self.assertIs(action["dispatch_authorized"], False)
        self.assertIs(action["retry_authorized"], False)

    def test_exactly_two_mutually_unselected_remediation_routes(self):
        routes = self.doc["remediation_routes"]
        self.assertEqual(tuple(item["id"] for item in routes), (
            "ADMIN_EXCLUSIVE_CONTINUOUS_MAIN_LOCK",
            "SEPARATELY_APPROVED_IMMUTABLE_REF_CODE_AMENDMENT",
        ))
        self.assertTrue(all(item["status"] == "BLOCKED" for item in routes))
        self.assertTrue(all(item["selected"] is False for item in routes))
        self.assertTrue(all(item["independently_reviewed"] is False for item in routes))

    def test_admin_lock_route_includes_no_bypass_and_dispatch_continuity(self):
        claim = self.doc["remediation_routes"][0]["required_claim"]
        self.assertIn("complete server-side dispatch", claim)
        self.assertIn("bypass actors", claim)
        self.assertIn("deletion/recreation", claim)

    def test_immutable_route_is_not_an_unreviewed_source_change(self):
        claim = self.doc["remediation_routes"][1]["required_claim"]
        self.assertIn("source-of-truth amendment", claim)
        self.assertIn("fully retested installed workflow/runtime", claim)

    def test_eight_distinct_external_proofs_are_explicitly_unavailable(self):
        proofs = self.doc["external_proofs"]
        self.assertEqual(tuple(item["id"] for item in proofs), PROOF_IDS)
        self.assertEqual(len(proofs), len(set(item["id"] for item in proofs)))
        for item in proofs:
            with self.subTest(proof=item["id"]):
                self.assertEqual(set(item), {
                    "id", "status", "evidence_ref", "reviewer_signoff"
                })
                self.assertEqual(item["status"], "MISSING")
                self.assertIsNone(item["evidence_ref"])
                self.assertIsNone(item["reviewer_signoff"])

    def test_downstream_gate_inventory_is_exact_and_still_blocked(self):
        state = self.doc["downstream_gate_state"]
        self.assertEqual(tuple(state), DOWNSTREAM)
        self.assertTrue(all(state[value] == "BLOCKED" for value in DOWNSTREAM))

    def test_profit_and_strategy_selection_remain_unknown_not_zero(self):
        self.assertIsNone(self.doc["measured_strategy_v1_profit"])
        self.assertIsNone(self.doc["candidate_strategy_identity"])

    def test_no_active_execution_or_broker_action_may_be_derived(self):
        self.assertEqual(self.doc["approved_actions"], [])
        self.assertEqual(self.doc["release_status"], "BLOCKED")
        for flag in ("one_shot_annual_action_authorized",
                     "broker_action_authorized",
                     "trading_authorized",
                     "snapshot_authorizes_anything"):
            with self.subTest(flag=flag):
                self.assertIs(type(self.doc[flag]), bool)
                self.assertIs(self.doc[flag], False)

    def test_snapshot_expressly_cannot_authorize_dispatch_or_trades(self):
        self.assertIn("cannot authorize any workflow dispatch", self.doc["caveat"])
        self.assertIn("any trade", self.doc["caveat"])

    def test_duplicate_nested_member_refused_by_real_json_loader(self):
        with self.assertRaisesRegex(ValueError, "duplicate snapshot object key"):
            json.loads('{"public_observation":{"main_branch_protected":false,'
                       '"main_branch_protected":true}}',
                       object_pairs_hook=_unique_pairs)

    def test_no_embedded_write_or_execution_instructions(self):
        for forbidden in ("gh workflow run ", "git push --force",
                          "place_order(", '"approved_actions": [\n    "'):
            self.assertNotIn(forbidden, self.raw)
