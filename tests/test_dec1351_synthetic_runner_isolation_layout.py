from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

MODULE=Path(__file__).resolve().parents[1]/(
    "scripts/dec1351_synthetic_runner_isolation_layout.py")
spec=importlib.util.spec_from_file_location("dec1351_layout",MODULE)
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


class OfflineRunnerLayoutMustNeverApprove(unittest.TestCase):
    def _assess(self,packet,consistent=False):
        r=module.assess_synthetic_runner_layout(packet)
        self.assertIs(r["design_consistent"],consistent)
        self.assertEqual(r["status"],"BLOCKED")
        self.assertEqual(
            r["gate_states"],{"DEC-650/#820":"BLOCKED",
                              "DEC-651/#821/#779":"BLOCKED"})
        for key in ("independent_os_proof_verified",
                    "immutable_annual_admission_verified",
                    "can_authorize_dispatch","may_access_protected_evidence",
                    "may_install_workflow_or_policy","may_trade"):
            self.assertIs(r[key],False,key)
        return r["violations"]

    def test_even_complete_synthetic_three_stage_layout_never_authorizes(self):
        self.assertEqual(self._assess(canonical(),consistent=True),())

    def test_missing_or_wrong_stage_order_is_rejected(self):
        for order in (
            ("restricted_consumer","trusted_staging","trusted_uploader"),
            ("trusted_staging","trusted_uploader","restricted_consumer"),
            ("trusted_staging","restricted_consumer"),
            ["trusted_staging","restricted_consumer","trusted_uploader"],
        ):
            with self.subTest(order=order):
                x=canonical();x["stages"]=order
                b=self._assess(x)
                self.assertIn("STAGING_CONSUMER_UPLOADER_ORDER_NOT_PINNED",b)

    def test_writable_original_and_shared_scratch_are_rejected(self):
        for field,value,label in (
            ("original_source_mode","read_write",
             "SYNTHETIC_ORIGINAL_NOT_READONLY"),
            ("scratch_mode","same_as_original",
             "SCRATCH_NOT_INDEPENDENT_OF_ORIGINAL"),
            ("publication","inside_original",
             "REPORT_PUBLICATION_NOT_EXTERNAL"),
        ):
            with self.subTest(field=field):
                x=canonical();x[field]=value
                self.assertIn(label,self._assess(x))

    def test_inherited_writable_descriptors_or_maps_fail_closed(self):
        for field in ("inherited_writable_source_fds",
                      "inherited_writable_source_maps"):
            for value in (1,True):
                with self.subTest(field=field,value=value):
                    x=canonical();x["consumer"][field]=value
                    b=self._assess(x)
                    self.assertIn(
                        "INHERITED_ORIGINAL_WRITE_CAPABILITY_EXISTS",b)

    def test_privileged_or_late_child_cannot_pass_design_check(self):
        for key,value,label in (
            ("uid_isolated",False,"CONSUMER_PRIVILEGE_ISOLATION_UNVERIFIED"),
            ("no_new_privs",False,"CONSUMER_PRIVILEGE_ISOLATION_UNVERIFIED"),
            ("can_sudo",True,"CONSUMER_PRIVILEGE_ISOLATION_UNVERIFIED"),
            ("ambient_caps",1,"CONSUMER_PRIVILEGE_ISOLATION_UNVERIFIED"),
            ("policy_before_first_access",False,
             "ORIGINAL_ACCESS_PRECEDES_POLICY"),
        ):
            with self.subTest(key=key):
                x=canonical();x["consumer"][key]=value
                self.assertIn(label,self._assess(x))

    def test_standard_descriptor_redirection_must_be_safe(self):
        for key in ("fd0","fd1","fd2"):
            x=canonical();x["consumer"][key]="protected_original"
            self.assertIn("STANDARD_DESCRIPTOR_TARGETS_NOT_SAFE",
                          self._assess(x))

    def test_real_source_scope_extra_fields_and_custom_object_fail_closed(self):
        for field,value,label in (
            ("scope","protected_real",
             "UNAUTHORIZED_REAL_SOURCE_SCOPE"),
            ("unknown",True,"MISSING_OR_EXTRA_LAYOUT_FIELDS"),
        ):
            x=canonical();x[field]=value
            self.assertIn(label,self._assess(x))
        class Hostile(dict):
            def get(self,key,default=None):
                raise AssertionError("caller mapping get executed")
        self.assertIn("UNTRUSTED_LAYOUT_INPUT",
                      self._assess(Hostile(canonical())))

    def test_input_remains_unmodified(self):
        x=canonical();before=copy.deepcopy(x)
        self._assess(x,consistent=True)
        self.assertEqual(x,before)

    def test_custom_stage_tuple_member_cannot_execute_equality(self):
        class Explosive:
            def __eq__(self,other):
                raise AssertionError("stage member equality executed")
        x=canonical()
        x["stages"]=("trusted_staging",Explosive(),"trusted_uploader")
        b=self._assess(x)
        self.assertIn("STAGING_CONSUMER_UPLOADER_ORDER_NOT_PINNED",b)

    def test_custom_mount_scope_and_publication_values_do_not_run_equality(self):
        class Explosive:
            def __eq__(self,other):
                raise AssertionError("symbolic field equality executed")
        fields=(
            ("original_source_mode","SYNTHETIC_ORIGINAL_NOT_READONLY"),
            ("scratch_mode","SCRATCH_NOT_INDEPENDENT_OF_ORIGINAL"),
            ("publication","REPORT_PUBLICATION_NOT_EXTERNAL"),
            ("scope","UNAUTHORIZED_REAL_SOURCE_SCOPE"),
        )
        for field,reason in fields:
            with self.subTest(field=field):
                x=canonical();x[field]=Explosive()
                self.assertIn(reason,self._assess(x))

    def test_custom_standard_fd_targets_do_not_run_equality(self):
        class Explosive:
            def __eq__(self,other):
                raise AssertionError("descriptor target equality executed")
        for fd in ("fd0","fd1","fd2"):
            with self.subTest(fd=fd):
                x=canonical();x["consumer"][fd]=Explosive()
                self.assertIn("STANDARD_DESCRIPTOR_TARGETS_NOT_SAFE",
                              self._assess(x))

    def test_hash_colliding_outer_nonstring_key_does_not_run_equality(self):
        class Colliding:
            def __hash__(self):
                return hash("scope")
            armed=False
            def __eq__(self,other):
                if self.armed:
                    raise AssertionError("untrusted outer key equality executed")
                return False
        x=canonical()
        key=Colliding()
        x[key]="generated_public_only"
        key.armed=True
        b=self._assess(x)
        self.assertIn("UNTRUSTED_LAYOUT_INPUT",b)

    def test_hash_colliding_nested_consumer_nonstring_key_is_rejected(self):
        class Colliding:
            def __hash__(self):
                return hash("fd0")
            armed=False
            def __eq__(self,other):
                if self.armed:
                    raise AssertionError("untrusted consumer key equality executed")
                return False
        x=canonical()
        key=Colliding()
        x["consumer"][key]="safe_input"
        key.armed=True
        b=self._assess(x)
        self.assertIn("UNTRUSTED_CONSUMER_SPEC",b)

    def test_untrusted_keys_cannot_claim_ideal_design(self):
        class ForeignKey:
            def __hash__(self):
                return 9
        for nested in (False,True):
            with self.subTest(nested=nested):
                x=canonical()
                if nested:
                    x["consumer"][ForeignKey()]=False
                    self.assertIn("UNTRUSTED_CONSUMER_SPEC",
                                  self._assess(x))
                else:
                    x[ForeignKey()]=False
                    self.assertIn("UNTRUSTED_LAYOUT_INPUT",
                                  self._assess(x))

    def test_all_plain_key_canonical_design_remains_non_authorizing(self):
        x=canonical()
        self.assertTrue(all(type(k) is str for k in x))
        self.assertTrue(all(type(k) is str for k in x["consumer"]))
        self.assertEqual(self._assess(x,consistent=True),())
