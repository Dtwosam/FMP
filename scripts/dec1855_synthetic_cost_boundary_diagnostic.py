"""DEC-1855: synthetic-only cost-input boundary diagnostic; never trading."""
from __future__ import annotations

import argparse
import json
import sys

from fmp.backtest.costs import (
    FixedCommissionPerMillion,
    apply_adverse_slippage,
)
from fmp.contracts import OrderSide


SYNTHETIC_PRICE = 1.20000
SYNTHETIC_PIPS = 1.0
SYNTHETIC_SYMBOL = "EURUSD"


def inspect_synthetic_cost_boundaries():
    """Expose a contract gap with constants only, no market or broker inputs."""
    buy = apply_adverse_slippage(
        SYNTHETIC_PRICE, side=OrderSide.BUY,
        pips=SYNTHETIC_PIPS, symbol=SYNTHETIC_SYMBOL,
    )
    sell = apply_adverse_slippage(
        SYNTHETIC_PRICE, side=OrderSide.SELL,
        pips=SYNTHETIC_PIPS, symbol=SYNTHETIC_SYMBOL,
    )
    try:
        mistyped_buy = apply_adverse_slippage(
            SYNTHETIC_PRICE, side="BUY",
            pips=SYNTHETIC_PIPS, symbol=SYNTHETIC_SYMBOL,
        )
    except (TypeError, ValueError):
        mistyped_buy = None
    commission = FixedCommissionPerMillion(usd_per_million_per_side=30.0)
    try:
        fractional_units_cost = commission.cost_usd(units=0.5)
    except (TypeError, ValueError):
        fractional_units_cost = None
    if not (buy > SYNTHETIC_PRICE > sell):
        raise ValueError("synthetic enum-side slippage direction inconsistent")
    return {
        "schema": "fmp_dec1855_synthetic_cost_boundary_diagnostic_v1",
        "disposition": "BLOCKED_NO_STRATEGY_OR_TRADING_PERMISSION",
        "source_material": "constants_only_no_market_data",
        "synthetic_price": SYNTHETIC_PRICE,
        "synthetic_pips": SYNTHETIC_PIPS,
        "symbol": SYNTHETIC_SYMBOL,
        "enum_buy_moves_up": True,
        "enum_sell_moves_down": True,
        "untyped_buy_string_interpreted_as_sell":
            mistyped_buy is not None and mistyped_buy == sell,
        "fractional_commission_units_currently_accepted":
            fractional_units_cost is not None,
        "known_issues_require_separate_backtester_review": True,
        "economic_expectancy_or_profitable_strategy_verified": False,
        "protected_2023_run385_attempt1_authorized": False,
        "broker_demo_live_or_real_money_authorized": False,
        "allowed_actions": [],
        "no_external_actions_performed": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Synthetic cost contract review; always BLOCKED"
    )
    parser.add_argument("--format", choices=("json",), default="json")
    args = parser.parse_args(argv)
    try:
        report = inspect_synthetic_cost_boundaries()
        output = json.dumps(report, sort_keys=True, indent=2, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as exc:
        print("BLOCKED: synthetic cost diagnostic invalid", file=sys.stderr)
        return 2
    print(output)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
