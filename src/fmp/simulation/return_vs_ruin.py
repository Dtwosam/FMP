"""Deterministic return-versus-ruin calculations for a fixed sizing policy.

The calculator answers a narrow question: given a trade distribution, a cost
assumption, and a fixed fraction of equity risked on every trade, what are the
chances of doubling, of large losses, and of ending below the start over a
stated number of trades. It does not search leverage, martingale, or recovery
rules, and a result here is not trading authorization.

The 17 November 2026 feasibility study's script ``fmpsim.py`` was not in the
PDF. The binary model below is the independent reconstruction of the formulas
and scenario table in that study. ESMA leverage, margin close-out, and
negative-balance protection are optional account assumptions. They are not
applied unless the caller sets them.
"""

from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date

_DOUBLE = 2.0
_HALF = 0.5
_TEN_PERCENT = 0.1
_PROBABILITY_FIELDS = (
    "end_at_least_double",
    "touch_double",
    "lose_at_least_half",
    "lose_at_least_ninety",
    "account_exhausted",
    "end_below_start",
)


def _finite(value: float, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def _positive(value: float, *, name: str) -> float:
    number = _finite(value, name=name)
    if number <= 0:
        raise ValueError(f"{name} must be positive")
    return number


def _probability(value: float, *, name: str) -> float:
    number = _finite(value, name=name)
    if number < 0 or number > 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return number


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _inverse_normal_cdf(p: float) -> float:
    """Acklam's rational approximation of the standard-normal quantile."""
    if p <= 0.0 or p >= 1.0:
        raise ValueError("normal quantile requires a probability strictly between 0 and 1")
    a = (
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    )
    b = (
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    )
    c = (
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    )
    d = (
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    )
    plow = 0.02425
    phigh = 1.0 - plow
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )
    if p > phigh:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )
    q = p - 0.5
    r = q * q
    return (
        (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5])
        * q
        / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    )


@dataclass(frozen=True, slots=True)
class BinaryPayoff:
    """One-trade payoff in R units.

    A win pays ``+reward_to_risk`` before cost. A loss pays ``-1`` before cost.
    Round-trip cost is subtracted from the win and added to the loss. Net
    expectancy is::

        mu = p * b - (1 - p) - c

    which is the same quantity as ``p * (b - c) - (1 - p) * (1 + c)``.
    ``evidence_basis`` records whether those inputs are a hypothetical
    assumption or a summary of a supplied record. This object does not load
    market data.
    """

    reward_to_risk: float
    cost_r: float
    net_edge_r: float
    evidence_basis: str = "hypothetical_distribution"

    def __post_init__(self) -> None:
        reward = _positive(self.reward_to_risk, name="reward_to_risk")
        cost = _finite(self.cost_r, name="cost_r")
        edge = _finite(self.net_edge_r, name="net_edge_r")
        if cost < 0:
            raise ValueError("cost_r must be non-negative")
        if reward <= cost:
            raise ValueError("reward_to_risk must exceed cost_r so a win still gains")
        if self.evidence_basis not in {
            "hypothetical_distribution",
            "supplied_trade_record",
        }:
            raise ValueError("evidence_basis is not recognized")
        object.__setattr__(self, "reward_to_risk", reward)
        object.__setattr__(self, "cost_r", cost)
        object.__setattr__(self, "net_edge_r", edge)
        probability = self.win_probability()
        if probability <= 0.0 or probability >= 1.0:
            raise ValueError("net edge, payoff and cost imply a win probability outside (0, 1)")

    def win_probability(self) -> float:
        return (self.net_edge_r + 1.0 + self.cost_r) / (self.reward_to_risk + 1.0)

    def with_net_edge(self, net_edge_r: float) -> BinaryPayoff:
        return BinaryPayoff(
            reward_to_risk=self.reward_to_risk,
            cost_r=self.cost_r,
            net_edge_r=net_edge_r,
            evidence_basis=self.evidence_basis,
        )

    def with_cost(self, cost_r: float, *, gross_edge_r: float) -> BinaryPayoff:
        """Hold the gross edge fixed and change the round-trip cost.

        Net edge becomes ``gross_edge_r - cost_r``. Use this for cost
        sensitivity. Do not pass an already-net edge as ``gross_edge_r``.
        """
        return BinaryPayoff(
            reward_to_risk=self.reward_to_risk,
            cost_r=cost_r,
            net_edge_r=gross_edge_r - cost_r,
            evidence_basis=self.evidence_basis,
        )


@dataclass(frozen=True, slots=True)
class FixedFractionalSizing:
    """Risk a fixed fraction of current equity on every trade.

    The fraction does not rise after a loss. There is no martingale, averaging,
    or replenishment parameter.
    """

    risk_fraction: float

    def __post_init__(self) -> None:
        fraction = _positive(self.risk_fraction, name="risk_fraction")
        if fraction >= 1.0:
            raise ValueError("risk_fraction must be below 1")
        object.__setattr__(self, "risk_fraction", fraction)


@dataclass(frozen=True, slots=True)
class AccountAssumptions:
    """Broker and jurisdiction assumptions.

    Leave a field unset to skip that constraint. European retail rules are not
    the default. ``max_leverage`` is reported and, when a margin close-out is
    also set, used as a liquidation floor. It is never used to search for a
    larger position.
    """

    negative_balance_protection: bool = False
    ruined_equity_fraction: float = 0.01
    max_leverage: float | None = None
    stop_price_fraction: float | None = None
    margin_closeout_ratio: float | None = None
    label: str = "unconstrained"

    def __post_init__(self) -> None:
        ruined = _probability(self.ruined_equity_fraction, name="ruined_equity_fraction")
        if ruined <= 0.0:
            raise ValueError("ruined_equity_fraction must be positive")
        object.__setattr__(self, "ruined_equity_fraction", ruined)
        if self.max_leverage is not None:
            object.__setattr__(self, "max_leverage", _positive(self.max_leverage, name="max_leverage"))
        if self.stop_price_fraction is not None:
            stop = _positive(self.stop_price_fraction, name="stop_price_fraction")
            if stop >= 1.0:
                raise ValueError("stop_price_fraction must be below 1")
            object.__setattr__(self, "stop_price_fraction", stop)
        if self.margin_closeout_ratio is not None:
            ratio = _positive(self.margin_closeout_ratio, name="margin_closeout_ratio")
            if ratio >= 1.0:
                raise ValueError("margin_closeout_ratio must be below 1")
            object.__setattr__(self, "margin_closeout_ratio", ratio)
            if self.max_leverage is None or self.stop_price_fraction is None:
                raise ValueError("margin close-out requires max_leverage and stop_price_fraction")
        if not self.label.strip():
            raise ValueError("account label must be non-empty")


