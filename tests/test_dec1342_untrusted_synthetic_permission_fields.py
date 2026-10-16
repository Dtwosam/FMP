from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/(
    "scripts/dec1330_synthetic_annual_gate_proof_nonauthorizing.py")
spec=importlib.util.spec_from_file_location("dec1342_self_report_permissions",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ForgedSyntheticPermissionsNeverAuthorize(unittest.TestCase):
    def _evaluate(self,payload):
        r=module.assess_synthetic_claims(payload)
        self.assertEqual(r["status"],"BLOCKED")
        self.assertEqual(r["gate_states"],{"DEC-650/#820":"BLOCKED",
                                           "DEC-651/#821/#779":"BLOCKED"})
        for name in ("can_authorize_dispatch",
                     "independent_os_proof_verified",
                     "run385_action_authorized",
                     "exclusive_annual_admission_verified",
                     "may_access_protected_evidence",
                     "may_merge_or_promote","may_trade",
                     "reviewer_evidence_authenticated"):
            self.assertIs(r[name],False)
        return r["blockers"]

    def test_self_asserted_gate_states_cannot_override_blocked(self):
        b=self._evaluate(
            {"gate_states":{"DEC-650/#820":"VERIFIED",
                            "DEC-651/#821/#779":"AUTHORIZED"}})
        self.assertIn("UNTRUSTED_PERMISSION_FIELDS_IGNORED",b)

    def test_each_permission_field_even_false_is_untrusted_claim(self):
        for key in module.UNTRUSTED_AUTHORITY_FIELDS:
            with self.subTest(key=key):
                b=self._evaluate({key:False})
                self.assertIn("UNTRUSTED_PERMISSION_FIELDS_IGNORED",b)

    def test_approval_looking_mixed_packet_is_rejected(self):
        claimed={key:True for key in module.UNTRUSTED_AUTHORITY_FIELDS}
        claimed["annual"]={"run_number":385,"attempt":1,
                           "expected_sha":"a"*40,"observed_sha":"a"*40}
        claimed["proof"]={"kind":"x509","independent":True,
                          "signed_by_admin":True}
        b=self._evaluate(claimed)
        self.assertIn("UNTRUSTED_PERMISSION_FIELDS_IGNORED",b)
        self.assertIn("CALLER_SELF_ASSERTED_AUTHORITY_IGNORED",b)
        self.assertIn("SHA_EQUALITY_ALONE_NOT_INDEPENDENT_REF_AUTHORITY",b)
        self.assertIn("INDEPENDENCE_SELF_ASSERTION_NOT_AUTHENTICATED",b)

    def test_packet_without_asserted_permission_keys_never_authorizes(self):
        b=self._evaluate(
            {"proof":{"kind":"inotify_quiet"},
             "annual":{"run_number":385,"attempt":1}})
        self.assertNotIn("UNTRUSTED_PERMISSION_FIELDS_IGNORED",b)
        self.assertIn("INDEPENDENT_PROTECTED_ORIGINAL_OS_NO_WRITE_UNVERIFIED",b)
