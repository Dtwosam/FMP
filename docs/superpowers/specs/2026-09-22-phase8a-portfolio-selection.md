# Phase 8A — Portfolio Selection Protocol

**Date:** 2026-09-22  
**Status:** APPROVED  
**Decision:** DEC-041  
**Experiment:** EXP-20260922-013  
**Scope:** Predeclared retrospective portfolio selection only

## 1. Purpose

DEC-039 expanded Phase 8A to a multi-pair, multi-strategy research architecture. DEC-040 then added a shared-account joint simulator. DEC-041 freezes the rules that may later choose a retrospective portfolio candidate **before any strategy-combination search is run**.

This protocol is deliberately separate from strategy discovery. A strategy must first qualify under its own experiment. DEC-041 may combine already-qualified immutable strategy versions; it may not invent, retune, rescue, or resurrect strategies.

All evidence under this protocol is retrospective and already seen. A selected set becomes at most a **prospective shadow candidate** after a later explicit acceptance review. It is not demo/live approval.

## 2. Eligible strategy pool

A strategy version may enter the DEC-041 pool only if all of the following are true:

- immutable `StrategyVersion` identity is present;
- lifecycle is `HISTORICAL_QUALIFIED`, `SHADOW_CANDIDATE`, `SHADOW_VALIDATED`, or `DEMO_ELIGIBLE`;
- its qualifying experiment/evidence ID is present;
- symbol is EURUSD, GBPUSD, or USDJPY;
- signal timeframe is 5m, 15m, or 1h;
- exact parameters, code commit, data identity, cost assumptions, and risk assumptions are known;
- it has not been retired;
- it was not created or materially changed after observing the DEC-041 selection results.

`DISCOVERY`, `CHALLENGER`, and `RETIRED` records are ineligible.

The existing Phase 7 USDJPY 15m session-breakout survivor is eligible as the baseline control. Earlier rejected Phase 4/7 configurations remain ineligible unless a separate new experiment creates a genuinely new immutable challenger version and qualifies it.

## 3. Pool-size fail-closed rule

The exact eligible pool is frozen before combination evaluation.

- Minimum eligible pool size to search multi-strategy portfolios: 2.
- Maximum eligible pool size: 12.
- If more than 12 strategies are eligible, DEC-041 fails closed and no portfolio search runs. A separate predeclared pool-reduction amendment is required.

This prevents an unbounded combinatorial search after results are visible.

## 4. Portfolio set universe

If the frozen pool contains 2 through 12 eligible strategies, evaluate every unique unordered strategy set with cardinality:

- minimum: 1 strategy;
- maximum: 6 strategies.

The 1-strategy sets are retained only as controls. A portfolio cannot be selected as the multi-strategy Phase 8A candidate unless it contains at least 2 strategies.

No strategy identity may appear twice in one set.

The exact ordered list of evaluated fingerprint sets must be written to evidence before performance results are ranked.

## 5. Joint simulation contract

Every set is evaluated using DEC-040:

- one shared $100,000 account per slippage scenario;
- exact canonical 1m BID/ASK execution bars;
- native 5m/15m/1h strategy signal bars;
- `DECLARED_EARLIEST_BAR` execution timing;
- 0.25% requested risk per approved directional decision;
- 0.50% hard per-trade risk maximum;
- 1.00% simultaneous open-risk maximum;
- 1.50% UTC day-start realized-loss halt;
- same-time same-symbol opposite directions fail closed before risk;
- no interpolation, reconstructed fills, or alternate-provider repair.

Cost scenarios remain exactly 0.2, 0.5, and 1.0 adverse pips per fill.

## 6. Frozen retrospective selection range

DEC-041 selection uses one continuous joint-account run over:

- start: `2019-01-01` inclusive;
- end: `2026-08-21` exclusive.

The account does not reset at calendar-year boundaries.

The run must additionally report calendar-year contribution/stability for:

- 2019
- 2020
- 2021
- 2022
- 2023
- 2024
- 2025
- 2026 partial through 2026-08-20

All of this history is labeled `RETROSPECTIVE_ALREADY_SEEN`; none of it is untouched OOS.

## 7. Mandatory portfolio gates