@dataclass(frozen=True, slots=True)
class DependenceModel:
    """Illustrative dependence, gap, and cost-noise assumptions.

    These parameters reconstruct the 17 November 2026 stress table. They are
    not estimates from FMP's trade record. The regime updates once per group
    of trades. A group of three is the study's cross-pair block: one shared
    normal factor with the stated correlation, then independent residuals.
    """

    regime_shift: float = 0.08
    regime_stay_probability: float = 0.97
    group_size: int = 3
    group_correlation: float = 0.5
    gap_probability: float = 0.005
    gap_pareto_alpha: float = 1.5
    gap_cap_r: float = 20.0
    cost_log_sigma: float = 0.5
    cost_noise_mean_preserving: bool = True
    regime_clock: str = "per_group"

    def __post_init__(self) -> None:
        shift = _finite(self.regime_shift, name="regime_shift")
        if shift < 0.0 or shift >= 0.5:
            raise ValueError("regime_shift must be in [0, 0.5)")
        stay = _probability(self.regime_stay_probability, name="regime_stay_probability")
        if stay <= 0.0:
            raise ValueError("regime_stay_probability must be positive")
        if isinstance(self.group_size, bool) or not isinstance(self.group_size, int) or self.group_size < 1:
            raise ValueError("group_size must be a positive integer")
        corr = _probability(self.group_correlation, name="group_correlation")
        gap_p = _probability(self.gap_probability, name="gap_probability")
        alpha = _positive(self.gap_pareto_alpha, name="gap_pareto_alpha")
        cap = _positive(self.gap_cap_r, name="gap_cap_r")
        if cap < 1.0:
            raise ValueError("gap_cap_r must be at least 1R")
        sigma = _finite(self.cost_log_sigma, name="cost_log_sigma")
        if sigma < 0.0:
            raise ValueError("cost_log_sigma must be non-negative")
        if self.regime_clock not in {"per_group", "per_trade"}:
            raise ValueError("regime_clock must be 'per_group' or 'per_trade'")
        object.__setattr__(self, "regime_shift", shift)
        object.__setattr__(self, "regime_stay_probability", stay)
        object.__setattr__(self, "group_correlation", corr)
        object.__setattr__(self, "gap_probability", gap_p)
        object.__setattr__(self, "gap_pareto_alpha", alpha)
        object.__setattr__(self, "gap_cap_r", cap)
        object.__setattr__(self, "cost_log_sigma", sigma)


@dataclass(frozen=True, slots=True)
class RuinProbabilities:
    """Outcome probabilities for one stated trade count, interpreted by the caller as one window."""

    end_at_least_double: float
    touch_double: float
    lose_at_least_half: float
    lose_at_least_ninety: float
    account_exhausted: float
    end_below_start: float
    median_terminal_multiple: float
    expected_terminal_multiple: float
    expected_log_growth: float
    log_growth_per_trade: float | None
    mean_max_drawdown: float | None
    max_drawdown_p50: float | None
    max_drawdown_p95: float | None
    effective_leverage: float | None
    leverage_cap_exceeded: bool | None
    method: str
    evidence_basis: str
    standard_errors: Mapping[str, float]
    wilson_intervals: Mapping[str, tuple[float, float]]
    paths: int | None
    seed: int | None
    account_label: str

    def as_dict(self) -> dict[str, object]:
        return {
            "end_at_least_double": self.end_at_least_double,
            "touch_double": self.touch_double,
            "lose_at_least_half": self.lose_at_least_half,
            "lose_at_least_ninety": self.lose_at_least_ninety,
            "account_exhausted": self.account_exhausted,
            "end_below_start": self.end_below_start,
            "median_terminal_multiple": self.median_terminal_multiple,
            "expected_terminal_multiple": self.expected_terminal_multiple,
            "expected_log_growth": self.expected_log_growth,
            "log_growth_per_trade": self.log_growth_per_trade,
            "mean_max_drawdown": self.mean_max_drawdown,
            "max_drawdown_p50": self.max_drawdown_p50,
            "max_drawdown_p95": self.max_drawdown_p95,
            "effective_leverage": self.effective_leverage,
            "leverage_cap_exceeded": self.leverage_cap_exceeded,
            "method": self.method,
            "evidence_basis": self.evidence_basis,
            "standard_errors": dict(self.standard_errors),
            "paths": self.paths,
            "seed": self.seed,
            "account_label": self.account_label,
        }


@dataclass(frozen=True, slots=True)
class EdgeVarianceSplit:
    """Same sizing, frequency, payoff, and execution; only the net edge changes."""

    strategy: RuinProbabilities
    zero_edge: RuinProbabilities

    @property
    def doubling_probability_difference(self) -> float:
        return self.strategy.end_at_least_double - self.zero_edge.end_at_least_double

    @property
    def log_growth_difference(self) -> float:
        return self.strategy.expected_log_growth - self.zero_edge.expected_log_growth


@dataclass(frozen=True, slots=True)
class StudyScenario:
    """One hypothetical row from the 17 November 2026 scenario table."""

    scenario_id: str
    name: str
    net_edge_r: float
    reward_to_risk: float
    risk_fraction: float
    trades_per_window: int
    evidence_basis: str = "hypothetical_distribution"


