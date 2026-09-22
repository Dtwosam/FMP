from __future__ import annotations

from pathlib import Path
import unittest


HISTORICAL_PLAN = Path("docs/superpowers/plans/2026-09-15-phase8-live-shadow.md")
HANDOFF = Path("docs/phase8-mt5-operator-handoff.md")


class Phase8OperatorHandoffTests(unittest.TestCase):
    def test_historical_oanda_plan_is_clearly_superseded_for_operator_use(self) -> None:
        text = HISTORICAL_PLAN.read_text(encoding="utf-8")
        header = text[:1600]
        self.assertIn("SUPERSEDED FOR OPERATOR USE", header)
        self.assertIn("DEC-037", header)
        self.assertIn("docs/phase8-mt5-operator-handoff.md", header)

    def test_mac_handoff_pins_read_only_mt5_install_and_startup_checks(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        for required in (
            "FMPPhase8BQuoteBridge.mq5",
            "Open Data Folder",
            "MQL5/Experts",
            "MetaEditor",
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "AutoTrading OFF",
            "FPMarketsSC-Demo",
            "FPMarketsSC-Demo2",
            "FILE_COMMON",
            "FMP/phase8b-eurusd-feed.jsonl",
            "FMP/phase8b-gbpusd-feed.jsonl",
            "FMP/phase8b-usdjpy-feed.jsonl",
        ):
            self.assertIn(required, text)

        lowered = text.lower()
        self.assertIn("do not", lowered)
        self.assertIn("password", lowered)
        self.assertIn("read-only", lowered)
        self.assertIn("never places an order", lowered)
        self.assertIn("not a usdjpy-only campaign", lowered)
        for forbidden in (
            "OANDA_PRACTICE_ACCOUNT_ID",
            "OANDA_PRACTICE_TOKEN",
            "stream-fxpractice.oanda.com",
            "FPMarketsSC-Live",
            "FPMarketsSC-Live2",
        ):
            self.assertNotIn(forbidden, text)

    def test_handoff_commands_match_the_implemented_mt5_cli(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        for command in (
            "python scripts/phase8b_shadow.py design",
            "python scripts/phase8b_shadow.py qualify",
            "python scripts/phase8b_shadow.py register",
            "python scripts/phase8b_shadow.py authorize-start",
            "python scripts/phase8b_shadow.py freeze-spread-reference",
            "python scripts/phase8b_shadow.py readiness",
            "python scripts/phase8b_shadow.py capture-segment",
            "python scripts/phase8b_shadow.py close-campaign",
            "python scripts/phase8b_shadow.py review-campaign",
        ):
            self.assertIn(command, text)
        self.assertIn("--dataset-root <accepted-phase2-dataset-root>", text)
        self.assertIn("--duration-seconds <1-to-86400>", text)
        self.assertIn("--closure-id <closure-id>", text)
        self.assertNotIn("python scripts/phase8_shadow.py run", text)
        self.assertNotIn("python scripts/phase8_shadow.py replay", text)

    def test_handoff_pins_qualification_outcomes_and_no_backfill_rules(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        for outcome in (
            "PASS",
            "INCONCLUSIVE",
            "CONNECTOR_UNAVAILABLE",
            "CONNECTOR_REJECTED",
        ):
            self.assertIn(outcome, text)
        lowered = text.lower()
        self.assertIn("no-backfill", lowered)
        self.assertIn("quiet market", lowered)
        self.assertIn("15-second liveness", lowered)
        self.assertIn("5-second quote", lowered)
        self.assertIn("phase 9", lowered)
        self.assertIn("design", lowered)
        self.assertIn("does not authorize", lowered)


if __name__ == "__main__":
    unittest.main()
