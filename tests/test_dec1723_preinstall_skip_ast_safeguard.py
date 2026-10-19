"""DEC-1723: source-level no-bypass guard on the DEC-1722 CI mode exclusion.

Always runs in both the historical preinstall snapshot and full checkout:
parse source as AST without importing a missing installed workflow.
"""
import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "test_dec1716_installed_annual_workflow_blocker_contract.py"
EXPECTED_SHA = "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
CLASS = "InstalledAnnualWorkflowBlockerContractTests"


class SourceBoundPreinstallSkipAstSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = TARGET.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source, filename=str(TARGET))
        matches = [n for n in cls.tree.body
                   if isinstance(n, ast.ClassDef) and n.name == CLASS]
        if len(matches) != 1:
            raise AssertionError("DEC-1716 class missing or duplicated")
        cls.target = matches[0]

    def test_focused_installed_source_suite_keeps_twelve_methods(self):
        names = [n.name for n in self.target.body
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and n.name.startswith("test_")]
        self.assertEqual(len(names), 12)
        self.assertEqual(len(set(names)), 12)

    def test_exactly_one_class_skip_decorator(self):
        self.assertEqual(len(self.target.decorator_list), 1)
        decorator = self.target.decorator_list[0]
        self.assertIsInstance(decorator, ast.Call)
        self.assertEqual(ast.unparse(decorator.func), "unittest.skipIf")

    def test_skip_predicate_only_matches_documented_preinstall_env(self):
        decorator = self.target.decorator_list[0]
        self.assertEqual(len(decorator.args), 2)
        self.assertEqual(
            ast.unparse(decorator.args[0]),
            "os.environ.get('FMP_PREINSTALL_SNAPSHOT') == '1'",
        )

    def test_skip_does_not_match_missing_file_or_generic_ci(self):
        predicate = ast.unparse(self.target.decorator_list[0].args[0])
        for forbidden in ("is_file", "exists", "CI", "GITHUB_ACTIONS",
                          "FileNotFoundError", "try:"):
            self.assertNotIn(forbidden, predicate)

    def test_unexpected_workflow_absence_still_raises(self):
        self.assertIn("return WORKFLOW.read_text(encoding=\"utf-8\")",
                      self.source)
        self.assertNotIn("except FileNotFoundError", self.source)
        self.assertNotIn("except OSError", self.source)

    def test_installed_workflow_blob_identity_remains_exact(self):
        self.assertIn('PINNED_GIT_BLOB = "' + EXPECTED_SHA + '"',
                      self.source)

    def test_authorization_order_assertions_are_not_removed(self):
        names = {n.name for n in self.target.body
                 if isinstance(n, ast.FunctionDef)}
        for name in (
            "test_checkout_is_first_step_in_every_job",
            "test_main_ref_shell_guard_is_post_checkout_in_every_job",
            "test_jobs_lack_precheckout_job_level_admission_condition",
            "test_setup_and_install_precede_runtime_authorization_in_all_jobs",
            "test_preflight_metadata_fetch_is_before_execution_authorization",
            "test_exact_18_cell_matrix_inventory",
        ):
            self.assertIn(name, names)

    def test_source_guard_requires_no_privileged_or_network_calls(self):
        for forbidden in ("subprocess.", "requests.", "urllib.request",
                          "gh workflow run ", "gh api --method POST",
                          "trading_authorized = True"):
            self.assertNotIn(forbidden, self.source)
