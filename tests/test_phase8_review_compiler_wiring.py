from __future__ import annotations

import inspect
import unittest

from fmp.shadow import gates


class Phase8ReviewCompilerWiringTests(unittest.TestCase):
    def test_review_campaign_derives_evidence_before_loading_it(self) -> None:
        source = inspect.getsource(gates.review_campaign)
        self.assertIn("compile_review_evidence", source)
        self.assertLess(
            source.index("compile_review_evidence(campaign_dir)"),
            source.index("load_review_evidence"),
        )


if __name__ == "__main__":
    unittest.main()
