"""Source-backed retail FX costs for EURUSD, GBPUSD, and USDJPY.

The figures are quotations retrieved on 2026-11-17. They are not observed
FMP fills, and no broker has been selected. Historical Phase 3 and Phase 7
fills already pay the Dukascopy bid/ask spread. Adding another spread on top
of those fills double-counts it.

This module does not connect to a broker and does not place orders.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from fmp.backtest.costs import FixedCommissionPerMillion, ZeroCommission, pip_size
from fmp.contracts import Direction
from fmp.simulation.return_vs_ruin import (
    STUDY_COST_R,
    BinaryPayoff,
    FixedFractionalSizing,
    documented_phase7_monthly_inputs,
    exact_binary_outcomes,
    log_growth_per_trade,
)

ACCESS_DATE = date(2026, 11, 17)
STANDARD_LOT_UNITS = 100_000
NEW_YORK = ZoneInfo("America/New_York")
QUOTE_USD = frozenset({"EURUSD", "GBPUSD"})
SYMBOLS = frozenset({"EURUSD", "GBPUSD", "USDJPY"})

# OANDA's worked example. The page says these rates are not the live swap.
OANDA_EXAMPLE_LONG_ANNUAL_RATE = -0.03
OANDA_EXAMPLE_EURUSD_PRICE = 1.15826

IC_EU_SPREADS_URL = "https://www.icmarkets.eu/en/trading-pricing/spreads-and-swaps"
IC_EU_COSTS_URL = "https://www.icmarkets.eu/en/trading-pricing/trading-costs"
OANDA_US_SPREADS_URL = "https://www.oanda.com/us-en/trading/our-pricing/"
OANDA_US_FINANCING_URL = "https://www.oanda.com/us-en/trading/financing-fees/"
PEPPERSTONE_COSTS_URL = "https://pepperstone.com/en/trading/costs-and-fees"


class MissingCostError(ValueError):
    """A complete cost was requested while a component is still unknown."""


class DoubleCountedSpreadError(ValueError):
    """A bid/ask fill was asked to pay the spread a second time."""


def _finite(value: float, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def _symbol(symbol: str) -> str:
    if symbol not in SYMBOLS:
        raise ValueError(f"unsupported symbol: {symbol!r}")
    return symbol


def pip_value_usd(symbol: str, units: int, conversion_price: float | None) -> float:
    """USD value of one pip.

    EURUSD and GBPUSD are quoted in USD, so one pip is ``units * 0.0001``.
    USDJPY is quoted in JPY. Phase 3 converts that quote PnL by the exit
    price, so one pip is ``units * 0.01 / conversion_price``.
    """
    pair = _symbol(symbol)
    if isinstance(units, bool) or not isinstance(units, int) or units <= 0:
        raise ValueError("units must be a positive integer")
    size = pip_size(pair)
    if pair in QUOTE_USD:
        return units * size
    if conversion_price is None:
        raise MissingCostError("USDJPY pip value needs a positive conversion price")
    price = _finite(conversion_price, name="conversion_price")
    if price <= 0.0:
        raise ValueError("conversion price must be positive")
    return units * size / price


def pips_to_r(pips: float, stop_pips: float) -> float:
    """Convert a pip charge into R. The USDJPY conversion rate cancels."""
    charge = _finite(pips, name="pips")
    stop = _finite(stop_pips, name="stop_pips")
    if charge < 0.0 or stop <= 0.0:
        raise ValueError("pip charge must be non-negative and the stop must be positive")
    return charge / stop


def usd_to_r(
    usd: float,
    *,
    symbol: str,
    units: int,
    stop_pips: float,
    conversion_price: float | None,
) -> float:
    risk = stop_pips * pip_value_usd(symbol, units, conversion_price)
    if risk <= 0.0:
        raise ValueError("risk in USD must be positive")
    return _finite(usd, name="usd") / risk


@dataclass(frozen=True, slots=True)
class SpreadQuote:
    broker: str
    entity: str
    account_type: str
    symbol: str
    source_url: str
    accessed_on: date
    currency: str
    conditions: str
    advertised_minimum_pips: float | None
    published_average_pips: float | None
    unlabeled_quote_pips: float | None
    marketing_average_pips: float | None = None

    @property
    def conservative_published_average_pips(self) -> float | None:
        averages = [
            value
            for value in (self.published_average_pips, self.marketing_average_pips)
            if value is not None
        ]
        if not averages:
            return None
        return max(averages)


@dataclass(frozen=True, slots=True)
class CommissionQuote:
    broker: str
    account_type: str
    platform: str
    source_url: str
    accessed_on: date
    currency: str
    usd_per_standard_lot_per_side: float | None
    included_in_spread: bool
    conditions: str


@dataclass(frozen=True, slots=True)
class SwapPointQuote:
    broker: str
    symbol: str
    long_points: float
    short_points: float
    source_url: str
    accessed_on: date
    usd_per_point_per_standard_lot: float | None
    sign_note: str


def _ic_spread(symbol: str, table_average: float, marketing_average: float | None) -> SpreadQuote:
    return SpreadQuote(
        broker="IC Markets",
        entity="IC Markets (EU) Ltd, CySEC 362/18",
        account_type="Raw Spread, MetaTrader",
        symbol=symbol,
        source_url=IC_EU_SPREADS_URL,
        accessed_on=ACCESS_DATE,
        currency="pips",
        conditions=(
            "Variable spreads. The EU site says it is not intended for US residents. "
            "The same access also states an EURUSD average of 0.1 pips, while the "
            "pair table states AVG 0.06. The minimum of 0 is not a typical cost. "
            "No hourly or session spread was published."
        ),
        advertised_minimum_pips=0.0,
        published_average_pips=table_average,
        unlabeled_quote_pips=None,
        marketing_average_pips=marketing_average,
    )


def _ic_standard(symbol: str) -> SpreadQuote:
    return SpreadQuote(
        broker="IC Markets",
        entity="IC Markets (EU) Ltd, CySEC 362/18",
        account_type="Standard, MetaTrader",
        symbol=symbol,
        source_url=IC_EU_SPREADS_URL,
        accessed_on=ACCESS_DATE,
        currency="pips",
        conditions=(
            "Only a minimum is published (0.8 pips, or 0.80 for EURUSD). "
            "No average was on the pair table. The minimum is not a typical cost."
        ),
        advertised_minimum_pips=0.8,
        published_average_pips=None,
        unlabeled_quote_pips=None,
    )


def _oanda_spread(symbol: str, quoted: float) -> SpreadQuote:
    return SpreadQuote(
        broker="OANDA",
        entity="OANDA Corporation, US",
        account_type="spread-only",
        symbol=symbol,
        source_url=OANDA_US_SPREADS_URL,
        accessed_on=ACCESS_DATE,
        currency="pips",
        conditions=(
            "The page lists one spread and does not say whether it is a minimum, "
            "a typical, or an average. It says spreads can be wider at the open, "
            "the close, and around events. Commission on this account type is "
            "described as wrapped into the spread. No hourly curve was published."
        ),
        advertised_minimum_pips=None,
        published_average_pips=None,
        unlabeled_quote_pips=quoted,
    )


def _pepperstone_razor(symbol: str) -> SpreadQuote:
    return SpreadQuote(
        broker="Pepperstone",
        entity="Pepperstone Group; SCB leverage table on the same page",
        account_type="Razor",
        symbol=symbol,
        source_url=PEPPERSTONE_COSTS_URL,
        accessed_on=ACCESS_DATE,
        currency="pips",
        conditions=(
            "FX spreads start from 0.0 points. That is an advertised floor, not a "
            "typical spread. No pair average was published. Standard FX is described "
            "as a 1 pip markup with no commission, which is also not a measured spread."
        ),
        advertised_minimum_pips=0.0,
        published_average_pips=None,
        unlabeled_quote_pips=None,
    )


PUBLISHED_SPREADS: tuple[SpreadQuote, ...] = (
    _ic_spread("EURUSD", 0.06, 0.1),
    _ic_spread("GBPUSD", 0.26, None),
    _ic_spread("USDJPY", 0.22, None),
    _ic_standard("EURUSD"),
    _ic_standard("GBPUSD"),
    _ic_standard("USDJPY"),
    _oanda_spread("EURUSD", 1.4),
    _oanda_spread("GBPUSD", 2.0),
    _oanda_spread("USDJPY", 1.4),
    _pepperstone_razor("EURUSD"),
    _pepperstone_razor("GBPUSD"),
    _pepperstone_razor("USDJPY"),
)

IC_MT4_RAW_COMMISSION = CommissionQuote(
    broker="IC Markets",
    account_type="Raw Spread, MetaTrader",
    platform="MetaTrader 4/5",
    source_url=IC_EU_COSTS_URL,
    accessed_on=ACCESS_DATE,
    currency="USD",
    usd_per_standard_lot_per_side=3.50,
    included_in_spread=False,
    conditions=(
        "USD account: 3.50 per standard lot per side, 7.00 round turn. "
        "A 0.01 lot is 0.035 per side. EUR and GBP accounts use different figures. "
        "cTrader is a separate schedule: 3 USD per 100,000 USD traded, per side."
    ),
)

OANDA_SPREAD_ONLY_COMMISSION = CommissionQuote(
    broker="OANDA",
    account_type="spread-only",
    platform="spread-only pricing",
    source_url=OANDA_US_SPREADS_URL,
    accessed_on=ACCESS_DATE,
    currency="USD",
    usd_per_standard_lot_per_side=None,
    included_in_spread=True,
    conditions="Spread-only pricing says the commission is wrapped into the quoted spread.",
)

PEPPERSTONE_RAZOR_COMMISSION = CommissionQuote(
    broker="Pepperstone",
    account_type="Razor",
    platform="Pepperstone platform",
    source_url=PEPPERSTONE_COSTS_URL,
    accessed_on=ACCESS_DATE,
    currency="USD",
    usd_per_standard_lot_per_side=3.50,
    included_in_spread=False,
    conditions=(
        "Published as 3.50 USD per standard lot per side, and also as 'from' 3.50. "
        "cTrader is 6 USD round turn. TradingView is 7 USD round turn. "
        "The typical Razor spread on this page is unavailable."
    ),
)

# Spreads-page points are the linked "latest" table. The costs page's worked
# example uses different EURUSD points (-6.25 / +2.56) and shows that, for
# EURUSD, lots x points x nights equals USD. One point is therefore 1 USD per
# standard lot in that example. The other pairs do not get that identity.
PUBLISHED_SWAP_POINTS: tuple[SwapPointQuote, ...] = (
    SwapPointQuote("IC Markets", "EURUSD", -8.239, 1.521, IC_EU_SPREADS_URL, ACCESS_DATE, 1.0,
                   "Negative points are a charge in the EURUSD worked example. The example's own point values differ from this table."),
    SwapPointQuote("IC Markets", "GBPUSD", -3.916, -4.092, IC_EU_SPREADS_URL, ACCESS_DATE, None,
                   "Point size in USD is not stated for GBPUSD."),
    SwapPointQuote("IC Markets", "USDJPY", 8.379, -17.204, IC_EU_SPREADS_URL, ACCESS_DATE, None,
                   "Point size in USD is not stated for USDJPY."),
)


def published_spreads(symbol: str, *, account_type: str) -> SpreadQuote:
    pair = _symbol(symbol)
    for quote in PUBLISHED_SPREADS:
        if quote.symbol == pair and quote.account_type == account_type:
            return quote
    raise ValueError(f"no published spread for {symbol} / {account_type}")


def typical_spread_pips(quote: SpreadQuote) -> float:
    """Return a published average. An advertised minimum is never substituted."""
    average = quote.conservative_published_average_pips
    if average is None:
        raise MissingCostError(
            f"{quote.broker} {quote.account_type} {quote.symbol} has no published "
            "average spread. The advertised minimum is not used as a typical cost."
        )
    return average


def rollover_day_count(
    entry_utc: datetime,
    exit_utc: datetime,
    *,
    triple_wednesday: bool,
) -> int:
    """Financing days for a position held across 17:00 America/New_York.

    A cutoff counts when entry < cutoff <= exit. Wednesday counts as three
    days when ``triple_wednesday`` is set, which is the rule stated by OANDA
    US, Pepperstone, and IC Markets for T+2 forex. Saturday and Sunday have
    no cutoff. A holiday multiplier is not inferred.
    """
    if entry_utc.tzinfo is None or exit_utc.tzinfo is None:
        raise ValueError("entry and exit must be timezone-aware")
    if exit_utc <= entry_utc:
        raise ValueError("exit must be after entry")
    entry = entry_utc.astimezone(NEW_YORK)
    exit_ = exit_utc.astimezone(NEW_YORK)
    total = 0
    day = entry.date()
    while day <= exit_.date():
        if day.weekday() < 5:
            cutoff = datetime(day.year, day.month, day.day, 17, 0, tzinfo=NEW_YORK)
            if entry < cutoff <= exit_:
                total += 3 if triple_wednesday and day.weekday() == 2 else 1
        day += timedelta(days=1)
    return total


def weekend_inside_hold(entry_utc: datetime, exit_utc: datetime) -> bool:
    """True when the open interval contains any New York Saturday or Sunday time."""
    entry = entry_utc.astimezone(NEW_YORK)
    exit_ = exit_utc.astimezone(NEW_YORK)
    day = entry.date()
    while day <= exit_.date():
        if day.weekday() >= 5:
            start = datetime(day.year, day.month, day.day, tzinfo=NEW_YORK)
            end = start + timedelta(days=1)
            if max(entry, start) < min(exit_, end):
                return True
        day += timedelta(days=1)
    return False


def wednesday_triple_was_charged(entry_utc: datetime, exit_utc: datetime) -> bool:
    entry = entry_utc.astimezone(NEW_YORK)
    exit_ = exit_utc.astimezone(NEW_YORK)
    day = entry.date()
    while day <= exit_.date():
        if day.weekday() == 2:
            cutoff = datetime(day.year, day.month, day.day, 17, 0, tzinfo=NEW_YORK)
            if entry < cutoff <= exit_:
                return True
        day += timedelta(days=1)
    return False


def financing_hold_is_identified(entry_utc: datetime, exit_utc: datetime) -> bool:
    """Weekend holds are identified only when the Wednesday triple covers them."""
    if weekend_inside_hold(entry_utc, exit_utc) and not wednesday_triple_was_charged(entry_utc, exit_utc):
        return False
    return True


def oanda_signed_financing_usd(
    symbol: str,
    units: int,
    price: float,
    annual_rate: float,
    day_count: int,
) -> float:
    """OANDA US formula. Negative means the account is charged.

    ``position value x rate x day_count / 365``. The published EURUSD example
    is ``(100000 x 1.15826) x -3% / 365 = -9.52 USD``. The rate is an input.
    The page's -3% figure is an example, not a stored live quote. USDJPY
    notional in USD is the base-unit count after converting the JPY value.
    """
    pair = _symbol(symbol)
    if isinstance(units, bool) or not isinstance(units, int) or units <= 0:
        raise ValueError("units must be a positive integer")
    if isinstance(day_count, bool) or not isinstance(day_count, int) or day_count < 0:
        raise ValueError("day_count must be a non-negative integer")
    px = _finite(price, name="price")
    rate = _finite(annual_rate, name="annual_rate")
    if px <= 0.0:
        raise ValueError("price must be positive")
    position_usd = units * px if pair in QUOTE_USD else float(units)
    return position_usd * rate * day_count / 365.0


def financing_cost_usd_from_annual_rate(
    symbol: str,
    units: int,
    price: float,
    annual_rate: float,
    day_count: int,
) -> float:
    """Positive when the account pays. This is the engine's financing sign."""
    return -oanda_signed_financing_usd(symbol, units, price, annual_rate, day_count)


