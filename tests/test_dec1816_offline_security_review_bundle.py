"""DEC-1816 seven-source source-only owner parity stays BLOCKED."""
import contextlib
import io
import json
import os
from pathlib import Path
from unittest import mock
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MOD = runpy.run_path(
    str(ROOT / "scripts" / "dec1816_offline_security_review_bundle.py")
)
SIX = runpy.run_path(str(MOD["SIX"]))
BLANK = runpy.run_path(str(MOD["BLANK"]))
BUILD = MOD["compile_blocked_review_bundle"]


class Phase8ABlockedSevenSourceIndexTests(unittest.TestCase):
    def test_exact_missing_owner_identity_matches_both_reports(self):
        report = BUILD()
        self.assertEqual(report["eight_missing_independent_proofs"],
                         SIX["compile_blocked_handoff"]()[
                             "eight_missing_independent_proofs"])
        self.assertEqual(report["eight_missing_independent_proofs"],
                         BLANK["report_blocked_blank_worksheet"]()[
                             "eight_independent_proofs"])
        self.assertEqual(len(report["eight_missing_independent_proofs"]), 8)

    def test_historical_fingerprints_do_not_claim_current_main(self):
        report = BUILD()
        self.assertEqual(len(report["five_documentary_source_sha256"]), 5)
        self.assertEqual(len(report["historical_workflow_sha256"]), 64)
        self.assertEqual(
            report["blank_worksheet_git_blob_sha1"],
            BLANK["PINNED_BLANK_WORKSHEET_GIT_BLOB_SHA1"])
        self.assertIn("observed_main_sha_not_live_ref", report)

    def test_no_review_index_would_grant_protected_or_broker_action(self):
        report = BUILD()
        self.assertEqual(report["disposition"], "BLOCKED_NO_EXECUTION_PERMISSION")
        self.assertFalse(report["independent_external_admin_runner_proof_verified"])
        self.assertFalse(report["2023_run385_attempt1_authorized"])
        self.assertFalse(report["broker_demo_live_or_real_money_authorized"])
        self.assertEqual(report["allowed_actions"], [])
        self.assertTrue(report["no_external_actions_performed"])

    def test_forged_worksheet_rejects_seven_source_index(self):
        with tempfile.TemporaryDirectory() as folder:
            edited = Path(folder) / "worksheet.md"
            edited.write_bytes(BLANK["WORKSHEET"].read_bytes() + b"APPROVED")
            with self.assertRaises((OSError, ValueError)):
                BUILD(worksheet=edited)

    def test_bundle_exposes_exact_irreversible_2023_run385_attempt1(self):
        report = BUILD()
        self.assertEqual(report["next_irreversible_annual_identity_no_dispatch"], {
            "segment": "2023",
            "run_number": 385,
            "attempt_number": 1,
            "authorization": "BLOCKED",
        })

    def test_bundle_exposes_stale_not_current_source_observation(self):
        report = BUILD()
        self.assertEqual(
            report["observed_date_utc_not_current_attestation"], "2026-10-19")
        self.assertEqual(
            report["observed_main_sha_not_live_ref"],
            SIX["compile_blocked_handoff"]()[
                "source_main_sha_not_current_dispatch_ref"])

    def test_bundle_exposes_all_eight_blocked_downstream_stages(self):
        report = BUILD()
        stages = report["blocked_downstream_research_and_trading_stages"]
        self.assertEqual(stages, SIX["compile_blocked_handoff"]()[
            "blocked_downstream_stages"])
        self.assertEqual(len(stages), 8)
        self.assertTrue(stages)

    def test_irreversible_identity_never_overrides_execution_denials(self):
        report = BUILD()
        self.assertEqual(
            report["next_irreversible_annual_identity_no_dispatch"][
                "authorization"], "BLOCKED")
        self.assertFalse(report["2023_run385_attempt1_authorized"])
        self.assertFalse(report["independent_external_admin_runner_proof_verified"])
        self.assertEqual(report["allowed_actions"], [])

    @staticmethod
    def _forged_source(module_path, builder_name, edit):
        import copy
        original_run = runpy.run_path
        file_name = str(module_path)
        module = original_run(file_name)
        original_build = module[builder_name]

        def altered(*args, **kwargs):
            report = copy.deepcopy(original_build(*args, **kwargs))
            edit(report)
            return report

        def intercept(path):
            if str(path) == file_name:
                return dict(module, **{builder_name: altered})
            return original_run(path)

        return mock.patch.object(MOD["runpy"], "run_path",
                                 side_effect=intercept)

    def test_rejects_unreviewed_approval_field_in_six_source_report(self):
        def forge(report):
            report["independently_approved_run385"] = True
        with self._forged_source(
                MOD["SIX"], "compile_blocked_handoff", forge):
            with self.assertRaisesRegex(
                    MOD["InvalidReviewBundle"], "unreviewed"):
                BUILD()

    def test_rejects_unreviewed_signoff_field_in_blank_worksheet(self):
        def forge(report):
            report["reviewer_signoff_authorizing_live_trade"] = "APPROVED"
        with self._forged_source(
                MOD["BLANK"], "report_blocked_blank_worksheet", forge):
            with self.assertRaisesRegex(
                    MOD["InvalidReviewBundle"], "unreviewed"):
                BUILD()

    def test_rejects_deleted_review_field_from_either_upstream(self):
        for source_path, builder, field in (
            (MOD["SIX"], "compile_blocked_handoff", "human_review_request"),
            (MOD["BLANK"], "report_blocked_blank_worksheet", "source_material"),
        ):
            with self.subTest(field=field):
                def forge(report):
                    del report[field]
                with self._forged_source(source_path, builder, forge):
                    with self.assertRaises(MOD["InvalidReviewBundle"]):
                        BUILD()

    def test_cli_rejects_forged_source_authorization_without_stdout(self):
        def forge(report):
            report["security_proofs_autocompleted"] = True
        out, err = io.StringIO(), io.StringIO()
        with self._forged_source(
                MOD["SIX"], "compile_blocked_handoff", forge):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = MOD["main"]([])
        self.assertEqual(status, 2)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("BLOCKED:", err.getvalue())

    def test_human_index_contains_every_missing_owner_and_criterion(self):
        report = BUILD()
        md = MOD["format_blocked_review_bundle_markdown"](report)
        self.assertEqual(md.count("| **MISSING** |"), 8)
        for row in report["eight_missing_independent_proofs"]:
            self.assertIn(f"| {row['id']} | {row['review_role']} |", md)
            self.assertIn(report[
                "independent_proof_acceptance_criteria"][row["id"]], md)

    def test_human_index_labels_irreversible_scope_and_historical_hashes(self):
        report = BUILD()
        md = MOD["format_blocked_review_bundle_markdown"](report)
        self.assertIn("**BLOCKED.", md)
        self.assertIn("Annual segment: 2023", md)
        self.assertIn("Run: 385", md)
        self.assertIn("Attempt: 1", md)
        self.assertIn(report["historical_workflow_sha256"], md)
        self.assertIn(report["blank_worksheet_git_blob_sha1"], md)
        self.assertIn("NOT current dispatch ref", md)

    def test_human_index_uses_actual_markdown_lines_not_escaped_text(self):
        md = MOD["format_blocked_review_bundle_markdown"](BUILD())
        self.assertIn(chr(10) + "## Eight independently owned proofs", md)
        self.assertNotIn(chr(92) + "n##", md)
        self.assertGreater(md.count(chr(10)), 25)

    def test_human_index_refuses_injected_approval_field_or_proof(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["reviewer_self_approved_run385"] = True
        with self.assertRaisesRegex(MOD["InvalidReviewBundle"],
                                    "canonical BLOCKED"):
            MOD["format_blocked_review_bundle_markdown"](report)
        report = copy.deepcopy(BUILD())
        report["eight_missing_independent_proofs"][0]["status"] = "APPROVED"
        with self.assertRaises(MOD["InvalidReviewBundle"]):
            MOD["format_blocked_review_bundle_markdown"](report)

    def test_human_index_rejects_nonfinite_and_nonobject_injections(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["after_cost_profit"] = float("nan")
        with self.assertRaisesRegex(MOD["InvalidReviewBundle"], "nonfinite"):
            MOD["format_blocked_review_bundle_markdown"](report)
        with self.assertRaises(MOD["InvalidReviewBundle"]):
            MOD["format_blocked_review_bundle_markdown"](["APPROVED"])

    def test_human_cli_stays_nonzero_blocked_and_rejects_forged_worksheet(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = MOD["main"](["--format", "markdown"])
        self.assertEqual(code, 3)
        self.assertEqual(err.getvalue(), "")
        self.assertIn("**BLOCKED.", out.getvalue())
        with tempfile.TemporaryDirectory() as folder:
            forged = Path(folder) / "worksheet.md"
            forged.write_bytes(b"READY")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = MOD["main"](["--format", "markdown", "--worksheet", str(forged)])
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("BLOCKED:", err.getvalue())

    def test_eight_review_requests_bind_roles_and_exact_criteria(self):
        report = BUILD()
        requests = report["unfulfilled_independent_review_requests"]
        self.assertEqual(len(requests), 8)
        for request, proof in zip(requests, report["eight_missing_independent_proofs"]):
            with self.subTest(proof=proof["id"]):
                self.assertEqual(request["id"], proof["id"])
                self.assertEqual(request["review_role"], proof["review_role"])
                self.assertEqual(
                    request["acceptance_requirement"],
                    report["independent_proof_acceptance_criteria"][proof["id"]])

    def test_review_requests_contain_no_signoffs_evidence_or_execution(self):
        requests = BUILD()["unfulfilled_independent_review_requests"]
        expected_fields = {
            "id", "review_role", "acceptance_requirement",
            "status", "evidence_ref", "reviewer_signoff",
            "tracking_refs_not_approvals"
        }
        for request in requests:
            with self.subTest(request=request["id"]):
                self.assertEqual(set(request), expected_fields)
                self.assertEqual(request["status"], "MISSING")
                self.assertIsNone(request["evidence_ref"])
                self.assertIsNone(request["reviewer_signoff"])

    def test_human_render_shows_no_collected_owner_evidence(self):
        md = MOD["format_blocked_review_bundle_markdown"](BUILD())
        self.assertEqual(md.count("Evidence reference: MISSING; reviewer signoff: MISSING."), 8)
        self.assertIn("NOT attestations", md)
        self.assertIn("**BLOCKED.", md)

    def test_json_cli_review_requests_are_all_unfulfilled(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = MOD["main"](["--format", "json"])
        self.assertEqual(code, 3)
        self.assertEqual(err.getvalue(), "")
        report = json.loads(out.getvalue())
        self.assertEqual(len(report["unfulfilled_independent_review_requests"]), 8)
        self.assertTrue(all(
            row["evidence_ref"] is None and row["reviewer_signoff"] is None
            for row in report["unfulfilled_independent_review_requests"]
        ))
        self.assertFalse(report["2023_run385_attempt1_authorized"])

    def test_review_fingerprint_matches_full_canonical_index(self):
        import hashlib
        report = BUILD()
        self.assertTrue(MOD["validate_review_index_fingerprint"](report))
        fingerprint = report["offline_request_fingerprint_sha256"]
        self.assertEqual(len(fingerprint), 64)
        canonical = json.dumps({
            k: v for k, v in report.items()
            if k != "offline_request_fingerprint_sha256"
        }, sort_keys=True, separators=(",", ":"), allow_nan=False)
        self.assertEqual(hashlib.sha256(canonical.encode()).hexdigest(), fingerprint)

    def test_review_fingerprint_is_deterministic_across_source_reads(self):
        first, second = BUILD(), BUILD()
        self.assertEqual(first["offline_request_fingerprint_sha256"],
                         second["offline_request_fingerprint_sha256"])
        self.assertEqual(first, second)

    def test_review_fingerprint_rejects_edited_or_nonfinite_report(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["2023_run385_attempt1_authorized"] = True
        with self.assertRaises(MOD["InvalidReviewBundle"]):
            MOD["validate_review_index_fingerprint"](report)
        report = copy.deepcopy(BUILD())
        report["claimed_profit"] = float("inf")
        with self.assertRaisesRegex(MOD["InvalidReviewBundle"], "nonfinite"):
            MOD["validate_review_index_fingerprint"](report)

    def test_markdown_and_json_include_same_local_index_digest(self):
        report = BUILD()
        md = MOD["format_blocked_review_bundle_markdown"](report)
        self.assertIn(report["offline_request_fingerprint_sha256"], md)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = MOD["main"](["--format", "json"])
        self.assertEqual(code, 3)
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(
            json.loads(out.getvalue())["offline_request_fingerprint_sha256"],
            report["offline_request_fingerprint_sha256"])

    def test_seven_source_compiler_spawns_no_process(self):
        with mock.patch("subprocess.Popen",
                        side_effect=AssertionError("unexpected subprocess")):
            result = BUILD()
        self.assertEqual(result["allowed_actions"], [])
        self.assertFalse(result["2023_run385_attempt1_authorized"])

    def test_seven_source_compiler_creates_no_network_socket(self):
        with mock.patch("socket.socket",
                        side_effect=AssertionError("unexpected socket")):
            result = BUILD()
        self.assertTrue(result["no_external_actions_performed"])
        self.assertFalse(result["broker_demo_live_or_real_money_authorized"])

    def test_both_review_cli_formats_work_with_process_and_socket_denied(self):
        with mock.patch("subprocess.Popen",
                        side_effect=AssertionError("unexpected subprocess")):
            with mock.patch("socket.socket",
                            side_effect=AssertionError("unexpected network")):
                for fmt in ("json", "markdown"):
                    with self.subTest(fmt=fmt):
                        out, err = io.StringIO(), io.StringIO()
                        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                            code = MOD["main"](["--format", fmt])
                        self.assertEqual(code, 3)
                        self.assertEqual(err.getvalue(), "")
                        self.assertIn("BLOCKED", out.getvalue())

    def test_compact_export_contains_only_eight_missing_review_requests(self):
        report = BUILD()
        short = MOD["format_unfulfilled_review_requests"](report)
        self.assertEqual(short["disposition"], "BLOCKED_NO_EXECUTION_PERMISSION")
        self.assertEqual(len(short["unfulfilled_independent_review_requests"]), 8)
        self.assertEqual(
            short["unfulfilled_independent_review_requests"],
            report["unfulfilled_independent_review_requests"])
        self.assertEqual(
            short["parent_offline_index_sha256"],
            report["offline_request_fingerprint_sha256"])
        self.assertEqual(short["allowed_actions"], [])

    def test_compact_export_rejects_injected_signoff_and_approval(self):
        import copy
        report = copy.deepcopy(BUILD())
        report["unfulfilled_independent_review_requests"][0][
            "reviewer_signoff"] = "APPROVED"
        with self.assertRaises(MOD["InvalidReviewBundle"]):
            MOD["format_unfulfilled_review_requests"](report)

    def test_requests_cli_is_nonzero_and_denies_trading(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = MOD["main"](["--format", "requests"])
        self.assertEqual(code, 3)
        self.assertEqual(err.getvalue(), "")
        result = json.loads(out.getvalue())
        self.assertEqual(result["schema"],
                         "fmp_dec1826_offline_unfulfilled_review_requests_v1")
        self.assertEqual(result["protected_annual_identity"]["authorization"],
                         "BLOCKED")
        self.assertFalse(result["annual_dispatch_or_retry_authorized"])
        self.assertFalse(result["broker_demo_live_or_real_money_authorized"])

    def test_requests_cli_rejects_forged_worksheet_without_stdout(self):
        with tempfile.TemporaryDirectory() as folder:
            forged = Path(folder) / "worksheet.md"
            forged.write_bytes(b"APPROVED")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = MOD["main"]([
                    "--format", "requests", "--worksheet", str(forged)])
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("BLOCKED:", err.getvalue())

    def test_saved_json_packet_reverifies_as_blocked_not_approved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "packet.json"
            path.write_text(json.dumps(BUILD()), encoding="utf-8")
            validated = MOD["verify_saved_blocked_review_packet"](path)
        self.assertEqual(validated, BUILD())
        self.assertFalse(validated["2023_run385_attempt1_authorized"])
        self.assertEqual(validated["allowed_actions"], [])

    def test_saved_json_packet_refuses_forged_approval_even_with_rehash(self):
        import copy
        import hashlib
        original = copy.deepcopy(BUILD())
        original["2023_run385_attempt1_authorized"] = True
        raw = json.dumps({
            k: v for k, v in original.items()
            if k != "offline_request_fingerprint_sha256"
        }, sort_keys=True, separators=(",", ":"), allow_nan=False)
        original["offline_request_fingerprint_sha256"] = hashlib.sha256(
            raw.encode()).hexdigest()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "packet.json"
            path.write_text(json.dumps(original), encoding="utf-8")
            with self.assertRaisesRegex(
                    MOD["InvalidReviewBundle"], "differs from freshly"):
                MOD["verify_saved_blocked_review_packet"](path)

    def test_saved_json_rejects_duplicate_keys_and_nonfinite_values(self):
        for text in ('{"schema":"x","schema":"y"}',
                     '{"paid_profit": NaN}', '{"paid_profit": 1e999}'):
            with self.subTest(payload=text):
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "packet.json"
                    path.write_text(text, encoding="utf-8")
                    with self.assertRaises(MOD["InvalidReviewBundle"]):
                        MOD["verify_saved_blocked_review_packet"](path)

    def test_saved_json_rejects_symlinked_packet(self):
        with tempfile.TemporaryDirectory() as folder:
            link = Path(folder) / "packet.json"
            original = Path(folder) / "real.json"
            original.write_text(json.dumps(BUILD()), encoding="utf-8")
            link.symlink_to(original)
            with self.assertRaises((OSError, ValueError)):
                MOD["verify_saved_blocked_review_packet"](link)

    def test_saved_json_cli_blocked_or_rejected_without_stdout(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "packet.json"
            path.write_text(json.dumps(BUILD()), encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = MOD["main"](["--verify-report", str(path)])
            self.assertEqual(code, 3)
            self.assertEqual(err.getvalue(), "")
            self.assertEqual(json.loads(out.getvalue())["disposition"],
                             "BLOCKED_NO_EXECUTION_PERMISSION")
            path.write_text('{"decision":"APPROVED"}', encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = MOD["main"](["--verify-report", str(path)])
            self.assertEqual(code, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("BLOCKED:", err.getvalue())

    def test_saved_json_verifier_rejects_parent_directory_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            real = root / "real"
            real.mkdir()
            packet = real / "packet.json"
            packet.write_text(json.dumps(BUILD()), encoding="utf-8")
            alias = root / "alias"
            alias.symlink_to(real, target_is_directory=True)
            with self.assertRaises((OSError, ValueError)):
                MOD["verify_saved_blocked_review_packet"](alias / "packet.json")

    def test_saved_json_verifier_rejects_oversized_file(self):
        with tempfile.TemporaryDirectory() as folder:
            packet = Path(folder) / "packet.json"
            packet.write_bytes(b" " * (1024 * 1024 + 1))
            with self.assertRaises((OSError, ValueError)):
                MOD["verify_saved_blocked_review_packet"](packet)

    def test_saved_json_verifier_rejects_nonobject_and_nonstrict_numeric_alias(self):
        for value in ('[]', 'null', 'true', '{"attempt": 1.0}',
                      '{"approval": 1e999}'):
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "packet.json"
                    path.write_text(value, encoding="utf-8")
                    with self.assertRaises(MOD["InvalidReviewBundle"]):
                        MOD["verify_saved_blocked_review_packet"](path)

    def test_verifier_cli_refuses_mixed_source_override_without_stdout(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / "packet.json"
            path.write_text(json.dumps(BUILD()), encoding="utf-8")
            for option in ("--docs-root", "--workflow", "--worksheet"):
                with self.subTest(option=option):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        code = MOD["main"]([
                            "--verify-report", str(path), option, str(root)
                        ])
                    self.assertEqual(code, 2)
                    self.assertEqual(out.getvalue(), "")
                    self.assertIn("BLOCKED:", err.getvalue())

    def test_verifier_never_changes_the_saved_input_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "packet.json"
            original = json.dumps(BUILD(), indent=2).encode("utf-8")
            path.write_bytes(original)
            for fmt in ("json", "markdown", "requests"):
                with self.subTest(fmt=fmt):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        code = MOD["main"]([
                            "--verify-report", str(path), "--format", fmt
                        ])
                    self.assertEqual(code, 3)
                    self.assertEqual(err.getvalue(), "")
                    self.assertEqual(path.read_bytes(), original)
                    self.assertIn("BLOCKED", out.getvalue())

    def test_deeply_nested_saved_json_returns_controlled_blocked_error(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "nested.json"
            path.write_text("[" * 1200 + "]" * 1200, encoding="utf-8")
            with self.assertRaises(MOD["InvalidReviewBundle"]):
                MOD["verify_saved_blocked_review_packet"](path)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = MOD["main"](["--verify-report", str(path)])
            self.assertEqual(code, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("BLOCKED:", err.getvalue())

    def test_duplicate_nested_json_member_is_denied_without_stdout(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "duplicated.json"
            path.write_text(
                '{"proofs":[{"id":"one","id":"approved"}]}', encoding="utf-8"
            )
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = MOD["main"](["--verify-report", str(path)])
            self.assertEqual(code, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("BLOCKED:", err.getvalue())

    def test_saved_json_refuses_invalid_utf8_and_multiple_json_roots(self):
        for payload in (bytes((255, 254)),
                        b'{} {}',
                        b'{}' + bytes((0,)) + b'{}'):
            with self.subTest(payload=repr(payload)):
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "packet.json"
                    path.write_bytes(payload)
                    with self.assertRaises(MOD["InvalidReviewBundle"]):
                        MOD["verify_saved_blocked_review_packet"](path)

    def test_saved_verifier_rejects_directory_instead_of_regular_file(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises((OSError, ValueError)):
                MOD["verify_saved_blocked_review_packet"](Path(folder))

    def test_saved_compact_requests_revalidate_only_when_all_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "requests.json"
            expected = MOD["format_unfulfilled_review_requests"](BUILD())
            path.write_text(json.dumps(expected), encoding="utf-8")
            actual = MOD["verify_saved_unfulfilled_review_requests"](path)
            self.assertEqual(actual, expected)
            self.assertEqual(len(actual["unfulfilled_independent_review_requests"]), 8)
            self.assertFalse(actual["annual_dispatch_or_retry_authorized"])

    def test_saved_compact_requests_reject_forged_signoff_with_unchanged_parent(self):
        import copy
        expected = MOD["format_unfulfilled_review_requests"](BUILD())
        forged = copy.deepcopy(expected)
        forged["unfulfilled_independent_review_requests"][0][
            "reviewer_signoff"] = "APPROVED"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "requests.json"
            path.write_text(json.dumps(forged), encoding="utf-8")
            with self.assertRaisesRegex(
                    MOD["InvalidReviewBundle"], "fresh MISSING-only"):
                MOD["verify_saved_unfulfilled_review_requests"](path)

    def test_compact_request_reader_rejects_nested_duplicates_and_nonfinite(self):
        for payload in (
            '{"proofs":[{"status":"MISSING","status":"APPROVED"}]}',
            '{"profit": NaN}', '{"profit": 1e999}', "[]" * 2,
        ):
            with self.subTest(value=payload):
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "requests.json"
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaises(MOD["InvalidReviewBundle"]):
                        MOD["verify_saved_unfulfilled_review_requests"](path)

    def test_compact_request_reader_rejects_symlink_and_oversized_input(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            real = root / "requests.json"
            real.write_text(json.dumps(
                MOD["format_unfulfilled_review_requests"](BUILD())),
                encoding="utf-8")
            link = root / "requests-link.json"
            link.symlink_to(real)
            with self.assertRaises((OSError, ValueError)):
                MOD["verify_saved_unfulfilled_review_requests"](link)
            real.write_bytes(b" " * (1024 * 1024 + 1))
            with self.assertRaises((OSError, ValueError)):
                MOD["verify_saved_unfulfilled_review_requests"](real)

    def test_compact_verification_cli_rejects_mixed_modes_and_forgery(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / "requests.json"
            path.write_text(json.dumps(
                MOD["format_unfulfilled_review_requests"](BUILD())),
                encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = MOD["main"](["--verify-requests", str(path)])
            self.assertEqual(code, 3)
            self.assertEqual(err.getvalue(), "")
            self.assertEqual(json.loads(out.getvalue())["disposition"],
                             "BLOCKED_NO_EXECUTION_PERMISSION")
            for addition in (
                ["--verify-report", str(path)],
                ["--docs-root", str(root)],
                ["--format", "markdown"],
            ):
                with self.subTest(extra=addition):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        code = MOD["main"](["--verify-requests", str(path)] + addition)
                    self.assertEqual(code, 2)
                    self.assertEqual(out.getvalue(), "")
                    self.assertIn("BLOCKED:", err.getvalue())
            path.write_bytes(b"APPROVED")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = MOD["main"](["--verify-requests", str(path)])
            self.assertEqual(code, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("BLOCKED:", err.getvalue())

    def test_saved_verification_modes_share_exact_strict_json_reader(self):
        self.assertIn("_read_strict_saved_json",
                      MOD["verify_saved_blocked_review_packet"].__code__.co_names)
        self.assertIn("_read_strict_saved_json",
                      MOD["verify_saved_unfulfilled_review_requests"].__code__.co_names)

    def test_both_saved_json_modes_reject_deep_nested_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "nested.json"
            path.write_text("[" * 1200 + "]" * 1200, encoding="utf-8")
            for verifier in (
                MOD["verify_saved_blocked_review_packet"],
                MOD["verify_saved_unfulfilled_review_requests"],
            ):
                with self.subTest(verifier=verifier.__name__):
                    with self.assertRaises(MOD["InvalidReviewBundle"]):
                        verifier(path)

    def test_saved_packet_reading_is_offline_under_process_and_socket_denials(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            full = base / "full.json"
            requests = base / "requests.json"
            full.write_text(json.dumps(BUILD()), encoding="utf-8")
            requests.write_text(json.dumps(
                MOD["format_unfulfilled_review_requests"](BUILD())
            ), encoding="utf-8")
            with mock.patch("subprocess.Popen",
                            side_effect=AssertionError("unexpected process")):
                with mock.patch("socket.socket",
                                side_effect=AssertionError("unexpected network")):
                    self.assertEqual(
                        MOD["verify_saved_blocked_review_packet"](full)[
                            "disposition"], "BLOCKED_NO_EXECUTION_PERMISSION")
                    self.assertEqual(
                        MOD["verify_saved_unfulfilled_review_requests"](requests)[
                            "disposition"], "BLOCKED_NO_EXECUTION_PERMISSION")

    @staticmethod
    @contextlib.contextmanager
    def _deny_writable_os_opens():
        real_open = os.open
        mutating = (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                    | os.O_TRUNC | os.O_APPEND)
        opened = []

        def audit(path, flags, mode=0o777, *, dir_fd=None):
            if flags & mutating:
                raise AssertionError("offline seven-source reader attempted a write")
            opened.append((str(path), flags))
            if dir_fd is None:
                return real_open(path, flags, mode)
            return real_open(path, flags, mode, dir_fd=dir_fd)

        # Keep the actual dirfd capability visible to the nofollow reader:
        # a patched callable otherwise lacks membership in supports_dir_fd.
        with mock.patch("os.open", side_effect=audit) as guarded:
            with mock.patch.object(os, "supports_dir_fd",
                                   os.supports_dir_fd | {guarded}):
                yield opened

    def test_seven_source_compilation_never_uses_writable_os_open(self):
        with self._deny_writable_os_opens() as observed:
            report = BUILD()
        self.assertTrue(observed)
        self.assertEqual(report["allowed_actions"], [])
        self.assertTrue(report["no_external_actions_performed"])

    def test_saved_full_report_verification_never_uses_writable_os_open(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "packet.json"
            path.write_text(json.dumps(BUILD()), encoding="utf-8")
            with self._deny_writable_os_opens() as observed:
                result = MOD["verify_saved_blocked_review_packet"](path)
            self.assertTrue(observed)
            self.assertEqual(result["disposition"], "BLOCKED_NO_EXECUTION_PERMISSION")

    def test_saved_compact_requests_verification_never_uses_writable_os_open(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "requests.json"
            path.write_text(json.dumps(
                MOD["format_unfulfilled_review_requests"](BUILD())
            ), encoding="utf-8")
            with self._deny_writable_os_opens() as observed:
                result = MOD["verify_saved_unfulfilled_review_requests"](path)
            self.assertTrue(observed)
            self.assertEqual(result["allowed_actions"], [])

    def test_all_cli_review_modes_only_read_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            full = root / "full.json"
            requests = root / "requests.json"
            full.write_text(json.dumps(BUILD()), encoding="utf-8")
            requests.write_text(json.dumps(
                MOD["format_unfulfilled_review_requests"](BUILD())
            ), encoding="utf-8")
            modes = (
                ["--format", "json"],
                ["--format", "markdown"],
                ["--format", "requests"],
                ["--verify-report", str(full)],
                ["--verify-requests", str(requests)],
            )
            for mode in modes:
                with self.subTest(mode=mode):
                    out, err = io.StringIO(), io.StringIO()
                    with self._deny_writable_os_opens() as seen:
                        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                            status = MOD["main"](mode)
                    self.assertEqual(status, 3)
                    self.assertEqual(err.getvalue(), "")
                    self.assertIn("BLOCKED", out.getvalue())
                    self.assertTrue(seen)

    def test_all_eight_proofs_have_exact_review_issue_traceability(self):
        report = BUILD()
        rows = report["unfulfilled_independent_review_requests"]
        expected = MOD["REVIEW_ISSUE_REFERENCES"]
        self.assertEqual({row["id"] for row in rows}, set(expected))
        self.assertEqual(len(rows), 8)
        for row in rows:
            with self.subTest(proof=row["id"]):
                self.assertEqual(
                    row["tracking_refs_not_approvals"], list(expected[row["id"]]))
                self.assertTrue(all(
                    ref.startswith("https://github.com/Dtwosam/FMP/")
                    for ref in row["tracking_refs_not_approvals"]
                ))

    def test_all_issue_tracking_refs_are_navigation_not_approval(self):
        report = BUILD()
        rows = report["unfulfilled_independent_review_requests"]
        md = MOD["format_blocked_review_bundle_markdown"](report)
        self.assertEqual(md.count("Related unresolved review:"), 8)
        self.assertTrue(all(
            row["status"] == "MISSING"
            and row["evidence_ref"] is None
            and row["reviewer_signoff"] is None
            for row in rows
        ))
        self.assertFalse(report["2023_run385_attempt1_authorized"])

    def test_compact_requests_preserve_issue_refs_without_permissions(self):
        report = MOD["format_unfulfilled_review_requests"](BUILD())
        self.assertEqual(len(report["unfulfilled_independent_review_requests"]), 8)
        self.assertEqual(report["allowed_actions"], [])
        self.assertFalse(report["annual_dispatch_or_retry_authorized"])
        self.assertTrue(all(
            row["tracking_refs_not_approvals"]
            for row in report["unfulfilled_independent_review_requests"]
        ))

    def test_saved_markdown_exact_cli_round_trip_is_only_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "review.md"
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                original_status = MOD["main"](["--format", "markdown"])
            self.assertEqual(original_status, 3)
            self.assertEqual(err.getvalue(), "")
            path.write_bytes(out.getvalue().encode("utf-8"))
            fresh = MOD["verify_saved_blocked_markdown"](path)
            self.assertFalse(fresh["2023_run385_attempt1_authorized"])
            verified_out, verified_err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(verified_out), contextlib.redirect_stderr(verified_err):
                code = MOD["main"](["--verify-markdown", str(path)])
            self.assertEqual(code, 3)
            self.assertEqual(verified_out.getvalue(), out.getvalue())
            self.assertEqual(verified_err.getvalue(), "")
            self.assertEqual(path.read_bytes(), out.getvalue().encode("utf-8"))

    def test_saved_markdown_rejects_approval_and_changed_line_endings(self):
        original = MOD["format_blocked_review_bundle_markdown"](BUILD()) + chr(10)
        for forged in (
            original.replace("MISSING", "APPROVED", 1),
            original.replace(chr(10), chr(13) + chr(10), 1),
            original + "APPROVED: dispatch 385",
        ):
            with self.subTest(forged=forged[-40:]):
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "review.md"
                    path.write_text(forged, encoding="utf-8")
                    with self.assertRaises(MOD["InvalidReviewBundle"]):
                        MOD["verify_saved_blocked_markdown"](path)

    def test_saved_markdown_rejects_symlinks_and_oversized_text(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            actual = root / "actual.md"
            actual.write_text(MOD["format_blocked_review_bundle_markdown"](BUILD())
                              + chr(10), encoding="utf-8")
            alias = root / "alias.md"
            alias.symlink_to(actual)
            with self.assertRaises((OSError, ValueError)):
                MOD["verify_saved_blocked_markdown"](alias)
            actual.write_bytes(b"x" * (1024 * 1024 + 1))
            with self.assertRaises((OSError, ValueError)):
                MOD["verify_saved_blocked_markdown"](actual)

    def test_saved_markdown_cli_rejects_mixed_inputs_without_stdout(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "review.md"
            path.write_text(MOD["format_blocked_review_bundle_markdown"](BUILD())
                            + chr(10), encoding="utf-8")
            for extra in (
                ["--verify-report", str(path)],
                ["--verify-requests", str(path)],
                ["--worksheet", str(path)],
                ["--format", "requests"],
            ):
                with self.subTest(extra=extra):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        code = MOD["main"](["--verify-markdown", str(path)] + extra)
                    self.assertEqual(code, 2)
                    self.assertEqual(out.getvalue(), "")
                    self.assertIn("BLOCKED:", err.getvalue())

    def test_saved_markdown_verification_remains_offline_and_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "review.md"
            path.write_text(MOD["format_blocked_review_bundle_markdown"](BUILD())
                            + chr(10), encoding="utf-8")
            original = path.read_bytes()
            with mock.patch("subprocess.Popen",
                            side_effect=AssertionError("unexpected subprocess")):
                with mock.patch("socket.socket",
                                side_effect=AssertionError("unexpected socket")):
                    with self._deny_writable_os_opens() as seen:
                        fresh = MOD["verify_saved_blocked_markdown"](path)
            self.assertTrue(seen)
            self.assertEqual(fresh["allowed_actions"], [])
            self.assertEqual(path.read_bytes(), original)

    def test_saved_markdown_explicit_format_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "review.md"
            path.write_text(MOD["format_blocked_review_bundle_markdown"](BUILD())
                            + chr(10), encoding="utf-8")
            for other in ("json", "requests"):
                with self.subTest(format=other):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        code = MOD["main"]([
                            "--verify-markdown", str(path), "--format", other
                        ])
                    self.assertEqual(code, 2)
                    self.assertEqual(out.getvalue(), "")
                    self.assertIn("BLOCKED:", err.getvalue())

    def test_saved_compact_explicit_format_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "requests.json"
            path.write_text(json.dumps(
                MOD["format_unfulfilled_review_requests"](BUILD())),
                encoding="utf-8")
            for other in ("json", "markdown"):
                with self.subTest(format=other):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        code = MOD["main"]([
                            "--verify-requests", str(path), "--format", other
                        ])
                    self.assertEqual(code, 2)
                    self.assertEqual(out.getvalue(), "")
                    self.assertIn("BLOCKED:", err.getvalue())

    def test_explicit_matching_saved_format_remains_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            md = root / "review.md"
            requests = root / "requests.json"
            md.write_text(MOD["format_blocked_review_bundle_markdown"](BUILD())
                          + chr(10), encoding="utf-8")
            requests.write_text(json.dumps(
                MOD["format_unfulfilled_review_requests"](BUILD())),
                encoding="utf-8")
            for args in (
                ["--verify-markdown", str(md), "--format", "markdown"],
                ["--verify-requests", str(requests), "--format", "requests"],
            ):
                with self.subTest(args=args):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        code = MOD["main"](args)
                    self.assertEqual(code, 3)
                    self.assertEqual(err.getvalue(), "")
                    self.assertIn("BLOCKED", out.getvalue())

    @staticmethod
    def _write_three_canonical_saved_review_artifacts(root):
        full = root / "full.json"
        requests = root / "requests.json"
        md = root / "human.md"
        report = BUILD()
        full.write_text(json.dumps(report), encoding="utf-8")
        requests.write_text(json.dumps(
            MOD["format_unfulfilled_review_requests"](report)),
            encoding="utf-8")
        md.write_text(MOD["format_blocked_review_bundle_markdown"](report)
                      + chr(10), encoding="utf-8")
        return full, requests, md

    def test_three_saved_formats_validate_without_execution_permission(self):
        with tempfile.TemporaryDirectory() as folder:
            artifacts = self._write_three_canonical_saved_review_artifacts(
                Path(folder))
            result = MOD["verify_complete_blocked_review_triplet"](*artifacts)
        self.assertEqual(result["disposition"], "BLOCKED_NO_EXECUTION_PERMISSION")
        self.assertTrue(result["three_saved_formats_consistent_with_pinned_sources"])
        self.assertTrue(result["all_eight_review_requests_still_missing"])
        self.assertEqual(result["allowed_actions"], [])
        self.assertFalse(result["protected_2023_run385_attempt1_authorized"])

    def test_three_saved_formats_reject_tamper_in_any_single_artifact(self):
        for index in range(3):
            with self.subTest(artifact=index):
                with tempfile.TemporaryDirectory() as folder:
                    files = self._write_three_canonical_saved_review_artifacts(
                        Path(folder))
                    target = files[index]
                    target.write_bytes(target.read_bytes() + b"APPROVED")
                    with self.assertRaises((OSError, ValueError)):
                        MOD["verify_complete_blocked_review_triplet"](*files)

    def test_three_saved_formats_cli_stays_blocked_and_rejects_mixed_modes(self):
        with tempfile.TemporaryDirectory() as folder:
            files = self._write_three_canonical_saved_review_artifacts(Path(folder))
            args = ["--verify-triplet"] + list(map(str, files))
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = MOD["main"](args)
            self.assertEqual(status, 3)
            self.assertEqual(err.getvalue(), "")
            self.assertEqual(
                json.loads(out.getvalue())["disposition"],
                "BLOCKED_NO_EXECUTION_PERMISSION")
            for extra in (["--format", "json"], ["--worksheet", str(files[2])],
                          ["--verify-report", str(files[0])],
                          ["--verify-markdown", str(files[2])]):
                with self.subTest(extra=extra):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        status = MOD["main"](args + extra)
                    self.assertEqual(status, 2)
                    self.assertEqual(out.getvalue(), "")
                    self.assertIn("BLOCKED:", err.getvalue())

    def test_three_saved_formats_are_read_only_and_offline(self):
        with tempfile.TemporaryDirectory() as folder:
            files = self._write_three_canonical_saved_review_artifacts(Path(folder))
            initial = [f.read_bytes() for f in files]
            with mock.patch("subprocess.Popen",
                            side_effect=AssertionError("unexpected subprocess")):
                with mock.patch("socket.socket",
                                side_effect=AssertionError("unexpected socket")):
                    with self._deny_writable_os_opens() as seen:
                        result = MOD["verify_complete_blocked_review_triplet"](*files)
            self.assertTrue(seen)
            self.assertTrue(result["no_external_actions_performed"])
            self.assertEqual([f.read_bytes() for f in files], initial)

    @contextlib.contextmanager
    def _deny_external_actions_on_invalid_review(self):
        with mock.patch("subprocess.Popen",
                        side_effect=AssertionError("unexpected subprocess")):
            with mock.patch("socket.socket",
                            side_effect=AssertionError("unexpected socket")):
                with self._deny_writable_os_opens() as opened:
                    yield opened

    def test_forged_full_saved_report_is_rejected_without_external_io(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "full.json"
            tampered = BUILD()
            tampered["2023_run385_attempt1_authorized"] = True
            path.write_text(json.dumps(tampered), encoding="utf-8")
            with self._deny_external_actions_on_invalid_review() as opened:
                with self.assertRaises(MOD["InvalidReviewBundle"]):
                    MOD["verify_saved_blocked_review_packet"](path)
            self.assertTrue(opened)

    def test_forged_compact_signoff_is_rejected_without_external_io(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "requests.json"
            tampered = MOD["format_unfulfilled_review_requests"](BUILD())
            tampered["unfulfilled_independent_review_requests"][0][
                "reviewer_signoff"] = "APPROVED"
            path.write_text(json.dumps(tampered), encoding="utf-8")
            with self._deny_external_actions_on_invalid_review() as opened:
                with self.assertRaises(MOD["InvalidReviewBundle"]):
                    MOD["verify_saved_unfulfilled_review_requests"](path)
            self.assertTrue(opened)

    def test_forged_saved_markdown_is_rejected_without_external_io(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "human.md"
            original = MOD["format_blocked_review_bundle_markdown"](BUILD())
            path.write_text(original.replace("MISSING", "APPROVED", 1)
                            + chr(10), encoding="utf-8")
            with self._deny_external_actions_on_invalid_review() as opened:
                with self.assertRaises(MOD["InvalidReviewBundle"]):
                    MOD["verify_saved_blocked_markdown"](path)
            self.assertTrue(opened)

    def test_forged_three_format_cli_returns_no_output_under_denials(self):
        with tempfile.TemporaryDirectory() as folder:
            files = self._write_three_canonical_saved_review_artifacts(
                Path(folder))
            files[2].write_bytes(files[2].read_bytes() + b"APPROVED")
            out, err = io.StringIO(), io.StringIO()
            with self._deny_external_actions_on_invalid_review() as opened:
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    status = MOD["main"]([
                        "--verify-triplet", *map(str, files)
                    ])
            self.assertEqual(status, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("BLOCKED:", err.getvalue())
            self.assertTrue(opened)

    def test_three_artifact_verdict_declares_nonatomic_snapshot_limitation(self):
        with tempfile.TemporaryDirectory() as folder:
            files = self._write_three_canonical_saved_review_artifacts(
                Path(folder))
            verdict = MOD["verify_complete_blocked_review_triplet"](*files)
        self.assertIs(
            verdict["sequential_snapshot_not_atomic_or_future_file_lock"], True)
        self.assertIs(verdict["source_only_not_independent_attestation"], True)
        self.assertFalse(verdict["protected_2023_run385_attempt1_authorized"])

    def test_triplet_rejects_human_edit_between_saved_file_checks(self):
        with tempfile.TemporaryDirectory() as folder:
            files = self._write_three_canonical_saved_review_artifacts(
                Path(folder))
            verify_triplet = MOD["verify_complete_blocked_review_triplet"]
            globals_ = verify_triplet.__globals__
            original = globals_["verify_saved_unfulfilled_review_requests"]

            def mutate_after_requests(path):
                checked = original(path)
                files[2].write_bytes(files[2].read_bytes() + b"APPROVED")
                return checked

            with mock.patch.dict(
                    globals_,
                    {"verify_saved_unfulfilled_review_requests":
                        mutate_after_requests}):
                with self.assertRaises((OSError, ValueError)):
                    verify_triplet(*files)

    def test_triplet_rejects_compact_edit_after_full_packet_check(self):
        with tempfile.TemporaryDirectory() as folder:
            files = self._write_three_canonical_saved_review_artifacts(
                Path(folder))
            verify_triplet = MOD["verify_complete_blocked_review_triplet"]
            globals_ = verify_triplet.__globals__
            original = globals_["verify_saved_blocked_review_packet"]

            def mutate_after_full(path):
                checked = original(path)
                files[1].write_bytes(files[1].read_bytes() + b"APPROVED")
                return checked

            with mock.patch.dict(
                    globals_, {"verify_saved_blocked_review_packet":
                               mutate_after_full}):
                with self.assertRaises((OSError, ValueError)):
                    verify_triplet(*files)

    def test_triplet_cli_race_fails_without_stdout_or_permissions(self):
        with tempfile.TemporaryDirectory() as folder:
            files = self._write_three_canonical_saved_review_artifacts(
                Path(folder))
            builder = MOD["verify_complete_blocked_review_triplet"]
            globals_ = builder.__globals__
            original = globals_["verify_saved_unfulfilled_review_requests"]

            def mutate_between(path):
                value = original(path)
                files[2].write_bytes(files[2].read_bytes() + b"APPROVED")
                return value

            out, err = io.StringIO(), io.StringIO()
            with mock.patch.dict(
                    globals_,
                    {"verify_saved_unfulfilled_review_requests":
                        mutate_between}):
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    code = MOD["main"]([
                        "--verify-triplet", *map(str, files)])
            self.assertEqual(code, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("BLOCKED:", err.getvalue())

    def test_cli_success_is_blocked_and_invalid_has_no_stdout(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = MOD["main"]([])
        self.assertEqual(code, 3)
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(json.loads(out.getvalue())["disposition"],
                         "BLOCKED_NO_EXECUTION_PERMISSION")
        with tempfile.TemporaryDirectory() as folder:
            edited = Path(folder) / "worksheet.md"
            edited.write_bytes(b"READY")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = MOD["main"](["--worksheet", str(edited)])
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("BLOCKED:", err.getvalue())


if __name__ == "__main__":
    unittest.main()
