"""DEC-1782 offline security-review handoff is permanently nonauthorizing."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "dec1782_offline_security_handoff.py"
MOD = runpy.run_path(str(SCRIPT))
BUILD = MOD["compile_blocked_handoff"]
WORKFLOW = MOD["WORKFLOW"]
FILES = runpy.run_path(str(MOD["DOC_AUDIT"]))["FILES"]


class Phase8AConsolidatedSourceOnlyHandoffTests(unittest.TestCase):
    def test_all_eight_proofs_missing_in_one_review_packet(self):
        report = BUILD()
        self.assertEqual(len(report["eight_missing_independent_proofs"]), 8)
        self.assertTrue(all(
            row["status"] == "MISSING"
            for row in report["eight_missing_independent_proofs"]))

    def test_three_installed_jobs_and_eighteen_cells_reported(self):
        report = BUILD()
        self.assertEqual(
            tuple(report["installed_jobs_pregate_and_runtime_gate"]),
            ("annual_preflight", "annual_cell", "annual_freeze"),
        )
        self.assertEqual(report["installed_historical_cell_count"], 18)
        self.assertEqual(
            report["installed_historical_pair_timeframe_source_count"], 9)

    def test_preflight_actions_expose_actual_read_before_gate(self):
        report = BUILD()
        step = report["installed_jobs_pregate_and_runtime_gate"]["annual_preflight"]
        self.assertEqual(step["runtime_gate_zero_based_index"], 7)
        self.assertIn(
            "Fetch exact accepted EXP-044 source snapshots",
            [row["name"] for row in
             step["observed_setup_and_read_payloads_before_gate"]],
        )

    def test_fixed_stale_source_date_and_2023_one_shot(self):
        report = BUILD()
        self.assertEqual(
            report["source_observation_date_utc_not_current_attestation"],
            "2026-10-19",
        )
        self.assertEqual(
            report["one_shot_run_identity"],
            {"segment": "2023", "run_number": 385,
             "attempt_number": 1, "authorization": "BLOCKED"},
        )

    def test_six_pinned_source_identifiers_are_included(self):
        report = BUILD()
        self.assertEqual(tuple(report["documentary_packet_source_sha256"]),
                         tuple(FILES))
        self.assertEqual(
            report["installed_workflow_historical_git_blob_sha1"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_all_permissions_and_economic_claims_refused(self):
        report = BUILD()
        for key in (
            "continuous_admin_ref_lock_verified",
            "real_runner_os_isolation_verified",
            "fresh_one_shot_inventory_verified",
            "protected_2023_run385_authorized",
            "annual_dispatch_or_retry_authorized",
            "broker_order_or_real_money_authorized",
        ):
            with self.subTest(key=key):
                self.assertIs(report[key], False)
        self.assertIsNone(report["preregistered_strategy_v1_profit"])
        self.assertEqual(report["allowed_actions"], [])

    def test_default_json_is_deterministic_and_nonzero_exit(self):
        a, b = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(a):
            c1 = MOD["main"]([])
        with contextlib.redirect_stdout(b):
            c2 = MOD["main"]([])
        self.assertEqual((c1, c2), (3, 3))
        self.assertEqual(a.getvalue(), b.getvalue())
        self.assertEqual(
            json.loads(a.getvalue())["disposition"],
            "BLOCKED_NO_EXECUTION_PERMISSION",
        )

    def test_markdown_handoff_keeps_missing_proofs_and_blocked(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = MOD["main"](["--format", "markdown"])
        self.assertEqual(status, 3)
        self.assertIn("**BLOCKED. NOT AUTHORIZED.", out.getvalue())
        self.assertEqual(out.getvalue().count("| **MISSING** |"), 8)
        self.assertIn("Zero-based in-job runtime gate index", out.getvalue())
        self.assertIn("NOT A CURRENT DISPATCH REF", out.getvalue())

    def test_forged_one_shot_authority_cannot_render_handoff(self):
        result = BUILD()
        result["annual_dispatch_or_retry_authorized"] = True
        with self.assertRaises(MOD["InvalidHandoff"]):
            MOD["format_blocked_handoff_markdown"](result)

    def test_changed_workflow_fails_both_formats_without_stdout(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "changed.yml"
            path.write_bytes(WORKFLOW.read_bytes() + b"\n# altered\n")
            for fmt in ("json", "markdown"):
                with self.subTest(format=fmt):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        status = MOD["main"]([
                            "--workflow", str(path), "--format", fmt])
                    self.assertEqual(status, 2)
                    self.assertEqual(out.getvalue(), "")
                    self.assertIn("BLOCKED:", err.getvalue())

    def test_changed_documentary_packet_fails_without_stdout(self):
        with tempfile.TemporaryDirectory() as folder:
            docs = Path(folder)
            for filename in FILES.values():
                original = MOD["DOCS"] / filename
                (docs / filename).write_bytes(original.read_bytes())
            target = docs / FILES["admin_snapshot"]
            target.write_bytes(target.read_bytes() + b"\n")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = MOD["main"](["--docs-root", str(docs)])
            self.assertEqual(status, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("BLOCKED:", err.getvalue())


    def test_human_handoff_includes_independent_workflow_sha256(self):
        report = BUILD()
        self.assertEqual(
            report["installed_workflow_historical_source_sha256"],
            "a61fa663b42a680e3ce08f82d7e42f410a30c801d37a19cc82fdb5f8d6fbb29f")
        self.assertFalse(report["protected_2023_run385_authorized"])

    def test_formatter_rejects_forged_proof_identifier_even_if_missing(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["eight_missing_independent_proofs"][0]["id"] = "approval_granted"
        with self.assertRaisesRegex(MOD["InvalidHandoff"], "proof identities"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_rejects_forged_security_review_owner(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["eight_missing_independent_proofs"][1]["review_role"] = (
            "An unqualified auto-approval actor")
        with self.assertRaisesRegex(MOD["InvalidHandoff"], "proof identities"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_rejects_wrong_history_sha_even_with_blocked_flags(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["installed_workflow_historical_source_sha256"] = "0" * 64
        with self.assertRaisesRegex(MOD["InvalidHandoff"], "fingerprints"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_rejects_faked_early_gate_position(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["installed_jobs_pregate_and_runtime_gate"][
            "annual_preflight"]["runtime_gate_zero_based_index"] = 0
        with self.assertRaisesRegex(MOD["InvalidHandoff"], "gate positions"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_rejects_rewritten_stale_main_source(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["source_observation_date_utc_not_current_attestation"] = (
            "2099-01-01")
        with self.assertRaisesRegex(MOD["InvalidHandoff"], "stale source"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_rejects_malicious_human_approval_message(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["human_review_request"] = (
            "APPROVED: dispatch run385 and place a live order")
        with self.assertRaisesRegex(MOD["InvalidHandoff"], "next approval"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_shows_fixture_not_a_current_workflow_attestation(self):
        report = BUILD()
        markdown = MOD["format_blocked_handoff_markdown"](report)
        self.assertIn("frozen historical workflow fixture", markdown)
        self.assertIn("NOT current installed workflow", markdown)
        self.assertIn("**BLOCKED. NOT AUTHORIZED.", markdown)

    def test_markdown_displays_complete_blocked_one_shot_identity(self):
        report = BUILD()
        md = MOD["format_blocked_handoff_markdown"](report)
        self.assertIn("Frozen next run: 385", md)
        self.assertIn("Annual segment: 2023", md)
        self.assertIn("Attempt: 1", md)
        self.assertIn("BLOCKED — no one-shot run may be consumed", md)

    def test_markdown_displays_each_blocked_downstream_stage(self):
        report = BUILD()
        md = MOD["format_blocked_handoff_markdown"](report)
        self.assertEqual(len(report["blocked_downstream_stages"]), 8)
        for stage in report["blocked_downstream_stages"]:
            with self.subTest(stage=stage):
                self.assertIn(f"| {stage} | **BLOCKED** |", md)
        self.assertEqual(md.count(" | **BLOCKED** |"), 8)

    def test_markdown_lists_historic_eighteen_cell_scope_without_attestation(self):
        report = BUILD()
        md = MOD["format_blocked_handoff_markdown"](report)
        self.assertIn("Declared historical research cells: 18", md)
        self.assertIn(
            "Declared historical distinct pair/timeframe input sources: 9", md)
        self.assertIn(
            "not reauthenticated against any live runner", md)
        self.assertIn("NOT CURRENT", md)

    def test_both_human_and_json_formats_remain_nonzero_blocked(self):
        for fmt in ("markdown", "json"):
            with self.subTest(fmt=fmt):
                output, errors = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                    code = MOD["main"](["--format", fmt])
                self.assertEqual(code, 3)
                self.assertEqual(errors.getvalue(), "")
                self.assertTrue(output.getvalue())
        self.assertIs(BUILD()["protected_2023_run385_authorized"], False)


    def test_markdown_numeric_values_never_have_accidental_currency_prefix(self):
        result = BUILD()
        md = MOD["format_blocked_handoff_markdown"](result)
        for exact in (
            "Annual segment: 2023",
            "Frozen next run: 385",
            "Attempt: 1",
            "Declared historical research cells: 18 ",
            "Declared historical distinct pair/timeframe input sources: 9.",
        ):
            with self.subTest(field=exact):
                self.assertIn(exact, md)
        for misleading in (
            "Annual segment: $",
            "Frozen next run: $",
            "Attempt: $",
            "Declared historical research cells: $",
            "Declared historical distinct pair/timeframe input sources: $",
        ):
            self.assertNotIn(misleading, md)

    def test_formatter_refuses_injected_gate_step_name(self):
        import copy
        report = copy.deepcopy(BUILD())
        step = report["installed_jobs_pregate_and_runtime_gate"][
            "annual_preflight"]["observed_setup_and_read_payloads_before_gate"][1]
        step["name"] = "Set up Python\n| fake_approved | **READY** |"
        with self.assertRaisesRegex(
                MOD["InvalidHandoff"], "pre-gate command trace"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_refuses_forged_pre_gate_payload(self):
        import copy
        report = copy.deepcopy(BUILD())
        step = report["installed_jobs_pregate_and_runtime_gate"][
            "annual_cell"]["observed_setup_and_read_payloads_before_gate"][2]
        step["payload"] = "unreviewed pip install script"
        with self.assertRaisesRegex(
                MOD["InvalidHandoff"], "pre-gate command trace"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_refuses_shifted_pre_gate_step_index(self):
        import copy
        report = copy.deepcopy(BUILD())
        step = report["installed_jobs_pregate_and_runtime_gate"][
            "annual_freeze"]["observed_setup_and_read_payloads_before_gate"][1]
        step["zero_based_step_index"] = 0
        with self.assertRaisesRegex(
                MOD["InvalidHandoff"], "pre-gate command trace"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_refuses_missing_preflight_metadata_read(self):
        import copy
        report = copy.deepcopy(BUILD())
        rows = report["installed_jobs_pregate_and_runtime_gate"][
            "annual_preflight"]["observed_setup_and_read_payloads_before_gate"]
        report["installed_jobs_pregate_and_runtime_gate"][
            "annual_preflight"]["observed_setup_and_read_payloads_before_gate"] = [
                x for x in rows if x["name"]
                != "Fetch exact accepted EXP-044 source snapshots"
            ]
        with self.assertRaisesRegex(
                MOD["InvalidHandoff"], "pre-gate command trace"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_preserves_exact_reviewed_steps_when_untampered(self):
        report = BUILD()
        output = MOD["format_blocked_handoff_markdown"](report)
        self.assertIn(
            "Fetch exact accepted EXP-044 source snapshots", output)
        self.assertIn("Install pinned annual catalogue runtime", output)
        self.assertIn("**BLOCKED. NOT AUTHORIZED.", output)

    def test_malformed_nested_step_row_fails_closed_not_attribute_error(self):
        import copy
        for bad in (None, [], "injected", 123, True):
            with self.subTest(value=repr(bad)):
                report = copy.deepcopy(BUILD())
                report["installed_jobs_pregate_and_runtime_gate"][
                    "annual_preflight"][
                        "observed_setup_and_read_payloads_before_gate"] = [
                            bad
                        ]
                with self.assertRaises(MOD["InvalidHandoff"]):
                    MOD["format_blocked_handoff_markdown"](report)

    def test_nested_step_extra_key_is_not_implicitly_authorized(self):
        import copy
        report = copy.deepcopy(BUILD())
        step = report["installed_jobs_pregate_and_runtime_gate"][
            "annual_cell"]["observed_setup_and_read_payloads_before_gate"][0]
        step["new_unknown_approved"] = True
        with self.assertRaisesRegex(
                MOD["InvalidHandoff"], "gate positions"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_nested_step_name_index_and_payload_require_exact_types(self):
        import copy
        for field, invalid in (
            ("name", None),
            ("zero_based_step_index", True),
            ("payload", ["untrusted"]),
        ):
            with self.subTest(field=field):
                report = copy.deepcopy(BUILD())
                step = report["installed_jobs_pregate_and_runtime_gate"][
                    "annual_freeze"][
                        "observed_setup_and_read_payloads_before_gate"][0]
                step[field] = invalid
                with self.assertRaises(MOD["InvalidHandoff"]):
                    MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_rejects_extra_approval_field_on_report(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["broker_execution_permitted_by_reviewer"] = True
        with self.assertRaisesRegex(
                MOD["InvalidHandoff"], "canonical six-source report"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_rejects_missing_schema_or_changed_schema(self):
        import copy
        for mode in ("delete", "rename"):
            with self.subTest(mode=mode):
                report = copy.deepcopy(BUILD())
                if mode == "delete":
                    del report["schema"]
                else:
                    report["schema"] = "approved_handoff_v99"
                with self.assertRaisesRegex(
                        MOD["InvalidHandoff"], "canonical six-source report"):
                    MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_rejects_false_to_zero_numeric_alias(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["no_external_actions_performed"] = 1
        with self.assertRaisesRegex(
                MOD["InvalidHandoff"], "human handoff"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_rejects_modified_ignored_metadata(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["no_external_actions_performed"] = True
        report["self_asserted_approval_comment"] = "READY"
        with self.assertRaisesRegex(
                MOD["InvalidHandoff"], "canonical six-source report"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_formatter_rejects_nonfinite_injected_metadata(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["price_target"] = float("nan")
        with self.assertRaisesRegex(
                MOD["InvalidHandoff"], "nonfinite"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_canonical_handoff_rebuild_is_deterministic_and_blocked(self):
        first = BUILD()
        second = BUILD()
        self.assertEqual(
            json.dumps(first, sort_keys=True, allow_nan=False),
            json.dumps(second, sort_keys=True, allow_nan=False),
        )
        self.assertIn(
            "**BLOCKED. NOT AUTHORIZED.",
            MOD["format_blocked_handoff_markdown"](first),
        )
        self.assertEqual(first["allowed_actions"], [])
        self.assertFalse(first["protected_2023_run385_authorized"])

    def test_human_handoff_includes_all_eight_evidence_acceptance_criteria(self):
        requirements = runpy.run_path(str(MOD["DOC_AUDIT"]))[
            "PROOF_ACCEPTANCE_CRITERIA"]
        md = MOD["format_blocked_handoff_markdown"](BUILD())
        self.assertEqual(len(requirements), 8)
        for proof_id, explanation in requirements.items():
            with self.subTest(proof=proof_id):
                self.assertIn(f"**{proof_id}**", md)
                self.assertIn(explanation, md)
                self.assertIn(f"| {proof_id} |", md)
        self.assertIn("requirements, not attestations", md)

    def test_acceptance_criteria_require_effective_not_only_repo_rules(self):
        md = MOD["format_blocked_handoff_markdown"](BUILD())
        self.assertIn("repository", md)
        self.assertIn("organization and enterprise", md)
        self.assertIn("bypass", md)
        self.assertIn("continuous", md)
        self.assertIn("exclusive", md)

    def test_acceptance_criteria_demand_real_runner_and_fresh_inventory(self):
        md = MOD["format_blocked_handoff_markdown"](BUILD())
        self.assertIn("Real runner UID/caps/mount", md)
        self.assertIn("full workflow dispatch/run-attempt inventory", md)
        self.assertIn("reverified immediately before", md)
        self.assertIn("a separate human run385/attempt1 decision", md)

    def test_detailed_requirements_cannot_convert_blocked_report_to_approval(self):
        report = BUILD()
        md = MOD["format_blocked_handoff_markdown"](report)
        self.assertEqual(md.count("| **MISSING** |"), 8)
        self.assertIn("**BLOCKED. NOT AUTHORIZED.", md)
        self.assertFalse(report["protected_2023_run385_authorized"])
        self.assertIsNone(report["preregistered_strategy_v1_profit"])
        self.assertEqual(report["allowed_actions"], [])

    def test_json_handoff_contains_eight_exact_external_acceptance_requirements(self):
        docs = runpy.run_path(str(MOD["DOC_AUDIT"]))
        report = BUILD()
        criteria = report["independent_proof_acceptance_criteria"]
        self.assertEqual(criteria, docs["PROOF_ACCEPTANCE_CRITERIA"])
        self.assertEqual(tuple(criteria), docs["PROOFS"])
        self.assertEqual(len(criteria), 8)
        self.assertTrue(all(type(value) is str and value.strip()
                            for value in criteria.values()))

    def test_machine_and_human_external_requirements_agree_exactly(self):
        report = BUILD()
        md = MOD["format_blocked_handoff_markdown"](report)
        for proof, requirement in report[
                "independent_proof_acceptance_criteria"].items():
            with self.subTest(proof=proof):
                self.assertIn(f"**{proof}**", md)
                self.assertIn(requirement, md)
        self.assertIn("all missing", md.lower())
        self.assertFalse(report["annual_dispatch_or_retry_authorized"])

    def test_formatter_refuses_unknown_approval_field_in_requirements_map(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["independent_proof_acceptance_criteria"][
            "self_certified_no_bypass_approval"] = "PASSED"
        with self.assertRaisesRegex(
                MOD["InvalidHandoff"], "canonical six-source report"):
            MOD["format_blocked_handoff_markdown"](report)

    def test_machine_readable_proof_criteria_never_grant_execution(self):
        report = BUILD()
        self.assertTrue(report["independent_proof_acceptance_criteria"])
        self.assertEqual(report["disposition"], "BLOCKED_NO_EXECUTION_PERMISSION")
        self.assertFalse(report["protected_2023_run385_authorized"])
        self.assertFalse(report["broker_order_or_real_money_authorized"])
        self.assertEqual(report["allowed_actions"], [])

    def test_markdown_includes_all_exact_historical_pregate_payloads(self):
        report = BUILD()
        md = MOD["format_blocked_handoff_markdown"](report)
        self.assertIn("Exact pinned pre-gate payloads", md)
        for job, state in report["installed_jobs_pregate_and_runtime_gate"].items():
            with self.subTest(job=job):
                self.assertIn(
                    f"### {job}: historical runtime gate at step "
                    f"{state['runtime_gate_zero_based_index']}", md)
                for step in state["observed_setup_and_read_payloads_before_gate"]:
                    self.assertIn(
                        f"**Step {step['zero_based_step_index']}: "
                        f"{step['name']}**", md)
                    self.assertIn(
                        "    " + json.dumps(step["payload"], ensure_ascii=True),
                        md)

    def test_markdown_payloads_are_labeled_nonexecuting_historical_literals(self):
        md = MOD["format_blocked_handoff_markdown"](BUILD())
        self.assertIn("HISTORICAL, NOT CURRENT", md)
        self.assertIn("JSON-escaped literals", md)
        self.assertIn("not a command to run", md)
        self.assertIn("never proves early admission", md)
        self.assertIn("**BLOCKED. NOT AUTHORIZED.", md)

    def test_forged_payload_cannot_reach_detailed_markdown(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["installed_jobs_pregate_and_runtime_gate"]["annual_cell"][
            "observed_setup_and_read_payloads_before_gate"][0]["payload"] = (
                "APPROVED: allow protected annual dispatch and broker orders")
        with self.assertRaises(MOD["InvalidHandoff"]):
            MOD["format_blocked_handoff_markdown"](report)

    def test_detailed_human_handoff_cli_stays_blocked_without_stderr(self):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = MOD["main"](["--format", "markdown"])
        self.assertEqual(code, 3)
        self.assertEqual(errors.getvalue(), "")
        self.assertIn("Exact pinned pre-gate payloads", output.getvalue())
        self.assertIn("**BLOCKED. NOT AUTHORIZED.", output.getvalue())

    @staticmethod
    def _with_forged_documentary_proofs(mutate):
        import copy
        real_run_path = runpy.run_path
        doc_path = str(MOD["DOC_AUDIT"])
        doc_module = real_run_path(doc_path)
        actual_render = doc_module["render_readiness"]

        def altered_render(path):
            report = copy.deepcopy(actual_render(path))
            mutate(report["missing_external_proofs"])
            return report

        def source_swap(path):
            if str(path) == doc_path:
                return dict(doc_module, render_readiness=altered_render)
            return real_run_path(path)

        return mock.patch.object(MOD["runpy"], "run_path",
                                 side_effect=source_swap)

    def test_json_builder_rejects_forged_external_proof_reviewer_role(self):
        def forge(proofs):
            proofs[0]["review_role"] = "Automated self-approval"
        with self._with_forged_documentary_proofs(forge):
            with self.assertRaisesRegex(
                    MOD["InvalidHandoff"], "exact missing roles and shape"):
                BUILD()

    def test_json_builder_rejects_extra_external_approval_field(self):
        def forge(proofs):
            proofs[1]["approved_by_unreviewed_actor"] = True
        with self._with_forged_documentary_proofs(forge):
            with self.assertRaisesRegex(
                    MOD["InvalidHandoff"], "exact missing roles and shape"):
                BUILD()

    def test_json_builder_rejects_nonobject_proof_without_unhandled_crash(self):
        for bad in (None, [], "ready", True):
            with self.subTest(bad=repr(bad)):
                def forge(proofs):
                    proofs[2] = bad
                with self._with_forged_documentary_proofs(forge):
                    with self.assertRaises(MOD["InvalidHandoff"]):
                        BUILD()

    def test_both_cli_formats_reject_forged_roles_without_stdout(self):
        def forge(proofs):
            proofs[7]["review_role"] = "Nobody"
        for fmt in ("json", "markdown"):
            with self.subTest(fmt=fmt):
                out, err = io.StringIO(), io.StringIO()
                with self._with_forged_documentary_proofs(forge):
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        code = MOD["main"](["--format", fmt])
                self.assertEqual(code, 2)
                self.assertEqual(out.getvalue(), "")
                self.assertIn("BLOCKED:", err.getvalue())

    @staticmethod
    def _with_forged_upstream_report(script_path, reporter_name, modify):
        import copy
        original_run = runpy.run_path
        script_path = str(script_path)
        module = original_run(script_path)
        build_report = module[reporter_name]

        def altered_report(*args, **kwargs):
            report = copy.deepcopy(build_report(*args, **kwargs))
            modify(report)
            return report

        def intercept(path):
            if str(path) == script_path:
                return dict(module, **{reporter_name: altered_report})
            return original_run(path)

        return mock.patch.object(MOD["runpy"], "run_path",
                                 side_effect=intercept)

    def test_compiler_rejects_upstream_shadow_and_demo_approval_claims(self):
        for key in ("allows_shadow", "allows_demo"):
            with self.subTest(key=key):
                def forge(report):
                    report[key] = True
                with self._with_forged_upstream_report(
                        MOD["DOC_AUDIT"], "render_readiness", forge):
                    with self.assertRaisesRegex(
                            MOD["InvalidHandoff"], "non-authorizing"):
                        BUILD()

    def test_compiler_rejects_upstream_documentary_schema_and_decision_drift(self):
        for key, fake in (
            ("schema", "source_only_approved_v2"),
            ("decision", "DEC-APPROVE-385"),
        ):
            with self.subTest(key=key):
                def forge(report):
                    report[key] = fake
                with self._with_forged_upstream_report(
                        MOD["DOC_AUDIT"], "render_readiness", forge):
                    with self.assertRaises(MOD["InvalidHandoff"]):
                        BUILD()

    def test_compiler_rejects_workflow_live_ref_or_fixture_claim_drift(self):
        for key, fake in (
            ("source_sha_and_live_ref_at_dispatch_not_authenticated", False),
            ("source_material", "live_installed_runner_attested"),
            ("source_workflow", ".github/workflows/unreviewed.yml"),
        ):
            with self.subTest(key=key):
                def forge(report):
                    report[key] = fake
                with self._with_forged_upstream_report(
                        MOD["WORKFLOW_AUDIT"], "report_blocked_admission", forge):
                    with self.assertRaisesRegex(
                            MOD["InvalidHandoff"], "no verified execution authority"):
                        BUILD()

    def test_both_cli_formats_reject_forged_shadow_permission_without_stdout(self):
        def forge(report):
            report["allows_shadow"] = True
        for fmt in ("json", "markdown"):
            with self.subTest(fmt=fmt):
                stdout, stderr = io.StringIO(), io.StringIO()
                with self._with_forged_upstream_report(
                        MOD["DOC_AUDIT"], "render_readiness", forge):
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        code = MOD["main"](["--format", fmt])
                self.assertEqual(code, 2)
                self.assertEqual(stdout.getvalue(), "")
                self.assertIn("BLOCKED:", stderr.getvalue())

    def test_consolidated_handoff_never_invokes_external_permission_or_trading(self):
        report = BUILD()
        self.assertIs(report["no_external_actions_performed"], True)
        self.assertEqual(report["allowed_actions"], [])
        self.assertFalse(report["protected_2023_run385_authorized"])
