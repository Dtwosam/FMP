from __future__ import annotations

import unittest
from pathlib import Path


class EdgeDependencyPinTests(unittest.TestCase):
    def test_edge_runtime_dependencies_are_exactly_pinned(self) -> None:
        expected = {
            'import { createClient } from "npm:@supabase/supabase-js@2.116.0";',
            'import { createRemoteJWKSet, jwtVerify } from "npm:jose@5.10.0";',
        }
        for path in (
            Path("supabase/functions/fmp-raw-ingest/index.ts"),
            Path("supabase/functions/fmp-raw-audit/index.ts"),
        ):
            with self.subTest(path=path.as_posix()):
                source = path.read_text(encoding="utf-8")
                for line in expected:
                    self.assertIn(line, source)
                self.assertNotIn('npm:@supabase/supabase-js@2";', source)
                self.assertNotIn('npm:jose@5";', source)


if __name__ == "__main__":
    unittest.main()
