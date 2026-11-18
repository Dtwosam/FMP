from __future__ import annotations

import math
import unittest

from fmp.simulation.return_vs_ruin import (
    STUDY_COST_R,
    STUDY_PUBLISHED_EXACT,
    STUDY_SCENARIOS,
    AccountAssumptions,
    BinaryPayoff,
    DependenceModel,
    FixedFractionalSizing,
    apply_net_r_path,
    block_bootstrap_outcomes,
    documented_phase7_monthly_inputs,
    evaluate_against_zero_edge,
    exact_binary_outcomes,
    kelly_fraction,
    leverage_for_uncapped_gbm_doubling,
    log_growth_per_trade,
    minimum_net_edge_for_doubling_probability,
    monte_carlo_binary_outcomes,
    probability_of_loss_streak,
    risk_fraction_at_stop,
    study_candidate_f2_gaps,
    study_stress_dependence,
    uncapped_gbm_doubling_probability,
)


def _payoff(edge: float, reward: float = 1.0, cost: float = 0.0) -> BinaryPayoff:
    return BinaryPayoff(reward, cost, edge)


class ExactLatticeTests(unittest.TestCase):
    def test_two_trade_hand_calculation(self) -> None:
        result = exact_binary_outcomes(
            _payoff(0.0),
            FixedFractionalSizing(0.5),
            2,
        )
        self.assertAlmostEqual(result.end_at_least_double, 0.25, places=12)
        self.assertAlmostEqual(result.touch_double, 0.25, places=12)
        self.assertAlmostEqual(result.lose_at_least_half, 0.25, places=12)
        self.assertAlmostEqual(result.end_below_start, 0.75, places=12)
        self.assertAlmostEqual(result.median_terminal_multiple, 0.75, places=12)
        self.assertAlmostEqual(result.expected_terminal_multiple, 1.0, places=12)
        self.assertEqual(result.method, "exact_independent_binomial")
        self.assertEqual(result.standard_errors["end_at_least_double"], 0.0)

    def test_zero_edge_expected_terminal_is_one_and_log_growth_is_negative(self) -> None:
        payoff = BinaryPayoff(1.0, STUDY_COST_R, 0.0)
        sizing = FixedFractionalSizing(0.04)
        result = exact_binary_outcomes(payoff, sizing, 60)
        self.assertAlmostEqual(result.expected_terminal_multiple, 1.0, places=9)
        self.assertLess(result.expected_log_growth, 0.0)
        self.assertGreater(result.end_at_least_double, 0.0)

    def test_all_wins_cannot_double_at_low_risk_and_short_sample(self) -> None:
        payoff = BinaryPayoff(1.5, STUDY_COST_R, 0.005)
        result = exact_binary_outcomes(payoff, FixedFractionalSizing(0.04), 10)
        self.assertEqual(result.end_at_least_double, 0.0)
        self.assertEqual(result.touch_double, 0.0)
        gross_ten_wins = (1.0 + 0.04 * 1.5) ** 10
        net_ten_wins = (1.0 + 0.04 * (1.5 - STUDY_COST_R)) ** 10
        self.assertAlmostEqual(gross_ten_wins, 1.7908476965428546, places=12)
        self.assertLess(net_ten_wins, 2.0)
        self.assertGreater(result.expected_terminal_multiple, 0.0)

    def test_published_exact_scenario_table(self) -> None:
        for scenario in STUDY_SCENARIOS:
            result = exact_binary_outcomes(
                BinaryPayoff(scenario.reward_to_risk, STUDY_COST_R, scenario.net_edge_r),
                FixedFractionalSizing(scenario.risk_fraction),
                scenario.trades_per_window,
            )
            published = STUDY_PUBLISHED_EXACT[scenario.scenario_id]
            got = (
                100.0 * result.end_at_least_double,
                100.0 * result.touch_double,
                100.0 * result.lose_at_least_half,
                100.0 * result.lose_at_least_ninety,
                100.0 * result.account_exhausted,
                100.0 * result.end_below_start,
                result.median_terminal_multiple,
            )
            for index, (actual, expected) in enumerate(zip(got, published, strict=True)):
                tolerance = 0.011 if index == 6 else 0.08
                self.assertLessEqual(
                    abs(actual - expected),
                    tolerance,
                    f"{scenario.scenario_id} column {index}: {actual} vs {expected}",
                )

    def test_one_loss_exhausts_with_negative_balance_protection(self) -> None:
        payoff = BinaryPayoff(1.0, 0.1, 0.0)
        account = AccountAssumptions(negative_balance_protection=True, label="nbp")
        result = exact_binary_outcomes(payoff, FixedFractionalSizing(0.95), 1, account)
        self.assertEqual(result.method, "exact_independent_binomial_loss_exhausts")
        self.assertAlmostEqual(result.account_exhausted, 1.0 - payoff.win_probability(), places=9)
        self.assertEqual(result.end_at_least_double, 0.0)
        self.assertTrue(math.isinf(result.expected_log_growth) and result.expected_log_growth < 0)


