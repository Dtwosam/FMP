"""DEC-1752: source-only offline blocker report refuses forged readiness.

Tests never invoke GitHub or a broker, and write only temporary JSON copies.
"""
import copy
import json
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "dec1752_phase8a_readiness_report.py"
MOD = runpy.run_path(str(SCRIPT))
RENDER = MOD["render_readiness"]
FILES = MOD["FILES"]
FAILURE = MOD["InvalidDocumentaryState"]


class OfflineBlockerDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = ROOT / "docs"

    def _tamper(self, file_key, mutate):
        with tempfile.TemporaryDirectory() as d:
            temp = Path(d)
            for filename in FILES.values():
                (temp / filename).write_bytes((self.docs / filename).read_bytes())
            target = temp / FILES[file_key]
            original = json.loads(target.read_text(encoding="utf-8"))
            changed = copy.deepcopy(original)
            mutate(changed)
            self.assertNotEqual(
                json.dumps(changed, sort_keys=True, separators=(",", ":")),
                json.dumps(original, sort_keys=True, separators=(",", ":")),
                "mutation should be observable even for bool/int confusion")
            target.write_text(
                json.dumps(changed, sort_keys=True, indent=2) + "\n",
                encoding="utf-8")
            with self.assertRaises((FAILURE, KeyError, TypeError)):
                RENDER(temp)

    def test_clean_report_cannot_authorize_anything(self):
        result = RENDER(self.docs)
        self.assertEqual(result["documentary_status"], "BLOCKED")
        self.assertTrue(result["no_actions_were_performed"])
        for flag in ("allows_protected_run", "allows_broker_actions",
                     "allows_shadow", "allows_demo", "allows_live_trading"):
            self.assertIs(result[flag], False)

    def test_report_is_reproducible_without_a_clock_or_network(self):
        self.assertEqual(RENDER(self.docs), RENDER(self.docs))

    def test_every_source_is_fingerprinted(self):
        report = RENDER(self.docs)
        self.assertEqual(tuple(report["source_sha256"]), tuple(FILES))
        self.assertTrue(all(len(value) == 64 for value in
                            report["source_sha256"].values()))

    def test_old_sha_does_not_become_fresh_authority(self):
        result = RENDER(self.docs)
        self.assertEqual(result["source_observation_date_utc"], "2026-10-19")
        self.assertIs(result["current_main_verified"], False)
        self.assertIs(result["current_rulesets_and_os_verified"], False)
        self.assertIs(result["fresh_run_inventory_verified"], False)

    def test_exact_eight_missing_human_witnesses(self):
        result = RENDER(self.docs)
        self.assertEqual(len(result["missing_external_proofs"]), 8)
        self.assertTrue(all(item["status"] == "MISSING"
                            for item in result["missing_external_proofs"]))

    def test_exact_eight_blocked_downstream_stages(self):
        result = RENDER(self.docs)
        self.assertEqual(len(result["blocked_downstream_stages"]), 8)
        self.assertIsNone(result["strategy_v1_profit"])

    def test_boolean_run385_alias_is_rejected(self):
        self._tamper("admin_snapshot", lambda d: d["next_protected_action"].__setitem__(
            "run_number", True))

    def test_attempt2_cannot_be_read_as_one_shot(self):
        self._tamper("admin_snapshot", lambda d: d["next_protected_action"].__setitem__(
            "attempt_number", 2))

    def test_unprotected_main_forged_protection_is_rejected(self):
        self._tamper("admin_snapshot", lambda d: d["public_observation"].__setitem__(
            "main_branch_protected", True))

    def test_forged_fresh_current_main_is_rejected(self):
        self._tamper("admin_snapshot", lambda d: d["public_observation"].__setitem__(
            "observation_current_at_future_action_time", True))

    def test_inherited_rulesets_unverified_cannot_be_forged(self):
        self._tamper("admin_snapshot", lambda d: d["public_observation"].__setitem__(
            "inherited_org_ruleset_scope_verified", True))

    def test_fake_external_proof_is_rejected(self):
        self._tamper("admin_snapshot", lambda d: d["external_proofs"][0].__setitem__(
            "status", "PASS"))

    def test_fake_signoff_is_rejected(self):
        self._tamper("admin_snapshot", lambda d: d["external_proofs"][3].__setitem__(
            "reviewer_signoff", "verified"))

    def test_unapproved_route_relabelled_selected_is_rejected(self):
        self._tamper("admin_snapshot", lambda d: d["remediation_routes"][0].__setitem__(
            "selected", True))

    def test_live_stage_unblocked_is_rejected(self):
        self._tamper("admin_snapshot", lambda d: d["downstream_gate_state"].__setitem__(
            "phase11_real_money", "PASS"))

    def test_annual_run_authorization_flag_rejected(self):
        self._tamper("annual", lambda d: d["authority_flags"].__setitem__(
            "run385_authorized", True))

    def test_economic_return_zero_claim_rejected(self):
        self._tamper("economics", lambda d: d["reported_economic_measurements"].__setitem__(
            "strategy_v1_net_return", 0))

    def test_early_cross_year_strategy_shortcut_rejected(self):
        self._tamper("preregistration", lambda d: d.__setitem__(
            "method", "SELECT_STRATEGY_FIRST"))

    def test_approval_graph_promotion_rejected(self):
        self._tamper("dependency", lambda d: d["nodes"][0].__setitem__(
            "authorizes_execution", True))

    def test_new_broker_action_rejected(self):
        self._tamper("admin_snapshot", lambda d: d["approved_actions"].append(
            "broker_place_order"))

    def test_nested_duplicate_json_member_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for filename in FILES.values():
                (root / filename).write_bytes((self.docs / filename).read_bytes())
            target = root / FILES["admin_snapshot"]
            raw = target.read_text(encoding="utf-8")
            target.write_text(raw.replace(
                '"release_status": "BLOCKED",',
                '"release_status": "BLOCKED",\n  "release_status": "PASS",'),
                encoding="utf-8")
            with self.assertRaises(FAILURE):
                RENDER(root)

    def test_missing_required_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                RENDER(Path(d))


    def test_unexpected_snapshot_authority_member_rejected(self):
        self._tamper("admin_snapshot", lambda d: d.__setitem__(
            "broker_execution_approved", True))

    def test_unexpected_annual_authority_member_rejected(self):
        self._tamper("annual", lambda d: d.__setitem__(
            "allow_all_annual_workflows", True))

    def test_missing_annual_flag_name_rejected_even_when_false(self):
        self._tamper("annual", lambda d: d["authority_flags"].__setitem__(
            "run385_authorized", False) or d["authority_flags"].__setitem__(
            "secret_workflow_authorized", d["authority_flags"].pop(
                "run385_executed")))

    def test_extra_provisional_profit_metric_rejected(self):
        self._tamper("economics", lambda d: d["reported_economic_measurements"].__setitem__(
            "strategy_v1_live_return_forecast", "5%"))

    def test_graph_order_or_skipped_shadow_prerequisite_rejected(self):
        self._tamper("dependency", lambda d: d["nodes"][10].__setitem__(
            "prerequisites", []))

    def test_duplicate_review_category_still_blocked_rejected(self):
        self._tamper("preregistration", lambda d: d["gates"][1].__setitem__(
            "id", d["gates"][0]["id"]))

    def test_unapproved_proof_with_extra_verified_key_rejected(self):
        self._tamper("admin_snapshot", lambda d: d["external_proofs"][0].__setitem__(
            "verified", True))

    def test_remediation_route_hidden_authority_rejected(self):
        self._tamper("admin_snapshot", lambda d: d["remediation_routes"][0].__setitem__(
            "authorized", True))

    def test_preregistration_extra_execution_flag_rejected(self):
        self._tamper("preregistration", lambda d: d.__setitem__(
            "allow_broker_orders", True))

    def test_review_category_extra_signoff_booleans_rejected(self):
        self._tamper("preregistration", lambda d: d["gates"][0].__setitem__(
            "signed_off", True))


    def test_2024_frozen_without_2023_dispatched_is_rejected(self):
        self._tamper("annual", lambda d: d["yearly_catalogue_status"][9].__setitem__(
            "research_evidence", "HISTORICALLY_FROZEN"))

    def test_2025_promotion_eligibility_cannot_flip(self):
        self._tamper("annual", lambda d: d["yearly_catalogue_status"][10].__setitem__(
            "promotion_eligible", True))

    def test_2026_partial_segment_cannot_disappear(self):
        self._tamper("annual", lambda d: d["yearly_catalogue_status"].pop())

    def test_duplicate_reordered_historical_segment_is_detected(self):
        self._tamper("annual", lambda d: d["yearly_catalogue_status"][1].__setitem__(
            "segment", "2015"))

    def test_historical_frozen_segment_must_not_become_promotable(self):
        self._tamper("annual", lambda d: d["yearly_catalogue_status"][0].__setitem__(
            "promotion_eligible", True))

    def test_forged_2022_predecessor_run_id_rejected(self):
        self._tamper("annual", lambda d: d["previous_annual_freeze"].__setitem__(
            "run_id", 37663157286))

    def test_claims_2022_predecessor_reauthenticated_rejected(self):
        self._tamper("annual", lambda d: d["previous_annual_freeze"].__setitem__(
            "source_provenance", "FRESHLY_AUTHENTICATED_FOR_DISPATCH"))

    def test_2023_external_admin_prerequisite_cannot_disappear(self):
        self._tamper("annual", lambda d: d["required_external_gates"].pop(0))

    def test_2023_separate_action_prerequisite_cannot_disappear(self):
        self._tamper("annual", lambda d: d["required_external_gates"].pop())

    def test_strategy_v1_claim_while_annual_blocked_rejected(self):
        self._tamper("annual", lambda d: d.__setitem__(
            "phase8a_strategy_v1_frozen", True))

    def test_economic_no_longer_annual_first_rejected(self):
        self._tamper("economics", lambda d: d.__setitem__(
            "research_method", "STRATEGY_FIRST"))

    def test_economic_full_annual_series_forge_rejected(self):
        self._tamper("economics", lambda d: d["annual_series"].__setitem__(
            "full_year_series_frozen", True))

    def test_forged_human_approved_economic_action_rejected(self):
        self._tamper("economics", lambda d: d.__setitem__(
            "human_approved_action", "approved"))

    def test_preregistration_claims_threshold_pass_rejected(self):
        self._tamper("preregistration", lambda d: d.__setitem__(
            "current_disposition", "RESEARCHER_REVIEW_AFTER_ANNUAL_FREEZE"))

    def test_preregistration_negative_disposition_must_remain(self):
        self._tamper("preregistration", lambda d: d["possible_dispositions"].remove(
            "REJECT"))

    def test_phase7_cost_sensitive_negative_return_not_laundered(self):
        self._tamper("preregistration", lambda d: d[
            "known_historical_context"]["reported_phase7_net_return_pct_by_slippage_pips"].__setitem__(
                "1.0", "0.562118"))

    def test_phase7_is_not_phase8a_strategy_v1_oos_rejected(self):
        self._tamper("preregistration", lambda d: d[
            "known_historical_context"].__setitem__(
                "not_phase8a_strategy_v1_results", False))

    def test_forecast_not_substituted_for_unproven_profit(self):
        self._tamper("preregistration", lambda d: d[
            "known_historical_context"].__setitem__(
                "live_return_forecast", "10 percent"))

    def test_stale_main_protected_flag_cannot_be_forged_in_annual(self):
        self._tamper("annual", lambda d: d[
            "main_branch_last_public_observation"].__setitem__(
                "protected", True))

    def test_zero_repo_rulesets_is_not_a_boolean_flag(self):
        self._tamper("admin_snapshot", lambda d: d[
            "public_observation"].__setitem__(
                "repo_rulesets_count", False))

    def test_immutable_remediation_route_retains_separate_amendment(self):
        self._tamper("admin_snapshot", lambda d: d[
            "remediation_routes"][1].__setitem__(
                "required_claim", "all clear"))

    def test_continuous_main_lock_route_mentions_bypass_paths(self):
        self._tamper("admin_snapshot", lambda d: d[
            "remediation_routes"][0].__setitem__(
                "required_claim", "branch protection is enabled"))

    def test_module_entrypoint_has_no_import_time_side_effects(self):
        self.assertIn("render_readiness", MOD)
        self.assertIn("main", MOD)
