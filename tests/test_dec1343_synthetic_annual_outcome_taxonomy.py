from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE=Path(__file__).resolve().parents[1]/(
    "scripts/dec1330_synthetic_annual_gate_proof_nonauthorizing.py")
spec=importlib.util.spec_from_file_location("dec1343_synthetic_outcome",MODULE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SyntheticAnnualOutcomeClaimsRemainNonauthorizing(unittest.TestCase):
    def _blockers(self,outcome_given=False,outcome=None):
        annual={"run_number":385,"attempt":1,
                "expected_sha":"a"*40,"observed_sha":"a"*40}
        if outcome_given:
            annual["outcome"]=outcome
        r=module.assess_synthetic_claims({"annual":annual})
        self.assertEqual(r["status"],"BLOCKED")
        self.assertEqual(
            r["gate_states"],{"DEC-650/#820":"BLOCKED",
                              "DEC-651/#821/#779":"BLOCKED"})
        for key in ("can_authorize_dispatch","run385_action_authorized",
                    "independent_os_proof_verified",
                    "exclusive_annual_admission_verified",
                    "may_access_protected_evidence","may_trade",
                    "may_merge_or_promote","reviewer_evidence_authenticated"):
            self.assertIs(r[key],False)
        return r["blockers"]

    def test_missing_and_nonstring_outcomes_are_explicitly_unrecognized(self):
        b=self._blockers()
        self.assertIn("ANNUAL_OUTCOME_MISSING_OR_UNRECOGNIZED",b)
        for value in (None,False,1,[],{}):
            with self.subTest(outcome=repr(value)):
                b=self._blockers(True,value)
                self.assertIn("ANNUAL_OUTCOME_MISSING_OR_UNRECOGNIZED",b)

    def test_unrecognized_success_spelling_and_whitespace_are_not_accepted(self):
        for value in ("SUCCESS"," success","success ","succeeded",
                      "in_progress","ok",""):
            with self.subTest(outcome=value):
                b=self._blockers(True,value)
                self.assertIn("ANNUAL_OUTCOME_MISSING_OR_UNRECOGNIZED",b)
                self.assertNotIn(
                    "CLAIMED_SUCCESS_NOT_INDEPENDENT_SLOT_ATTESTATION",b)

    def test_claimed_success_never_proves_actual_run385_slot(self):
        b=self._blockers(True,"success")
        self.assertIn("CLAIMED_SUCCESS_NOT_INDEPENDENT_SLOT_ATTESTATION",b)
        self.assertNotIn("TERMINAL_NO_RETRY_AMBIGUOUS_OR_FAILED_SLOT",b)
        self.assertIn("EXCLUSIVE_IMMUTABLE_ANNUAL_REF_SHA_UNVERIFIED",b)

    def test_all_terminal_and_retry_claims_remain_terminal_hold(self):
        for value in ("ambiguous","failed","cancelled",
                      "retry","replacement"):
            with self.subTest(outcome=value):
                b=self._blockers(True,value)
                self.assertIn(
                    "TERMINAL_NO_RETRY_AMBIGUOUS_OR_FAILED_SLOT",b)
