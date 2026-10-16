"""DEC-1391 — offline schematic review receipt; NEVER an OS acceptance.

These synthetic dictionaries contain no real protected paths, source identifiers
or signatures. An in-process structural check cannot authenticate a custodian.
All possible outcomes have dispatch_authorized=False and status=BLOCKED.
"""
from __future__ import annotations

import copy
import unittest

REQUIRED = {
    "source": ("reviewed_commit", "original_object_identity", "alias_inventory"),
    "process": ("runner_uid", "effective_capabilities", "no_new_privs",
                "standard_fd_targets", "inherited_writable_fd_inventory"),
    "isolation": ("enforced_mount_policy_receipt", "child_lifecycle_proof",
                  "scratch_separation", "trusted_uploader_identity"),
    "witness": ("privileged_skips", "write_denial_evidence",
                "positive_publication_evidence", "failure_cleanup_evidence"),
    "review": ("independent_reviewer", "current_server_provenance"),
}


def synthetic_receipt() -> dict:
    return {
        "source": {
            "reviewed_commit": "SYNTHETIC_NOT_A_GIT_COMMIT",
            "original_object_identity": "SYNTHETIC_DEV_INODE",
            "alias_inventory": "SYNTHETIC_ALIASES",
        },
        "process": {
            "runner_uid": "SYNTHETIC_UID",
            "effective_capabilities": "SYNTHETIC_CAPS",
            "no_new_privs": "SYNTHETIC_NNP",
            "standard_fd_targets": "SYNTHETIC_FD_0_TO_2",
            "inherited_writable_fd_inventory": "SYNTHETIC_DESCRIPTOR_SET",
        },
        "isolation": {
            "enforced_mount_policy_receipt": "SYNTHETIC_MOUNT",
            "child_lifecycle_proof": "SYNTHETIC_CHILD_TREE",
            "scratch_separation": "SYNTHETIC_SCRATCH",
            "trusted_uploader_identity": "SYNTHETIC_UPLOADER",
        },
        "witness": {
            "privileged_skips": 0,
            "write_denial_evidence": "SYNTHETIC_DENIAL",
            "positive_publication_evidence": "SYNTHETIC_PUBLICATION",
            "failure_cleanup_evidence": "SYNTHETIC_CLEANUP",
        },
        "review": {
            "independent_reviewer": "SYNTHETIC_REVIEWER",
            "current_server_provenance": "SYNTHETIC_SERVER",
        },
    }


def receipt_review(value: object) -> dict:
    """Diagnostic completeness only. No input can make this authorize."""
    absent = []
    if type(value) is not dict:
        absent = ["INVALID_RECEIPT_TYPE"]
    else:
        for domain, fields in REQUIRED.items():
            data = value.get(domain)
            if type(data) is not dict:
                absent.append(domain + ":NOT_A_MAPPING")
                continue
            extra = set(data) - set(fields)
            if extra:
                absent.append(domain + ":EXTRA_FIELDS")
            for field in fields:
                item = data.get(field)
                if field == "privileged_skips":
                    if type(item) is not int or item != 0:
                        absent.append(domain + ":" + field)
                elif type(item) is not str or not item.strip():
                    absent.append(domain + ":" + field)
    return {
        "status": "BLOCKED",
        "dispatch_authorized": False,
        "real_os_attestation_verified": False,
        "independent_review_verified": False,
        "structure_diagnostics": tuple(sorted(absent)),
    }


class FakeReceiptStructureIsNotIndependentOriginalNoWrite(unittest.TestCase):
    def setUp(self):
        self.receipt = synthetic_receipt()

    def test_even_structurally_filled_synthetic_receipt_remains_blocked(self):
        report = receipt_review(self.receipt)
        self.assertEqual(report["structure_diagnostics"], ())
        self.assertEqual(report["status"], "BLOCKED")
        self.assertIs(report["dispatch_authorized"], False)

    def test_non_mapping_receipt_remains_blocked(self):
        report = receipt_review([])
        self.assertIn("INVALID_RECEIPT_TYPE",
                      report["structure_diagnostics"])

    def test_missing_source_object_identity_is_diagnosed(self):
        del self.receipt["source"]["original_object_identity"]
        self.assertIn("source:original_object_identity",
                      receipt_review(self.receipt)["structure_diagnostics"])

    def test_absent_alias_inventory_is_diagnosed(self):
        self.receipt["source"]["alias_inventory"] = ""
        self.assertIn("source:alias_inventory",
                      receipt_review(self.receipt)["structure_diagnostics"])

    def test_runner_capabilities_and_standard_fd_inventory_required(self):
        del self.receipt["process"]["effective_capabilities"]
        del self.receipt["process"]["standard_fd_targets"]
        diagnostic = receipt_review(self.receipt)["structure_diagnostics"]
        self.assertIn("process:effective_capabilities", diagnostic)
        self.assertIn("process:standard_fd_targets", diagnostic)

    def test_missing_os_mount_and_child_proofs_are_diagnosed(self):
        self.receipt["isolation"]["enforced_mount_policy_receipt"] = None
        del self.receipt["isolation"]["child_lifecycle_proof"]
        diagnostic = receipt_review(self.receipt)["structure_diagnostics"]
        self.assertIn("isolation:enforced_mount_policy_receipt", diagnostic)
        self.assertIn("isolation:child_lifecycle_proof", diagnostic)

    def test_skip_count_cannot_be_positive_or_boolean(self):
        for item in (True, 1, -1, "0"):
            with self.subTest(item=item):
                value = copy.deepcopy(self.receipt)
                value["witness"]["privileged_skips"] = item
                self.assertIn("witness:privileged_skips",
                              receipt_review(value)["structure_diagnostics"])

    def test_no_denial_witness_is_diagnosed(self):
        del self.receipt["witness"]["write_denial_evidence"]
        self.assertIn("witness:write_denial_evidence",
                      receipt_review(self.receipt)["structure_diagnostics"])

    def test_successful_publication_and_cleanup_fields_are_both_required(self):
        self.receipt["witness"]["positive_publication_evidence"] = ""
        del self.receipt["witness"]["failure_cleanup_evidence"]
        diagnostic = receipt_review(self.receipt)["structure_diagnostics"]
        self.assertIn("witness:positive_publication_evidence", diagnostic)
        self.assertIn("witness:failure_cleanup_evidence", diagnostic)

    def test_unverified_reviewer_identity_does_not_make_status_pass(self):
        self.receipt["review"]["independent_reviewer"] = "FAKE_SIGNER"
        report = receipt_review(self.receipt)
        self.assertIs(report["independent_review_verified"], False)
        self.assertEqual(report["status"], "BLOCKED")

    def test_unknown_evidence_fields_require_fresh_source_review(self):
        self.receipt["review"]["unknown_authorized"] = True
        self.assertIn("review:EXTRA_FIELDS",
                      receipt_review(self.receipt)["structure_diagnostics"])

    def test_fake_claimed_success_field_cannot_override_blocked(self):
        self.receipt["status"] = "PASS"
        self.receipt["dispatch_authorized"] = True
        report = receipt_review(self.receipt)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertIs(report["dispatch_authorized"], False)
