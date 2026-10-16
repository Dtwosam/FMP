from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

SOURCE=Path(__file__).resolve().parents[1]/(
    "scripts/dec1330_synthetic_annual_gate_proof_nonauthorizing.py")
spec=importlib.util.spec_from_file_location("dec1349_report_schema",SOURCE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

AUTHORITY_FLAGS=(
    "can_authorize_dispatch",
    "independent_os_proof_verified",
    "exclusive_annual_admission_verified",
    "run385_action_authorized",
    "may_access_protected_evidence",
    "may_merge_or_promote",
    "may_trade",
    "reviewer_evidence_authenticated",
)


class SyntheticReviewerOutputContract(unittest.TestCase):
    def test_exact_output_schema_has_no_unexpected_authority_field(self):
        r=module.assess_synthetic_claims({})
        self.assertEqual(
            set(r),
            {"classification","status","gate_states","blockers",
             *AUTHORITY_FLAGS})
        self.assertEqual(r["status"],"BLOCKED")
        self.assertEqual(
            r["classification"],"SOURCE_ONLY_SYNTHETIC_NONAUTHORITATIVE")
        for flag in AUTHORITY_FLAGS:
            self.assertIs(r[flag],False,flag)

    def test_required_static_blockers_always_prefix_diagnostics(self):
        cases=(
            None,
            {},
            {"proof":{"kind":"public_memfd_seals"}},
            {"annual":{"run_number":385,"attempt":1,
                       "outcome":"success",
                       "expected_sha":"a"*40,
                       "observed_sha":"a"*40}},
            {"gate_states":{"DEC-650/#820":"green"}},
        )
        for value in cases:
            with self.subTest(case=type(value).__name__):
                r=module.assess_synthetic_claims(value)
                self.assertIsInstance(r["blockers"],tuple)
                self.assertEqual(
                    r["blockers"][:len(module.STATIC_BLOCKERS)],
                    module.STATIC_BLOCKERS)
                self.assertEqual(
                    r["gate_states"],{"DEC-650/#820":"BLOCKED",
                                      "DEC-651/#821/#779":"BLOCKED"})

    def test_reports_have_deterministic_json_encoding(self):
        packet={"proof":{"kind":"source_only_model","independent":True},
                "annual":{"run_number":385,"attempt":1,
                          "outcome":"success",
                          "expected_sha":"a"*40,
                          "observed_sha":"a"*40}}
        first=module.assess_synthetic_claims(packet)
        second=module.assess_synthetic_claims(packet)
        self.assertEqual(first,second)
        serialized=json.dumps(first,sort_keys=True,
                              separators=(",",":"),ensure_ascii=True)
        self.assertEqual(
            serialized,json.dumps(second,sort_keys=True,
                                  separators=(",",":"),ensure_ascii=True))
        self.assertEqual(json.loads(serialized)["status"],"BLOCKED")
        self.assertIs(json.loads(serialized)["can_authorize_dispatch"],False)

    def test_unused_untrusted_metadata_cannot_change_diagnostics(self):
        baseline={"proof":{"kind":"inotify_quiet"},
                  "annual":{"run_number":385,"attempt":1,
                            "outcome":"failed"}}
        original=module.assess_synthetic_claims(baseline)
        forged={"proof":{"kind":"inotify_quiet",
                         "signed_by":"fabricated-security-reviewer",
                         "private_claims":{"grant":"ALL"}},
                "annual":{"run_number":385,"attempt":1,
                          "outcome":"failed",
                          "mutable_git_ref":"refs/heads/main",
                          "one_shot_authority":{"approved":True}},
                "unused":{"secret_like":"PUBLIC-FAKE-CANARY"}}
        other=module.assess_synthetic_claims(forged)
        self.assertEqual(original,other)
        self.assertNotIn("PUBLIC-FAKE-CANARY",repr(other))
        self.assertEqual(other["status"],"BLOCKED")
