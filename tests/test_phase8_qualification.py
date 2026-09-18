from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import unittest

import fmp.shadow.qualification as qualification_module
from fmp.shadow.qualification import (
    QualificationOutcome,
    QualificationResult,
    mt5_boundary_audit,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 18, 10, 0, tzinfo=UTC)
SESSION = "a" * 64
FINGERPRINT = "b" * 64
SERVER = "FPMarketsSC-Demo2"


class Phase8QualificationSurfaceTests(unittest.TestCase):
    def test_boundary_audit_is_exact_fixed_mt5_demo_surface(self) -> None:
        self.assertEqual(
            mt5_boundary_audit(),
            {
                "connector_protocol": "fmp-mt5-demo-file-bridge-v1",
                "provider": "FP_MARKETS_MT5_DEMO",
                "transport": "MT5_FILE_COMMON_JSONL",
                "bridge_file": "FMP/phase8-usdjpy-feed.jsonl",
                "instrument": "USDJPY",
                "allowed_servers": ["FPMarketsSC-Demo", "FPMarketsSC-Demo2"],
            },
        )

    def test_active_qualification_exports_only_mt5_bridge_entry_point(self) -> None:
        self.assertIn("qualify_bridge", qualification_module.__all__)
        self.assertIn("mt5_boundary_audit", qualification_module.__all__)
        for forbidden in ("qualify_stream", "practice_boundary_audit", "PricingLineStream"):
            self.assertNotIn(forbidden, qualification_module.__all__)
            self.assertFalse(hasattr(qualification_module, forbidden))

    def test_qualification_module_has_no_oanda_strategy_or_risk_imports(self) -> None:
        source = Path("src/fmp/shadow/qualification.py").read_text(encoding="utf-8")
        for forbidden in (
            ".oanda",
            "OandaPractice",
            "practice_boundary_audit",
            "qualify_stream",
            "fmp.strategies",
            "fmp.research.adapter",
            "fmp.risk",
            ".bars",
            ".simulation",
            ".strategy",
        ):
            self.assertNotIn(forbidden, source)

    def test_result_persists_only_fingerprint_and_bridge_identity(self) -> None:
        result = QualificationResult(
            outcome=QualificationOutcome.PASS,
            account_fingerprint=FINGERPRINT,
            started_at_utc=NOW,
            ended_at_utc=NOW,
            elapsed_seconds=0.0,
            price_count=100,
            heartbeat_count=6,
            max_liveness_gap_seconds=5.0,
            boundary_audit=mt5_boundary_audit(),
            rejection_codes=(),
            bridge_session_id=SESSION,
            server=SERVER,
            max_bridge_liveness_gap_seconds=5.0,
            max_market_liveness_gap_seconds=5.0,
        )
        record = result.to_record()
        self.assertEqual(record["account_fingerprint"], FINGERPRINT)
        self.assertEqual(record["bridge_session_id"], SESSION)
        self.assertEqual(record["server"], SERVER)
        self.assertNotIn("account_id", record)
        self.assertNotIn("token", record)
        self.assertFalse(hasattr(result, "account_id"))
        self.assertFalse(hasattr(result, "token"))


if __name__ == "__main__":
    unittest.main()