def ic_eurusd_financing_cost_usd(*, long: bool, lots: float, day_count: int) -> float:
    """EURUSD only. Uses the spreads-page points and the example's USD identity."""
    if lots <= 0.0 or day_count < 0:
        raise ValueError("lots and day_count must be non-negative, and lots positive")
    quote = next(item for item in PUBLISHED_SWAP_POINTS if item.symbol == "EURUSD")
    if quote.usd_per_point_per_standard_lot is None:
        raise MissingCostError("EURUSD point value is unavailable")
    points = quote.long_points if long else quote.short_points
    signed_usd = lots * points * day_count * quote.usd_per_point_per_standard_lot
    return -signed_usd


def swap_points_usd(symbol: str) -> float:
    quote = next(item for item in PUBLISHED_SWAP_POINTS if item.symbol == _symbol(symbol))
    if quote.usd_per_point_per_standard_lot is None:
        raise MissingCostError(
            f"{symbol} swap points are published, but the page does not define their USD value"
        )
    return quote.usd_per_point_per_standard_lot


def commission_round_turn_usd(units: int, *, usd_per_standard_lot_per_side: float) -> float:
    """Reuse the Phase 3 per-million commission model. Two sides, no third charge."""
    per_million = usd_per_standard_lot_per_side * (1_000_000 / STANDARD_LOT_UNITS)
    model = FixedCommissionPerMillion(per_million)
    return model.cost_usd(units=units) * 2.0


