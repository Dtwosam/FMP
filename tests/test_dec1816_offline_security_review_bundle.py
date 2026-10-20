"""DEC-1816 seven-source source-only owner parity stays BLOCKED."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest import mock

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
            "status", "evidence_ref", "reviewer_signoff"
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
