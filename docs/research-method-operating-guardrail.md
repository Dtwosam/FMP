# FMP Discovery-First Annual Pattern Catalogue Operating Guardrail

**Status:** MANDATORY OPERATING INTERPRETATION OF SOURCE OF TRUTH  
**Authority:** DEC-268, DEC-469, `docs/master-spec.md`, and `docs/research-testing-standard.md`  
**Effect:** Governing research workflow. This document does not by itself authorize historical execution, protected-history access, Strategy V1 synthesis, candidate promotion, Phase 8B, demo orders, broker mutation, live orders, real-money action, or trading.

## 1. Governing method

FMP's governing post-EXP-065 research method is **discovery-first annual pattern catalogue research**.

The project must not choose one narrow mathematical representation and treat it as the research method.

The governing loop is:

`historical collection -> year-by-year pattern catalogues -> freeze each annual catalogue -> cross-year pattern comparison -> Strategy V1 synthesis -> freeze Strategy V1 -> robustness/backtest -> prospective shadow -> fixed-version demo -> completed demo evidence review -> new immutable challenger -> fresh prospective evidence`

The purpose is to discover what the market repeatedly did in each year, compare those behaviours across years, and construct the first strategy only from recurring evidence that survives costs, instability checks, and concentration review.

## 2. Mandatory distinction: method vs pattern type

Every research session must keep these separate:

- **Governing method:** annual pattern catalogue discovery under DEC-469 / DEC-268.
- **Pattern type or tool:** a bounded representation used inside an annual catalogue.

Pattern types/tools may include:

- atomic market states;
- trend/range conditions;
- volatility level/change;
- momentum/return structure;
- candle/range structure;
- session/time context;
- location;
- spread/quote quality;
- state transitions and short sequences;
- pairwise or other bounded interactions;
- clustering;
- statistical estimators;
- model families;
- historical named strategy families.

None of these is the governing method by itself.

A negative result for one pattern type rejects only its frozen representation/protocol. It does not establish that annual discovery or market learning is exhausted.

## 3. Mandatory new-session bootstrap

Before proposing or continuing research, every new session must:

1. read `docs/project-state.md`;
2. read the latest relevant entries in `docs/decision-log.md`;
3. read the strategy-research section of `docs/master-spec.md`;
4. read the current Phase 8A section of `docs/build-order.md`;
5. read `docs/research-testing-standard.md`;
6. read this guardrail;
7. state separately:
   - governing method: annual pattern catalogue discovery;
   - which annual segments are currently authorized;
   - current task stage: annual discovery, cross-year comparison, Strategy V1 synthesis, robustness, prospective shadow/demo, or challenger learning;
   - current protected/closed-data boundary;
   - next authorized gate.

If `docs/project-state.md` is stale relative to later decision-log entries, refresh it before continuing.

## 4. What “derive every pattern” means

“Every pattern” means every pattern surfaced by the **predeclared bounded discovery grammar** for that annual segment.

It does not mean an unlimited search over arbitrary formulas until something profitable appears.

Before an annual catalogue run can be used, freeze:

- source/data identities;
- exact annual segment;
- leakage-safe measurement vocabulary;
- pattern grammar/representation families allowed in that catalogue;
- future-outcome definitions and horizons;
- minimum support;
- cost treatment;
- bounded search budget;
- search-volume accounting;
- duplicate/near-duplicate handling;
- annual pattern identity/evidence schema.

The catalogue must preserve winners, losers, non-qualifiers, and failed/negative patterns. Do not save only the profitable discoveries.

## 5. Stage A — Build each annual catalogue independently

Process each historical year or year-segment independently before cross-year synthesis.

The accepted collection spans:

- full calendar years 2015 through 2025;
- partial 2026 from 2026-01-01 through 2026-08-20.

For comparability, annual runs should use the same frozen measurement vocabulary and pattern grammar unless a later explicit decision creates a new catalogue version.

Each annual catalogue should record at minimum:

- canonical pattern identity;
- pair;
- timeframe;
- future-outcome horizon;
- support;
- effect direction and magnitude;
- economics after declared costs;
- session/regime/location/spread context where relevant;
- search volume;
- qualification state;
- negative/failure evidence.

Each annual catalogue gets an immutable identity before cross-year comparison.

## 6. Stage B — Cross-year pattern comparison

Do not synthesize Strategy V1 from one year's results.

Cross-year comparison begins only after the required annual catalogues are frozen.

For each canonical pattern, compare:

- number of years in which it appears;
- support by year;
- effect direction by year;
- effect magnitude by year;
- after-cost economics by year;
- pair/timeframe/horizon applicability;
- session/regime/location/spread context;
- failure years;
- sign reversals;
- concentration in one year;
- concentration in a small number of observations.

A spectacular single year is evidence about that year, not sufficient evidence for Strategy V1.