def session_spread_pips(symbol: str, session: str) -> None:
    """No session or hourly spread was published. Do not invent one."""
    _symbol(symbol)
    known = {"asia", "london", "new_york", "rollover", "event"}
    if session not in known:
        raise ValueError(f"unknown session label: {session!r}")
    raise MissingCostError(
        f"no observed or published {session} spread for {symbol}. "
        "An hourly curve is not estimated here."
    )


@dataclass(frozen=True, slots=True)
class CostLine:
    name: str
    provenance: str
    pips: float | None
    usd: float | None
    r_multiple: float | None
    note: str


@dataclass(frozen=True, slots=True)
class RetailCost:
    symbol: str
    fill_basis: str
    complete: bool
    missing: tuple[str, ...]
    lines: tuple[CostLine, ...]
    cost_r: float | None
    package: str
    notes: tuple[str, ...]

    def require_complete(self) -> float:
        if not self.complete or self.cost_r is None:
            raise MissingCostError("missing cost components: " + ", ".join(self.missing))
        return self.cost_r


def _line_r(line: CostLine) -> float:
    if line.r_multiple is None:
        raise MissingCostError(f"{line.name} has no R cost")
    return line.r_multiple


def _package_lines(
    quote: SpreadQuote,
    commission: CommissionQuote,
    *,
    symbol: str,
    units: int,
    stop_pips: float,
    conversion_price: float | None,
    use_unlabeled_quote: bool,
) -> tuple[list[CostLine], list[str]]:
    if quote.broker != commission.broker or quote.account_type != commission.account_type:
        raise ValueError("spread and commission must come from the same published package")
    missing: list[str] = []
    lines: list[CostLine] = []
    if use_unlabeled_quote:
        if quote.unlabeled_quote_pips is None:
            missing.append("unlabeled_spread")
            pips = None
        else:
            pips = quote.unlabeled_quote_pips
        lines.append(CostLine(
            "spread",
            "published_specification",
            pips,
            None if pips is None else pips * pip_value_usd(symbol, units, conversion_price),
            None if pips is None else pips_to_r(pips, stop_pips),
            "Single published quote. Not labeled as a minimum or an average.",
        ))
    else:
        try:
            pips = typical_spread_pips(quote)
        except MissingCostError:
            missing.append("typical_spread")
            pips = None
        lines.append(CostLine(
            "spread",
            "published_specification" if pips is not None else "unavailable",
            pips,
            None if pips is None else pips * pip_value_usd(symbol, units, conversion_price),
            None if pips is None else pips_to_r(pips, stop_pips),
            "Higher of the published average figures. The advertised minimum is not used.",
        ))
    if commission.included_in_spread:
        lines.append(CostLine(
            "commission",
            "published_specification",
            0.0,
            0.0,
            0.0,
            "Wrapped into the quoted spread. ZeroCommission is the added amount.",
        ))
        ZeroCommission().cost_usd(units=units)
    elif commission.usd_per_standard_lot_per_side is None:
        missing.append("commission")
        lines.append(CostLine("commission", "unavailable", None, None, None, commission.conditions))
    else:
        usd = commission_round_turn_usd(
            units, usd_per_standard_lot_per_side=commission.usd_per_standard_lot_per_side
        )
        lines.append(CostLine(
            "commission",
            "published_specification",
            None,
            usd,
            usd_to_r(usd, symbol=symbol, units=units, stop_pips=stop_pips, conversion_price=conversion_price),
            commission.conditions,
        ))
    return lines, missing


