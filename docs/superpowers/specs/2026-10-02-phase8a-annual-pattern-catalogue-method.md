# Phase 8A Annual Pattern Catalogue Research-Method Amendment

**Decision:** DEC-469  
**Status:** GOVERNING RESEARCH-METHOD AMENDMENT / EXECUTION LOCKED  
**Parent method:** DEC-268 discovery-first market-pattern research  
**Supersedes as operating priority:** choosing one narrow successor representation as the main research direction after EXP-065

## Operator intent

FMP must research the accepted historical collection **year by year first**.

For each historical year or year-segment, the system should derive and preserve the patterns surfaced by a frozen, bounded discovery vocabulary and search process. Only after the annual catalogues are frozen should the project compare those patterns across years and use recurring, economically credible behaviour to synthesize the first strategy.

The intended high-level loop is:

`historical collection -> annual pattern catalogues -> freeze each annual catalogue -> cross-year pattern comparison -> Strategy V1 synthesis -> freeze Strategy V1 -> robustness/backtest -> prospective shadow -> fixed-version demo -> completed demo review -> Strategy V2 challenger -> fresh prospective evidence`

This is now the governing operating interpretation of DEC-268.

## What “derive every pattern” means

“Every pattern” means every pattern surfaced by the **predeclared bounded discovery grammar** for that annual segment. It does not mean an unlimited search over arbitrary formulas until something profitable appears.

The annual catalogue must preserve:

- qualifying patterns;
- non-qualifying patterns;
- failed/negative patterns;
- support counts;
- after-cost outcome summaries;
- pair, timeframe, outcome horizon, session/regime/location/spread context;
- search volume and pattern identity.

The project must not keep only the winners.

## Annual-first rule

Each annual segment is processed independently before cross-year synthesis.

The collection currently spans:

- full calendar years 2015 through 2025;
- partial 2026 from 2026-01-01 through 2026-08-20.

The same frozen measurement vocabulary and search grammar should be used where comparability requires it. Each annual catalogue must receive an immutable identity before the cross-year comparison may use it.

At the current DEC-469 source-only gate, 2015-2022 remains the already-open retrospective research block. The 2023-2026 block is **not silently opened by this method amendment**. A separate explicit source-of-truth decision must authorize its catalogue access. Strategy V1 synthesis is not authorized at DEC-469.

Once a historical year is used to design Strategy V1, it is research/training evidence and cannot later be called fresh validation for Strategy V1.

## Pattern vocabulary

The annual catalogue should be broad enough to inspect market behaviour rather than presuppose a named strategy. It may include bounded representations of:

- direction/trend;
- sideways/range;
- volatility level and change;
- momentum and return structure;
- candle/range structure;
- session/time context;
- location relative to recent/session/previous-period structure;
- spread/quote quality;
- state transitions and short temporal sequences;
- bounded interactions among accepted measurements;
- fixed future return or price-path outcomes.

State transitions are therefore one **pattern type inside the annual catalogue**, not the governing research method. The same is true of pairwise interactions, clustering, model families, and named rule families.

## Cross-year comparison

Only frozen annual catalogues may enter cross-year comparison.

Patterns need canonical identities so the same behavioural pattern can be compared across years. The comparison must record at minimum:

- number of years in which the pattern appears;
- support by year;
- effect direction and magnitude by year;
- after-cost economics by year;
- pair/timeframe/horizon applicability;
- session/regime/location/spread context;
- failure years;
- sign reversals;
- concentration in one year or a small number of events.

A spectacular single year is evidence about that year, not sufficient evidence for Strategy V1.

## Strategy V1 synthesis

Strategy V1 should be built from the strongest recurring cross-year behaviour, not from one preselected indicator or one narrow sub-experiment.

It may combine multiple recurring patterns when the combination is frozen and justified by the cross-year catalogue evidence.

Before prospective evidence, Strategy V1 must freeze:

- exact LONG/SHORT/NO TRADE conditions;
- applicability/regime rules;
- conflict handling;
- entry and exit timing;
- spread/slippage/cost assumptions;
- risk interface;
- exact code/config identity.

Strategy V1 cannot be tuned on prospective evidence while it is running.

## Shadow/demo learning loop

Strategy V1 is the first intended demo candidate, but the existing Phase 8B safety order remains:

`frozen Strategy V1 -> prospective live shadow -> fixed Strategy V1 demo`

The demo campaign observes what works and what does not under real forward conditions, but the running strategy is not edited trade by trade.

At a frozen review boundary:

1. completed shadow/demo evidence is analysed;
2. that evidence may motivate or train Strategy V2;
3. Strategy V2 receives a new immutable identity;
4. the evidence used to build V2 becomes training/research evidence for V2;
5. V2 must prove itself on a later fresh prospective window.

This preserves the user’s improvement loop without allowing outcome-aware live self-modification.

## Mandatory new-session interpretation

Every future research session must state, before proposing a narrow experiment:

- governing method: annual pattern catalogue discovery under DEC-469 / DEC-268;
- which annual catalogue(s) are currently authorized;
- whether the task is annual discovery, cross-year comparison, Strategy V1 synthesis, or prospective learning;
- the current closed-data boundary;
- the next authorized gate.

A narrow transform/model experiment may be used only as a component of the annual catalogue or a later explicitly justified analysis. It may not silently replace the annual-first workflow.

## Authority

DEC-469 changes the governing research workflow only.

It does not by itself authorize:

- historical catalogue execution;
- access to the protected 2023-2026 block;
- Strategy V1 synthesis;
- candidate compilation or promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action or trading.

## Next gate

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_PROTOCOL_AND_PROTECTED_HISTORY_ACCESS_DECISION`

That next gate must freeze the annual catalogue grammar, annual evidence schema, cross-year canonical pattern identity, search-volume accounting, and the explicit decision on whether/how the protected 2023-2026 history joins the catalogue.