class MonteCarloTests(unittest.TestCase):
    def test_independent_draws_match_the_exact_lattice(self) -> None:
        payoff = BinaryPayoff(1.0, STUDY_COST_R, 0.0)
        sizing = FixedFractionalSizing(0.15)
        exact = exact_binary_outcomes(payoff, sizing, 20)
        paths = 20_000
        sampled = monte_carlo_binary_outcomes(
            payoff,
            sizing,
            20,
            n_paths=paths,
            seed=7,
            dependence=None,
        )
        self.assertEqual(sampled.method, "monte_carlo_independent")
        for name in ("end_at_least_double", "touch_double", "lose_at_least_half", "end_below_start"):
            exact_p = getattr(exact, name)
            sampled_p = getattr(sampled, name)
            standard_error = math.sqrt(exact_p * (1.0 - exact_p) / paths)
            self.assertLess(abs(sampled_p - exact_p), 4.0 * standard_error + 1e-12)
            self.assertAlmostEqual(sampled.standard_errors[name], math.sqrt(sampled_p * (1.0 - sampled_p) / paths))

    def test_same_seed_is_deterministic(self) -> None:
        payoff = BinaryPayoff(1.5, STUDY_COST_R, 0.005)
        sizing = FixedFractionalSizing(0.04)
        kwargs = {"n_paths": 500, "seed": 11, "dependence": study_stress_dependence()}
        first = monte_carlo_binary_outcomes(payoff, sizing, 60, **kwargs)
        second = monte_carlo_binary_outcomes(payoff, sizing, 60, **kwargs)
        self.assertEqual(first.as_dict(), second.as_dict())

    def test_stress_model_reproduces_s2_and_s6(self) -> None:
        published = {
            "S2": STUDY_SCENARIOS[1],
            "S6": STUDY_SCENARIOS[5],
        }
        targets = {
            "S2": (7.4, 10.6, 11.6, 53.5),
            "S6": (12.1, 17.9, 16.7, 54.2),
        }
        for scenario_id, scenario in published.items():
            result = monte_carlo_binary_outcomes(
                BinaryPayoff(scenario.reward_to_risk, STUDY_COST_R, scenario.net_edge_r),
                FixedFractionalSizing(scenario.risk_fraction),
                scenario.trades_per_window,
                n_paths=20_000,
                seed=11,
                dependence=study_stress_dependence(),
                account=AccountAssumptions(negative_balance_protection=True, label="study-nbp-only"),
            )
            got = (
                100.0 * result.end_at_least_double,
                100.0 * result.touch_double,
                100.0 * result.lose_at_least_half,
                100.0 * result.end_below_start,
            )
            for actual, expected in zip(got, targets[scenario_id], strict=True):
                self.assertLess(
                    abs(actual - expected),
                    1.0,
                    f"{scenario_id}: {actual} vs published {expected}",
                )