def assemble_cost(
    *,
    symbol: str,
    units: int,
    stop_pips: float,
    conversion_price: float | None,
    fill_basis: str,
    slippage_pips_per_side: float | None,
    slippage_provenance: str,
    stress_multiplier: float = 1.0,
    day_count: int = 0,
    financing_cost_usd: float | None = None,
    financing_provenance: str = "unavailable",
    financing_note: str = "",
    added_commission_usd: float | None = None,
    added_commission_provenance: str = "unavailable",
    added_commission_note: str = "",
    package_choice: str = "conservative",
) -> RetailCost:
    """Build one explicit cost. Bid/ask fills cannot take a spread line."""
    pair = _symbol(symbol)
    if fill_basis not in {"bid_ask", "mid"}:
        raise ValueError("fill_basis must be 'bid_ask' or 'mid'")
    stop = _finite(stop_pips, name="stop_pips")
    if stop <= 0.0:
        raise ValueError("stop_pips must be positive")
    multiplier = _finite(stress_multiplier, name="stress_multiplier")
    if multiplier < 1.0:
        raise ValueError("stress multiplier cannot shrink a published cost")
    if isinstance(day_count, bool) or not isinstance(day_count, int) or day_count < 0:
        raise ValueError("day_count must be a non-negative integer")
    pip_value_usd(pair, units, conversion_price)

    missing: list[str] = []
    notes: list[str] = []
    if fill_basis == "mid" and added_commission_usd is not None:
        raise ValueError("a mid-price package already carries its own commission")
    if fill_basis == "mid":
        ic_lines, ic_missing = _package_lines(
            published_spreads(pair, account_type="Raw Spread, MetaTrader"),
            IC_MT4_RAW_COMMISSION,
            symbol=pair,
            units=units,
            stop_pips=stop,
            conversion_price=conversion_price,
            use_unlabeled_quote=False,
        )
        oanda_lines, oanda_missing = _package_lines(
            published_spreads(pair, account_type="spread-only"),
            OANDA_SPREAD_ONLY_COMMISSION,
            symbol=pair,
            units=units,
            stop_pips=stop,
            conversion_price=conversion_price,
            use_unlabeled_quote=True,
        )
        ic_r = None if ic_missing else sum(_line_r(line) for line in ic_lines)
        oanda_r = None if oanda_missing else sum(_line_r(line) for line in oanda_lines)
        if package_choice == "ic_raw":
            lines = ic_lines
            missing.extend(ic_missing)
            package = "IC Markets EU Raw Spread MetaTrader USD"
        elif package_choice == "oanda_spread_only":
            lines = oanda_lines
            missing.extend(oanda_missing)
            package = "OANDA US spread-only"
        elif package_choice != "conservative":
            raise ValueError("package_choice is not recognized")
        elif ic_r is None and oanda_r is None:
            missing.extend(ic_missing)
            lines = ic_lines
            package = "incomplete"
        elif oanda_r is None or (ic_r is not None and ic_r >= oanda_r):
            lines = ic_lines
            package = "IC Markets EU Raw Spread MetaTrader USD"
            notes.append("Conservative choice is the higher published package cost before slippage.")
        else:
            lines = oanda_lines
            package = "OANDA US spread-only"
            notes.append(
                "OANDA's single quote is higher than the IC average-plus-commission package. "
                "It is not labeled as an average on the page."
            )
    else:
        lines = [CostLine(
            "spread",
            "observed",
            0.0,
            0.0,
            0.0,
            "Bid/ask fill already contains the historical spread. It is not added again.",
        )]
        package = "historical bid/ask fill"
        if added_commission_usd is None:
            missing.append("commission")
            lines.append(CostLine(
                "commission",
                "unavailable",
                None,
                None,
                None,
                added_commission_note or "No commission figure was supplied. Zero is not assumed.",
            ))
        else:
            usd = _finite(added_commission_usd, name="added_commission_usd")
            if usd < 0.0:
                raise ValueError("commission usd must be non-negative")
            lines.append(CostLine(
                "commission",
                added_commission_provenance,
                None,
                usd,
                usd_to_r(usd, symbol=pair, units=units, stop_pips=stop, conversion_price=conversion_price),
                added_commission_note or "Added once. The spread was not added again.",
            ))

    if multiplier != 1.0:
        scaled: list[CostLine] = []
        for line in lines:
            if line.name == "spread" and line.pips is not None and line.r_multiple is not None:
                scaled.append(CostLine(
                    "spread",
                    "assumption",
                    line.pips * multiplier,
                    None if line.usd is None else line.usd * multiplier,
                    line.r_multiple * multiplier,
                    f"Stressed by an assumed multiplier of {multiplier:g}. Not an observed hour.",
                ))
            else:
                scaled.append(line)
        lines = scaled
        notes.append("Stress is an assumption applied to spread only. It is not a measured hourly curve.")

    if slippage_pips_per_side is None:
        missing.append("slippage")
        lines.append(CostLine(
            "slippage",
            "unavailable",
            None,
            None,
            None,
            "No broker page retrieved here publishes a typical slippage. Zero is not assumed.",
        ))
    else:
        per_side = _finite(slippage_pips_per_side, name="slippage_pips_per_side")
        if per_side < 0.0:
            raise ValueError("slippage pips must be non-negative")
        if slippage_provenance not in {"assumption", "observed", "published_specification"}:
            raise ValueError("slippage provenance is not recognized")
        round_trip = per_side * 2.0 * multiplier
        lines.append(CostLine(
            "slippage",
            "assumption" if multiplier != 1.0 else slippage_provenance,
            round_trip,
            round_trip * pip_value_usd(pair, units, conversion_price),
            pips_to_r(round_trip, stop),
            "Adverse on entry and on exit, matching the Phase 3 per-fill rule. "
            + ("Stress multiplier applied." if multiplier != 1.0 else "No stress multiplier."),
        ))

    if day_count == 0:
        lines.append(CostLine(
            "financing",
            "published_specification",
            None,
            0.0,
            0.0,
            "No 17:00 New York cutoff is crossed, so the published rollover charge is zero.",
        ))
    elif financing_cost_usd is None:
        missing.append("financing")
        lines.append(CostLine(
            "financing",
            "unavailable",
            None,
            None,
            None,
            financing_note or "A rollover is crossed and no usable financing rate was supplied.",
        ))
    else:
        usd = _finite(financing_cost_usd, name="financing_cost_usd")
        lines.append(CostLine(
            "financing",
            financing_provenance,
            None,
            usd,
            usd_to_r(usd, symbol=pair, units=units, stop_pips=stop, conversion_price=conversion_price),
            financing_note or "Positive financing is an account debit.",
        ))

    complete = not missing and all(line.r_multiple is not None for line in lines)
    cost_r = sum(line.r_multiple or 0.0 for line in lines) if complete else None
    return RetailCost(pair, fill_basis, complete, tuple(missing), tuple(lines), cost_r, package, tuple(notes))


