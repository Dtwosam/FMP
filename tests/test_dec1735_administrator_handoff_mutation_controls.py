"""DEC-1735: negative controls for source-only admin witness checklist.

Mutations occur in in-memory text only. These checks neither observe nor
attest to effective live GitHub permissions, runner OS, or one-shot state.
"""
import unittest

import test_dec1721_independent_admin_witness_handoff_contract as original


class AdministratorHandoffChecklistMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = original.DOC.read_text(encoding="utf-8")

    def _assert_handoff_guard_rejects(self, guard, before, after):
        self.assertEqual(self.original.count(before), 1)
        tampered = self.original.replace(before, after, 1)
        self.assertNotEqual(tampered, self.original)
        case = original.IndependentAdminWitnessHandoffSourceTests(guard)
        case.document = tampered
        with self.assertRaises(AssertionError):
            getattr(case, guard)()
        self.assertEqual(original.DOC.read_text(encoding="utf-8"),
                         self.original)

    def test_unverified_proof_cannot_be_checked_independent_read_access_to_effective_main_protection_and_inherited_rulesets(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec613_human_proof_ids_are_in_document",
            "- [ ] `independent_read_access_to_effective_main_protection_and_inherited_rulesets`",
            "- [x] `independent_read_access_to_effective_main_protection_and_inherited_rulesets`")

    def test_unverified_proof_cannot_be_checked_explicit_admin_approval_and_proven_no_bypass_or_concurrent_main_updates(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec613_human_proof_ids_are_in_document",
            "- [ ] `explicit_admin_approval_and_proven_no_bypass_or_concurrent_main_updates`",
            "- [x] `explicit_admin_approval_and_proven_no_bypass_or_concurrent_main_updates`")

    def test_unverified_proof_cannot_be_checked_lock_applied_after_any_dispatch_controller_source_is_merged(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec613_human_proof_ids_are_in_document",
            "- [ ] `lock_applied_after_any_dispatch_controller_source_is_merged`",
            "- [x] `lock_applied_after_any_dispatch_controller_source_is_merged`")

    def test_unverified_proof_cannot_be_checked_lock_remains_enforced_across_entire_server_side_dispatch_request(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec613_human_proof_ids_are_in_document",
            "- [ ] `lock_remains_enforced_across_entire_server_side_dispatch_request`",
            "- [x] `lock_remains_enforced_across_entire_server_side_dispatch_request`")

    def test_unverified_proof_cannot_be_checked_current_main_matches_independently_reviewed_dispatch_source_commit(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec613_human_proof_ids_are_in_document",
            "- [ ] `current_main_matches_independently_reviewed_dispatch_source_commit`",
            "- [x] `current_main_matches_independently_reviewed_dispatch_source_commit`")

    def test_unverified_proof_cannot_be_checked_source_runtime_and_dec609_dec610_dec611_dec612_evidence_reauthenticated(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec613_human_proof_ids_are_in_document",
            "- [ ] `source_runtime_and_dec609_dec610_dec611_dec612_evidence_reauthenticated`",
            "- [x] `source_runtime_and_dec609_dec610_dec611_dec612_evidence_reauthenticated`")

    def test_unverified_proof_cannot_be_checked_exact_ten_run_history_and_unconsumed_run_385_verified(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec613_human_proof_ids_are_in_document",
            "- [ ] `exact_ten_run_history_and_unconsumed_run_385_verified`",
            "- [x] `exact_ten_run_history_and_unconsumed_run_385_verified`")

    def test_unverified_proof_cannot_be_checked_separate_run385_action_decision_reviewed_before_single_submission(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec613_human_proof_ids_are_in_document",
            "- [ ] `separate_run385_action_decision_reviewed_before_single_submission`",
            "- [x] `separate_run385_action_decision_reviewed_before_single_submission`")

    def test_unverified_proof_cannot_be_checked_failure_is_non_retryable_and_run_result_is_not_claimed_by_submission(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec613_human_proof_ids_are_in_document",
            "- [ ] `failure_is_non_retryable_and_run_result_is_not_claimed_by_submission`",
            "- [x] `failure_is_non_retryable_and_run_result_is_not_claimed_by_submission`")

    def test_unverified_proof_cannot_be_checked_subsequent_2023_freeze_and_cell_results_reviewed_before_unlock(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec613_human_proof_ids_are_in_document",
            "- [ ] `subsequent_2023_freeze_and_cell_results_reviewed_before_unlock`",
            "- [x] `subsequent_2023_freeze_and_cell_results_reviewed_before_unlock`")

    def test_continuity_interval_cannot_disappear_reviewed_sha_check_to_dispatch_submission(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec620_continuity_intervals_are_listed",
            "- `reviewed_sha_check_to_dispatch_submission`",
            "- [unverified interval] `reviewed_sha_check_to_dispatch_submission`")

    def test_continuity_interval_cannot_disappear_dispatch_submission_to_server_ref_resolution(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec620_continuity_intervals_are_listed",
            "- `dispatch_submission_to_server_ref_resolution`",
            "- [unverified interval] `dispatch_submission_to_server_ref_resolution`")

    def test_continuity_interval_cannot_disappear_server_ref_resolution_to_run_record(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec620_continuity_intervals_are_listed",
            "- `server_ref_resolution_to_run_record`",
            "- [unverified interval] `server_ref_resolution_to_run_record`")

    def test_continuity_interval_cannot_disappear_run_record_to_post_dispatch_audit(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec620_continuity_intervals_are_listed",
            "- `run_record_to_post_dispatch_audit`",
            "- [unverified interval] `run_record_to_post_dispatch_audit`")

    def test_enforcement_claim_cannot_disappear_lock_effective(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec620_enforcement_claims_are_listed",
            "- `lock_effective`",
            "- [not observed] `lock_effective`")

    def test_enforcement_claim_cannot_disappear_ref_updates_blocked(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec620_enforcement_claims_are_listed",
            "- `ref_updates_blocked`",
            "- [not observed] `ref_updates_blocked`")

    def test_enforcement_claim_cannot_disappear_ref_deletion_blocked(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec620_enforcement_claims_are_listed",
            "- `ref_deletion_blocked`",
            "- [not observed] `ref_deletion_blocked`")

    def test_enforcement_claim_cannot_disappear_ref_recreation_blocked(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec620_enforcement_claims_are_listed",
            "- `ref_recreation_blocked`",
            "- [not observed] `ref_recreation_blocked`")

    def test_enforcement_claim_cannot_disappear_all_bypass_paths_blocked(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec620_enforcement_claims_are_listed",
            "- `all_bypass_paths_blocked`",
            "- [not observed] `all_bypass_paths_blocked`")

    def test_enforcement_claim_cannot_disappear_all_inherited_rules_visible(self):
        self._assert_handoff_guard_rejects(
            "test_all_dec620_enforcement_claims_are_listed",
            "- `all_inherited_rules_visible`",
            "- [not observed] `all_inherited_rules_visible`")

    def test_forged_release_status_cannot_silence_blocked_guard(self):
        self._assert_handoff_guard_rejects(
            "test_human_review_packet_cannot_claim_authorization",
            "release_status=BLOCKED",
            "release_status=AUTHORIZED")

    def test_authorization_command_does_not_enter_review_handoff(self):
        case = original.IndependentAdminWitnessHandoffSourceTests(
            "test_no_executable_dispatch_examples_in_review_packet")
        case.document = self.original + "\ngh workflow run test.yml\n"
        with self.assertRaises(AssertionError):
            case.test_no_executable_dispatch_examples_in_review_packet()
        self.assertEqual(original.DOC.read_text(encoding="utf-8"),
                         self.original)

    def test_no_separate_human_run385_decision_cannot_disappear(self):
        self._assert_handoff_guard_rejects(
            "test_frozen_historical_run_and_distinct_one_shot_identity",
            "2023/run385/attempt1",
            "2023/run385/attempt2")

    def test_unmodified_human_handoff_passes_all_twelve_source_guards(self):
        original.IndependentAdminWitnessHandoffSourceTests.setUpClass()
        case = original.IndependentAdminWitnessHandoffSourceTests(
            "test_all_dec613_human_proof_ids_are_in_document")
        case.document = self.original
        methods = [key for key in dir(case) if key.startswith("test_")]
        self.assertEqual(len(methods), 12)
        for method in methods:
            with self.subTest(method=method):
                getattr(case, method)()
