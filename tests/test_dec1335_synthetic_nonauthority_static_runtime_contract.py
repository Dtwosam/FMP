from __future__ import annotations

import ast
import builtins
from contextlib import ExitStack
import importlib.util
import os
from pathlib import Path
import socket
import subprocess
import unittest
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parents[1]/(
    "scripts/dec1330_synthetic_annual_gate_proof_nonauthorizing.py")
spec=importlib.util.spec_from_file_location("dec1335_synthetic_contract",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SyntheticProofSourceIsNeverLiveAuthority(unittest.TestCase):
    def test_source_module_imports_only_future_annotations(self):
        syntax=ast.parse(SCRIPT.read_text(encoding="utf-8"))
        imports=[node for node in ast.walk(syntax)
                 if isinstance(node,(ast.Import,ast.ImportFrom))]
        self.assertEqual(len(imports),1)
        self.assertIsInstance(imports[0],ast.ImportFrom)
        self.assertEqual(imports[0].module,"__future__")
        self.assertEqual([alias.name for alias in imports[0].names],
                         ["annotations"])

    def test_module_source_contains_no_io_or_dynamic_execution_calls(self):
        syntax=ast.parse(SCRIPT.read_text(encoding="utf-8"))
        dangerous={
            "open","exec","eval","compile","__import__","input",
            "read_text","read_bytes","write_text","write_bytes",
            "system","popen","Popen","run","call","check_call",
            "check_output","connect","socket","request","urlopen",
            "send","sendall","fetch","post","put","delete",
            "dispatch","execute","merge","promote","place_order",
        }
        for node in ast.walk(syntax):
            if not isinstance(node,ast.Call):
                continue
            invoked=(node.func.id if isinstance(node.func,ast.Name)
                     else node.func.attr if isinstance(node.func,ast.Attribute)
                     else None)
            self.assertNotIn(invoked,dangerous,invoked)

    def test_assessment_never_calls_host_file_socket_or_process_io(self):
        packet={"proof":{"kind":"public_memfd_seals","independent":True},
                "annual":{"run_number":385,"attempt":1,
                          "expected_sha":"abc","observed_sha":"abc"},
                "can_authorize_dispatch":True}
        with ExitStack() as stack:
            for location in ("builtins.open","os.open","socket.socket",
                             "subprocess.Popen","subprocess.run"):
                stack.enter_context(patch(location,side_effect=AssertionError(
                    "synthetic classifier attempted IO: "+location)))
            result=module.assess_synthetic_claims(packet)
        self.assertEqual(result["status"],"BLOCKED")
        self.assertIs(result["can_authorize_dispatch"],False)
        self.assertIs(result["may_access_protected_evidence"],False)
        self.assertIs(result["may_trade"],False)

    def test_mutating_prior_result_cannot_affect_next_result(self):
        first=module.assess_synthetic_claims({})
        first["gate_states"]["DEC-650/#820"]="UNTRUSTED_FORGED_GREEN"
        first["blockers"]=()
        first["status"]="UNTRUSTED_FORGED_GREEN"
        second=module.assess_synthetic_claims({})
        self.assertEqual(second["status"],"BLOCKED")
        self.assertEqual(second["gate_states"]["DEC-650/#820"],"BLOCKED")
        self.assertIn("INDEPENDENT_PROTECTED_ORIGINAL_OS_NO_WRITE_UNVERIFIED",
                      second["blockers"])
        self.assertIs(second["independent_os_proof_verified"],False)

    def test_adversarial_plain_dictionary_all_green_stays_blocked(self):
        packet={name:True for name in module.SELF_ASSERTIONS}
        packet.update({
            "proof":{"kind":"x509","independent":True,"verified":True,
                     "signed":True,"protected_original":True},
            "annual":{"run_number":385,"attempt":1,
                      "expected_sha":"same-hash","observed_sha":"same-hash",
                      "outcome":"success","immutable":True,
                      "unique_slot":True,"admitted":True},
            "gate_states":{"DEC-650/#820":"VERIFIED",
                           "DEC-651/#821/#779":"APPROVED"},
            "may_trade":True,
        })
        result=module.assess_synthetic_claims(packet)
        self.assertEqual(result["status"],"BLOCKED")
        self.assertEqual(result["gate_states"],
                         {"DEC-650/#820":"BLOCKED",
                          "DEC-651/#821/#779":"BLOCKED"})
        for key in ("can_authorize_dispatch","independent_os_proof_verified",
                    "run385_action_authorized","may_access_protected_evidence",
                    "exclusive_annual_admission_verified",
                    "reviewer_evidence_authenticated","may_trade",
                    "may_merge_or_promote"):
            self.assertIs(result[key],False,key)
        self.assertIn("SHA_EQUALITY_ALONE_NOT_INDEPENDENT_REF_AUTHORITY",
                      result["blockers"])
