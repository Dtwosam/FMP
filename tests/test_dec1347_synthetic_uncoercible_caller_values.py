from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

SOURCE=Path(__file__).resolve().parents[1]/(
    "scripts/dec1330_synthetic_annual_gate_proof_nonauthorizing.py")
spec=importlib.util.spec_from_file_location("dec1347_uncoercible",SOURCE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExplosiveValue:
    def __eq__(self, other):
        raise AssertionError("untrusted value __eq__ executed")

    def __bool__(self):
        raise AssertionError("untrusted value __bool__ executed")

    def __str__(self):
        raise AssertionError("untrusted value __str__ executed")

    def __repr__(self):
        raise AssertionError("untrusted value __repr__ executed")

    def __iter__(self):
        raise AssertionError("untrusted value __iter__ executed")


class SyntheticPacketObjectsMustNeverExecute(unittest.TestCase):
    def _blocked(self, packet):
        result=module.assess_synthetic_claims(packet)
        self.assertEqual(result["classification"],
                         "SOURCE_ONLY_SYNTHETIC_NONAUTHORITATIVE")
        self.assertEqual(result["status"],"BLOCKED")
        self.assertEqual(result["gate_states"],
                         {"DEC-650/#820":"BLOCKED",
                          "DEC-651/#821/#779":"BLOCKED"})
        for key in (
            "can_authorize_dispatch", "independent_os_proof_verified",
            "exclusive_annual_admission_verified", "run385_action_authorized",
            "may_access_protected_evidence", "may_merge_or_promote",
            "may_trade", "reviewer_evidence_authenticated",
        ):
            self.assertIs(result[key],False,key)
        return result["blockers"]

    def test_explosive_proof_kind_and_independent_value_not_evaluated(self):
        b=self._blocked(
            {"proof":{"kind":ExplosiveValue(),
                      "independent":ExplosiveValue()}})
        self.assertIn("UNVERIFIABLE_CLAIM_CANNOT_ESTABLISH_TRUST",b)
        self.assertNotIn("INDEPENDENCE_SELF_ASSERTION_NOT_AUTHENTICATED",b)

    def test_explosive_annual_identity_and_sha_values_not_evaluated(self):
        b=self._blocked(
            {"annual":{"run_number":ExplosiveValue(),
                       "attempt":ExplosiveValue(),
                       "outcome":ExplosiveValue(),
                       "expected_sha":ExplosiveValue(),
                       "observed_sha":ExplosiveValue()}})
        for reason in (
            "NOT_THE_EXCLUSIVE_RUN385_ATTEMPT1",
            "ANNUAL_OUTCOME_MISSING_OR_UNRECOGNIZED",
            "SHA_BINDING_IDENTITIES_ABSENT_OR_INVALID",
        ):
            self.assertIn(reason,b)

    def test_explosive_permission_values_are_never_coerced(self):
        b=self._blocked(
            {"can_authorize_dispatch":ExplosiveValue(),
             "independent_os_proof_verified":ExplosiveValue(),
             "gate_states":ExplosiveValue(),
             "passed_ci":ExplosiveValue()})
        self.assertIn("UNTRUSTED_PERMISSION_FIELDS_IGNORED",b)
        self.assertNotIn("CALLER_SELF_ASSERTED_AUTHORITY_IGNORED",b)

    def test_arbitrary_unused_nested_objects_are_not_inspected(self):
        b=self._blocked(
            {"untrusted_metadata":{"private_key":ExplosiveValue()},
             "proof":{"kind":"source_only_model","other":ExplosiveValue()},
             "annual":{"run_number":385,"attempt":1,
                       "outcome":"success","unused":ExplosiveValue(),
                       "expected_sha":"a"*40,"observed_sha":"a"*40}})
        self.assertIn(
            "DISPOSABLE_OR_SELF_REPORTED_PROOF_IS_NOT_PROTECTED_WITNESS",b)
        self.assertIn("CLAIMED_SUCCESS_NOT_INDEPENDENT_SLOT_ATTESTATION",b)
        self.assertIn("SHA_EQUALITY_ALONE_NOT_INDEPENDENT_REF_AUTHORITY",b)

    def test_nonstring_binary_claims_do_not_become_strings(self):
        b=self._blocked(
            {"proof":{"kind":b"public_memfd_seals"},
             "annual":{"run_number":385,"attempt":1,
                       "outcome":b"success",
                       "expected_sha":b"a"*40,
                       "observed_sha":b"a"*40}})
        self.assertIn("UNVERIFIABLE_CLAIM_CANNOT_ESTABLISH_TRUST",b)
        self.assertIn("ANNUAL_OUTCOME_MISSING_OR_UNRECOGNIZED",b)
        self.assertIn("SHA_BINDING_IDENTITIES_ABSENT_OR_INVALID",b)
