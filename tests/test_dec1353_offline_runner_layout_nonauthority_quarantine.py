from __future__ import annotations

import ast
from contextlib import ExitStack
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"scripts"/"dec1351_synthetic_runner_isolation_layout.py"
spec=importlib.util.spec_from_file_location("dec1353_layout_scope",MODULE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def canonical():
    return {
        "stages":(
            "trusted_staging","restricted_consumer","trusted_uploader"),
        "original_source_mode":"read_only",
        "scratch_mode":"separate_read_write",
        "publication":"trusted_external_only",
        "scope":"generated_public_only",
        "consumer":{
            "uid_isolated":True,"no_new_privs":True,
            "can_sudo":False,"ambient_caps":0,
            "inherited_writable_source_fds":0,
            "inherited_writable_source_maps":0,
            "fd0":"safe_input","fd1":"scratch_output",
            "fd2":"scratch_error","policy_before_first_access":True,
        },
    }


class SyntheticRunnerLayoutMustRemainSourceOnly(unittest.TestCase):
    def _blocked(self):
        r=module.assess_synthetic_runner_layout(canonical())
        self.assertIs(r["design_consistent"],True)
        self.assertEqual(r["status"],"BLOCKED")
        for key in (
            "independent_os_proof_verified",
            "immutable_annual_admission_verified",
            "can_authorize_dispatch",
            "may_access_protected_evidence",
            "may_install_workflow_or_policy",
            "may_trade",
        ):
            self.assertIs(r[key],False,key)
        return r

    def test_runner_layout_module_imports_no_host_or_io_libraries(self):
        syntax=ast.parse(MODULE.read_text(encoding="utf-8"))
        imports=[n for n in ast.walk(syntax)
                 if isinstance(n,(ast.Import,ast.ImportFrom))]
        self.assertEqual(len(imports),1)
        self.assertIsInstance(imports[0],ast.ImportFrom)
        self.assertEqual(imports[0].module,"__future__")
        self.assertEqual([n.name for n in imports[0].names],
                         ["annotations"])

    def test_no_installed_workflow_or_packaged_python_uses_layout_model(self):
        names=("dec1351_synthetic_runner_isolation_layout",
               "assess_synthetic_runner_layout")
        checked=0
        for folder,pattern in (
            (ROOT/".github"/"workflows","*.yml"),
            (ROOT/"src","*.py"),
        ):
            self.assertTrue(folder.is_dir())
            entries=sorted(p for p in folder.rglob(pattern) if p.is_file())
            self.assertGreater(len(entries),0)
            for file in entries:
                body=file.read_text(encoding="utf-8")
                for name in names:
                    self.assertNotIn(
                        name,body,
                        "symbolic layout must not be part of production")
                checked+=1
        self.assertGreater(checked,0)

    def test_rehearsal_never_calls_file_process_or_network_apis(self):
        with ExitStack() as stack:
            for api in (
                "builtins.open","os.open","os.system",
                "subprocess.Popen","subprocess.run","socket.socket",
            ):
                stack.enter_context(patch(
                    api,side_effect=AssertionError(
                        "offline layout attempted host action: "+api)))
            self._blocked()

    def test_result_mutation_does_not_change_fresh_gate_denial(self):
        first=self._blocked()
        first["gate_states"]["DEC-650/#820"]="FORGED_APPROVAL"
        first["status"]="FORGED_APPROVAL"
        first["violations"]=("forged",)
        again=self._blocked()
        self.assertEqual(again["gate_states"]["DEC-650/#820"],"BLOCKED")
        self.assertEqual(again["status"],"BLOCKED")
        self.assertEqual(again["violations"],())