def cost_for_timestamps(
    *,
    symbol: str,
    units: int,
    stop_pips: float,
    conversion_price: float | None,
    fill_basis: str,
    entry_utc: datetime,
    exit_utc: datetime,
    slippage_pips_per_side: float | None,
    slippage_provenance: str,
    triple_wednesday: bool = True,
    annual_rate: float | None = None,
    rate_provenance: str = "assumption",
    direction: Direction = Direction.LONG,
    stress_multiplier: float = 1.0,
    added_commission_usd: float | None = None,
    added_commission_provenance: str = "unavailable",
) -> RetailCost:
    """Apply the published 17:00 New York rollover to one hold.

    A weekend that is not covered by a Wednesday triple in the same hold is
    rejected. Holiday multipliers are not invented. EURUSD can use the
    published IC point table. Other pairs need an explicit annual rate.
    """
    if direction not in {Direction.LONG, Direction.SHORT}:
        raise ValueError("financing direction must be LONG or SHORT")
    if not financing_hold_is_identified(entry_utc, exit_utc):
        raise MissingCostError(
            "this hold crosses a weekend and does not include the Wednesday "
            "triple that the retrieved pages use to price that weekend"
        )
    days = rollover_day_count(entry_utc, exit_utc, triple_wednesday=triple_wednesday)
    financing: float | None
    provenance = "published_specification"
    note = "No cutoff was crossed."
    package_choice = "conservative"
    if days == 0:
        financing = 0.0
    elif symbol == "EURUSD" and annual_rate is None:
        financing = ic_eurusd_financing_cost_usd(
            long=direction is Direction.LONG,
            lots=units / STANDARD_LOT_UNITS,
            day_count=days,
        )
        note = (
            "IC Markets spreads-page points, converted at 1 USD per point per "
            "standard lot as in the EURUSD worked example. This financing stays "
            "on the IC package. OANDA's live annual rate was not on the retrieved page."
        )
        package_choice = "ic_raw"
    elif annual_rate is None:
        financing = None
        provenance = "unavailable"
        note = "Rollover is crossed and no financing rate was supplied."
    else:
        if conversion_price is None and symbol == "USDJPY":
            raise MissingCostError("USDJPY financing needs a conversion price")
        price = conversion_price if conversion_price is not None else 1.0
        if symbol in QUOTE_USD and conversion_price is None:
            raise MissingCostError("annual-rate financing needs the price used in the position value")
        financing = financing_cost_usd_from_annual_rate(symbol, units, price, annual_rate, days)
        provenance = rate_provenance
        note = "OANDA's signed formula, flipped so a positive amount is an account debit."
    return assemble_cost(
        symbol=symbol,
        units=units,
        stop_pips=stop_pips,
        conversion_price=conversion_price,
        fill_basis=fill_basis,
        slippage_pips_per_side=slippage_pips_per_side,
        slippage_provenance=slippage_provenance,
        stress_multiplier=stress_multiplier,
        day_count=days,
        financing_cost_usd=financing,
        financing_provenance=provenance,
        financing_note=note,
        added_commission_usd=added_commission_usd,
        added_commission_provenance=added_commission_provenance,
        package_choice=package_choice,
    )


