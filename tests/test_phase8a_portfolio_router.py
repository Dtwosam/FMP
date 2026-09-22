from datetime import datetime, timezone
import unittest

from fmp.contracts import Direction
from fmp.portfolio import (
    CandidateRejectionCode,
    PortfolioCandidate,
    StrategyLifecycle,
    StrategyRecord,
    StrategyVersion,
    freeze_shadow_champion_set,
    route_shadow_candidates,
)


COMMIT = "b" * 40
NOW = datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc)


def _strategy(family: str, symbol: str, timeframe: str = "15m") -> StrategyVersion:
    return StrategyVersion.create(
        family=family,
        version="v1",
        symbol=symbol,
        timeframe=timeframe,
        parameters={"test": 1},
        signal_contract_version="signal-v1",
        code_commit=COMMIT,
    )


def _champions(*strategies: StrategyVersion):
    records = [
        StrategyRecord(
            strategy=item,
            lifecycle=StrategyLifecycle.SHADOW_CANDIDATE,
            evidence_id=f"evidence-{index}",
        )
        for index, item in enumerate(strategies)
    ]
    return freeze_shadow_champion_set(records, champion_set_id="champions")


def _candidate(
    candidate_id: str,
    strategy: StrategyVersion,
    direction: Direction,
    *,
    risk: float = 0.0025,
    applicable: bool = True,
) -> PortfolioCandidate:
    return PortfolioCandidate(
        candidate_id=candidate_id,
        strategy_fingerprint=strategy.fingerprint,
        symbol=strategy.symbol,
        direction=direction,
        observed_at_utc=NOW,
        requested_risk_fraction=risk,
        applicability_passed=applicable,
    )


class Phase8APortfolioRouterTests(unittest.TestCase):
    def test_nonchampion_and_not_applicable_candidates_are_rejected(self) -> None:
        eur = _strategy("session_breakout", "EURUSD")
        gbp = _strategy("trend_continuation", "GBPUSD")
        champions = _champions(eur)

        result = route_shadow_candidates(
            champions,
            [
                _candidate("eur", eur, Direction.LONG, applicable=False),
                _candidate("gbp", gbp, Direction.LONG),
            ],
        )

        self.assertEqual(result.accepted, ())
        self.assertEqual(
            {(item.candidate_id, item.code) for item in result.rejected},
            {
                ("eur", CandidateRejectionCode.NOT_APPLICABLE),
                ("gbp", CandidateRejectionCode.NOT_CHAMPION),
            },
        )

    def test_opposite_directions_on_same_symbol_fail_closed(self) -> None:
        a = _strategy("session_breakout", "EURUSD")
        b = _strategy("mean_reversion", "EURUSD", "5m")
        champions = _champions(a, b)

        result = route_shadow_candidates(
            champions,
            [
                _candidate("long", a, Direction.LONG),
                _candidate("short", b, Direction.SHORT),
            ],
        )

        self.assertEqual(result.accepted, ())
        self.assertEqual(
            [(item.candidate_id, item.code) for item in result.rejected],
            [
                ("long", CandidateRejectionCode.DIRECTION_CONFLICT),
                ("short", CandidateRejectionCode.DIRECTION_CONFLICT),
            ],
        )

    def test_multi_pair_candidates_are_deterministic_and_report_usd_risk_direction(self) -> None:
        eur = _strategy("session_breakout", "EURUSD")
        gbp = _strategy("trend_continuation", "GBPUSD")
        jpy = _strategy("volatility_breakout", "USDJPY", "1h")
        champions = _champions(eur, gbp, jpy)

        result = route_shadow_candidates(
            champions,
            [
                _candidate("jpy", jpy, Direction.LONG),
                _candidate("eur", eur, Direction.LONG),
                _candidate("gbp", gbp, Direction.SHORT),
            ],
        )

        self.assertEqual(tuple(item.candidate_id for item in result.accepted), ("eur", "gbp", "jpy"))
        self.assertEqual(result.rejected, ())
        self.assertAlmostEqual(result.exposure.total_requested_risk_fraction, 0.0075)
        self.assertAlmostEqual(result.exposure.usd_long_requested_risk_fraction, 0.0050)
        self.assertAlmostEqual(result.exposure.usd_short_requested_risk_fraction, 0.0025)
        self.assertAlmostEqual(result.exposure.gross_usd_directional_risk_fraction, 0.0075)
        self.assertAlmostEqual(result.exposure.net_usd_directional_risk_fraction, 0.0025)

    def test_candidate_validation_rejects_no_trade_and_mismatched_strategy_symbol(self) -> None:
        eur = _strategy("session_breakout", "EURUSD")
        champions = _champions(eur)

        with self.assertRaises(ValueError):
            PortfolioCandidate(
                candidate_id="bad",
                strategy_fingerprint=eur.fingerprint,
                symbol="EURUSD",
                direction=Direction.NO_TRADE,
                observed_at_utc=NOW,
                requested_risk_fraction=0.0025,
                applicability_passed=True,
            )

        mismatch = PortfolioCandidate(
            candidate_id="mismatch",
            strategy_fingerprint=eur.fingerprint,
            symbol="GBPUSD",
            direction=Direction.LONG,
            observed_at_utc=NOW,
            requested_risk_fraction=0.0025,
            applicability_passed=True,
        )
        result = route_shadow_candidates(champions, [mismatch])
        self.assertEqual(result.accepted, ())
        self.assertEqual(result.rejected[0].code, CandidateRejectionCode.STRATEGY_SYMBOL_MISMATCH)

    def test_duplicate_candidate_ids_fail_closed(self) -> None:
        eur = _strategy("session_breakout", "EURUSD")
        champions = _champions(eur)
        candidate = _candidate("dup", eur, Direction.LONG)

        with self.assertRaises(ValueError):
            route_shadow_candidates(champions, [candidate, candidate])


if __name__ == "__main__":
    unittest.main()
