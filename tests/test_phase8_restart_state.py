from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fmp.shadow.contracts import ShadowOutcome
import fmp.shadow.runner as runner_module


UTC = timezone.utc
RESTART_AT = datetime(2026, 9, 16, 14, 0, tzinfo=UTC)


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n" for item in records),
        encoding="utf-8",
    )


def _trade_record(*, decision_id: str, net_pnl_usd: float, before: float, after: float) -> dict[str, object]:
    return {
        "trade_id": decision_id,
        "decision_id": decision_id,
        "symbol": "USDJPY",
        "direction": "LONG",
        "units": 1000,
        "entry_timestamp_utc": "2026-09-16T08:15:00Z",
        "exit_timestamp_utc": "2026-09-16T09:00:00Z",
        "entry_reference_price": 140.02,
        "exit_reference_price": 139.8,
        "entry_price": 140.022,
        "exit_price": 139.798,
        "stop_price": 139.5,
        "target_price": 140.5,
        "exit_reason": "STOP",
        "intrabar_ambiguous": False,
        "gross_pnl_usd": net_pnl_usd,
        "slippage_cost_usd": 0.0,
        "commission_cost_usd": 0.0,
        "financing_cost_usd": 0.0,
        "net_pnl_usd": net_pnl_usd,
        "risk_equity_before_usd": before,
        "risk_equity_after_usd": after,
    }


def _position_record(*, decision_id: str, reserved_risk_usd: float) -> dict[str, object]:
    return {
        "position": {
            "position_id": decision_id,
            "decision_id": decision_id,
            "symbol": "USDJPY",
            "direction": "LONG",
            "units": 1000,
            "entry_timestamp_utc": "2026-09-16T10:00:00Z",
            "entry_reference_price": 140.02,
            "entry_price": 140.022,
            "entry_commission_usd": 0.0,
            "stop_price": 139.5,
            "target_price": 140.5,
            "reserved_risk_usd": reserved_risk_usd,
        },
        "scheduled_exit": {
            "decision_id": decision_id,
            "symbol": "USDJPY",
            "timestamp_utc": "2026-09-16T15:00:00Z",
        },
        "slippage_pips": 0.2,
    }


class _EvidenceSpy:
    code_commit = "a" * 40
    account_fingerprint_sha256 = "b" * 64

    def __init__(self) -> None:
        self.scenarios: list[dict[str, object]] = []
        self.decisions: list[dict[str, object]] = []
        self.operational: list[dict[str, object]] = []

    def append_raw(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return None

    def append_normalized(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return None

    def append_bar(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return None

    def append_decision(self, record):  # type: ignore[no-untyped-def]
        self.decisions.append(dict(record))

    def append_scenario(self, record):  # type: ignore[no-untyped-def]
        self.scenarios.append(dict(record))

    def append_operational(self, record):  # type: ignore[no-untyped-def]
        self.operational.append(dict(record))


class Phase8RestartStateTests(unittest.TestCase):
    def test_restore_carries_forward_each_scenario_equity_and_daily_halt(self) -> None:
        self.assertTrue(
            hasattr(runner_module, "restore_shadow_simulator"),
            "Phase 8 must reconstruct virtual account state from durable campaign evidence",
        )
        with TemporaryDirectory() as tmp:
            campaign = Path(tmp)
            segment = campaign / "segment-20260916T080000.000000Z"
            _write_jsonl(
                segment / "scenarios.jsonl",
                [
                    {
                        "event": "trade_completed",
                        "slippage_pips": 0.2,
                        "decision_id": "d-02",
                        "trade": _trade_record(
                            decision_id="d-02",
                            net_pnl_usd=-1600.0,
                            before=100000.0,
                            after=98400.0,
                        ),
                    },
                    {
                        "event": "trade_completed",
                        "slippage_pips": 0.5,
                        "decision_id": "d-05",
                        "trade": _trade_record(
                            decision_id="d-05",
                            net_pnl_usd=500.0,
                            before=100000.0,
                            after=100500.0,
                        ),
                    },
                    {
                        "event": "trade_completed",
                        "slippage_pips": 1.0,
                        "decision_id": "d-10",
                        "trade": _trade_record(
                            decision_id="d-10",
                            net_pnl_usd=-250.0,
                            before=100000.0,
                            after=99750.0,
                        ),
                    },
                ],
            )

            simulator = runner_module.restore_shadow_simulator(campaign)
            self.assertEqual(simulator.states[0.2].risk_state.risk_equity_usd, 98400.0)
            self.assertEqual(simulator.states[0.5].risk_state.risk_equity_usd, 100500.0)
            self.assertEqual(simulator.states[1.0].risk_state.risk_equity_usd, 99750.0)
            self.assertTrue(simulator.states[0.2].risk_state.daily_halt_active)
            self.assertFalse(simulator.states[0.5].risk_state.daily_halt_active)
            self.assertFalse(simulator.states[1.0].risk_state.daily_halt_active)
            for state in simulator.states.values():
                self.assertEqual(state.completed_trades, [])

    def test_unresolved_open_positions_restore_then_become_unknown_on_restart(self) -> None:
        self.assertTrue(hasattr(runner_module, "restore_shadow_simulator"))
        with TemporaryDirectory() as tmp:
            campaign = Path(tmp)
            segment = campaign / "segment-20260916T095500.000000Z"
            records: list[dict[str, object]] = []
            for scenario in (0.2, 0.5, 1.0):
                decision_id = f"open-{scenario}"
                position = _position_record(decision_id=decision_id, reserved_risk_usd=250.0)
                position["slippage_pips"] = scenario
                records.append(
                    {
                        "event": "position_opened",
                        "slippage_pips": scenario,
                        "decision_id": decision_id,
                        "position": position,
                    }
                )
            _write_jsonl(segment / "scenarios.jsonl", records)

            simulator = runner_module.restore_shadow_simulator(campaign)
            for scenario, state in simulator.states.items():
                self.assertEqual(len(state.open_positions), 1)
                self.assertEqual(state.risk_state.total_reserved_risk_usd, 250.0)

            evidence = _EvidenceSpy()
            runner = runner_module.ShadowRunner(evidence=evidence, simulator=simulator)
            runner.start(now_utc=RESTART_AT, restarted=True)

            for state in simulator.states.values():
                self.assertEqual(state.open_positions, {})
                self.assertEqual(state.risk_state.total_reserved_risk_usd, 0.0)
                self.assertEqual(set(state.outcomes.values()), {ShadowOutcome.OUTCOME_UNKNOWN_AFTER_GAP})
            outcomes = [item for item in evidence.scenarios if item.get("event") == "outcome"]
            self.assertEqual(len(outcomes), 3)


if __name__ == "__main__":
    unittest.main()