def reject_spread_on_bid_ask(spread_pips: float) -> None:
    pips = _finite(spread_pips, name="spread_pips")
    if pips > 0.0:
        raise DoubleCountedSpreadError(
            "the bid/ask fill already includes the spread; do not add it again"
        )
    if pips < 0.0:
        raise ValueError("spread pips must be non-negative")


def outcomes_at_cost(
    *,
    reward_to_risk: float,
    gross_edge_r: float,
    cost_r: float,
    risk_fraction: float,
    trades: int,
) -> dict[str, float | str | None]:
    """Map one labeled round-trip cost into the existing exact lattice.

    The payoff is hypothetical. Gross edge is held fixed, so a higher cost
    lowers net expectancy and does not invent a new win rate.
    """
    payoff = BinaryPayoff(reward_to_risk, 0.0, gross_edge_r).with_cost(
        cost_r, gross_edge_r=gross_edge_r
    )
    result = exact_binary_outcomes(payoff, FixedFractionalSizing(risk_fraction), trades)
    return {
        "net_expectancy_r": payoff.net_edge_r,
        "probability_end_at_least_double": result.end_at_least_double,
        "probability_lose_at_least_half": result.lose_at_least_half,
        "probability_lose_at_least_ninety": result.lose_at_least_ninety,
        "median_terminal_multiple": result.median_terminal_multiple,
        "expected_log_growth": result.expected_log_growth,
        "log_growth_per_trade": result.log_growth_per_trade,
        "evidence_basis": payoff.evidence_basis,
    }


