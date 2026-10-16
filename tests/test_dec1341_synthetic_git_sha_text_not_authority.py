from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE=Path(__file__).resolve().parents[1]/(
    "scripts/dec1330_synthetic_annual_gate_proof_nonauthorizing.py")
spec=importlib.util.spec_from_file_location("dec1341_synthetic_oid",MODULE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SyntheticOidSyntaxCanNeverAuthorize(unittest.TestCase):
    def _check(self, expected, observed):
        r=module.assess_synthetic_claims(
            {"proof":{"kind":"self_signed_sha","independent":True},
             "annual":{"run_number":385,"attempt":1,
                       "expected_sha":expected,"observed_sha":observed},
             "can_authorize_dispatch":True})
        self.assertEqual(r["status"],"BLOCKED")
        self.assertEqual(r["classification"],
                         "SOURCE_ONLY_SYNTHETIC_NONAUTHORITATIVE")
        self.assertEqual(
            r["gate_states"],{"DEC-650/#820":"BLOCKED",
                              "DEC-651/#821/#779":"BLOCKED"})
        for k in ("can_authorize_dispatch","independent_os_proof_verified",
                  "exclusive_annual_admission_verified",
                  "run385_action_authorized","may_access_protected_evidence",
                  "reviewer_evidence_authenticated","may_merge_or_promote",
                  "may_trade"):
            self.assertIs(r[k],False,k)
        return r["blockers"]

    def test_two_normal_40_digit_lower_hex_strings_also_not_authority(self):
        blocks=self._check("a"*40,"a"*40)
        self.assertNotIn("SHA_CLAIMS_MALFORMED_GIT_SHA1_TEXT",blocks)
        self.assertIn("SHA_EQUALITY_ALONE_NOT_INDEPENDENT_REF_AUTHORITY",
                      blocks)

    def test_two_distinct_normal_40_digit_hex_strings_are_not_authority(self):
        blocks=self._check("a"*40,"b"*40)
        self.assertNotIn("SHA_CLAIMS_MALFORMED_GIT_SHA1_TEXT",blocks)
        self.assertIn("SHA_MISMATCH_BLOCKS_ADMISSION",blocks)

    def test_truncated_or_excessively_long_sha_claim_is_marked_malformed(self):
        for value in ("a","a"*39,"a"*41,"a"*64):
            with self.subTest(length=len(value)):
                blocks=self._check(value,value)
                self.assertIn("SHA_CLAIMS_MALFORMED_GIT_SHA1_TEXT",blocks)
                self.assertIn(
                    "SHA_EQUALITY_ALONE_NOT_INDEPENDENT_REF_AUTHORITY",
                    blocks)

    def test_uppercase_nonhex_and_unicode_sha_claims_are_malformed(self):
        for value in ("A"*40,"g"*40,"é"*40,"ａ"*40):
            with self.subTest(repr=repr(value)):
                blocks=self._check(value,value)
                self.assertIn("SHA_CLAIMS_MALFORMED_GIT_SHA1_TEXT",blocks)

    def test_equal_short_self_reported_sha_from_legacy_fixture_is_malformed(self):
        blocks=self._check("abc","abc")
        self.assertIn("SHA_CLAIMS_MALFORMED_GIT_SHA1_TEXT",blocks)
        self.assertIn("SHA_EQUALITY_ALONE_NOT_INDEPENDENT_REF_AUTHORITY",
                      blocks)
