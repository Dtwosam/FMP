"""Reproduce the 17 November 2026 return-versus-ruin scenario table.

The study named fmpsim.py. That file was not in the PDF. This script runs the
in-repository reconstruction and prints the differences. It does not read
market data, dispatch research, or authorize trading.

Usage:
    PYTHONPATH=src python scripts/reproduce_100pct_30day_study.py
    PYTHONPATH=src python scripts/reproduce_100pct_30day_study.py --paths 200000
"""

from __future__ import annotations

import argparse

from fmp.simulation.return_vs_ruin import (
    STUDY_COST_R,
    STUDY_PUBLISHED_EXACT,
    STUDY_PUBLISHED_STRESS,
    STUDY_SCENARIOS,
    AccountAssumptions,
    BinaryPayoff,
    FixedFractionalSizing,
    documented_phase7_monthly_inputs,
    evaluate_against_zero_edge,
    exact_binary_outcomes,
    monte_carlo_binary_outcomes,
    risk_fraction_at_stop,
    study_candidate_f2_gaps,
    study_stress_dependence,
)


def _percent(probability: float) -> str:
    return f"{100.0 * probability:6.2f}"


def _row(result) -> tuple[float, float, float, float, float, float, float]:
    return (
        100.0 * result.end_at_least_double,
        100.0 * result.touch_double,
        100.0 * result.lose_at_least_half,
        100.0 * result.lose_at_least_ninety,
        100.0 * result.account_exhausted,
        100.0 * result.end_below_start,
        result.median_terminal_multiple,
    )