STUDY_COST_R = 0.08
STUDY_SCENARIOS: tuple[StudyScenario, ...] = (
    StudyScenario("S1", "No gross edge, pays the stated cost", -0.08, 1.0, 0.02, 60),
    StudyScenario("S2", "Zero net edge at 4% risk", 0.0, 1.0, 0.04, 60),
    StudyScenario("S3", "Zero net edge at 15% risk", 0.0, 1.0, 0.15, 20),
    StudyScenario("S4", "Zero net edge, lottery sizing", 0.0, 2.0, 0.30, 6),
    StudyScenario("S5", "Rounded FMP-sized edge at policy risk", 0.005, 1.5, 0.0025, 60),
    StudyScenario("S6", "Rounded FMP-sized edge at 4% risk", 0.005, 1.5, 0.04, 60),
    StudyScenario("S7", "Hypothetical +0.05R", 0.05, 1.5, 0.04, 120),
    StudyScenario("S8", "Hypothetical +0.10R", 0.10, 1.5, 0.04, 120),
    StudyScenario("S9", "Hypothetical +0.10R above the stated cap", 0.10, 1.5, 0.08, 120),
    StudyScenario("S10", "Hypothetical +0.20R", 0.20, 2.0, 0.04, 200),
    StudyScenario("S11", "Hypothetical -0.05R at aggressive size", -0.05, 2.0, 0.10, 40),
)


def study_stress_dependence() -> DependenceModel:
    """Dependence settings that reconstruct the study's stress table."""
    return DependenceModel()


# Printed study figures. They are the comparison target, not inputs to the calculator.
# Columns: P(end>=2x), P(touch 2x), P(lose>=50%), P(lose>=90%), P(account lost),
# P(end<start), median terminal multiple.
STUDY_PUBLISHED_EXACT: dict[str, tuple[float, float, float, float, float, float, float]] = {
    "S1": (0.00, 0.00, 0.01, 0.0, 0.0, 74.1, 0.90),
    "S2": (0.8, 1.4, 2.0, 0.00, 0.0, 50.9, 0.92),
    "S3": (11.2, 17.9, 27.9, 0.2, 0.0, 62.1, 0.84),
    "S4": (12.9, 22.4, 30.1, 6.9, 0.0, 62.7, 0.52),
    "S5": (0.0, 0.0, 0.0, 0.0, 0.0, 44.6, 1.00),
    "S6": (2.7, 4.7, 4.3, 0.00, 0.0, 55.0, 0.94),
    "S7": (12.6, 23.4, 7.7, 0.00, 0.00, 44.7, 1.07),
    "S8": (24.0, 37.6, 3.1, 0.00, 0.00, 28.3, 1.44),
    "S9": (36.6, 61.1, 17.4, 0.8, 0.00, 34.8, 1.55),
    "S10": (75.5, 85.7, 0.8, 0.00, 0.00, 6.0, 3.36),
    "S11": (5.9, 20.2, 47.6, 1.5, 0.0, 72.5, 0.60),
}
STUDY_PUBLISHED_STRESS: dict[str, tuple[float, float, float, float, float, float, float]] = {
    "S1": (0.02, 0.02, 0.9, 0.0, 0.0, 65.3, 0.90),
    "S2": (7.4, 10.6, 11.6, 0.02, 0.00, 53.5, 0.94),
    "S3": (20.3, 31.1, 34.8, 2.0, 0.1, 58.2, 0.83),
    "S4": (19.8, 30.6, 41.7, 14.8, 0.2, 59.8, 0.52),
    "S5": (0.0, 0.0, 0.0, 0.0, 0.0, 50.3, 1.00),
    "S6": (12.1, 17.9, 16.7, 0.04, 0.0, 54.2, 0.93),
    "S7": (27.0, 40.0, 23.5, 0.5, 0.00, 48.1, 1.07),
    "S8": (35.4, 48.5, 16.3, 0.2, 0.00, 38.7, 1.36),
    "S9": (42.5, 63.9, 31.9, 9.6, 0.8, 43.8, 1.33),
    "S10": (62.1, 76.5, 11.6, 0.9, 0.00, 23.0, 3.32),
    "S11": (16.5, 34.6, 50.2, 10.1, 0.2, 65.8, 0.48),
}


def risk_fraction_at_stop(*, leverage: float, stop_price_fraction: float) -> float:
    """Equity fraction lost if a stop at ``stop_price_fraction`` is hit at ``leverage``.

    Ten EUR/USD pips are 0.001 of price. At 30:1 that is 3.0% of equity. The
    feasibility study text says 2.7% for that case. This function does not
    apply that unpublished haircut. The study's scenario rows use explicit
    risk fractions rather than the 2.7% figure.
    """
    return _positive(leverage, name="leverage") * _positive(
        stop_price_fraction, name="stop_price_fraction"
    )


def _leverage_report(
    sizing: FixedFractionalSizing,
    account: AccountAssumptions,
) -> tuple[float | None, bool | None]:
    if account.stop_price_fraction is None:
        return None, None
    leverage = sizing.risk_fraction / account.stop_price_fraction
    if account.max_leverage is None:
        return leverage, None
    return leverage, leverage > account.max_leverage + 1e-12


def kelly_fraction(payoff: BinaryPayoff) -> float:
    """Fixed fraction that maximizes expected log growth for this payoff.

    For an even-money payoff and zero extra cost, this equals the net edge.
    A non-positive edge returns 0. The result is a research reference. It is
    not applied unless the caller passes it as the sizing fraction.
    """
    if payoff.net_edge_r <= 0.0:
        return 0.0
    denominator = (payoff.reward_to_risk - payoff.cost_r) * (1.0 + payoff.cost_r)
    fraction = payoff.net_edge_r / denominator
    ruin_limit = 1.0 / (1.0 + payoff.cost_r)
    return min(fraction, ruin_limit * (1.0 - 1e-12))


def log_growth_per_trade(payoff: BinaryPayoff, sizing: FixedFractionalSizing) -> float:
    """Expected log equity change of one independent trade at the fixed fraction."""
    probability = payoff.win_probability()
    win_factor, loss_factor = _base_factors(payoff, sizing)
    if loss_factor <= 0.0 or win_factor <= 0.0:
        return float("-inf")
    return probability * math.log(win_factor) + (1.0 - probability) * math.log(loss_factor)


def _base_factors(payoff: BinaryPayoff, sizing: FixedFractionalSizing) -> tuple[float, float]:
    win_factor = 1.0 + sizing.risk_fraction * (payoff.reward_to_risk - payoff.cost_r)
    loss_factor = 1.0 - sizing.risk_fraction * (1.0 + payoff.cost_r)
    return win_factor, loss_factor


