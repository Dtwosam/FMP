# Phase 8A — Multi-Pair, Multi-Strategy Portfolio Research Redesign

**Date:** 2026-09-22  
**Status:** APPROVED  
**Decision:** DEC-039  
**Experiment:** EXP-20260922-012  
**Scope:** V1 EURUSD / GBPUSD / USDJPY only

## 1. Reason for the amendment

Phase 7 correctly promoted one robust rule candidate, USDJPY 15m `session_breakout`, but its seven-window Stage 2 aggregate return was only +0.757266% at 0.2-pip adverse slippage and +0.262176% at 0.5 pips. That result satisfied the frozen Phase 7 promotion gate but is not economically attractive enough for the operator's revised objective.

The project therefore stops the planned EXP-011 live-shadow launch before campaign registration and changes Phase 8 from a single-strategy shadow campaign into two ordered subphases:

- **Phase 8A — Multi-pair, multi-strategy portfolio research**
- **Phase 8B — Multi-strategy live shadow**

This amendment does not rewrite or invalidate any earlier evidence. It changes what FMP must prove before spending weeks on a new live-shadow campaign.

## 2. Data scope remains frozen

The V1 instrument universe remains exactly:

- EURUSD
- GBPUSD
- USDJPY

The accepted Dukascopy Phase 1/2 history remains the canonical historical research source:

- 1-minute BID/ASK source-faithful history
- deterministic 5m, 15m, and 1h derived bars
- accepted Phase 2 manifests and checksums remain authoritative

All three accepted pair histories must be reused in Phase 8A. No paid data, extra FX pairs, indices, commodities, crypto, or broker historical candles are introduced by this amendment.

## 3. Historical-data honesty after Phase 7

The project has already inspected the former 2024-01-01 through 2026-08-20 final-test period during Phase 7. Strategies invented or materially changed after that inspection may use those observations for discovery, diagnostics, robustness analysis, and rolling historical simulation, but **must not describe them as an untouched final test**.

For every new strategy version created under Phase 8A:

- its historical evidence is labeled as research / retrospective walk-forward evidence;
- the exact data ranges used in discovery and selection are recorded;
- repeated search over the same history is treated as multiple-comparison / overfitting risk;
- genuinely prospective evidence begins only after the strategy version and promotion protocol are frozen;
- Phase 8B shadow data becomes the first new forward evidence for post-Phase-7 challengers.

No historical result may be relabeled as prospective evidence.

## 4. Strategy-library architecture

FMP is no longer limited to one active research strategy. Phase 8A builds a versioned strategy library across the three V1 pairs.

Every strategy version has an immutable identity containing at minimum:

- strategy family
- strategy version
- pair
- timeframe
- complete parameters
- signal-timing contract
- stop / target / time-exit semantics
- required market/regime inputs
- code commit
- data identities used for its historical evaluation
- cost assumptions
- risk assumptions
- lifecycle status

Lifecycle statuses are:

1. `DISCOVERY`
2. `CHALLENGER`
3. `HISTORICAL_QUALIFIED`
4. `SHADOW_CANDIDATE`
5. `SHADOW_VALIDATED`
6. `DEMO_ELIGIBLE`
7. `RETIRED`

A status change creates new auditable evidence. Failed and retired versions remain in history.

## 5. Champion / challenger rule

Continuous learning is permitted only through a separated research path.

- A currently approved champion set is immutable during a registered shadow/demo/live campaign.
- New market observations may be stored and analyzed by the research path.
- The research path may create a new challenger version.
- A challenger cannot hot-swap, mutate, or silently replace a champion.
- A challenger must pass the frozen historical gates and then prospective shadow gates before later promotion.
- No learning process may autonomously authorize demo or real-money execution.
- Every promotion requires an explicit version transition with evidence.

This prevents self-modifying production behavior while still allowing the system to keep learning.

## 6. Multi-strategy routing

At each decision time, FMP may evaluate multiple approved strategy versions across EURUSD, GBPUSD, and USDJPY.

The future Phase 8B route is:

`market state -> eligible approved strategies -> regime/applicability checks -> candidate set -> portfolio conflict/exposure filter -> risk engine -> shadow decision`

Rules:

- no strategy is forced to trade;
- multiple strategies may be eligible at the same time;
- overlapping or correlated USD exposure must be measured before risk approval;
- one strategy cannot bypass portfolio risk because another strategy produced the exposure;
- strategy logic never owns position sizing;
- the risk engine remains authoritative for portfolio-level caps.

## 7. Regime awareness

Phase 8A may research deterministic or leakage-safe regime descriptors such as:

- directional trend / persistence
- range / mean-reverting conditions
- volatility level and volatility expansion
- session state
- spread / quote-quality state