def zero_edge_is_not_rescued_by_sizing(
    *,
    reward_to_risk: float,
    cost_r: float,
    trades: int,
    risk_fractions: tuple[float, ...] = (0.0025, 0.04, 0.15),
) -> tuple[dict[str, float], ...]:
    """A non-positive gross edge stays non-positive at every fixed fraction."""
    rows = []
    for fraction in risk_fractions:
        outcome = outcomes_at_cost(
            reward_to_risk=reward_to_risk,
            gross_edge_r=0.0,
            cost_r=cost_r,
            risk_fraction=fraction,
            trades=trades,
        )
        growth = log_growth_per_trade(
            BinaryPayoff(reward_to_risk, cost_r, -cost_r),
            FixedFractionalSizing(fraction),
        )
        rows.append({
            "risk_fraction": fraction,
            "net_expectancy_r": float(outcome["net_expectancy_r"]),
            "expected_terminal_multiple": exact_binary_outcomes(
                BinaryPayoff(reward_to_risk, cost_r, -cost_r),
                FixedFractionalSizing(fraction),
                trades,
            ).expected_terminal_multiple,
            "log_growth_per_trade": growth,
        })
    return tuple(rows)


def phase7_documented_revaluation() -> dict[str, object]:
    """Re-read the published Phase 7 aggregates. Do not invent trade records.

    The 0.2, 0.5, and 1.0 pip columns already include the historical bid/ask
    spread and that per-side adverse slippage, with zero commission and zero
    financing. They are aggregate dollars. They do not identify the payoff
    ratio, the win rate, or the dependence, so the lattice probabilities are
    not estimates for this strategy.
    """
    inputs = documented_phase7_monthly_inputs()
    reject_spread_on_bid_ask(0.0)
    return {
        "candidate": inputs["candidate"],
        "experiment_id": inputs["experiment_id"],
        "evidence_basis": inputs["evidence_basis"],
        "reliable_probability_estimate": False,
        "probability_blocker": (
            "Stage 2 reports 199 trades and three aggregate expectancies. "
            "It does not report the trade-level R series, the reward-to-risk "
            "distribution, or the overnight share. A doubling or loss probability "
            "would require those records."
        ),
        "fill_basis": "bid_ask",
        "spread_already_in_result": True,
        "stage2_mean_r_estimate": inputs["stage2_mean_r_estimate"],
        "stage2_expectancy_usd": {0.2: 3.8054, 0.5: 1.3175, 1.0: -2.8247},
        "dollars_per_1r_at_window_start": inputs["dollars_per_1r_at_window_start"],
        "edge_first_candidate_for_doubling": False,
        "edge_first_reason": inputs["edge_first_reason"],
        "incremental_commission_r": None,
        "incremental_financing_r": None,
        "incremental_blocker": (
            "Commission and financing in R need the stop distance and the hold. "
            "Those are not in the aggregate evidence. A 15-pip stop is not assumed."
        ),
        "holdout_note": inputs["holdout_note"],
    }


