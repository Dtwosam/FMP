from __future__ import annotations

import importlib.util
from itertools import product
from pathlib import Path
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/(
    "scripts/dec1330_synthetic_annual_gate_proof_nonauthorizing.py")
spec=importlib.util.spec_from_file_location("dec1338_synthetic_matrix",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

MANDATORY_FALSE=(
    "can_authorize_dispatch","independent_os_proof_verified",
    "exclusive_annual_admission_verified","run385_action_authorized",
    "may_access_protected_evidence","may_merge_or_promote",
    "may_trade","reviewer_evidence_authenticated",
)


class SyntheticAnnualClaimCrossProductDenials(unittest.TestCase):
    def _deny(self,packet):
        result=module.assess_synthetic_claims(packet)
        self.assertEqual(result["status"],"BLOCKED")
        self.assertEqual(result["classification"],
                         "SOURCE_ONLY_SYNTHETIC_NONAUTHORITATIVE")
        self.assertEqual(result["gate_states"],
                         {"DEC-650/#820":"BLOCKED",
                          "DEC-651/#821/#779":"BLOCKED"})
        for flag in MANDATORY_FALSE:
            self.assertIs(result[flag],False,flag)
        return result

    def test_all_self_assertion_boolean_combinations_stay_blocked(self):
        flags=module.SELF_ASSERTIONS
        self.assertEqual(len(flags),7)
        for values in product((False,True),repeat=len(flags)):
            packet=dict(zip(flags,values))
            packet["annual"]={
                "run_number":385,"attempt":1,
                "expected_sha":"same","observed_sha":"same"}
            result=self._deny(packet)
            if any(values):
                self.assertIn("CALLER_SELF_ASSERTED_AUTHORITY_IGNORED",
                              result["blockers"])

    def test_every_known_proof_kind_and_independence_claim_is_untrusted(self):
        for kind,claimed in product(
                module.UNTRUSTED_PROOF_FORMS,(False,True)):
            with self.subTest(kind=kind,claimed=claimed):
                result=self._deny(
                    {"proof":{"kind":kind,"independent":claimed}})
                self.assertIn(
                    "DISPOSABLE_OR_SELF_REPORTED_PROOF_IS_NOT_PROTECTED_WITNESS",
                    result["blockers"])
                if claimed:
                    self.assertIn(
                        "INDEPENDENCE_SELF_ASSERTION_NOT_AUTHENTICATED",
                        result["blockers"])

    def test_all_terminal_outcomes_and_attempt_classes_stay_blocked(self):
        outcomes=("ambiguous","failed","cancelled",
                  "retry","replacement","success",None)
        attempts=(0,1,2,True,1.0)
        for outcome,attempt in product(outcomes,attempts):
            with self.subTest(outcome=outcome,attempt=repr(attempt)):
                result=self._deny(
                    {"annual":{"run_number":385,"attempt":attempt,
                               "outcome":outcome}})
                if outcome in outcomes[:5]:
                    self.assertIn(
                        "TERMINAL_NO_RETRY_AMBIGUOUS_OR_FAILED_SLOT",
                        result["blockers"])
                if type(attempt) is not int or attempt!=1:
                    self.assertIn(
                        "NOT_THE_EXCLUSIVE_RUN385_ATTEMPT1",
                        result["blockers"])

    def test_sha_claim_classes_cannot_override_absent_security_gates(self):
        sha_pairs=((None,None),("",""),("left","right"),
                   ("same","same"),(1,1),(True,True))
        for expected,observed in sha_pairs:
            with self.subTest(expected=repr(expected),
                              observed=repr(observed)):
                result=self._deny(
                    {"proof":{"kind":"self_signed_sha","independent":True},
                     "annual":{"run_number":385,"attempt":1,
                               "expected_sha":expected,
                               "observed_sha":observed}})
                if type(expected) is not str or not expected:
                    self.assertIn(
                        "SHA_BINDING_IDENTITIES_ABSENT_OR_INVALID",
                        result["blockers"])
                elif expected==observed:
                    self.assertIn(
                        "SHA_EQUALITY_ALONE_NOT_INDEPENDENT_REF_AUTHORITY",
                        result["blockers"])
                else:
                    self.assertIn("SHA_MISMATCH_BLOCKS_ADMISSION",
                                  result["blockers"])