def _print_comparison(title: str, got, published, tolerances: tuple[float, float]) -> bool:
    print(title)
    print(
        f"{'id':4} {'end2':>8} {'touch':>8} {'lose50':>8} {'lose90':>8} "
        f"{'lost':>8} {'below':>8} {'median':>8}"
    )
    matched = True
    probability_tolerance, median_tolerance = tolerances
    for scenario in STUDY_SCENARIOS:
        actual = got[scenario.scenario_id]
        expected = published[scenario.scenario_id]
        flags = []
        for index, (left, right) in enumerate(zip(actual, expected, strict=True)):
            tolerance = median_tolerance if index == 6 else probability_tolerance
            if abs(left - right) > tolerance:
                matched = False
                flags.append(str(index))
        mark = "" if not flags else "  differ cols " + ",".join(flags)
        print(
            f"{scenario.scenario_id:4} "
            f"{actual[0]:8.2f} {actual[1]:8.2f} {actual[2]:8.2f} {actual[3]:8.2f} "
            f"{actual[4]:8.2f} {actual[5]:8.2f} {actual[6]:8.3f}{mark}"
        )
        print(
            "     "
            f"{expected[0]:8.2f} {expected[1]:8.2f} {expected[2]:8.2f} {expected[3]:8.2f} "
            f"{expected[4]:8.2f} {expected[5]:8.2f} {expected[6]:8.3f}  published"
        )
    return matched


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()
    if args.paths <= 0:
        raise SystemExit("--paths must be positive")

    print("Evidence basis: hypothetical binary distribution, cost 0.08R on every scenario.")
    print("fmpsim.py was not supplied. Figures below are this repository's reconstruction.")
    print("Account rule used for the stress paths: negative-balance protection only.")
    print("A 30:1 cap and a 50% margin close-out are not applied inside these paths.")
    print(
        "Identity check: 30:1 times a 10-pip EUR/USD stop is "
        f"{100.0 * risk_fraction_at_stop(leverage=30.0, stop_price_fraction=0.001):.1f}% "
        "of equity. The study text says 2.7%. The scenario rows do not use 2.7%."
    )
    print()

    exact = {}
    for scenario in STUDY_SCENARIOS:
        payoff = BinaryPayoff(scenario.reward_to_risk, STUDY_COST_R, scenario.net_edge_r)
        exact[scenario.scenario_id] = _row(
            exact_binary_outcomes(
                payoff,
                FixedFractionalSizing(scenario.risk_fraction),
                scenario.trades_per_window,
            )
        )
    exact_match = _print_comparison(
        "Exact independent lattice versus the printed table",
        exact,
        STUDY_PUBLISHED_EXACT,
        (0.08, 0.011),
    )
    print()

    stress = {}
    dependence = study_stress_dependence()
    account = AccountAssumptions(negative_balance_protection=True, label="study-nbp-only")
    for scenario in STUDY_SCENARIOS:
        payoff = BinaryPayoff(scenario.reward_to_risk, STUDY_COST_R, scenario.net_edge_r)
        stress[scenario.scenario_id] = _row(
            monte_carlo_binary_outcomes(
                payoff,
                FixedFractionalSizing(scenario.risk_fraction),
                scenario.trades_per_window,
                n_paths=args.paths,
                seed=args.seed,
                dependence=dependence,
                account=account,
            )
        )
    # Sampling noise at the study's 200,000 paths is about 0.1 percentage point
    # for a 12% probability. The default run uses fewer paths, so the gate is wider.
    stress_tolerance = 1.0 if args.paths >= 20_000 else 2.0
    stress_match = _print_comparison(
        f"Stress Monte Carlo, {args.paths} paths, seed {args.seed}, versus the printed table",
        stress,
        STUDY_PUBLISHED_STRESS,
        (stress_tolerance, 0.03),
    )
    print()

    s6 = STUDY_SCENARIOS[5]
    s2 = STUDY_SCENARIOS[1]
    for scenario in (s2, s6):
        split = evaluate_against_zero_edge(
            BinaryPayoff(scenario.reward_to_risk, STUDY_COST_R, scenario.net_edge_r),
            FixedFractionalSizing(scenario.risk_fraction),
            scenario.trades_per_window,
        )
        print(
            f"{scenario.scenario_id} exact P(double) {_percent(split.strategy.end_at_least_double)}% "
            f"versus zero-edge {_percent(split.zero_edge.end_at_least_double)}% "
            f"difference {_percent(split.doubling_probability_difference)} pp"
        )
        print(
            f"    E[log equity] {split.strategy.expected_log_growth:.4f} "
            f"versus zero-edge {split.zero_edge.expected_log_growth:.4f}; "
            f"median {split.strategy.median_terminal_multiple:.3f}x "
            f"versus {split.zero_edge.median_terminal_multiple:.3f}x"
        )
    print()

    phase7 = documented_phase7_monthly_inputs()
    print("Documented Phase 7 session-breakout aggregate, not a trade-level record.")
    print(f"  {phase7['candidate']}")
    print(f"  Stage 2 trades per 30 days: {phase7['stage2_trades_per_30_days']:.2f}")
    print(f"  Stage 2 mean-R estimates at 0.2/0.5/1.0 pip slippage: {phase7['stage2_mean_r_estimate']}")
    print(f"  Edge-first candidate for doubling: {phase7['edge_first_candidate_for_doubling']}")
    print(f"  {phase7['edge_first_reason']}")
    print(f"  {phase7['holdout_note']}")
    monthly_trades = 10
    illustrations = (
        ("policy 0.25%", 0.0025, 0.005, STUDY_COST_R),
        ("study rounded +0.005R at 4%", 0.04, 0.005, STUDY_COST_R),
        ("study sentence at 20%, cost in the payoff", 0.20, 0.005, STUDY_COST_R),
        ("study sentence at 20%, cost not charged again", 0.20, 0.005, 0.0),
    )
    print("Illustrative 10-trade windows. These are not a candidate outcome.")
    for label, fraction, edge, cost in illustrations:
        result = exact_binary_outcomes(
            BinaryPayoff(1.5, cost, edge),
            FixedFractionalSizing(fraction),
            monthly_trades,
        )
        zero = exact_binary_outcomes(
            BinaryPayoff(1.5, cost, 0.0),
            FixedFractionalSizing(fraction),
            monthly_trades,
        )
        print(
            f"  {label}: P(double) {_percent(result.end_at_least_double)}% "
            f"P(lose half) {_percent(result.lose_at_least_half)}% "
            f"median {result.median_terminal_multiple:.3f}x "
            f"zero-edge P(double) {_percent(zero.end_at_least_double)}%"
        )
    print("Cost sensitivity with gross edge held fixed. Pip cost assumes a 15-pip stop, so c = pips/15.")
    print("Doubling probabilities are exact and can stay flat across a small cost change; log growth moves immediately.")
    for name, net, reward, trades in (
        ("S6", 0.005, 1.5, 60),
        ("S7", 0.05, 1.5, 120),
        ("S8", 0.10, 1.5, 120),
        ("S10", 0.20, 2.0, 200),
    ):
        gross = net + STUDY_COST_R
        for pips in (1.0, 1.2, 1.5, 2.5):
            cost = pips / 15.0
            result = exact_binary_outcomes(
                BinaryPayoff(reward, cost, gross - cost),
                FixedFractionalSizing(0.04),
                trades,
            )
            print(
                f"  {name} {pips:.1f} pip net {gross - cost:+.3f}R: "
                f"P(double) {_percent(result.end_at_least_double)}% "
                f"median {result.median_terminal_multiple:.3f}x "
                f"E[log] {result.expected_log_growth:.4f}"
            )
    print()
    screen = study_candidate_f2_gaps(
        exact_binary_outcomes(
            BinaryPayoff(1.5, STUDY_COST_R, 0.005),
            FixedFractionalSizing(0.04),
            60,
        )
    )
    print(f"Candidate F2 screen on S6 exact result, not an acceptance gate: {screen}")
    print()
    print(f"Exact table within rounding: {exact_match}")
    print(f"Stress table within {stress_tolerance:.2f} percentage points: {stress_match}")
    print("No trading authority is created by this script.")
    if not exact_match:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
