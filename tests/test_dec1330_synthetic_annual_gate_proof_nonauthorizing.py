from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

MODULE=Path(__file__).resolve().parents[1] / (
    "scripts/dec1330_synthetic_annual_gate_proof_nonauthorizing.py")
spec=importlib.util.spec_from_file_location("dec1330_synthetic_assessment",MODULE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SyntheticAnnualProofMustNotAuthorize(unittest.TestCase):
    def _blocked(self, packet):
        result=module.assess_synthetic_claims(packet)
        self.assertEqual(result["classification"],
                         "SOURCE_ONLY_SYNTHETIC_NONAUTHORITATIVE")
        self.assertEqual(result["status"],"BLOCKED")
        for key in (
            "can_authorize_dispatch","independent_os_proof_verified",
            "exclusive_annual_admission_verified","run385_action_authorized",
            "may_access_protected_evidence","may_merge_or_promote",
            "may_trade","reviewer_evidence_authenticated"):
            self.assertIs(result[key],False,key)
        self.assertEqual(result["gate_states"],
                         {"DEC-650/#820":"BLOCKED",
                          "DEC-651/#821/#779":"BLOCKED"})
        self.assertIn(
            "INDEPENDENT_PROTECTED_ORIGINAL_OS_NO_WRITE_UNVERIFIED",
            result["blockers"])
        self.assertIn(
            "EXCLUSIVE_IMMUTABLE_ANNUAL_REF_SHA_UNVERIFIED",
            result["blockers"])
        return result

    def test_empty_packet_never_authorizes(self):
        r=self._blocked({})
        self.assertIn("INDEPENDENT_PROOF_NOT_SUPPLIED",r["blockers"])
        self.assertIn("ANNUAL_ADMISSION_DETAILS_MISSING",r["blockers"])

    def test_non_mapping_packet_never_authorizes(self):
        for packet in (None,True,[],0,"green"):
            with self.subTest(packet=repr(packet)):
                r=self._blocked(packet)
                self.assertIn("INPUT_NOT_A_MAPPING",r["blockers"])

    def test_self_asserted_all_green_flags_ignored(self):
        data={name:True for name in module.SELF_ASSERTIONS}
        r=self._blocked(data)
        self.assertIn(
            "CALLER_SELF_ASSERTED_AUTHORITY_IGNORED",r["blockers"])

    def test_quiet_inotify_is_not_independent_no_write(self):
        r=self._blocked({"proof":{"kind":"inotify_quiet",
                                  "independent":True}})
        self.assertIn(
            "DISPOSABLE_OR_SELF_REPORTED_PROOF_IS_NOT_PROTECTED_WITNESS",
            r["blockers"])
        self.assertIn(
            "INDEPENDENCE_SELF_ASSERTION_NOT_AUTHENTICATED",
            r["blockers"])

    def test_public_memfd_seals_do_not_prove_protected_source(self):
        r=self._blocked({"proof":{"kind":"public_memfd_seals",
                                  "seal_bits":"all","independent":True}})
        self.assertIn(
            "DISPOSABLE_OR_SELF_REPORTED_PROOF_IS_NOT_PROTECTED_WITNESS",
            r["blockers"])

    def test_public_tmp_original_and_parent_events_are_not_enforcement(self):
        r=self._blocked({"proof":{"kind":"public_tmp_fixture",
                                  "source_wd":1,"parent_wd":2}})
        self.assertIn(
            "DISPOSABLE_OR_SELF_REPORTED_PROOF_IS_NOT_PROTECTED_WITNESS",
            r["blockers"])

    def test_self_signed_sha_equality_does_not_bind_dispatch(self):
        r=self._blocked({"proof":{"kind":"self_signed_sha"},
                         "annual":{"run_number":385,"attempt":1,
                                   "expected_sha":"abc","observed_sha":"abc"}})
        self.assertIn(
            "SHA_EQUALITY_ALONE_NOT_INDEPENDENT_REF_AUTHORITY",
            r["blockers"])

    def test_attempt_two_cannot_be_authorized(self):
        r=self._blocked({"annual":{"run_number":385,"attempt":2}})
        self.assertIn("NOT_THE_EXCLUSIVE_RUN385_ATTEMPT1",r["blockers"])

    def test_ambiguous_outcome_is_terminal_not_retry(self):
        for outcome in ("ambiguous","failed","cancelled","retry","replacement"):
            with self.subTest(outcome=outcome):
                r=self._blocked({"annual":{"run_number":385,"attempt":1,
                                           "outcome":outcome}})
                self.assertIn(
                    "TERMINAL_NO_RETRY_AMBIGUOUS_OR_FAILED_SLOT",
                    r["blockers"])

    def test_fake_independent_signature_still_unauthenticated(self):
        r=self._blocked({"proof":{"kind":"x509","independent":True,
                                  "signed":"yes","verified":"yes"},
                         "annual":{"run_number":385,"attempt":1}})
        self.assertIn(
            "UNVERIFIABLE_CLAIM_CANNOT_ESTABLISH_TRUST",
            r["blockers"])

    def test_input_packet_not_mutated(self):
        packet={"proof":{"kind":"public_memfd_seals","independent":True},
                "annual":{"run_number":385,"attempt":1},
                "can_authorize_dispatch":True}
        previous=copy.deepcopy(packet)
        self._blocked(packet)
        self.assertEqual(packet,previous)

    def test_status_stable_under_mapping_key_order(self):
        one={"annual":{"run_number":385,"attempt":1},
             "proof":{"kind":"inotify_quiet"}}
        two={"proof":{"kind":"inotify_quiet"},
             "annual":{"attempt":1,"run_number":385}}
        a=self._blocked(one)
        b=self._blocked(two)
        self.assertEqual(a,b)

    def test_missing_sha_pair_is_absent_not_equal(self):
        r=self._blocked({"annual":{"run_number":385,"attempt":1}})
        self.assertIn("SHA_BINDING_IDENTITIES_ABSENT_OR_INVALID",
                      r["blockers"])
        self.assertNotIn("SHA_EQUALITY_ALONE_NOT_INDEPENDENT_REF_AUTHORITY",
                         r["blockers"])

    def test_blank_or_nonstr_sha_claims_are_invalid(self):
        for expected,observed in (("", "abc"),("abc", ""), (None,None),
                                  (123,123), (True,True)):
            with self.subTest(expected=repr(expected),observed=repr(observed)):
                r=self._blocked(
                    {"annual":{"run_number":385,"attempt":1,
                               "expected_sha":expected,
                               "observed_sha":observed}})
                self.assertIn("SHA_BINDING_IDENTITIES_ABSENT_OR_INVALID",
                              r["blockers"])

    def test_different_sha_values_block_admission(self):
        r=self._blocked(
            {"annual":{"run_number":385,"attempt":1,
                       "expected_sha":"expected-commit",
                       "observed_sha":"different-commit"}})
        self.assertIn("SHA_MISMATCH_BLOCKS_ADMISSION",r["blockers"])
        self.assertNotIn("SHA_EQUALITY_ALONE_NOT_INDEPENDENT_REF_AUTHORITY",
                         r["blockers"])
