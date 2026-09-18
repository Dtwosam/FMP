from __future__ import annotations

import ast
from pathlib import Path
import unittest


RUNTIME_ROOT = Path(__file__).resolve().parents[1] / "src" / "fmp" / "shadow"

_PRODUCTION_HOSTS = (
    "stream-fxtrade.oanda.com",
    "api-fxtrade.oanda.com",
    "api-fxpractice.oanda.com",
    "FPMarketsSC-Live",
    "FPMarketsSC-Live2",
)
_ACTIVE_RUNTIME_FILES = (
    "__init__.py",
    "cli.py",
    "qualification.py",
    "runner.py",
    "replay.py",
    "review_compiler.py",
)
_MUTATION_ENDPOINT_FRAGMENTS = (
    "/orders",
    "/trades",
    "/positions",
    "/transactions",
    "/accountConfiguration",
    "/configuration",
)
_GENERIC_TRANSPORT_PARAMETERS = {"base_url", "host", "method", "path", "url"}
_MUTATING_PUBLIC_NAME_PARTS = (
    "order_send",
    "send_order",
    "submit_order",
    "place_order",
    "create_order",
    "cancel_order",
    "replace_order",
    "close_trade",
    "close_position",
    "modify_trade",
    "modify_position",
)


def _runtime_trees() -> dict[Path, ast.Module]:
    trees: dict[Path, ast.Module] = {}
    for path in sorted(RUNTIME_ROOT.glob("*.py")):
        trees[path] = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    if not trees:
        raise AssertionError("Phase 8 runtime surface is missing")
    return trees


def _string_literals(tree: ast.AST) -> tuple[str, ...]:
    return tuple(
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    )


def _public_mutation_names(tree: ast.AST) -> tuple[str, ...]:
    flagged: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("_"):
            continue
        lowered = node.name.lower()
        if any(fragment in lowered for fragment in _MUTATING_PUBLIC_NAME_PARTS):
            flagged.append(node.name)
    return tuple(flagged)


class Phase8StructuralSafetyTests(unittest.TestCase):
    def test_runtime_contains_no_production_hosts_or_mutation_endpoint_literals(self) -> None:
        for path, tree in _runtime_trees().items():
            for literal in _string_literals(tree):
                for forbidden in (*_PRODUCTION_HOSTS, *_MUTATION_ENDPOINT_FRAGMENTS):
                    self.assertNotIn(forbidden, literal, msg=f"{path}: forbidden runtime literal")

    def test_runtime_imports_no_mt5_or_broker_execution_adapter(self) -> None:
        for path, tree in _runtime_trees().items():
            imported: list[str] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.append(node.module)
            for module in imported:
                lowered = module.lower()
                parts = lowered.replace("-", "_").split(".")
                self.assertNotIn("metatrader5", lowered, msg=str(path))
                self.assertNotIn("mt5", parts, msg=str(path))
                self.assertNotIn("broker", parts, msg=str(path))

    def test_active_runtime_is_mt5_only_and_oanda_is_historical(self) -> None:
        active_source = "\n".join(
            (RUNTIME_ROOT / name).read_text(encoding="utf-8")
            for name in _ACTIVE_RUNTIME_FILES
        )
        for forbidden in (
            "from .oanda",
            "import .oanda",
            "OandaPractice",
            "practice_boundary_audit",
            "qualify_stream",
            "process_provider_message",
            "process_line(",
            "PRACTICE_STREAM_HOST",
            "PRACTICE_STREAM_PATH_TEMPLATE",
            "PROVIDER_INSTRUMENT",
            "OANDA_PRACTICE_ACCOUNT_ID",
            "OANDA_PRACTICE_TOKEN",
        ):
            self.assertNotIn(forbidden, active_source)

        self.assertIn("mt5_bridge", active_source)
        self.assertIn("qualify_bridge", active_source)
        self.assertIn("process_bridge_record", active_source)

    def test_historical_oanda_module_is_not_reexported(self) -> None:
        package_source = (RUNTIME_ROOT / "__init__.py").read_text(encoding="utf-8")
        for forbidden in (
            "PRACTICE_STREAM_HOST",
            "PRACTICE_STREAM_PATH_TEMPLATE",
            "PROVIDER_INSTRUMENT",
            "OandaPracticePricingStream",
        ):
            self.assertNotIn(forbidden, package_source)

    def test_runtime_has_no_public_broker_mutation_method_names(self) -> None:
        for path, tree in _runtime_trees().items():
            self.assertEqual(_public_mutation_names(tree), (), msg=str(path))

    def test_guard_itself_detects_synthetic_forbidden_surfaces(self) -> None:
        bad_names = ast.parse(
            "class Bad:\n"
            "    def place_order(self):\n"
            "        return None\n"
        )
        self.assertEqual(_public_mutation_names(bad_names), ("place_order",))

        bad_literal = ast.parse('ENDPOINT = "https://api-fxtrade.oanda.com/v3/accounts/x/orders"\n')
        literals = _string_literals(bad_literal)
        self.assertTrue(any("api-fxtrade.oanda.com" in value for value in literals))
        self.assertTrue(any("/orders" in value for value in literals))


if __name__ == "__main__":
    unittest.main()