Cross-year comparison should make both recurrence and failure visible.

## 7. Stage C — Synthesize Strategy V1

Only after the annual catalogues and cross-year comparison are complete may a separate gate synthesize Strategy V1.

Strategy V1 should be derived from the strongest recurring behaviours across years. It may combine multiple patterns when the combination is justified by the frozen cross-year evidence.

Before prospective evidence, freeze:

- exact LONG / SHORT / NO TRADE semantics;
- applicability/regime conditions;
- conflict rules;
- entry timing;
- exit/stop/target semantics;
- overlap rules;
- costs/slippage assumptions;
- risk interface;
- exact code/config/data identities.

Strategy V1 receives a new immutable version identity.

A weak pattern may not be rescued during strategy compilation through outcome-aware retuning.

## 8. Stage D — Robustness and realistic historical backtest

Test the frozen Strategy V1 with the existing FMP execution/risk machinery.

At minimum inspect:

- bid/ask semantics;
- spread/slippage stress;
- yearly breakdown;
- pair/timeframe/session/regime breakdown;
- drawdown and tail behaviour;
- contribution concentration;
- neighboring-condition sensitivity where meaningful;
- rejected signals and NO TRADE decisions.

Historical evidence already used to derive Strategy V1 remains research/training evidence. It must not be relabeled as untouched OOS.

## 9. Stage E — Prospective shadow then fixed-version demo

The first strategy intended for demo is Strategy V1, but the existing safety order remains:

`frozen Strategy V1 -> prospective live shadow -> fixed Strategy V1 demo`

Running shadow/demo champions never self-modify.

Do not edit Strategy V1 after a winning or losing trade, after a short streak, or because a current market condition looks unusual.

## 10. Stage F — Learn from completed demo evidence

At a frozen review boundary, completed shadow/demo evidence may be analysed to determine what worked, what failed, and under which conditions.

That evidence may motivate or train Strategy V2.

Once demo observations influence Strategy V2:

- they become research/training evidence for Strategy V2;
- Strategy V2 receives a new immutable identity;
- Strategy V1 remains unchanged in history;
- Strategy V2 must pass applicable retrospective checks;
- Strategy V2 must then prove itself on a later fresh prospective window.

The intended improvement loop is:

`fixed Strategy V1 -> observe completed forward evidence -> diagnose strengths/failures -> build Strategy V2 -> freeze -> fresh forward evidence -> later fixed demo version`

This is iterative learning, not online self-modification.

## 11. Historical collection and full-collection research scope

The governing method catalogues the accepted historical collection year by year.

DEC-470 explicitly authorizes all collected annual segments for the DEC-469 annual-catalogue / Strategy V1 research path:

- full calendar years 2015 through 2025;
- partial 2026 from 2026-01-01 through 2026-08-20.

The 2023-2026 block that EXP-061 through EXP-065 kept closed is no longer reserved for Strategy V1 under this path. It is authorized as retrospective catalogue research evidence only. This does not reopen or rerun those predecessor experiments.

Historical artifact reads and annual catalogue execution still require later explicit runtime/execution gates. DEC-470 changes the allowed research scope, not execution authority.

Once any historical segment contributes to Strategy V1 discovery or synthesis, it is research/training evidence for Strategy V1 and cannot be called untouched OOS. Genuine new forward evidence for Strategy V1 begins only after the exact Strategy V1 version is frozen.

## 12. EXP-065 interpretation

EXP-065 remains immutable negative evidence for one bounded pairwise continuous-feature interaction representation.

Its exact result was zero qualifying hypotheses from 13,680 evaluable frozen hypotheses.

That result does not reject the annual pattern catalogue method and does not establish that no market edge exists.

Pairwise interactions may still appear as one bounded pattern type inside a future annual catalogue version if explicitly included by the annual catalogue protocol; EXP-065 itself is not rerun or rescued.

## 13. Narrow-tool rule

Before adding a new transform, model, or representation to an annual catalogue, its source/spec must state:

1. what market behaviour it measures;
2. which accepted measurement vocabulary it uses;
3. what it deliberately omits;
4. why it adds information to the annual catalogue;
5. its bounded search volume;
6. what a negative result would mean;
7. what a negative result would not mean;
8. how its output maps to the canonical annual pattern identity.

No narrow tool may silently become “the next strategy” or replace the annual-first workflow.

## 14. Safety boundaries

This method does not weaken execution or deployment gates.

Future sessions must honor the latest source-of-truth state for:

- historical execution authority;
- protected-history access;
- consumed one-shot runs;
- rerun/no-retry rules;
- Strategy V1 synthesis;
- candidate compilation;
- promotion;
- Phase 8B;
- shadow/demo order permissions;
- broker mutation;
- live orders;
- real-money action.

Phase 11 remains impossible without separate explicit human approval.