A regime label is not allowed to use future information. A strategy may declare the regimes in which it is historically eligible, but regime routing must itself be tested out of sample / forward and cannot be fitted using future outcomes at decision time.

## 8. Economic objective

The operator's objective is materially higher return than the Phase 7 single-strategy result. The stated aspiration includes returns as high as 10% in a day.

FMP records that aspiration but **does not convert “10% every day” into a guaranteed or mandatory pass criterion**. Doing so would create a strong incentive to overfit or manufacture returns through leverage.

Phase 8A must instead measure, at fixed and explicitly reported risk:

- daily return distribution
- frequency of positive / negative days
- frequency of days at or above +10%
- monthly and annualized net return
- expectancy
- profit factor
- maximum drawdown
- downside / tail concentration
- longest losing streak
- turnover / trade count
- cost sensitivity
- pair, strategy, timeframe, session, and regime contribution
- portfolio concentration and correlated exposure

Return improvement must come from stronger or more diverse validated edges and better capital utilization, not from martingale, loss chasing, or silently multiplying leverage.

## 9. Phase 8A research universe

Phase 8A begins by reusing the existing implemented baseline families across all three pairs and supported timeframes where their signal contracts are valid:

- session breakout
- trend continuation
- mean reversion
- previous-day high/low rejection
- rolling volatility breakout
- session high/low sweep/rejection

Earlier rejected parameter points remain rejected under their original experiments. Phase 8A may create **new, predeclared experiments** for new parameter regions, new strategy versions, regime-conditioned variants, or portfolio combinations. It may not retroactively change earlier outcomes.

Additional strategy families may be added only through an experiment protocol recorded before their benchmark results are inspected.

## 10. Phase 8A implementation order

1. Versioned strategy registry and lifecycle contract.
2. Champion/challenger promotion lock.
3. Multi-pair candidate aggregation and deterministic routing contract.
4. Portfolio exposure/conflict accounting integrated with the existing independent risk engine.
5. Historical portfolio research runner using accepted EURUSD/GBPUSD/USDJPY data.
6. Regime/applicability research surface.
7. Return/drawdown/concentration reporting at strategy and portfolio levels.
8. Frozen challenger-selection protocol before broad search results are used for promotion.
9. Phase 8A acceptance review and immutable portfolio/shadow-candidate manifest.
10. Only then may Phase 8B expand the read-only live bridge and begin a new multi-strategy shadow campaign.

## 11. Initial Phase 8A acceptance gate

Phase 8A may PASS only when:

- all three V1 pairs are included in the research universe;
- strategy versions and lifecycle transitions are deterministic and auditable;
- only explicitly eligible lifecycle states can enter a portfolio candidate set;
- no research or learning output can mutate an active champion set;
- portfolio exposure and correlated USD risk are measured before approval;
- historical evaluations retain exact data/code/config/cost/risk identities;
- cost sensitivity includes the established 0.2, 0.5, and 1.0-pip adverse-slippage views unless a later strategy-specific decision documents why a different executable model is required;
- candidate/portfolio results include return, expectancy, PF, drawdown, trade count, concentration, and daily-return distribution;
- repeated historical search is explicitly accounted for and no post-Phase-7 strategy claims an untouched 2024-2026 holdout;
- at least one frozen portfolio/shadow candidate materially improves the economic case over the Phase 7 single-strategy baseline **or** the phase records a credible rejection showing that the expanded search did not find a sufficiently strong portfolio;
- repository-wide tests and the unchanged Phase 3 execution/risk acceptance suite remain green.

Passing Phase 8A authorizes only Phase 8B shadow design/capture. It does not authorize demo or live orders.

## 12. EXP-011 disposition

`EXP-20260922-011` is stopped **before campaign registration** due to the approved research-objective change.

Preserve as non-scored evidence:

- fresh MT5 connector qualification: PASS
- fresh historical USDJPY spread reference bound to commit `5cb884dfb15d7798b023658e025221a38dfec9fc`
- reference SHA-256 `e920b3254235d2bb0766762551b5eb9d21439d429c59aebd14c3e4bb16e8cc64`

No EXP-011 campaign was registered and no EXP-011 live-shadow segment is to be started. Those artifacts remain evidence that the read-only connector path qualified, not evidence about portfolio profitability.

## 13. Safety / execution locks

Throughout Phase 8A:

- MT5 AutoTrading remains OFF.
- No demo order placement is authorized.
- No live order placement is authorized.
- No real-money trading is authorized.
- The existing broker-mutation prohibition remains unchanged.
- Existing Phase 3 risk rules remain the default research risk contract unless a later explicit decision changes them.
