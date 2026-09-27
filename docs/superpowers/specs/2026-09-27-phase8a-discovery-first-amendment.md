# Phase 8A — Discovery-First Strategy Research and Iterative Demo Learning Amendment

**Date:** 2026-09-27  
**Status:** APPROVED SOURCE-OF-TRUTH AMENDMENT  
**Decision:** DEC-268  
**Scope:** Future Phase 8A research direction and later Phase 9 demo-learning semantics  
**Execution effect:** No historical, shadow, demo, broker, live, real-money, or trading execution is authorized by this document

## 1. Purpose

FMP previously emphasized a small set of transparent, human-predefined strategy families before broader model research. Those experiments remain valid historical evidence, but they are no longer the default way to generate new post-DEC-268 trading ideas.

For future research, FMP will start from the market data and ask which repeated, measurable behaviours occur under different market states. Strategy rules or models are derived only after those behaviours are found.

The intended loop is:

`historical pattern discovery -> freeze candidate -> separate chronological validation -> prospective shadow -> fixed-version demo -> learn from completed demo evidence -> create a new challenger version -> fresh prospective validation/demo`

The objective is not to keep tuning until a backtest or demo looks profitable. The objective is to find behaviour that repeats on data that was not used to invent or tune the candidate.

## 2. Historical experiments remain evidence

DEC-268 does not delete, rewrite, or relabel any prior experiment.

In particular:

- the six historical rule families remain transparent benchmarks and useful controls;
- EXP-20260922-015 and its 567 catalog identities remain immutable historical evidence;
- the already-consumed authoritative EXP-015 Stage A run may finish once and must still receive its terminal evidence review;
- that Stage A result does not automatically authorize the old Stage B/C path;
- no EXP-015 retry, rerun, replacement, threshold rescue, or silent parameter expansion is authorized.

Future chats must not describe the six historical families as the required or complete strategy universe.

## 3. Discovery-first research

A new discovery experiment may examine the accepted EURUSD, GBPUSD, and USDJPY histories and derive candidate patterns from repeated market behaviour rather than beginning with a named strategy family.

Allowed discovery dimensions include leakage-safe combinations of:

- direction/trend state;
- sideways/range state;
- volatility and volatility change;
- momentum and return structure;
- candle/range structure;
- session/time context;
- location relative to recent/session/previous-period structure;
- spread/quote-quality context;
- interactions among the above;
- forward price-path or return outcomes defined at fixed future horizons.

The list is a measurement vocabulary, not a list of strategies. A discovered candidate may resemble a known strategy or may describe a different conditional pattern.

## 4. Discovery protocol must be frozen before results are judged

Data-driven discovery creates a larger multiple-comparison risk than a small hand-written grid. Therefore each serious discovery run must freeze, before the run is used to select candidates:

- exact discovery data range and dataset identities;
- exact leakage-safe input features/measurements;
- exact future-outcome definitions and horizons;
- market-state/regime construction method, if any;
- minimum observation/support requirements;
- search algorithm and bounded search budget;
- treatment of transaction costs in candidate scoring;
- duplicate/near-duplicate pattern handling;
- multiple-comparison/search-volume accounting;
- candidate-freeze rule;
- the later chronological validation procedure.

The discovery algorithm is allowed to find the pattern. The validation data is not allowed to decide what pattern should have been discovered.

## 5. Candidate freeze and historical validation

Once a pattern is selected from discovery data:

1. translate it into an exact reproducible rule/model and immutable version identity;
2. freeze its entry, exit, no-trade, cost, and applicability semantics;
3. evaluate it on a later chronological window not used to choose or tune that candidate whenever such a window exists;
4. run cost, concentration, neighbouring-condition, regime, and subperiod robustness checks;
5. reject it if its edge materially collapses.

Because the original 2015-2026 history has already been extensively inspected, post-DEC-268 evidence from previously opened periods must be labelled retrospective. It may support robustness, but it cannot be called newly untouched evidence.

## 6. Prospective shadow remains the first genuinely new market evidence

Before a newly frozen candidate can place demo orders, FMP should observe it prospectively on live quotes with no order submission when practical.

Shadow evidence checks:

- signal timing;
- current spread behaviour;
- live data completeness/liveness;
- strategy applicability;
- hypothetical execution assumptions;
- portfolio/risk interactions.

Shadow does not tune the running candidate in place.

## 7. Demo trading is an iterative learning source

Demo trading is not only a final pass/fail rehearsal. Completed demo campaigns may supply valuable fresh observations for future research.

However:

- a registered demo campaign runs one immutable champion/candidate version;
- the running strategy/model does not self-modify;
- demo results may be analysed after or at a predeclared review boundary;
- any material change creates a new immutable challenger version;
- once demo data has been used to tune or choose that new version, that data becomes research/training evidence for it;
- the changed version must then prove itself on a later fresh prospective shadow/demo window that was not used for the change;
- losing demo periods must not trigger martingale, leverage escalation, emergency threshold relaxation, or outcome-aware rule changes.

This creates the repeatable loop:

`demo version N -> analyse -> challenger N+1 -> historical/retrospective checks -> fresh prospective evidence -> demo version N+1`

A better-looking fit to old demo observations is not itself evidence that N+1 is better.

## 8. Promotion meaning

Profitability remains a hypothesis, not an assumption.

A candidate may advance only when the evidence appropriate to its stage remains viable after realistic costs and risk controls. Data-driven discovery does not weaken the existing no-leakage, cost, drawdown, exposure, reproducibility, or human-approval requirements.

No demo result authorizes live trading. Phase 10 review and separate Phase 11 human approval remain mandatory.

## 9. Immediate Phase 8A consequence

After DEC-268:

- future strategy discovery is discovery-first by default;
- historical six-family work remains benchmark/history, not the mandatory next search;
- the current EXP-015 Stage A run is allowed only to finish and be reviewed as already-consumed evidence;
- old EXP-015 Stage B/C execution is not automatically opened by Stage A survivors;
- the next new research implementation should define a bounded discovery-first protocol that mines market states and future outcomes across the three V1 pairs without prespecifying the final strategy family;
- Phase 8B, Phase 9 demo orders, broker mutation, live orders, real-money action, and trading remain locked until their respective gates.

## 10. Precedence

This amendment supersedes statements in older source-of-truth documents that require all future strategy discovery to start with the six predefined baseline families or require ML to be strictly downstream of those families.

It does not supersede:

- the V1 instrument universe;
- canonical data rules;
- leakage controls;
- realistic-cost requirements;
- immutable experiment/version evidence;
- independent risk limits;
- phase safety boundaries;
- the requirement for separate explicit live-trading approval.
