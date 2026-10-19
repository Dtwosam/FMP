"""DEC-1779 static-only installed annual workflow admission diagnostics."""
import contextlib
import copy
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "dec1779_annual_workflow_admission_audit.py"
MOD = runpy.run_path(str(SCRIPT))
REPORT = MOD["report_blocked_admission"]
WORKFLOW = ROOT / "tests" / "fixtures" / "dec1779-historical-phase8a-annual-workflow.yml"


class InstalledAnnualWorkflowNonAdmissionTests(unittest.TestCase):
    def test_reviewed_workflow_blob_identity_is_fixed(self):
        result = REPORT()
        self.assertEqual(
            result["historical_source_git_blob_sha1"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1")

    def test_all_three_real_installed_jobs_are_identified(self):
        report = REPORT()
        self.assertEqual(tuple(report["observed_jobs"]),
                         ("annual_preflight", "annual_cell", "annual_freeze"))
        self.assertEqual(report["job_count"], 3)

    def test_checkout_before_any_required_runtime_gate(self):
        jobs = REPORT()["observed_jobs"]
        self.assertEqual(
            {job: value["zero_based_in_job_gate_index"]
             for job, value in jobs.items()},
            {"annual_preflight": 7, "annual_cell": 4, "annual_freeze": 4})
        self.assertTrue(all(value["checkout_before_runtime_gate"]
                            for value in jobs.values()))

    def test_installed_python_and_runtime_setup_appear_before_gate(self):
        report = REPORT()
        self.assertTrue(all(
            set(value["risky_setup_before_gate"]) == {
                "Checkout", "Set up Python",
                "Install pinned annual catalogue runtime"}
            for value in report["observed_jobs"].values()
        ))

    def test_annual_preflight_fetches_source_metadata_before_runtime_gate(self):
        report = REPORT()
        self.assertIs(
            report["observed_jobs"]["annual_preflight"][
                "source_snapshot_metadata_fetch_before_gate"], True)
        self.assertEqual(report["observed_jobs"]["annual_preflight"][
            "zero_based_in_job_gate_index"], 7)

    def test_all_jobs_still_use_mutable_main_after_checkout(self):
        report = REPORT()
        self.assertTrue(all(
            value["requires_mutable_main_ref_in_job"]
            and value["main_ref_check_after_checkout"]
            for value in report["observed_jobs"].values()
        ))

    def test_report_never_claims_pre_checkout_pre_install_or_dispatch(self):
        report = REPORT()
        for key in (
            "precheckout_admission_proven", "preinstall_admission_proven",
            "authoritative_pre_dispatch_ref_lock_proven",
            "protected_2023_run385_attempt1_authorized",
            "annual_research_dispatch_authorized", "broker_or_trading_authorized",
        ):
            with self.subTest(flag=key):
                self.assertIs(report[key], False)
        self.assertEqual(report["allowed_actions"], [])

    def test_static_parser_denies_synthetic_gate_moved_before_checkout(self):
        contents = WORKFLOW.read_text(encoding="utf-8")
        changed = contents.replace(
            "      - name: Checkout",
            "      - name: Modified checkout",
            1)
        self.assertNotEqual(changed, contents)
        with self.assertRaisesRegex(MOD["InvalidStaticEvidence"],
                                    "reviewed pre-gate sequence"):
            MOD["classify_reviewed_step_order"](changed)

    def test_static_parser_denies_missing_first_job_gate(self):
        contents = WORKFLOW.read_text(encoding="utf-8")
        changed = contents.replace(
            "      - name: Require separately authorized annual catalogue execution",
            "      - name: Legacy optional check", 1)
        self.assertNotEqual(changed, contents)
        with self.assertRaisesRegex(MOD["InvalidStaticEvidence"],
                                    "reviewed pre-gate sequence"):
            MOD["classify_reviewed_step_order"](changed)

    def test_static_parser_denies_duplicate_job_block(self):
        contents = WORKFLOW.read_text(encoding="utf-8")
        changed = contents + "\n  annual_freeze:\n    steps:\n      - name: Checkout\n"
        with self.assertRaisesRegex(MOD["InvalidStaticEvidence"],
                                    "missing or duplicate annual job"):
            MOD["extract_job_steps"](changed)

    def test_modified_workflow_source_never_produces_a_complete_report(self):
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "workflow.yml"
            changed.write_bytes(WORKFLOW.read_bytes() + b"\n# editorial drift\n")
            with self.assertRaisesRegex(MOD["InvalidStaticEvidence"],
                                        "reviewed historical source"):
                REPORT(changed)

    def test_valid_blocked_report_cli_exits_three_and_not_zero(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = MOD["main"]([])
        self.assertEqual(status, 3)
        self.assertEqual(stderr.getvalue(), "")
        report = json.loads(stdout.getvalue())
        self.assertFalse(report["annual_research_dispatch_authorized"])

    def test_modified_source_cli_exits_two_without_report(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / "annual.yml"
            bad.write_bytes(WORKFLOW.read_bytes() + b"\n# fake approval")
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = MOD["main"](["--workflow", str(bad)])
            self.assertEqual(status, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("BLOCKED:", stderr.getvalue())


    def test_eighteen_declared_cells_have_exact_symbol_timeframe_horizon_product(self):
        report = REPORT()
        matrix = report["historical_matrix_inventory"]
        self.assertEqual(matrix["historical_cell_count"], 18)
        self.assertEqual(matrix["historical_unique_pair_timeframe_inputs"], 9)
        self.assertEqual(matrix["symbols"], ["EURUSD", "GBPUSD", "USDJPY"])
        self.assertEqual(matrix["timeframes"], ["5m", "15m", "1h"])
        self.assertEqual(matrix["horizons_minutes"], [60, 240])
        self.assertEqual(len(matrix["matrix_cells"]), 18)

    def test_historic_artifact_matrix_is_not_current_source_authorization(self):
        report = REPORT()
        matrix = report["historical_matrix_inventory"]
        self.assertIs(
            matrix["dataset_artifact_ids_and_hashes_not_reauthenticated"], True)
        self.assertIs(
            matrix["historical_matrix_does_not_authorize_market_source_io"], True)
        self.assertIs(report["annual_research_dispatch_authorized"], False)
        self.assertEqual(report["allowed_actions"], [])

    def test_matrix_parser_rejects_one_missing_declared_cell(self):
        data = WORKFLOW.read_text(encoding="utf-8")
        marker = '          - symbol: EURUSD\n            timeframe: 5m\n            horizon: 60\n'
        self.assertIn(marker, data)
        bad = data.replace(marker,
                           '          - symbol: EURUSD\n            timeframe: 5m\n'
                           '            horizon: 60A\n', 1)
        with self.assertRaisesRegex(
                MOD["InvalidStaticEvidence"], "18-cell matrix"):
            MOD["inspect_installed_cell_matrix"](bad)

    def test_matrix_parser_rejects_a_duplicated_cell_key(self):
        data = WORKFLOW.read_text(encoding="utf-8")
        marker = '          - symbol: EURUSD\n            timeframe: 5m\n            horizon: 240\n'
        self.assertIn(marker, data)
        bad = data.replace(marker,
                           '          - symbol: EURUSD\n            timeframe: 5m\n'
                           '            horizon: 60\n', 1)
        with self.assertRaisesRegex(
                MOD["InvalidStaticEvidence"], "18-cell matrix"):
            MOD["inspect_installed_cell_matrix"](bad)

    def test_matrix_parser_rejects_divergent_artifact_digest_for_same_input(self):
        data = WORKFLOW.read_text(encoding="utf-8")
        expected = (
            "feature_zip_sha256: "
            "a466f0a128ea8cdc5818c6756bb71a57767f0c703eec68ad40a680f1bf9b06e2"
        )
        self.assertEqual(data.count(expected), 2)
        original_line = expected
        replacement_line = expected[:-1] + "3"
        self.assertNotEqual(original_line, replacement_line)
        idx = data.index(original_line)
        revised = data[:idx] + replacement_line + data[idx+len(original_line):]
        with self.assertRaisesRegex(
                MOD["InvalidStaticEvidence"], "immutable source artifact lineage"):
            MOD["inspect_installed_cell_matrix"](revised)

    def test_matrix_parser_rejects_broken_job_dependency(self):
        data = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("    needs: annual_preflight\n", data)
        bad = data.replace("    needs: annual_preflight\n",
                           "    needs: unrestricted_job\n", 1)
        with self.assertRaisesRegex(
                MOD["InvalidStaticEvidence"], "job dependency"):
            MOD["inspect_installed_cell_matrix"](bad)

    def test_matrix_parser_rejects_unsafe_parallelization_change(self):
        data = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("      max-parallel: 3\n", data)
        bad = data.replace("      max-parallel: 3\n",
                           "      max-parallel: 18\n", 1)
        with self.assertRaisesRegex(
                MOD["InvalidStaticEvidence"], "parallelization"):
            MOD["inspect_installed_cell_matrix"](bad)

    def test_new_matrix_inventory_still_exits_blocked_not_success(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = MOD["main"]([])
        self.assertEqual(code, 3)
        report = json.loads(out.getvalue())
        self.assertEqual(report["historical_matrix_inventory"][
            "historical_cell_count"], 18)
        self.assertEqual(report["disposition"],
                         "BLOCKED_NOT_EXECUTABLE_AND_NOT_ADMIN_ATTESTED")


    def test_pregate_commands_are_verified_not_only_step_names(self):
        report = REPORT()
        for job, item in report["historical_pregate_payloads"].items():
            with self.subTest(job=job):
                steps = item["actual_pregate_setup_and_read_payloads"]
                self.assertEqual(steps[0]["payload"], "actions/checkout@v6")
                self.assertTrue(any("pip install" in r["payload"]
                                    for r in steps))
                self.assertIs(item["static_source_only_not_actual_runner_trace"],
                              True)

    def test_preflight_network_calls_are_before_gate(self):
        steps = REPORT()["historical_pregate_payloads"][
            "annual_preflight"]["actual_pregate_setup_and_read_payloads"]
        self.assertEqual([step["zero_based_step_index"] for step in steps],
                         [0, 3, 4, 5, 6])
        self.assertIn("four gh api calls", steps[3]["payload"])

    def test_missing_checkout_action_payload_is_refused(self):
        data = WORKFLOW.read_text(encoding="utf-8")
        changed = data.replace("        uses: actions/checkout@v6",
                               "        uses: some/unreviewed-checkout@v6", 1)
        with self.assertRaisesRegex(
                MOD["InvalidStaticEvidence"], "checkout/setup command"):
            MOD["inspect_pregate_step_payloads"](changed)

    def test_changed_unprotected_pip_install_payload_is_refused(self):
        data = WORKFLOW.read_text(encoding="utf-8")
        line = "run: python -m pip install -r requirements/exp061-discovery-run.txt -e ."
        self.assertEqual(data.count(line), 3)
        changed = data.replace(line, "run: pip install newest -e .", 1)
        with self.assertRaisesRegex(
                MOD["InvalidStaticEvidence"], "unguarded install payload"):
            MOD["inspect_pregate_step_payloads"](changed)

    def test_removed_main_ref_guard_command_is_refused(self):
        data = WORKFLOW.read_text(encoding="utf-8")
        expected = 'test "$GITHUB_REF" = "refs/heads/main"'
        self.assertEqual(data.count(expected), 3)
        changed = data.replace(expected, 'echo "main"', 1)
        with self.assertRaisesRegex(
                MOD["InvalidStaticEvidence"], "main branch/test guard"):
            MOD["inspect_pregate_step_payloads"](changed)

    def test_missing_gate_commit_argument_is_refused(self):
        data = WORKFLOW.read_text(encoding="utf-8")
        original = '            --code-commit "$GITHUB_SHA"'
        self.assertEqual(data.count(original), 3)
        changed = data.replace(
            original, '            --code-commit "not-a-SHA"', 1)
        with self.assertRaisesRegex(
                MOD["InvalidStaticEvidence"], "guard command/arguments"):
            MOD["inspect_pregate_step_payloads"](changed)

    def test_preflight_missing_one_metadata_api_call_is_refused(self):
        data = WORKFLOW.read_text(encoding="utf-8")
        cmd = 'gh api "repos/$GITHUB_REPOSITORY/actions/runs/35867307338"'
        self.assertIn(cmd, data)
        changed = data.replace(cmd, "echo skipped-run-metadata", 1)
        with self.assertRaisesRegex(
                MOD["InvalidStaticEvidence"], "metadata fetch operation"):
            MOD["inspect_pregate_step_payloads"](changed)

    def test_preflight_missing_source_validation_is_refused(self):
        data = WORKFLOW.read_text(encoding="utf-8")
        cmd = "          python scripts/phase8a_annual_pattern_catalogue.py preflight \\"
        self.assertIn(cmd, data)
        changed = data.replace(cmd, "          echo omitted-preflight \\", 1)
        with self.assertRaisesRegex(
                MOD["InvalidStaticEvidence"], "source validation changed"):
            MOD["inspect_pregate_step_payloads"](changed)

    def test_reported_payloads_remain_non_authorizing_with_nonzero_cli(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = MOD["main"]([])
        self.assertEqual(status, 3)
        report = json.loads(out.getvalue())
        self.assertEqual(report["disposition"],
                         "BLOCKED_NOT_EXECUTABLE_AND_NOT_ADMIN_ATTESTED")
        self.assertFalse(report["protected_2023_run385_attempt1_authorized"])
        self.assertEqual(report["allowed_actions"], [])


    def test_workflow_is_a_pinned_offline_fixture_not_installed_ci_file(self):
        import hashlib
        fixture = WORKFLOW.read_bytes()
        digest = hashlib.sha1(
            b"blob " + str(len(fixture)).encode("ascii") + b"\0" + fixture
        ).hexdigest()
        self.assertEqual(digest, MOD["EXPECTED_GIT_BLOB_SHA1"])
        self.assertTrue(
            str(WORKFLOW).endswith(
                "tests/fixtures/dec1779-historical-phase8a-annual-workflow.yml")
        )
        self.assertEqual(
            REPORT()["source_material"],
            "exact_git_blob_pinned_historical_fixture_not_live_workflow",
        )

    def test_snapshot_does_not_claim_current_workflow_or_ci_installation(self):
        report = REPORT()
        self.assertIs(
            report["installed_workflow_file_absent_from_ci_not_an_attestation"],
            True)
        self.assertFalse(report["annual_research_dispatch_authorized"])
        self.assertEqual(report["allowed_actions"], [])

    def test_no_workflow_dispatch_or_broker_is_needed(self):
        report = REPORT()
        self.assertIn("Independent administrator/security", report["next_external_review"])
        self.assertEqual(report["disposition"],
                         "BLOCKED_NOT_EXECUTABLE_AND_NOT_ADMIN_ATTESTED")
        self.assertTrue(report["source_sha_and_live_ref_at_dispatch_not_authenticated"])
