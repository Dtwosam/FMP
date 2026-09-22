from dataclasses import FrozenInstanceError
import unittest

from fmp.portfolio import (
    PHASE8A_EXPERIMENT_ID,
    ChampionSet,
    StrategyLifecycle,
    StrategyRecord,
    StrategyVersion,
    freeze_shadow_champion_set,
    transition_strategy,
)


COMMIT = "a" * 40


def _version(
    *,
    family: str = "session_breakout",
    version: str = "v1",
    symbol: str = "EURUSD",
    timeframe: str = "15m",
    parameters: dict[str, object] | None = None,
) -> StrategyVersion:
    return StrategyVersion.create(
        family=family,
        version=version,
        symbol=symbol,
        timeframe=timeframe,
        parameters=parameters or {"buffer_pips": 5, "target_range_multiple": 1.5},
        signal_contract_version="signal-v1",
        code_commit=COMMIT,
    )


class Phase8APortfolioRegistryTests(unittest.TestCase):
    def test_phase8a_identity_and_lifecycle_values_are_exact(self) -> None:
        self.assertEqual(PHASE8A_EXPERIMENT_ID, "EXP-20260922-012")
        self.assertEqual(
            tuple(item.value for item in StrategyLifecycle),
            (
                "DISCOVERY",
                "CHALLENGER",
                "HISTORICAL_QUALIFIED",
                "SHADOW_CANDIDATE",
                "SHADOW_VALIDATED",
                "DEMO_ELIGIBLE",
                "RETIRED",
            ),
        )

    def test_strategy_version_is_frozen_canonical_and_order_independent(self) -> None:
        left = StrategyVersion.create(
            family="session_breakout",
            version="v1",
            symbol="EURUSD",
            timeframe="15m",
            parameters={"target_range_multiple": 1.5, "buffer_pips": 5},
            signal_contract_version="signal-v1",
            code_commit=COMMIT,
        )
        right = StrategyVersion.create(
            family="session_breakout",
            version="v1",
            symbol="EURUSD",
            timeframe="15m",
            parameters={"buffer_pips": 5, "target_range_multiple": 1.5},
            signal_contract_version="signal-v1",
            code_commit=COMMIT,
        )

        self.assertEqual(left.parameters_json, '{"buffer_pips":5,"target_range_multiple":1.5}')
        self.assertEqual(left.fingerprint, right.fingerprint)
        with self.assertRaises(FrozenInstanceError):
            left.symbol = "GBPUSD"  # type: ignore[misc]

    def test_strategy_version_rejects_invalid_scope_or_identity(self) -> None:
        with self.assertRaises(ValueError):
            _version(symbol="AUDUSD")
        with self.assertRaises(ValueError):
            _version(timeframe="4h")
        with self.assertRaises(ValueError):
            StrategyVersion.create(
                family="session_breakout",
                version="v1",
                symbol="EURUSD",
                timeframe="15m",
                parameters={"bad": float("nan")},
                signal_contract_version="signal-v1",
                code_commit=COMMIT,
            )
        with self.assertRaises(ValueError):
            StrategyVersion.create(
                family="session_breakout",
                version="v1",
                symbol="EURUSD",
                timeframe="15m",
                parameters={"buffer_pips": 5},
                signal_contract_version="signal-v1",
                code_commit="not-a-commit",
            )

    def test_lifecycle_requires_ordered_evidence_backed_transitions(self) -> None:
        record = StrategyRecord(
            strategy=_version(),
            lifecycle=StrategyLifecycle.DISCOVERY,
            evidence_id="EXP-012-DISCOVERY-1",
        )
        challenger = transition_strategy(
            record,
            StrategyLifecycle.CHALLENGER,
            evidence_id="EXP-012-CHALLENGER-1",
        )
        self.assertEqual(challenger.lifecycle, StrategyLifecycle.CHALLENGER)
        self.assertEqual(challenger.strategy.fingerprint, record.strategy.fingerprint)

        with self.assertRaises(ValueError):
            transition_strategy(
                record,
                StrategyLifecycle.HISTORICAL_QUALIFIED,
                evidence_id="skip",
            )
        with self.assertRaises(ValueError):
            transition_strategy(
                challenger,
                StrategyLifecycle.DISCOVERY,
                evidence_id="reverse",
            )

        retired = transition_strategy(
            challenger,
            StrategyLifecycle.RETIRED,
            evidence_id="retired",
        )
        with self.assertRaises(ValueError):
            transition_strategy(
                retired,
                StrategyLifecycle.CHALLENGER,
                evidence_id="resurrect",
            )

    def test_shadow_champion_set_accepts_only_shadow_eligible_records_and_is_deterministic(self) -> None:
        a = StrategyRecord(
            strategy=_version(symbol="USDJPY"),
            lifecycle=StrategyLifecycle.SHADOW_CANDIDATE,
            evidence_id="A",
        )
        b = StrategyRecord(
            strategy=_version(
                family="volatility_breakout",
                version="v2",
                symbol="GBPUSD",
                timeframe="1h",
                parameters={"range_multiplier": 2.0, "target_r": 1.0},
            ),
            lifecycle=StrategyLifecycle.SHADOW_VALIDATED,
            evidence_id="B",
        )
        first = freeze_shadow_champion_set([a, b], champion_set_id="champions-1")
        second = freeze_shadow_champion_set([b, a], champion_set_id="champions-1")

        self.assertIsInstance(first, ChampionSet)
        self.assertEqual(first.fingerprint, second.fingerprint)
        self.assertEqual(
            tuple(item.fingerprint for item in first.strategies),
            tuple(sorted(item.fingerprint for item in first.strategies)),
        )
        with self.assertRaises(FrozenInstanceError):
            first.champion_set_id = "changed"  # type: ignore[misc]

        challenger = StrategyRecord(
            strategy=_version(symbol="EURUSD"),
            lifecycle=StrategyLifecycle.CHALLENGER,
            evidence_id="C",
        )
        with self.assertRaises(ValueError):
            freeze_shadow_champion_set([challenger], champion_set_id="bad")

        with self.assertRaises(ValueError):
            freeze_shadow_champion_set([a, a], champion_set_id="duplicate")


if __name__ == "__main__":
    unittest.main()
