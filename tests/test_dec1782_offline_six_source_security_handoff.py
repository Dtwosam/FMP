"""DEC-1782 offline security-review handoff is permanently nonauthorizing."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest

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

    def test_consolidated_handoff_never_invokes_external_permission_or_trading(self):
        report = BUILD()
        self.assertIs(report["no_external_actions_performed"], True)
        self.assertEqual(report["allowed_actions"], [])
        self.assertFalse(report["protected_2023_run385_authorized"])