A multi-strategy set is **selection-eligible** only if every mandatory gate below passes.

At both 0.2 and 0.5 pips:

- net return > 0;
- expectancy USD/trade > 0;
- profit factor > 1.0;
- maximum drawdown <= 5%;
- at least 200 completed trades.

At 0.2 pips additionally:

- at least 5 of the 8 calendar-year windows have positive net PnL;
- no one calendar year contributes more than 45% of total positive-year PnL;
- no one strategy contributes more than 60% of total positive trade PnL;
- no one pair contributes more than 70% of total positive trade PnL;
- the set contains at least 2 strategy identities;
- completed trades come from at least 2 strategy families;
- completed trades come from at least 2 of the 3 V1 pairs.

The 1.0-pip scenario remains diagnostic and must be reported but is not a mandatory pass gate.

The frequency of days at or above +10% return must be reported at every cost scenario but is **not** a pass gate.

## 8. Deterministic ranking of passing sets

If no set passes all mandatory gates, the result is `NO_PORTFOLIO_SELECTED`.

If one or more sets pass, rank passing sets by the following immutable lexicographic order:

1. higher 0.5-pip annualized compounded return;
2. lower 0.5-pip maximum drawdown;
3. higher 0.5-pip profit factor;
4. higher 0.2-pip annualized compounded return;
5. lower 0.2-pip largest-strategy positive-PnL share;
6. lower 0.2-pip largest-pair positive-PnL share;
7. fewer strategy identities;
8. lexicographically smaller sorted strategy-fingerprint tuple.

No weights are tuned after observation. No manual override may replace the ranking winner while still calling the result DEC-041.

## 9. Annualized return definition

Annualized compounded return is:

`(ending_equity / starting_equity) ** (365.2425 / elapsed_calendar_days) - 1`

It is descriptive of the historical period. It is not a forecast and does not imply the return repeats every year.

## 10. Concentration definitions

Positive-PnL contribution ratios use only positive contribution in the denominator.

- strategy concentration: positive trade PnL by strategy / total positive trade PnL;
- pair concentration: positive trade PnL by pair / total positive trade PnL;
- positive-year concentration: positive net PnL by calendar year / total positive-year net PnL.

If the relevant positive-PnL denominator is zero, the portfolio fails the associated gate.

## 11. Evidence requirements

DEC-041 evidence must bind:

- exact eligible pool and each lifecycle/evidence ID;
- exact enumerated portfolio-set fingerprint list before ranking;
- runner code commit;
- dataset manifest identities for all used pairs;
- exact selection range;
- cost/risk identity;
- per-set results at all three slippage scenarios;
- yearly metrics;
- contribution/concentration metrics;
- every mandatory gate result;
- deterministic ranking fields;
- selected fingerprint set or `NO_PORTFOLIO_SELECTED`.

Evidence must state:

- `evidence_label = RETROSPECTIVE_ALREADY_SEEN`;
- `untouched_oos = false`;
- `promotion_authorized = false`.

## 12. Search discipline

DEC-041 cannot:

- modify the eligible pool after any combination result is observed;
- add a strategy because a first search disappointed;
- drop a strategy only because it hurt the aggregate;
- change the 2019–2026 range;
- change risk or slippage gates after observation;
- change concentration thresholds after observation;
- change ranking order after observation;
- create a new strategy during selection.

Any such change requires a new decision and a new experiment identity.

## 13. Outcome meaning

`PORTFOLIO_SELECTION_PASS` means only that one frozen historical set is selected for further Phase 8A acceptance review and prospective Phase 8B design.

It does not authorize:

- MT5 demo orders;
- broker mutation;
- live orders;
- real-money trading;
- automatic champion promotion.

A later prospective shadow campaign remains mandatory.

## 14. Next dependency: challenger discovery

The current historical inventory contains only one previously qualified baseline strategy. Therefore DEC-041 cannot yet run a meaningful multi-strategy search.

Before DEC-041 selection can execute, Phase 8A must produce at least one additional `HISTORICAL_QUALIFIED` immutable challenger through a separately predeclared discovery/qualification experiment.

DEC-041 is frozen now so that future challenger discovery cannot tailor the portfolio-selection criteria after seeing candidate results.
