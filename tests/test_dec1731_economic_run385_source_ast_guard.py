"""DEC-1731: AST test discovery guard for Phase8A gate and cost work.

Parses offline checked-in test sources without importing protected workflows,
broker modules, private annual artifacts or running the guarded test files.
"""
import ast
from pathlib import Path
import unittest


class Phase8ARun385AndEconomicRegressionSourceGuardTests(unittest.TestCase):
    def test_synthetic_gate_and_economic_modules_have_stable_test_inventory(self):
        root = Path(__file__).resolve().parent
        expected = {
            "test_dec1716_installed_annual_workflow_blocker_contract.py": 12,
            "test_dec1718_phase7_cost_fragility_baseline_audit.py": 10,
            "test_dec1721_independent_admin_witness_handoff_contract.py": 12,
            "test_dec1723_preinstall_skip_ast_safeguard.py": 8,
            "test_dec1725_preinstall_skip_synthetic_negative_controls.py": 10,
            "test_dec1726_sourceonly_segment_gate_ledger.py": 13,
            "test_dec1728_annual_readiness_ledger_strict_inventory.py": 8,
            "test_dec1729_phase8a_ledger_mutation_negative_controls.py": 35,
            "test_dec1730_phase7_cost_evidence_mutation_controls.py": 17,
        }
        names_across_files = set()
        total = 0
        for filename, count in sorted(expected.items()):
            path = root / filename
            parsed = ast.parse(path.read_text(encoding="utf-8"),
                               filename=str(path))
            methods = [
                node.name
                for cls in parsed.body if isinstance(cls, ast.ClassDef)
                for node in cls.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name.startswith("test_")
            ]
            self.assertEqual(len(methods), count, filename)
            self.assertEqual(len(set(methods)), count, filename)
            for method in methods:
                self.assertNotIn(method, names_across_files,
                                 filename + ":" + method)
                names_across_files.add(method)
            total += len(methods)
        self.assertEqual(total, 125)
        self.assertEqual(len(names_across_files), 125)