class EdgeAndAccountTests(unittest.TestCase):
    def test_zero_edge_benchmark_holds_size_and_payoff_fixed(self) -> None:
        payoff = BinaryPayoff(1.5, STUDY_COST_R, 0.005)
        sizing = FixedFractionalSizing(0.04)
        split = evaluate_against_zero_edge(payoff, sizing, 60)
        self.assertGreater(split.strategy.expected_log_growth, split.zero_edge.expected_log_growth)
        self.assertGreater(split.doubling_probability_difference, 0.0)
        self.assertAlmostEqual(split.zero_edge.expected_terminal_multiple, 1.0, places=9)
        self.assertEqual(split.strategy.evidence_basis, "hypothetical_distribution")

    def test_requested_size_is_not_reduced_when_a_leverage_cap_is_exceeded(self) -> None:
        payoff = BinaryPayoff(1.0, STUDY_COST_R, 0.0)
        sizing = FixedFractionalSizing(0.15)
        plain = exact_binary_outcomes(payoff, sizing, 20)
        capped = exact_binary_outcomes(
            payoff,
            sizing,
            20,
            AccountAssumptions(
                max_leverage=30.0,
                stop_price_fraction=0.0015,
                label="cap-reported-not-applied",
            ),
        )
        self.assertEqual(plain.end_at_least_double, capped.end_at_least_double)
        self.assertTrue(capped.leverage_cap_exceeded)
        self.assertAlmostEqual(capped.effective_leverage, 0.15 / 0.0015)

    def test_margin_closeout_and_negative_balance_are_explicit(self) -> None:
        sizing = FixedFractionalSizing(0.04)
        closeout = AccountAssumptions(
            max_leverage=30.0,
            stop_price_fraction=0.0015,
            margin_closeout_ratio=0.5,
            label="esma-style-closeout",
        )
        closed = apply_net_r_path((-20.0,), sizing, closeout)
        self.assertAlmostEqual(float(closed["terminal_multiple"]), 0.5 * (0.04 / 0.0015) / 30.0)
        self.assertTrue(closed["halted"])
        unprotected = apply_net_r_path((-30.0,), sizing, AccountAssumptions(label="no-floor"))
        protected = apply_net_r_path(
            (-30.0,),
            sizing,
            AccountAssumptions(negative_balance_protection=True, label="floor"),
        )
        self.assertLess(float(unprotected["terminal_multiple"]), 0.0)
        self.assertEqual(float(protected["terminal_multiple"]), 0.0)
        self.assertTrue(protected["account_exhausted"])

    def test_path_drawdown(self) -> None:
        path = apply_net_r_path((1.0, -0.5), FixedFractionalSizing(0.5))
        self.assertAlmostEqual(float(path["terminal_multiple"]), 1.125)
        self.assertAlmostEqual(float(path["max_drawdown"]), 0.25)

    def test_block_bootstrap_uses_the_record_and_is_deterministic(self) -> None:
        sizing = FixedFractionalSizing(0.1)
        record = (1.0,) * 30
        first = block_bootstrap_outcomes(
            record, sizing, 10, n_paths=20, seed=3, mean_block_length=5.0
        )
        second = block_bootstrap_outcomes(
            record, sizing, 10, n_paths=20, seed=3, mean_block_length=5.0
        )
        self.assertEqual(first.as_dict(), second.as_dict())
        self.assertEqual(first.end_at_least_double, 1.0)
        self.assertEqual(first.evidence_basis, "supplied_trade_record")
        flat = block_bootstrap_outcomes(
            (0.0,) * 10,
            sizing,
            10,
            n_paths=15,
            seed=1,
            mean_block_length=2.0,
            evidence_basis="hypothetical_distribution",
        )
        self.assertEqual(flat.median_terminal_multiple, 1.0)
        self.assertEqual(flat.end_at_least_double, 0.0)
        self.assertEqual(flat.evidence_basis, "hypothetical_distribution")

    def test_kelly_and_log_growth_match_the_zero_cost_table(self) -> None:
        payoff = BinaryPayoff(1.0, 0.0, 0.05)
        fraction = kelly_fraction(payoff)
        self.assertAlmostEqual(fraction, 0.05, places=12)
        growth = log_growth_per_trade(payoff, FixedFractionalSizing(fraction))
        self.assertAlmostEqual(growth, 0.001250521, places=6)
        self.assertAlmostEqual(math.log(2.0) / growth, 554.3, delta=0.2)
        self.assertEqual(kelly_fraction(BinaryPayoff(1.0, 0.0, 0.0)), 0.0)

    def test_loss_streak_and_gbm_closed_forms(self) -> None:
        self.assertAlmostEqual(probability_of_loss_streak(2, 0.5, 2), 0.25)
        streak = probability_of_loss_streak(120, 0.5, 8)
        self.assertAlmostEqual(streak, 0.20, delta=0.015)
        self.assertAlmostEqual(100.0 * uncapped_gbm_doubling_probability(0.0), 12.0, delta=0.1)
        self.assertAlmostEqual(100.0 * uncapped_gbm_doubling_probability(2.0), 27.4, delta=0.1)
        self.assertAlmostEqual(leverage_for_uncapped_gbm_doubling(0.08), 51.0, delta=0.1)
        self.assertAlmostEqual(risk_fraction_at_stop(leverage=30.0, stop_price_fraction=0.001), 0.03)

    def test_minimum_edge_search_does_not_change_the_risk_fraction(self) -> None:
        sizing = FixedFractionalSizing(0.04)
        self.assertIsNone(
            minimum_net_edge_for_doubling_probability(
                reward_to_risk=1.5,
                cost_r=STUDY_COST_R,
                sizing=sizing,
                n_trades=10,
            )
        )
        found = minimum_net_edge_for_doubling_probability(
            reward_to_risk=1.5,
            cost_r=STUDY_COST_R,
            sizing=sizing,
            n_trades=120,
            target_probability=0.25,
        )
        self.assertIsNotNone(found)
        assert found is not None
        at_found = exact_binary_outcomes(BinaryPayoff(1.5, STUDY_COST_R, found), sizing, 120)
        below = exact_binary_outcomes(BinaryPayoff(1.5, STUDY_COST_R, found - 0.002), sizing, 120)
        self.assertGreaterEqual(at_found.end_at_least_double, 0.25)
        self.assertLess(below.end_at_least_double, 0.25)
        self.assertEqual(sizing.risk_fraction, 0.04)

    def test_candidate_screen_is_not_an_acceptance_gate(self) -> None:
        result = exact_binary_outcomes(BinaryPayoff(1.5, STUDY_COST_R, 0.005), FixedFractionalSizing(0.04), 60)
        gaps = study_candidate_f2_gaps(result)
        self.assertFalse(gaps["adopted_as_acceptance_gate"])
        self.assertFalse(gaps["meets_candidate_screen"])

    def test_documented_phase7_inputs_fail_the_edge_first_check(self) -> None:
        inputs = documented_phase7_monthly_inputs()
        self.assertAlmostEqual(float(inputs["stage2_trades_per_30_days"]), 10.0, delta=0.05)
        stage2 = inputs["stage2_mean_r_estimate"]
        assert isinstance(stage2, dict)
        self.assertAlmostEqual(stage2[0.5], 1.3175 / 250.0)
        self.assertLess(stage2[1.0], 0.0)
        self.assertFalse(inputs["edge_first_candidate_for_doubling"])
        self.assertIn("not an untouched", str(inputs["holdout_note"]))

    def test_dependence_model_rejects_a_fitted_clock_name(self) -> None:
        with self.assertRaises(ValueError):
            DependenceModel(regime_clock="optimized")


if __name__ == "__main__":
    unittest.main()
