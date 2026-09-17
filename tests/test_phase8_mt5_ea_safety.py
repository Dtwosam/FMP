from pathlib import Path
import unittest


EA_PATH = Path("mt5/Experts/FMPPhase8QuoteBridge.mq5")


class Phase8Mt5EaSafetyTests(unittest.TestCase):
    def test_read_only_bridge_source_is_present_and_frozen(self) -> None:
        self.assertTrue(EA_PATH.is_file(), f"missing {EA_PATH}")
        source = EA_PATH.read_text(encoding="utf-8")

        required = (
            "fmp-mt5-demo-file-bridge-v1",
            "FMP\\phase8-usdjpy-feed.jsonl",
            "FPMarketsSC-Demo",
            "FPMarketsSC-Demo2",
            "ACCOUNT_TRADE_MODE",
            "ACCOUNT_TRADE_MODE_DEMO",
            "ACCOUNT_SERVER",
            "ACCOUNT_LOGIN",
            '"USDJPY"',
            "_Symbol",
            "FILE_COMMON",
            "FILE_SHARE_READ",
            "FILE_SHARE_WRITE",
            "FileFlush",
            "CRYPT_HASH_SHA256",
            "BRIDGE_START",
            "TICK",
            "BRIDGE_HEARTBEAT",
            "MqlTick",
            "time_msc",
            "SymbolInfoTick",
            "MathIsValidNumber",
            "OnTick",
            "OnTimer",
            "EventSetTimer",
            "EventKillTimer",
        )
        for needle in required:
            with self.subTest(required=needle):
                self.assertIn(needle, source)

    def test_bridge_source_contains_no_execution_surface_or_live_server(self) -> None:
        self.assertTrue(EA_PATH.is_file(), f"missing {EA_PATH}")
        source = EA_PATH.read_text(encoding="utf-8").casefold()

        forbidden = (
            "ordersend",
            "ordersendasync",
            "mqltraderequest",
            "mqltraderesult",
            "ctrade",
            "positionopen",
            "positionclose",
            "positionmodify",
            "trade.mqh",
            "fpmarketssc-live",
            '"account_login"',
            '"password"',
            '"token"',
            '"account_name"',
        )
        for needle in forbidden:
            with self.subTest(forbidden=needle):
                self.assertNotIn(needle, source)

    def test_bridge_has_no_external_inputs_or_generic_provider_surface(self) -> None:
        self.assertTrue(EA_PATH.is_file(), f"missing {EA_PATH}")
        source = EA_PATH.read_text(encoding="utf-8")
        self.assertNotIn("input ", source.casefold())
        self.assertNotIn("#import", source.casefold())
        self.assertNotIn("WebRequest", source)
        self.assertNotIn("Socket", source)


if __name__ == "__main__":
    unittest.main()
