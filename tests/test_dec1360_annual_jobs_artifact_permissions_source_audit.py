from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github"/"workflows"/"phase8a-annual-pattern-catalogue.yml"


class AnnualJobDependenciesDoNotProveIndependentSecurityGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=WORKFLOW.read_text(encoding="utf-8")
        cls.jobs={}
        names=list(re.finditer(
            r"^  (annual_preflight|annual_cell|annual_freeze):\s*$",
            cls.source,re.MULTILINE))
        for i,m in enumerate(names):
            end=names[i+1].start() if i+1<len(names) else len(cls.source)
            cls.jobs[m.group(1)]=cls.source[m.start():end]

    def test_exact_three_job_chain_is_ordered_but_not_preallocation_gate(self):
        self.assertEqual(set(self.jobs),
                         {"annual_preflight","annual_cell","annual_freeze"})
        self.assertIn("needs: annual_preflight",self.jobs["annual_cell"])
        self.assertIn("needs: annual_cell",self.jobs["annual_freeze"])
        for job,source in self.jobs.items():
            with self.subTest(job=job):
                self.assertIn("- name: Checkout",source)
                self.assertIn("test \"$GITHUB_REF\" = \"refs/heads/main\"",source)

    def test_cell_matrix_is_eighteen_with_three_way_parallelism(self):
        src=self.jobs["annual_cell"]
        self.assertIn("max-parallel: 3",src)
        self.assertEqual(
            len(re.findall(r"^          - symbol:\s*",
                           src,re.MULTILINE)),18)
        self.assertIn("fail-fast: false",src)

    def test_each_job_uploads_from_its_own_checkout_workspace(self):
        expected={
            "annual_preflight":"path: .preflight",
            "annual_cell":"path: .result",
            "annual_freeze":"path: .annual-freeze/annual-freeze.json",
        }
        for job,relative_path in expected.items():
            with self.subTest(job=job):
                self.assertIn("uses: actions/upload-artifact@v6",
                              self.jobs[job])
                self.assertIn(relative_path,self.jobs[job])

    def test_read_only_github_token_does_not_set_checkout_read_only(self):
        self.assertIn("permissions:\n  contents: read\n  actions: read",
                      self.source)
        self.assertIn("uses: actions/checkout@v6",self.source)
        for job in self.jobs.values():
            self.assertIn("Install pinned annual catalogue runtime",job)
        self.assertIn("mkdir -p .preflight",self.jobs["annual_preflight"])
        self.assertIn("mkdir -p .result",self.jobs["annual_cell"])

    def test_every_job_is_still_subject_to_irreversible_manual_dispatch(self):
        self.assertIn("workflow_dispatch:",self.source)
        for job in self.jobs.values():
            self.assertIn("GITHUB_EVENT_NAME",job)
            self.assertIn("refs/heads/main",job)
            self.assertIn("authorized annual catalogue execution",job)
        self.assertNotIn("DEC-650/#820 VERIFIED",self.source)
        self.assertNotIn("DEC-651/#821/#779 VERIFIED",self.source)
