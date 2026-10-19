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


    def test_markdown_review_is_stable_and_permanently_blocked(self):
        result = RENDER(self.docs)
        format_review = MOD["render_human_review_markdown"]
        md = format_review(result)
        self.assertEqual(md, format_review(RENDER(self.docs)))
        self.assertIn("**Documentary status: BLOCKED — NOT AUTHORIZED.**", md)
        self.assertIn("annual run 385 / attempt 1", md)
        self.assertIn("**No action is authorized by this handoff.**", md)
        self.assertEqual(md.count("| **MISSING** |"), 8)
        self.assertNotIn("gh workflow run ", md)

    def test_markdown_lists_each_distinct_required_proof(self):
        rendered = MOD["render_human_review_markdown"](RENDER(self.docs))
        for proof in MOD["PROOFS"]:
            with self.subTest(proof=proof):
                self.assertEqual(rendered.count("`" + proof + "`"), 1)

    def test_markdown_carries_all_five_source_fingerprints(self):
        report = RENDER(self.docs)
        rendered = MOD["render_human_review_markdown"](report)
        for name in FILES:
            with self.subTest(name=name):
                self.assertIn("sha256:" + report["source_sha256"][name], rendered)

    def test_markdown_reports_eight_downstream_blocks(self):
        rendered = MOD["render_human_review_markdown"](RENDER(self.docs))
        for stage in MOD["STAGES"]:
            with self.subTest(stage=stage):
                self.assertIn("`" + stage + "` — BLOCKED", rendered)

    def test_markdown_rejects_any_forged_unblocked_or_live_claim(self):
        base = RENDER(self.docs)
        fmt = MOD["render_human_review_markdown"]
        for field, value in (
            ("documentary_status", "READY"),
            ("allows_protected_run", True),
            ("allows_live_trading", 0),
            ("current_main_verified", True),
            ("fresh_run_inventory_verified", True),
            ("strategy_v1_profit", 100.0),
        ):
            with self.subTest(field=field):
                modified = copy.deepcopy(base)
                modified[field] = value
                with self.assertRaises(FAILURE):
                    fmt(modified)

    def test_markdown_rejects_missing_human_proof_rows(self):
        result = RENDER(self.docs)
        result["missing_external_proofs"].pop()
        with self.assertRaises(FAILURE):
            MOD["render_human_review_markdown"](result)

    def test_markdown_rejects_a_fabricated_human_signoff(self):
        result = RENDER(self.docs)
        result["missing_external_proofs"][0]["status"] = "PASS"
        with self.assertRaises(FAILURE):
            MOD["render_human_review_markdown"](result)

    def test_markdown_rejects_omitted_downstream_gate(self):
        result = RENDER(self.docs)
        result["blocked_downstream_stages"].pop()
        with self.assertRaises(FAILURE):
            MOD["render_human_review_markdown"](result)

    def test_markdown_fails_closed_on_untrusted_source_hash(self):
        result = RENDER(self.docs)
        result["source_sha256"]["annual"] = "0" * 63 + "G"
        with self.assertRaises(FAILURE):
            MOD["render_human_review_markdown"](result)

    def test_markdown_cli_stdout_is_a_read_only_non_permission_handoff(self):
        import contextlib
        import io
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = MOD["main"]([
                "--docs-root", str(self.docs), "--format", "markdown"])
        self.assertEqual(status, 0)
        self.assertIn("NOT AUTHORIZED", output.getvalue())
        self.assertNotIn('"documentary_status":', output.getvalue())

    def test_json_cli_default_preserves_deterministic_machine_consumption(self):
        import contextlib
        import io
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = MOD["main"](["--docs-root", str(self.docs)])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue()), RENDER(self.docs))



    def test_markdown_real_backticks_are_not_backslash_escaped(self):
        markdown = MOD["render_human_review_markdown"](RENDER(self.docs))
        tick = chr(96)
        self.assertIn(tick + "main" + tick, markdown)
        self.assertIn(tick + "annual_2023" + tick + " — BLOCKED", markdown)
        self.assertNotIn(chr(92) + tick, markdown)

    def test_markdown_source_digest_is_printable_code_span(self):
        markdown = MOD["render_human_review_markdown"](RENDER(self.docs))
        tick = chr(96)
        self.assertIn(tick + "sha256:", markdown)
        self.assertIn(
            tick + "dec1750-phase8a-admin-blocker-evidence-snapshot.json" + tick,
            markdown)

    def test_markdown_cli_missing_source_fails_closed_without_stdout(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as dirname:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                exit_code = MOD["main"]([
                    "--docs-root", dirname, "--format", "markdown"])
            self.assertEqual(exit_code, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("BLOCKED: source evidence cannot be trusted",
                          err.getvalue())

    def test_markdown_cli_forged_annual_year_fails_closed_without_stdout(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            for filename in FILES.values():
                (root / filename).write_bytes(
                    (self.docs / filename).read_bytes())
            target = root / FILES["annual"]
            packet = json.loads(target.read_text(encoding="utf-8"))
            packet["yearly_catalogue_status"][9][
                "research_evidence"] = "HISTORICALLY_FROZEN"
            target.write_text(
                json.dumps(packet, sort_keys=True) + "\n", encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                exit_code = MOD["main"]([
                    "--docs-root", dirname, "--format", "markdown"])
            self.assertEqual(exit_code, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("BLOCKED:", err.getvalue())



    def test_human_review_criteria_cover_every_missing_external_proof(self):
        criteria = MOD["PROOF_ACCEPTANCE_CRITERIA"]
        self.assertEqual(tuple(criteria), MOD["PROOFS"])
        self.assertTrue(all(isinstance(value, str) and value.strip()
                            for value in criteria.values()))

    def test_human_review_sheet_has_explicit_independent_acceptance_evidence(self):
        md = MOD["render_human_review_markdown"](RENDER(self.docs))
        self.assertIn("| Required independent evidence |", md)
        self.assertIn("organization and enterprise protection", md)
        self.assertIn("server ref resolution", md)
        self.assertIn("all 18 cells and freeze jobs", md)
        self.assertIn("UID/caps/mount and alias isolation", md)
        self.assertIn("immutable predecessor 2022 freeze", md)
        self.assertIn("no consumed run385 or later run", md)
        self.assertIn("rollback/irreversible no-retry", md)
        self.assertEqual(md.count("| **MISSING** |"), 8)

    def test_human_review_evidence_descriptions_do_not_grant_action(self):
        md = MOD["render_human_review_markdown"](RENDER(self.docs))
        self.assertNotIn("gh workflow run ", md)
        self.assertNotIn("Authorization: PASS", md)
        self.assertIn("**No action is authorized by this handoff.**", md)
        self.assertIn("**execution and retry: BLOCKED**", md)

    def test_evidence_acceptance_criteria_are_not_dynamic_signoffs(self):
        report = RENDER(self.docs)
        self.assertTrue(all(row["status"] == "MISSING"
                            for row in report["missing_external_proofs"]))
        self.assertFalse(report["allows_protected_run"])
        md = MOD["render_human_review_markdown"](report)
        self.assertIn("**Documentary status: BLOCKED", md)



    def test_economic_review_rejects_missing_slippage_sensitivity(self):
        self._tamper("economics", lambda d: d['required_evidence_groups']['after_cost_economics'].remove('slippage_sensitivity'))

    def test_economic_review_rejects_missing_failure_years(self):
        self._tamper("economics", lambda d: d['required_evidence_groups']['cross_year_failure_and_concentration'].remove('sign_reversals_and_failure_years'))

    def test_economic_review_rejects_missing_multiplicity(self):
        self._tamper("economics", lambda d: d['required_evidence_groups']['annual_catalogue_and_selection'].remove('pattern_search_budget_and_multiplicity'))

    def test_economic_review_rejects_missing_nonqualifiers(self):
        self._tamper("economics", lambda d: d['required_evidence_groups']['annual_catalogue_and_selection'].remove('failed_and_negative_pattern_inventory'))

    def test_economic_review_rejects_missing_holdout_disclosure(self):
        self._tamper("economics", lambda d: d['required_evidence_groups']['annual_catalogue_and_selection'].remove('unseen_years_not_touched_as_future_final_test'))

    def test_economic_review_rejects_missing_commission(self):
        self._tamper("economics", lambda d: d['required_evidence_groups']['after_cost_economics'].remove('commission_and_rollover_when_relevant'))

    def test_economic_review_rejects_missing_drawdown_tail(self):
        self._tamper("economics", lambda d: d['required_evidence_groups']['after_cost_economics'].remove('drawdown_and_tail_events'))

    def test_economic_review_rejects_missing_portfolio_correlation(self):
        self._tamper("economics", lambda d: d['required_evidence_groups']['after_cost_economics'].remove('portfolio_correlated_usd_exposure'))

    def test_economic_review_rejects_missing_shadow_no_order(self):
        self._tamper("economics", lambda d: d['required_evidence_groups']['prospective_follow_through'].remove('predeclared_live_shadow_no_order_policy'))

    def test_economic_review_rejects_missing_phase11_human_gate(self):
        self._tamper("economics", lambda d: d['required_evidence_groups']['prospective_follow_through'].remove('phase10_and_phase11_separate_human_authorizations'))

    def test_economic_review_rejects_hidden_reordered_economic_requirement(self):
        self._tamper("economics", lambda d: d['required_evidence_groups']['after_cost_economics'].reverse())

    def test_economic_review_rejects_weakened_prereg_cost_proof(self):
        self._tamper("preregistration", lambda d: d['gates'][7].__setitem__('required_evidence', 'profitable results'))

    def test_economic_review_rejects_weakened_prereg_multiplicity(self):
        self._tamper("preregistration", lambda d: d['gates'][4].__setitem__('required_evidence', 'choose the best'))

    def test_economic_review_rejects_weakened_prereg_oos(self):
        self._tamper("preregistration", lambda d: d['gates'][11].__setitem__('required_evidence', 'historical returns'))

    def test_economic_review_rejects_weakened_no_orders(self):
        self._tamper("preregistration", lambda d: d['gates'][13].__setitem__('required_evidence', 'go live fast'))

    def test_economic_review_rejects_falsified_observation_date(self):
        self._tamper("admin_snapshot", lambda d: d.__setitem__('observed_date_utc', '2026-10-20'))

    def test_module_entrypoint_has_no_import_time_side_effects(self):
        self.assertIn("render_readiness", MOD)
        self.assertIn("main", MOD)
