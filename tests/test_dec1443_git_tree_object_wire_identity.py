"""DEC-1443: reproduce Git tree wire object SHA from complete entries.

Synthetic / reviewed Git source metadata only. No protected annual workflow,
archive, server setting mutation, dispatch, merge, broker or trading.
"""
from __future__ import annotations
import hashlib
import re
import unittest

TYPES = {"040000": "tree", "100644": "blob", "100755": "blob",
         "120000": "blob", "160000": "commit"}
HEX = re.compile(r"[0-9a-f]{40}\Z")


def reviewed_git_tree_sha(entries):
    if type(entries) is not list:
        return None
    chunks, order, seen = [], [], set()
    for item in entries:
        if type(item) is not dict:
            return None
        name, mode, kind, sha = (
            item.get("path"), item.get("mode"),
            item.get("type"), item.get("sha"))
        if (type(name) is not str or name in ("", ".", "..") or
                "/" in name or "\\" in name or "\0" in name):
            return None
        if type(mode) is not str or mode not in TYPES or kind != TYPES[mode]:
            return None
        if type(sha) is not str or HEX.fullmatch(sha) is None:
            return None
        try:
            encoded = name.encode("utf-8", "strict")
        except UnicodeEncodeError:
            return None
        if encoded in seen:
            return None
        seen.add(encoded)
        order.append(encoded + (b"/" if mode == "040000" else b""))
        wire_mode = "40000" if mode == "040000" else mode
        chunks.append(wire_mode.encode("ascii") + b" " + encoded +
                      b"\0" + bytes.fromhex(sha))
    if order != sorted(order):
        return None
    body = b"".join(chunks)
    return hashlib.sha1(b"tree " + str(len(body)).encode("ascii") +
                        b"\0" + body).hexdigest()


class GitTreeWireIdentityIsNotAnAnnualSecurityGate(unittest.TestCase):
    def setUp(self):
        self.items = [
            {"path": "docs", "mode": "040000", "type": "tree", "sha": "a"*40},
            {"path": "unit.py", "mode": "100644", "type": "blob", "sha": "b"*40},
        ]

    def test_canonical_tree_has_git_object_sha(self):
        self.assertRegex(reviewed_git_tree_sha(self.items), r"^[0-9a-f]{40}$")

    def test_empty_tree_matches_known_git_object_id(self):
        self.assertEqual(reviewed_git_tree_sha([]),
                         "4b825dc642cb6eb9a060e54bf8d69288fbee4904")

    def test_changed_child_sha_changes_parent_tree_sha(self):
        sha = reviewed_git_tree_sha(self.items)
        self.items[1]["sha"] = "c"*40
        self.assertNotEqual(reviewed_git_tree_sha(self.items), sha)

    def test_swapped_git_entry_order_fails(self):
        self.items.reverse()
        self.assertIsNone(reviewed_git_tree_sha(self.items))

    def test_duplicate_path_entry_fails(self):
        self.items.append(dict(self.items[1]))
        self.assertIsNone(reviewed_git_tree_sha(self.items))

    def test_parent_tree_with_blob_type_fails(self):
        self.items[0]["type"] = "blob"
        self.assertIsNone(reviewed_git_tree_sha(self.items))

    def test_gitlink_requires_commit_type(self):
        self.items[1]["mode"] = "160000"
        self.assertIsNone(reviewed_git_tree_sha(self.items))
        self.items[1]["type"] = "commit"
        self.assertIsNotNone(reviewed_git_tree_sha(self.items))

    def test_invalid_path_component_fails(self):
        self.items[1]["path"] = "../live.py"
        self.assertIsNone(reviewed_git_tree_sha(self.items))

    def test_invalid_child_sha_fails(self):
        self.items[1]["sha"] = "z"*40
        self.assertIsNone(reviewed_git_tree_sha(self.items))

    def test_invalid_mode_shape_fails(self):
        self.items[1]["mode"] = []
        self.assertIsNone(reviewed_git_tree_sha(self.items))

    def test_known_real_1666_root_git_object_id(self):
        # Read-only GitHub root tree captured at draft #1666.
        items = [
            (".github","040000","tree","251f38dce2fda0c8b869fff6d0cd09a74546dfd0"),
            (".gitignore","100644","blob","e03c080d22b99e46a4f32d90ab06bcd838f224e3"),
            ("AGENTS.md","100644","blob","bc5a7b03f8c5ada7c36484ca26ae29b45c07efe9"),
            ("README.md","100644","blob","4180736f70a3278df214831aa2d8c34570d11581"),
            ("docs","040000","tree","ec0740a64250965cfd62cfead6cac4e8e0f68938"),
            ("mt5","040000","tree","bcbf6731c0d83fb1e77b9959f4fe0fbc846fadcb"),
            ("pyproject.toml","100644","blob","de850a1ba397fc69ba634ecf178d732b5012c378"),
            ("requirements","040000","tree","3b01732cd0ee1eaf3e7f84e7debe624db0598bb2"),
            ("scripts","040000","tree","f8fe7ebd74365038e8665102ad2bcfbe6a76d0f4"),
            ("src","040000","tree","2aae4de77b2c665f2a8ca9c3c31eda772f7b7597"),
            ("supabase","040000","tree","5bb5024241e052c3a94d53ab7793a823a807845d"),
            ("tests","040000","tree","8bf5555a3eb2ef2ad312090548802ff0c914898e"),
        ]
        full = [{"path": a, "mode": b, "type": c, "sha": d}
                for a, b, c, d in items]
        self.assertEqual(reviewed_git_tree_sha(full),
                         "985365a6a6503d1a4b786888877ba8ef42c207d3")

    def test_tree_identity_does_not_authorize_annual_dispatch(self):
        self.assertIsNotNone(reviewed_git_tree_sha(self.items))
        self.assertNotEqual(reviewed_git_tree_sha(self.items),
                            "ANNUAL_DISPATCH_AUTHORIZED")
