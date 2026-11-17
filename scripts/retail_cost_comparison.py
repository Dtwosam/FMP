#!/usr/bin/env python3
"""Print the source-backed retail cost comparison.

The hypothetical lattice rows are not estimates for the documented Phase 7
strategy. No broker is selected and no order is sent.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fmp.research.retail_costs import (  # noqa: E402
    STANDARD_LOT_UNITS,
    hypothetical_cost_sensitivity,
    phase7_documented_revaluation,
    zero_edge_is_not_rescued_by_sizing,
)


def main() -> None:
    phase7 = phase7_documented_revaluation()
    print("Phase 7 documented USDJPY 15m session-breakout aggregates")
    print(f"  reliable doubling/loss probabilities: {phase7['reliable_probability_estimate']}")
    print(f"  {phase7['probability_blocker']}")
    print(f"  {phase7['incremental_blocker']}")
    for pips, dollars in phase7["stage2_expectancy_usd"].items():
        mean_r = phase7["stage2_mean_r_estimate"][pips]
        print(f"  {pips:.1f} pip per side, bid/ask spread already included: {dollars:+.4f} USD, {mean_r:+.5f}R")
    print(f"  edge-first doubling candidate: {phase7['edge_first_candidate_for_doubling']}")
    print()
    print("Hypothetical EURUSD lattice at a 15-pip stop, gross edge fixed at the study's +0.085R.")
    print("These rows are not a Phase 7 probability estimate.")
    for row in hypothetical_cost_sensitivity(units=STANDARD_LOT_UNITS):
        print(
            f"  {row['label']}: package {row['package']}; "
            f"cost {row['cost_r']:.4f}R; net {row['net_expectancy_r']:+.4f}R; "
            f"P(double) {100 * row['probability_end_at_least_double']:.2f}%; "
            f"P(lose half) {100 * row['probability_lose_at_least_half']:.2f}%; "
            f"P(lose 90) {100 * row['probability_lose_at_least_ninety']:.2f}%; "
            f"median {row['median_terminal_multiple']:.3f}x; "
            f"E[log] {row['expected_log_growth']:.4f}"
        )
    print()
    print("Zero gross edge at the study cost of 0.08R, fixed fractions only.")
    for row in zero_edge_is_not_rescued_by_sizing(reward_to_risk=1.5, cost_r=0.08, trades=60):
        print(
            f"  f={row['risk_fraction']:.4f}: net {row['net_expectancy_r']:+.3f}R, "
            f"E[terminal] {row['expected_terminal_multiple']:.4f}, "
            f"log growth/trade {row['log_growth_per_trade']:.6f}"
        )
    print()
    print("No trading authority is created by this script.")


if __name__ == "__main__":
    main()
