from __future__ import annotations

import inspect
from datetime import date, datetime, timezone
from pathlib import Path
import unittest

from fmp.shadow.cli import main
import fmp.shadow.review_compiler as review_compiler


UTC = timezone.utc
FIXED_NOW = datetime(2026, 9, 17, 20, 0, tzinfo=UTC)
CODE_COMMIT = "c" * 40


class Phase8ProviderClosureWiringTests(unittest.TestCase):
    def test_record_closure_is_source_free_and_uses_system_recorded_time(self) -> None:
        calls: list[dict[str, object]] = []
        rc = main(
            [
                "record-closure",
                "--campaign-dir",
                "campaign",
                "--london-date",
                "2026-09-18",
                "--documentation",
                "provider notice",
            ],
            environ={},
            utc_now=lambda: FIXED_NOW,
            code_commit_resolver=lambda: CODE_COMMIT,
            record_closure_command=lambda **kwargs: calls.append(dict(kwargs)),
        )
        self.assertEqual(rc, 0)
        self.assertEqual(
            calls,
            [
                {
                    "campaign_dir": Path("campaign"),
                    "code_commit": CODE_COMMIT,
                    "london_date": date(2026, 9, 18),
                    "documentation": "provider notice",
                    "recorded_at_utc": FIXED_NOW,
                }
            ],
        )

    def test_review_loads_persisted_closures_and_passes_them_to_denominator_aggregation(self) -> None:
        compile_source = inspect.getsource(review_compiler.compile_review_evidence)
        aggregate_source = inspect.getsource(review_compiler._compile_segments)
        self.assertIn("load_provider_closures", compile_source)
        self.assertIn("provider_closures=provider_closures", compile_source)
        self.assertIn("provider_closures=provider_closures", aggregate_source)
        self.assertNotIn("provider_closures=provider_closures", inspect.getsource(review_compiler._validate_segment))


if __name__ == "__main__":
    unittest.main()
