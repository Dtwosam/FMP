"""DEC-1736: source-only CI sanity check for recent Phase8A review tests.

Parses only local test sources. No protected workflow, research artifacts,
administrator evidence, API, annual dispatch or economic model execution.
"""
import ast
from pathlib import Path
import unittest


TESTS = Path(__file__).resolve().parent
NEW_MODULES = {
    "test_dec1732_phase8a_crossdocument_boundary_reconciliation.py": 13,
    "test_dec1733_phase8a_crossdocument_mutation_controls.py": 14,
    "test_dec1735_administrator_handoff_mutation_controls.py": 24,
}


def _methods(name):
    path = TESTS / name
    module = ast.parse(path.read_text(encoding="utf-8"),
                       filename=str(path))
    return [
        n.name
        for cls in module.body if isinstance(cls, ast.ClassDef)
        for n in cls.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.name.startswith("test_")
    ]


class Phase8ASourceOnlyReviewAstGuardTests(unittest.TestCase):
    def test_three_new_modules_have_fiftyone_unique_discoverable_methods(self):
        seen = set()
        count = 0
        for filename, expected_count in sorted(NEW_MODULES.items()):
            with self.subTest(module=filename):
                names = _methods(filename)
                self.assertEqual(len(names), expected_count)
                self.assertEqual(len(set(names)), expected_count)
                self.assertFalse(any(name in seen for name in names))
                seen.update(names)
                count += len(names)
        self.assertEqual(count, 51)
        self.assertEqual(len(seen), 51)

    def test_pristine_controls_and_source_gates_remain_discoverable(self):
        cross = _methods(
            "test_dec1732_phase8a_crossdocument_boundary_reconciliation.py")
        cross_negative = _methods(
            "test_dec1733_phase8a_crossdocument_mutation_controls.py")
        administrator = _methods(
            "test_dec1721_independent_admin_witness_handoff_contract.py")
        admin_negative = _methods(
            "test_dec1735_administrator_handoff_mutation_controls.py")
        self.assertIn("test_year_order_cannot_authorize_run_by_document_agreement",
                      cross)
        self.assertIn("test_pristine_documents_pass_thirteen_original_guards",
                      cross_negative)
        self.assertIn("test_no_executable_dispatch_examples_in_review_packet",
                      administrator)
        self.assertIn(
            "test_unmodified_human_handoff_passes_all_twelve_source_guards",
            admin_negative,
        )

    def test_phase8a_order_negative_uses_swap_not_missing_header(self):
        path = TESTS / (
            "test_dec1733_phase8a_crossdocument_mutation_controls.py")
        source = path.read_text(encoding="utf-8")
        self.assertIn(
            '.replace("### Phase 8A", "### DEC1734_TEMP", 1)',
            source)
        self.assertIn(
            '.replace("### Phase 8B", "### Phase 8A", 1)',
            source)
        self.assertIn(
            '.replace("### DEC1734_TEMP", "### Phase 8B", 1)',
            source)
        self.assertNotIn(
            '"### Phase 8C — Multi-pair, multi-strategy portfolio research"',
            source)