def _binomial_probabilities(n_trades: int, win_probability: float) -> list[float]:
    probabilities = [1.0]
    loss_probability = 1.0 - win_probability
    for _ in range(n_trades):
        nxt = [0.0] * (len(probabilities) + 1)
        for wins, mass in enumerate(probabilities):
            nxt[wins] += mass * loss_probability
            nxt[wins + 1] += mass * win_probability
        probabilities = nxt
    return probabilities


def _equity_after(wins: int, trades: int, log_win: float, log_loss: float) -> float:
    return math.exp(wins * log_win + (trades - wins) * log_loss)


def _sample_median(sorted_values: Sequence[float]) -> float:
    if not sorted_values:
        raise ValueError("cannot take a median of an empty sample")
    return sorted_values[len(sorted_values) // 2]


def _empirical_quantile(sorted_values: Sequence[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("cannot take a quantile of an empty sample")
    index = math.ceil(q * len(sorted_values)) - 1
    return sorted_values[min(len(sorted_values) - 1, max(0, index))]


def _wilson_interval(successes: int, paths: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if paths <= 0:
        raise ValueError("paths must be positive")
    phat = successes / paths
    z2 = z * z
    denom = 1.0 + z2 / paths
    centre = (phat + z2 / (2.0 * paths)) / denom
    half = z * math.sqrt(phat * (1.0 - phat) / paths + z2 / (4.0 * paths * paths)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def _proportion_se(probability: float, paths: int) -> float:
    return math.sqrt(probability * (1.0 - probability) / paths)


def _require_trades(n_trades: int) -> int:
    if isinstance(n_trades, bool) or not isinstance(n_trades, int) or n_trades <= 0:
        raise ValueError("n_trades must be a positive integer")
    return n_trades


def _terminal_flags(equity: float, ruined_equity_fraction: float) -> dict[str, bool]:
    return {
        "end_at_least_double": equity >= _DOUBLE,
        "lose_at_least_half": equity <= _HALF,
        "lose_at_least_ninety": equity <= _TEN_PERCENT,
        "account_exhausted": equity <= ruined_equity_fraction,
        "end_below_start": equity < 1.0,
    }


def exact_binary_outcomes(
    payoff: BinaryPayoff,
    sizing: FixedFractionalSizing,
    n_trades: int,
    account: AccountAssumptions | None = None,
) -> RuinProbabilities:
    """Exact independent-trade distribution.

    Terminal probabilities are the binomial distribution of win counts.
    Touching twice starting equity is the exact path probability from a
    dynamic program on ``(trades completed, wins so far)``, which fixes
    equity. Loss probabilities are terminal, matching the study table.
    Max drawdown is path-dependent beyond that state, so it is left unset.
    """
    account = account or AccountAssumptions()
    n_trades = _require_trades(n_trades)
    probability = payoff.win_probability()
    win_factor, loss_factor = _base_factors(payoff, sizing)
    if win_factor <= 0.0:
        raise ValueError("win factor must be positive")
    leverage, cap_exceeded = _leverage_report(sizing, account)
    per_trade_log = log_growth_per_trade(payoff, sizing)

    if loss_factor <= 0.0:
        return _exact_when_one_loss_exhausts(
            payoff=payoff,
            sizing=sizing,
            n_trades=n_trades,
            account=account,
            win_factor=win_factor,
            per_trade_log=per_trade_log,
            leverage=leverage,
            cap_exceeded=cap_exceeded,
        )

    log_win = math.log(win_factor)
    log_loss = math.log(loss_factor)
    masses = _binomial_probabilities(n_trades, probability)
    counts = {name: 0.0 for name in _PROBABILITY_FIELDS if name != "touch_double"}
    expected_terminal = 0.0
    expected_log = 0.0
    atoms: list[tuple[float, float]] = []
    for wins, mass in enumerate(masses):
        equity = _equity_after(wins, n_trades, log_win, log_loss)
        atoms.append((equity, mass))
        flags = _terminal_flags(equity, account.ruined_equity_fraction)
        for name, flag in flags.items():
            if flag:
                counts[name] += mass
        expected_terminal += mass * equity
        expected_log += mass * math.log(equity)
    atoms.sort()
    cdf = 0.0
    median = atoms[-1][0]
    for equity, mass in atoms:
        cdf += mass
        if cdf >= 0.5:
            median = equity
            break
    touch = _touch_probability(n_trades, probability, log_win, log_loss)
    return RuinProbabilities(
        end_at_least_double=counts["end_at_least_double"],
        touch_double=touch,
        lose_at_least_half=counts["lose_at_least_half"],
        lose_at_least_ninety=counts["lose_at_least_ninety"],
        account_exhausted=counts["account_exhausted"],
        end_below_start=counts["end_below_start"],
        median_terminal_multiple=median,
        expected_terminal_multiple=expected_terminal,
        expected_log_growth=expected_log,
        log_growth_per_trade=per_trade_log,
        mean_max_drawdown=None,
        max_drawdown_p50=None,
        max_drawdown_p95=None,
        effective_leverage=leverage,
        leverage_cap_exceeded=cap_exceeded,
        method="exact_independent_binomial",
        evidence_basis=payoff.evidence_basis,
        standard_errors={name: 0.0 for name in _PROBABILITY_FIELDS},
        wilson_intervals={},
        paths=None,
        seed=None,
        account_label=account.label,
    )


def _exact_when_one_loss_exhausts(
    *,
    payoff: BinaryPayoff,
    sizing: FixedFractionalSizing,
    n_trades: int,
    account: AccountAssumptions,
    win_factor: float,
    per_trade_log: float,
    leverage: float | None,
    cap_exceeded: bool | None,
) -> RuinProbabilities:
    """A single full loss cannot leave positive equity.

    The account stops on the first loss. Doubling is possible only on an
    unbroken prefix of wins. Negative-balance protection floors a negative
    loss at zero.
    """
    probability = payoff.win_probability()
    loss_probability = 1.0 - probability
    _win_factor, loss_factor = _base_factors(payoff, sizing)
    atoms: list[tuple[float, float]] = []
    equity = 1.0
    survival = 1.0
    for _ in range(n_trades):
        terminal = equity * loss_factor
        if account.negative_balance_protection and terminal < 0.0:
            terminal = 0.0
        atoms.append((terminal, survival * loss_probability))
        equity *= win_factor
        survival *= probability
    atoms.append((equity, survival))
    counts = {name: 0.0 for name in _PROBABILITY_FIELDS if name != "touch_double"}
    expected_terminal = 0.0
    expected_log = 0.0
    log_defined = True
    for terminal, mass in atoms:
        flags = _terminal_flags(terminal, account.ruined_equity_fraction)
        for name, flag in flags.items():
            if flag:
                counts[name] += mass
        expected_terminal += mass * terminal
        if terminal > 0.0:
            expected_log += mass * math.log(terminal)
        elif mass > 0.0:
            log_defined = False
    ordered = sorted(atoms)
    cdf = 0.0
    median = ordered[-1][0]
    for terminal, mass in ordered:
        cdf += mass
        if cdf >= 0.5:
            median = terminal
            break
    running = 1.0
    touch = 0.0
    for wins in range(1, n_trades + 1):
        running *= win_factor
        if running >= _DOUBLE:
            touch = probability**wins
            break
    return RuinProbabilities(
        end_at_least_double=counts["end_at_least_double"],
        touch_double=touch,
        lose_at_least_half=counts["lose_at_least_half"],
        lose_at_least_ninety=counts["lose_at_least_ninety"],
        account_exhausted=counts["account_exhausted"],
        end_below_start=counts["end_below_start"],
        median_terminal_multiple=median,
        expected_terminal_multiple=expected_terminal,
        expected_log_growth=expected_log if log_defined else float("-inf"),
        log_growth_per_trade=per_trade_log,
        mean_max_drawdown=None,
        max_drawdown_p50=None,
        max_drawdown_p95=None,
        effective_leverage=leverage,
        leverage_cap_exceeded=cap_exceeded,
        method="exact_independent_binomial_loss_exhausts",
        evidence_basis=payoff.evidence_basis,
        standard_errors={name: 0.0 for name in _PROBABILITY_FIELDS},
        wilson_intervals={},
        paths=None,
        seed=None,
        account_label=account.label,
    )


def _touch_probability(n_trades: int, win_probability: float, log_win: float, log_loss: float) -> float:
    untouched = [0.0] * (n_trades + 1)
    untouched[0] = 1.0
    touch = 0.0
    loss_probability = 1.0 - win_probability
    for trades in range(n_trades):
        nxt = [0.0] * (n_trades + 1)
        for wins, mass in enumerate(untouched):
            if mass == 0.0:
                continue
            equity_win = math.exp((wins + 1) * log_win + (trades - wins) * log_loss)
            if equity_win >= _DOUBLE:
                touch += mass * win_probability
            else:
                nxt[wins + 1] += mass * win_probability
            equity_loss = math.exp(wins * log_win + (trades + 1 - wins) * log_loss)
            if equity_loss >= _DOUBLE:
                touch += mass * loss_probability
            else:
                nxt[wins] += mass * loss_probability
        untouched = nxt
    return touch


def _closeout_equity(
    equity_before: float,
    sizing: FixedFractionalSizing,
    account: AccountAssumptions,
) -> float | None:
    if (
        account.margin_closeout_ratio is None
        or account.max_leverage is None
        or account.stop_price_fraction is None
    ):
        return None
    leverage = sizing.risk_fraction / account.stop_price_fraction
    margin_fraction = leverage / account.max_leverage
    return equity_before * account.margin_closeout_ratio * margin_fraction


def apply_net_r_path(
    net_r_multiples: Sequence[float],
    sizing: FixedFractionalSizing,
    account: AccountAssumptions | None = None,
) -> dict[str, float | bool]:
    """Apply a supplied net-R path at a fixed fraction.

    Each value is already net of the costs the caller wants charged. This
    function does not add another cost.
    """
    account = account or AccountAssumptions()
    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0
    touched = False
    halted = False
    for raw in net_r_multiples:
        r_multiple = _finite(raw, name="net R")
        if halted:
            break
        equity, halted, step_drawdown, step_peak, step_touch = _step_equity(
            equity=equity,
            peak=peak,
            multiplier=1.0 + sizing.risk_fraction * r_multiple,
            sizing=sizing,
            account=account,
        )
        peak = step_peak
        if step_drawdown > max_drawdown:
            max_drawdown = step_drawdown
        touched = touched or step_touch
    flags = _terminal_flags(equity, account.ruined_equity_fraction)
    return {
        "terminal_multiple": equity,
        "max_drawdown": max_drawdown,
        "touched_double": touched,
        "halted": halted,
        **flags,
    }


def _step_equity(
    *,
    equity: float,
    peak: float,
    multiplier: float,
    sizing: FixedFractionalSizing,
    account: AccountAssumptions,
) -> tuple[float, bool, float, float, bool]:
    if not math.isfinite(multiplier):
        raise ValueError("equity multiplier must be finite")
    nxt = equity * multiplier
    halted = False
    floor = _closeout_equity(equity, sizing, account)
    if floor is not None and nxt < floor:
        nxt = floor
        halted = True
    if account.negative_balance_protection and nxt < 0.0:
        nxt = 0.0
        halted = True
    elif nxt < 0.0:
        halted = True
    if nxt > peak:
        peak = nxt
    drawdown = 0.0 if peak <= 0.0 else (peak - nxt) / peak
    return nxt, halted, drawdown, peak, nxt >= _DOUBLE


def _summarize_paths(
    *,
    terminals: list[float],
    drawdowns: list[float],
    touch_count: int,
    method: str,
    evidence_basis: str,
    seed: int,
    account: AccountAssumptions,
    sizing: FixedFractionalSizing,
    log_growth_reference: float | None,
) -> RuinProbabilities:
    paths = len(terminals)
    if paths == 0:
        raise ValueError("paths must be positive")
    counts = {name: 0 for name in _PROBABILITY_FIELDS if name != "touch_double"}
    expected_terminal = 0.0
    expected_log = 0.0
    log_defined = True
    for equity in terminals:
        flags = _terminal_flags(equity, account.ruined_equity_fraction)
        for name, flag in flags.items():
            if flag:
                counts[name] += 1
        expected_terminal += equity
        if equity > 0.0:
            expected_log += math.log(equity)
        else:
            log_defined = False
    ordered = sorted(terminals)
    ordered_dd = sorted(drawdowns)
    probabilities = {name: counts[name] / paths for name in counts}
    probabilities["touch_double"] = touch_count / paths
    errors = {name: _proportion_se(probabilities[name], paths) for name in _PROBABILITY_FIELDS}
    intervals = {
        name: _wilson_interval(counts[name] if name != "touch_double" else touch_count, paths)
        for name in _PROBABILITY_FIELDS
    }
    leverage, cap_exceeded = _leverage_report(sizing, account)
    return RuinProbabilities(
        end_at_least_double=probabilities["end_at_least_double"],
        touch_double=probabilities["touch_double"],
        lose_at_least_half=probabilities["lose_at_least_half"],
        lose_at_least_ninety=probabilities["lose_at_least_ninety"],
        account_exhausted=probabilities["account_exhausted"],
        end_below_start=probabilities["end_below_start"],
        median_terminal_multiple=_sample_median(ordered),
        expected_terminal_multiple=expected_terminal / paths,
        expected_log_growth=expected_log / paths if log_defined else float("-inf"),
        log_growth_per_trade=log_growth_reference,
        mean_max_drawdown=sum(drawdowns) / paths,
        max_drawdown_p50=_sample_median(ordered_dd),
        max_drawdown_p95=_empirical_quantile(ordered_dd, 0.95),
        effective_leverage=leverage,
        leverage_cap_exceeded=cap_exceeded,
        method=method,
        evidence_basis=evidence_basis,
        standard_errors=errors,
        wilson_intervals=intervals,
        paths=paths,
        seed=seed,
        account_label=account.label,
    )


def monte_carlo_binary_outcomes(
    payoff: BinaryPayoff,
    sizing: FixedFractionalSizing,
    n_trades: int,
    *,
    n_paths: int,
    seed: int,
    account: AccountAssumptions | None = None,
    dependence: DependenceModel | None = None,
) -> RuinProbabilities:
    """Monte Carlo with a fixed seed.

    ``dependence=None`` draws independent wins at the solved win probability.
    A :class:`DependenceModel` adds the regime, within-group correlation, stop
    gaps, and cost noise. Independent draws are the check against the exact
    lattice. The dependence model is an assumption, not evidence of an edge.
    """
    account = account or AccountAssumptions()
    n_trades = _require_trades(n_trades)
    if isinstance(n_paths, bool) or not isinstance(n_paths, int) or n_paths <= 0:
        raise ValueError("n_paths must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    rng = random.Random(seed)
    terminals: list[float] = []
    drawdowns: list[float] = []
    touch_count = 0
    if dependence is None:
        method = "monte_carlo_independent"
        for _ in range(n_paths):
            equity, drawdown, touched = _independent_path(
                payoff, sizing, n_trades, account, rng
            )
            terminals.append(equity)
            drawdowns.append(drawdown)
            touch_count += int(touched)
    else:
        method = "monte_carlo_stress"
        for _ in range(n_paths):
            equity, drawdown, touched = _stress_path(
                payoff, sizing, n_trades, account, dependence, rng
            )
            terminals.append(equity)
            drawdowns.append(drawdown)
            touch_count += int(touched)
    return _summarize_paths(
        terminals=terminals,
        drawdowns=drawdowns,
        touch_count=touch_count,
        method=method,
        evidence_basis=payoff.evidence_basis,
        seed=seed,
        account=account,
        sizing=sizing,
        log_growth_reference=log_growth_per_trade(payoff, sizing) if dependence is None else None,
    )


def _independent_path(
    payoff: BinaryPayoff,
    sizing: FixedFractionalSizing,
    n_trades: int,
    account: AccountAssumptions,
    rng: random.Random,
) -> tuple[float, float, bool]:
    probability = payoff.win_probability()
    win_factor, loss_factor = _base_factors(payoff, sizing)
    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0
    touched = False
    halted = False
    for _ in range(n_trades):
        if halted:
            break
        multiplier = win_factor if rng.random() < probability else loss_factor
        equity, halted, drawdown, peak, step_touch = _step_equity(
            equity=equity,
            peak=peak,
            multiplier=multiplier,
            sizing=sizing,
            account=account,
        )
        if drawdown > max_drawdown:
            max_drawdown = drawdown
        touched = touched or step_touch
    return equity, max_drawdown, touched


def _stress_path(
    payoff: BinaryPayoff,
    sizing: FixedFractionalSizing,
    n_trades: int,
    account: AccountAssumptions,
    dependence: DependenceModel,
    rng: random.Random,
) -> tuple[float, float, bool]:
    base = payoff.win_probability()
    high = min(1.0 - 1e-6, max(1e-6, base + dependence.regime_shift))
    low = min(1.0 - 1e-6, max(1e-6, base - dependence.regime_shift))
    threshold_high = _inverse_normal_cdf(high)
    threshold_low = _inverse_normal_cdf(low)
    sigma = dependence.cost_log_sigma
    log_mean = -0.5 * sigma * sigma if dependence.cost_noise_mean_preserving else 0.0
    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0
    touched = False
    halted = False
    state_high = rng.random() < 0.5
    index = 0
    while index < n_trades and not halted:
        if dependence.regime_clock == "per_group":
            if index > 0 and rng.random() >= dependence.regime_stay_probability:
                state_high = not state_high
            block = min(dependence.group_size, n_trades - index)
            common = rng.gauss(0.0, 1.0)
            correlation = dependence.group_correlation
        else:
            block = 1
            common = 0.0
            correlation = 0.0
        for _ in range(block):
            if index >= n_trades or halted:
                break
            if dependence.regime_clock == "per_trade":
                if index > 0 and rng.random() >= dependence.regime_stay_probability:
                    state_high = not state_high
                common = rng.gauss(0.0, 1.0)
                correlation = dependence.group_correlation
            threshold = threshold_high if state_high else threshold_low
            latent = math.sqrt(correlation) * common + math.sqrt(1.0 - correlation) * rng.gauss(0.0, 1.0)
            win = latent < threshold
            cost = payoff.cost_r
            if sigma > 0.0 and cost > 0.0:
                cost = payoff.cost_r * math.exp(log_mean + sigma * rng.gauss(0.0, 1.0))
            loss_r = 1.0
            if not win and dependence.gap_probability > 0.0 and rng.random() < dependence.gap_probability:
                loss_r = min(dependence.gap_cap_r, rng.paretovariate(dependence.gap_pareto_alpha))
            if win:
                multiplier = 1.0 + sizing.risk_fraction * (payoff.reward_to_risk - cost)
            else:
                multiplier = 1.0 - sizing.risk_fraction * (loss_r + cost)
            equity, halted, drawdown, peak, step_touch = _step_equity(
                equity=equity,
                peak=peak,
                multiplier=multiplier,
                sizing=sizing,
                account=account,
            )
            if drawdown > max_drawdown:
                max_drawdown = drawdown
            touched = touched or step_touch
            index += 1
    return equity, max_drawdown, touched


def block_bootstrap_outcomes(
    net_r_multiples: Sequence[float],
    sizing: FixedFractionalSizing,
    n_trades: int,
    *,
    n_paths: int,
    seed: int,
    mean_block_length: float,
    account: AccountAssumptions | None = None,
    evidence_basis: str = "supplied_trade_record",
) -> RuinProbabilities:
    """Stationary bootstrap of a supplied net-R record.

    Block lengths follow Politis and Romano (1994): after each trade, start a
    new block at a random record index with probability ``1 / mean_block_length``;
    otherwise continue circularly. The record is used as given. Resampling it
    does not create an edge that is not already in the record.
    """
    account = account or AccountAssumptions()
    n_trades = _require_trades(n_trades)
    if evidence_basis not in {"hypothetical_distribution", "supplied_trade_record"}:
        raise ValueError("evidence_basis is not recognized")
    if not net_r_multiples:
        raise ValueError("trade record must contain at least one net R")
    record = tuple(_finite(value, name="net R") for value in net_r_multiples)
    block = _positive(mean_block_length, name="mean_block_length")
    restart = min(1.0, 1.0 / block)
    if isinstance(n_paths, bool) or not isinstance(n_paths, int) or n_paths <= 0:
        raise ValueError("n_paths must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    rng = random.Random(seed)
    terminals: list[float] = []
    drawdowns: list[float] = []
    touch_count = 0
    source_n = len(record)
    for _ in range(n_paths):
        index = rng.randrange(source_n)
        sampled: list[float] = []
        while len(sampled) < n_trades:
            sampled.append(record[index])
            if rng.random() < restart:
                index = rng.randrange(source_n)
            else:
                index = (index + 1) % source_n
        path = apply_net_r_path(sampled, sizing, account)
        terminals.append(float(path["terminal_multiple"]))
        drawdowns.append(float(path["max_drawdown"]))
        touch_count += int(path["touched_double"])
    return _summarize_paths(
        terminals=terminals,
        drawdowns=drawdowns,
        touch_count=touch_count,
        method="stationary_block_bootstrap",
        evidence_basis=evidence_basis,
        seed=seed,
        account=account,
        sizing=sizing,
        log_growth_reference=None,
    )


def evaluate_against_zero_edge(
    payoff: BinaryPayoff,
    sizing: FixedFractionalSizing,
    n_trades: int,
    *,
    account: AccountAssumptions | None = None,
    method: str = "exact",
    n_paths: int = 20_000,
    seed: int = 11,
    dependence: DependenceModel | None = None,
) -> EdgeVarianceSplit:
    """Compare a payoff with its zero-net-edge twin.

    Trade count, reward-to-risk, cost, sizing, account rules, seed, and
    dependence stay fixed. The difference in doubling probability is the
    contribution of the stated edge relative to variance and costs at that
    same size. It is not a measured market edge unless ``evidence_basis``
    says the inputs came from a supplied record.
    """
    if method not in {"exact", "monte_carlo"}:
        raise ValueError("method must be 'exact' or 'monte_carlo'")
    zero = payoff.with_net_edge(0.0)
    if method == "exact":
        strategy = exact_binary_outcomes(payoff, sizing, n_trades, account)
        benchmark = exact_binary_outcomes(zero, sizing, n_trades, account)
    else:
        strategy = monte_carlo_binary_outcomes(
            payoff,
            sizing,
            n_trades,
            n_paths=n_paths,
            seed=seed,
            account=account,
            dependence=dependence,
        )
        benchmark = monte_carlo_binary_outcomes(
            zero,
            sizing,
            n_trades,
            n_paths=n_paths,
            seed=seed,
            account=account,
            dependence=dependence,
        )
    return EdgeVarianceSplit(strategy=strategy, zero_edge=benchmark)


def probability_of_loss_streak(
    n_trades: int,
    loss_probability: float,
    streak_length: int,
) -> float:
    """Exact probability of at least one run of ``streak_length`` losses."""
    n_trades = _require_trades(n_trades)
    probability = _probability(loss_probability, name="loss_probability")
    if isinstance(streak_length, bool) or not isinstance(streak_length, int) or streak_length <= 0:
        raise ValueError("streak_length must be a positive integer")
    if streak_length == 1:
        return 1.0 - (1.0 - probability) ** n_trades
    win_probability = 1.0 - probability
    mass = [0.0] * streak_length
    mass[0] = 1.0
    hit = 0.0
    for _ in range(n_trades):
        nxt = [0.0] * streak_length
        for streak, weight in enumerate(mass):
            if weight == 0.0:
                continue
            nxt[0] += weight * win_probability
            if streak + 1 >= streak_length:
                hit += weight * probability
            else:
                nxt[streak + 1] += weight * probability
        mass = nxt
    return hit


def uncapped_gbm_doubling_probability(annual_sharpe: float, *, periods_per_year: int = 12) -> float:
    """Best P(end >= 2x) over leverage for a constant-Sharpe lognormal month.

    The study's continuous formula is ``Phi(monthly Sharpe - sqrt(2 ln 2))``.
    It assumes full-period exposure and no leverage cap. It is a benchmark,
    not a position-sizing rule.
    """
    sharpe = _finite(annual_sharpe, name="annual_sharpe")
    if isinstance(periods_per_year, bool) or not isinstance(periods_per_year, int) or periods_per_year <= 0:
        raise ValueError("periods_per_year must be a positive integer")
    monthly = sharpe / math.sqrt(periods_per_year)
    barrier = math.sqrt(2.0 * math.log(2.0))
    return _normal_cdf(monthly - barrier)


def leverage_for_uncapped_gbm_doubling(annual_volatility: float, *, periods_per_year: int = 12) -> float:
    """Leverage that reaches the monthly volatility ``sqrt(2 ln 2)``."""
    volatility = _positive(annual_volatility, name="annual_volatility")
    if isinstance(periods_per_year, bool) or not isinstance(periods_per_year, int) or periods_per_year <= 0:
        raise ValueError("periods_per_year must be a positive integer")
    monthly_volatility = volatility / math.sqrt(periods_per_year)
    return math.sqrt(2.0 * math.log(2.0)) / monthly_volatility


def minimum_net_edge_for_doubling_probability(
    *,
    reward_to_risk: float,
    cost_r: float,
    sizing: FixedFractionalSizing,
    n_trades: int,
    target_probability: float = 0.25,
) -> float | None:
    """Smallest net edge at this fixed size with exact doubling probability at least ``target``.

    The search moves the edge only. It does not change the risk fraction. If
    even a win on every trade finishes below twice starting equity, the target
    is unreachable and the result is ``None``.
    """
    target = _probability(target_probability, name="target_probability")
    n_trades = _require_trades(n_trades)
    reward = _positive(reward_to_risk, name="reward_to_risk")
    cost = _finite(cost_r, name="cost_r")
    if cost < 0.0 or reward <= cost:
        raise ValueError("reward_to_risk must exceed a non-negative cost_r")
    anchor = BinaryPayoff(reward, cost, 0.0)
    win_factor, _loss_factor = _base_factors(anchor, sizing)
    if win_factor <= 0.0 or win_factor**n_trades < _DOUBLE:
        return None
    # Valid net edges are those with a win probability inside (0, 1).
    low = -1.0 - cost + 1e-9
    high = reward - cost - 1e-9

    def probability_at(net_edge: float) -> float:
        return exact_binary_outcomes(anchor.with_net_edge(net_edge), sizing, n_trades).end_at_least_double

    if probability_at(high) < target:
        return None
    for _ in range(80):
        mid = 0.5 * (low + high)
        if probability_at(mid) >= target:
            high = mid
        else:
            low = mid
    return high


def study_candidate_f2_gaps(result: RuinProbabilities) -> dict[str, float | bool]:
    """Distances to the study's candidate F2 screen.

    The screen is recorded here so a result can be compared with it. DEC-627
    does not adopt the screen as an acceptance gate.
    """
    double = result.end_at_least_double
    lose_ninety = result.lose_at_least_ninety
    log_growth = result.expected_log_growth
    return {
        "adopted_as_acceptance_gate": False,
        "end_double_minus_0_25": double - 0.25,
        "lose_ninety_minus_0_10": lose_ninety - 0.10,
        "double_minus_three_times_lose_ninety": double - 3.0 * lose_ninety,
        "median_minus_1": result.median_terminal_multiple - 1.0,
        "log_growth": log_growth,
        "meets_candidate_screen": bool(
            double >= 0.25
            and lose_ninety <= 0.10
            and double >= 3.0 * lose_ninety
            and result.median_terminal_multiple >= 1.0
            and log_growth > 0.0
        ),
    }


def documented_phase7_monthly_inputs() -> dict[str, object]:
    """Aggregate inputs behind the study's "about 10 trades and +0.005R" sentence.

    Values are taken from the Phase 7 evidence documents and the frozen
    walk-forward constants (USDJPY 15m session breakout, buffer 5 pips,
    target multiple 1.5, $100,000 window start, 0.25% risk). Mean R is
    aggregate expectancy divided by $250. That is not a trade-level R series,
    and the 2024 stage-1 window was the selection window. Stage 2 at 1.0 pip
    of adverse slippage has negative expectancy, so the edge-first rule says
    this record is not a candidate for the doubling objective.
    """
    stage2_days = (date(2026, 8, 21) - date(2025, 1, 1)).days
    risk_dollars = 100_000.0 * 0.0025
    stage2_expectancy = {0.2: 3.8054, 0.5: 1.3175, 1.0: -2.8247}
    stage1_expectancy = {0.2: 11.3384, 0.5: 9.0370, 1.0: 5.2150}
    return {
        "candidate": "USDJPY 15m session_breakout buffer_pips=5 target_range_multiple=1.5",
        "experiment_id": "EXP-20260915-008",
        "evidence_basis": "published_aggregate_not_trade_record",
        "stage1_window": "2024-01-01 through 2024-12-31",
        "stage1_role": "selection window",
        "stage1_trades": 122,
        "stage2_window": "2025-01-01 inclusive through 2026-08-21 exclusive",
        "stage2_role": "forward windows already scored",
        "stage2_trades": 199,
        "stage2_calendar_days": stage2_days,
        "stage2_trades_per_30_days": 199 / stage2_days * 30.0,
        "starting_equity_usd": 100_000.0,
        "risk_fraction": 0.0025,
        "dollars_per_1r_at_window_start": risk_dollars,
        "stage2_mean_r_estimate": {
            pip: expectancy / risk_dollars for pip, expectancy in stage2_expectancy.items()
        },
        "stage1_mean_r_estimate": {
            pip: expectancy / risk_dollars for pip, expectancy in stage1_expectancy.items()
        },
        "edge_first_candidate_for_doubling": False,
        "edge_first_reason": (
            "Stage 2 aggregate expectancy at 1.0 pip of adverse slippage is negative, "
            "and the positive 0.5-pip aggregate is an approximate +0.005R with no "
            "trade-level record supplied to this calculator. Doubling probabilities "
            "for this candidate are illustrations, not a candidate outcome."
        ),
        "holdout_note": (
            "2024-01-01 through 2026-08-20 was opened in Phase 7. It is not an "
            "untouched 2023-2026 holdout for this candidate. Annual run 385 remains "
            "a separate unconsumed 2023 catalogue slot."
        ),
    }