def hypothetical_cost_sensitivity(
    *,
    symbol: str = "EURUSD",
    units: int = STANDARD_LOT_UNITS,
    stop_pips: float = 15.0,
    conversion_price: float | None = None,
    reward_to_risk: float = 1.5,
    gross_edge_r: float = 0.005 + STUDY_COST_R,
    risk_fraction: float = 0.04,
    trades: int = 60,
) -> tuple[dict[str, object], ...]:
    """Study-sized hypothetical only. The gross edge is not a Phase 7 measurement."""
    pair = _symbol(symbol)
    rows: list[dict[str, object]] = []
    specs: tuple[tuple[str, float | None, float | None], ...] = (
        ("study_1.2_pip_round_trip_assumption", 0.0, STUDY_COST_R),
        ("published_intraday_no_slippage_assumption", 0.0, None),
        ("published_plus_0.5_pip_per_side_assumption", 0.5, None),
        ("published_plus_0.5_pip_and_2x_stress_assumption", 0.5, None),
    )
    for label, slippage, fixed_cost in specs:
        multiplier = 2.0 if "2x_stress" in label else 1.0
        if fixed_cost is not None:
            cost_r = fixed_cost
            package = "study assumption, not a broker page"
            complete = True
        else:
            assessment = assemble_cost(
                symbol=pair,
                units=units,
                stop_pips=stop_pips,
                conversion_price=conversion_price,
                fill_basis="mid",
                slippage_pips_per_side=slippage,
                slippage_provenance="assumption",
                stress_multiplier=multiplier,
                day_count=0,
            )
            cost_r = assessment.require_complete()
            package = assessment.package
            complete = assessment.complete
        outcome = outcomes_at_cost(
            reward_to_risk=reward_to_risk,
            gross_edge_r=gross_edge_r,
            cost_r=cost_r,
            risk_fraction=risk_fraction,
            trades=trades,
        )
        rows.append({
            "label": label,
            "package": package,
            "complete": complete,
            "cost_r": cost_r,
            "hypothetical": True,
            "phase7_probability_estimate": False,
            **outcome,
        })
    return tuple(rows)
