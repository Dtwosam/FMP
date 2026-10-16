from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/(
    "scripts/dec1330_synthetic_annual_gate_proof_nonauthorizing.py")
spec=importlib.util.spec_from_file_location("dec1344_no_reflection",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CANARY="PUBLIC-SYNTHETIC-CANARY-NOT-A-REAL-TOKEN-DEC1344"


class SyntheticReviewerNeverEchoesCallerCanaries(unittest.TestCase):
    def _not_reflected(self, packet, canary=CANARY):
        r=module.assess_synthetic_claims(packet)
        self.assertNotIn(canary,repr(r))
        self.assertEqual(r["status"],"BLOCKED")
        for name in ("can_authorize_dispatch",
                     "independent_os_proof_verified",
                     "exclusive_annual_admission_verified",
                     "run385_action_authorized",
                     "may_access_protected_evidence",
                     "reviewer_evidence_authenticated",
                     "may_merge_or_promote","may_trade"):
            self.assertIs(r[name],False)
        self.assertEqual(r["gate_states"],
                         {"DEC-650/#820":"BLOCKED",
                          "DEC-651/#821/#779":"BLOCKED"})
        return r

    def test_untrusted_top_level_credential_fields_are_not_echoed(self):
        packet={"authorization":CANARY,"access_token":CANARY,
                "password":CANARY,"api_key":CANARY,
                "can_authorize_dispatch":True}
        result=self._not_reflected(packet)
        self.assertIn("CALLER_SELF_ASSERTED_AUTHORITY_IGNORED",
                      result["blockers"])

    def test_untrusted_nested_proof_canaries_are_not_echoed(self):
        packet={"proof":{"kind":"x509","independent":True,
                         "key_id":CANARY,"signature":CANARY,
                         "metadata":{"authorization":CANARY,
                                     "private_key":CANARY}}}
        result=self._not_reflected(packet)
        self.assertIn("UNVERIFIABLE_CLAIM_CANNOT_ESTABLISH_TRUST",
                      result["blockers"])

    def test_synthetic_sha_canary_does_not_leak_into_findings(self):
        packet={"annual":{"run_number":385,"attempt":1,
                          "expected_sha":CANARY,"observed_sha":CANARY,
                          "workflow_ref":CANARY,"reviewer":CANARY}}
        result=self._not_reflected(packet)
        self.assertIn("SHA_CLAIMS_MALFORMED_GIT_SHA1_TEXT",
                      result["blockers"])

    def test_multiline_unicode_canary_stays_absent_from_returned_report(self):
        canary="PUBLIC TEST ONLY 密碼\nBearer: dec1344-multiline-nonsecret"
        packet={"proof":{"kind":canary,"independent":True},
                "annual":{"run_number":385,"attempt":1,
                          "outcome":canary,
                          "expected_sha":canary,"observed_sha":canary},
                "metadata":{"note":canary}}
        result=self._not_reflected(packet,canary)
        self.assertIn("ANNUAL_OUTCOME_MISSING_OR_UNRECOGNIZED",
                      result["blockers"])
