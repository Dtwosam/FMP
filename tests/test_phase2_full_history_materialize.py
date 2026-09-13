from __future__ import annotations

import unittest

from fmp.data.phase2.full_history import materialize_pair


class FullHistoryMaterializationTests(unittest.TestCase):
    def test_materialize_pair_is_exposed(self) -> None:
        self.assertTrue(callable(materialize_pair))


if __name__ == "__main__":
    unittest.main()
