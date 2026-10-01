# FMP Discovery-First Research Operating Guardrail

**Status:** MANDATORY OPERATING INTERPRETATION OF EXISTING SOURCE OF TRUTH  
**Authority:** DEC-268, DEC-270, `docs/master-spec.md`, and `docs/research-testing-standard.md`  
**Effect:** Clarification only. This document does not authorize historical execution, reserved-data access, candidate promotion, Phase 8B, demo orders, broker mutation, live orders, real-money action, or trading.

## 1. Governing method

FMP's default post-DEC-268 research method is **discovery-first market-pattern research**.

The project starts from accepted leakage-safe market measurements and asks which repeated, measurable behaviours occur under different market states. It does not treat a named strategy family, one indicator, one model class, one feature transform, or one current experiment as the research method itself.

The governing loop is:

`market measurements -> bounded pattern discovery -> pattern freeze -> later chronological confirmation/validation -> exact strategy/model compilation -> robustness/backtest -> prospective shadow -> fixed-version demo -> completed-evidence learning -> new immutable challenger`

The goal is to discover repeatable conditional market behaviour and then test whether it survives later evidence and realistic costs.

## 2. Mandatory distinction: framework vs sub-experiment

Every session must keep two concepts separate:

- **Research framework:** discovery-first market-pattern research under DEC-268.
- **Current sub-experiment:** the specific bounded representation/search currently being tested.

Examples of sub-experiments include atomic market states, continuous single-feature stability, pairwise interactions, a particular statistical estimator, a particular clustering method, or a particular model family.

A sub-experiment may supply useful positive or negative evidence. It must never be described as the complete FMP research method.

A negative result from one representation means only that the exact frozen representation/protocol failed its gate. It does not prove that discovery-first market learning is exhausted.

## 3. Mandatory session bootstrap

Before proposing or continuing research, a new session must:

1. read `docs/project-state.md`;
2. read the latest relevant entries in `docs/decision-log.md`;
3. read the strategy-research section of `docs/master-spec.md`;
4. read `docs/research-testing-standard.md`;
5. read this guardrail;
6. identify separately:
   - the governing discovery-first method;
   - the currently active bounded experiment;
   - the current evidence window and any closed reserve;
   - the next authorized gate.

If `docs/project-state.md` is materially stale relative to later decision-log entries, refresh project state before opening a new research direction. Do not silently reason from the stale state.

## 4. Concrete discovery-first workflow

### Stage A — Define the measurement vocabulary

Use accepted leakage-safe measurements that describe the market rather than presuppose a final strategy. Relevant dimensions may include:

- direction/trend state;
- sideways/range state;
- volatility and volatility change;
- momentum and return structure;
- candle/range structure;
- session/time context;
- location relative to recent, session, or previous-period structure;
- spread/quote-quality context;
- bounded interactions among allowed measurements;
- fixed future return or price-path outcomes.

The vocabulary is not itself a strategy list.

### Stage B — Freeze the discovery protocol before judging results

Predeclare and freeze:

- exact discovery data range and source identities;
- exact leakage-safe measurements/features;
- exact future-outcome definitions and horizons;
- market-state/regime construction when used;
- minimum support;
- bounded search algorithm and search budget;
- transaction-cost treatment;
- duplicate/near-duplicate handling;
- search-volume and multiple-comparison accounting;
- candidate-freeze rule;
- later chronological confirmation/validation procedure.

Results may not be used to retroactively change these rules inside the same experiment.

### Stage C — Discover repeated behaviour

Search the frozen discovery window for conditional behaviours that repeat with adequate support.

The output at this stage is a **pattern hypothesis**, not automatically a tradable strategy.

The process must preserve failed searches and record the effective search volume.

### Stage D — Freeze selected patterns

Any selected pattern receives an immutable identity. Freeze the exact condition, direction, applicability, outcome interpretation, and any model/transform needed to reproduce it.

Validation data may test this frozen object. Validation data may not redesign it.

### Stage E — Chronological confirmation and validation

Evaluate the frozen pattern on later chronological evidence that was not used to invent or tune it whenever such evidence exists.

Require stability across appropriate years/subperiods, adequate support, realistic costs, and resistance to concentration in a tiny number of observations.

Previously inspected history remains retrospective evidence and must not be relabeled as untouched OOS.

### Stage F — Compile a strategy only after pattern survival

A surviving pattern may then be translated into exact executable research semantics, including:

- entry timing;
- LONG/SHORT/NO TRADE behavior;
- stop/target or exit semantics;
- overlap rules;
- applicability/regime conditions;
- cost assumptions;
- risk interface.

This compilation requires its own immutable version identity and must not rescue a weak pattern by outcome-aware tuning.

### Stage G — Robustness and realistic backtest

Test the compiled version with the existing FMP execution/risk machinery, including bid/ask semantics, spread/slippage stress, neighboring-condition checks where meaningful, yearly/regime breakdowns, concentration tests, and drawdown/tail behavior.

Complexity must earn its place.

### Stage H — Prospective evidence

Only after the exact challenger is frozen should genuinely new market evidence be collected.

The preferred progression is:

`prospective shadow -> fixed-version demo -> deployment review`

Running shadow/demo champions do not self-modify.

### Stage I — Learning loop

Completed prospective/demo evidence may motivate or train a new challenger.

Once evidence has influenced that new challenger, it becomes research/training evidence for that challenger and cannot also count as fresh validation. The materially changed challenger gets a new immutable identity and must prove itself on a later fresh prospective window.

## 5. Narrow-experiment rule

Before opening any successor experiment, its source/spec must answer:

1. What market behaviour is this representation intended to discover?
2. Which part of the DEC-268 measurement vocabulary does it cover?
3. What does it deliberately not cover?
4. Why is this bounded search useful after prior evidence?
5. What conclusion is justified by a negative result?
6. What conclusion is explicitly not justified by a negative result?
7. How does a survivor rejoin the main discovery-first workflow?

If those answers are absent, the experiment is not ready to become the next research direction.

## 6. EXP-065 interpretation

EXP-065 is a bounded **pairwise continuous-feature interaction sub-experiment** inside the discovery-first framework.

It tests whether exactly two existing continuous features have incremental interaction information after controlling their main effects under a frozen retrospective protocol.

It does **not** redefine FMP as a pairwise-interaction system, and a zero-qualifier EXP-065 result would not mean that discovery-first market-pattern research has failed.

After EXP-065 reaches its terminal result and that result is frozen, any successor direction must be justified explicitly against the broader discovery-first workflow rather than chosen merely as another mathematical transform.

## 7. Safety boundaries

This guardrail changes no existing execution authority.

Current and future sessions must honor the latest source-of-truth state for:

- consumed one-shot runs;
- no-rerun/no-retry rules;
- closed reserved data;
- candidate compilation;
- promotion;
- Phase 8B;
- shadow/demo order permissions;
- broker mutation;
- live orders;
- real-money action.

No research-method clarification can weaken those gates.
