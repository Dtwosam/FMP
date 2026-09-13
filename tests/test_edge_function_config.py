from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


class EdgeFunctionConfigTests(unittest.TestCase):
    def test_custom_github_oidc_functions_disable_platform_jwt_verification(self) -> None:
        config = tomllib.loads(
            Path("supabase/config.toml").read_text(encoding="utf-8")
        )
        functions = config.get("functions")
        self.assertIsInstance(functions, dict)

        for name in ("fmp-raw-ingest", "fmp-raw-audit", "fmp-raw-read"):
            with self.subTest(function=name):
                function = functions.get(name)
                self.assertIsInstance(function, dict)
                self.assertIs(
                    function.get("verify_jwt"),
                    False,
                    f"{name} must set verify_jwt=false because it validates GitHub OIDC in function code",
                )

    def test_raw_read_edge_function_has_no_storage_mutation_or_proxy_surface(self) -> None:
        source = Path("supabase/functions/fmp-raw-read/index.ts").read_text(
            encoding="utf-8"
        )
        self.assertIn(".download(", source)
        for forbidden in (
            ".upload(",
            ".update(",
            ".remove(",
            ".list(",
            ".createSignedUrl(",
            ".createSignedUrls(",
            ".move(",
            ".copy(",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
