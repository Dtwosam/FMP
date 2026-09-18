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
            "FMPPhase8QuoteBridge.mq5",
            "Open Data Folder",
            "MQL5/Experts",
            "MetaEditor",
            "USDJPY",
            "AutoTrading OFF",
            "FPMarketsSC-Demo",
            "FPMarketsSC-Demo2",
            "FILE_COMMON",
            "FMP/phase8-usdjpy-feed.jsonl",
        ):
            self.assertIn(required, text)

        lowered = text.lower()
        self.assertIn("do not share", lowered)
        self.assertIn("password", lowered)
        self.assertIn("no demo or live orders", lowered)
        self.assertIn("read-only", lowered)
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
        self.assertIn(
            "python scripts/phase8_shadow.py qualify --out evidence/phase8/qualification",
            text,
        )
        self.assertIn("python scripts/phase8_shadow.py build-reference \", text)
        self.assertIn("--dataset-root <accepted-phase2-dataset-root> \", text)
        self.assertIn(
            "--processed-manifest <accepted-usdjpy-processed-manifest> \",
            text,
        )
        self.assertIn("--out evidence/phase8/reference", text)
        self.assertIn(
            "python scripts/phase8_shadow.py register \",
            text,
        )
        self.assertIn("--reference evidence/phase8/reference \", text)
        self.assertIn("--campaign-dir evidence/phase8/campaign", text)
        self.assertIn(
            "python scripts/phase8_shadow.py run --campaign-dir evidence/phase8/campaign",
            text,
        )
        self.assertIn(
            "python scripts/phase8_shadow.py replay --segment-dir evidence/phase8/campaign/<segment>",
            text,
        )
        self.assertIn(
            "python scripts/phase8_shadow.py review --campaign-dir evidence/phase8/campaign",
            text,
        )

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
        self.assertIn("no backfill", lowered)
        self.assertIn("phase 9", lowered)
        self.assertIn("design", lowered)
        self.assertIn("does not authorize", lowered)


if __name__ == "__main__":
    unittest.main()
