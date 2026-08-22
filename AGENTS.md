# AGENTS.md — FMP Working Contract

This file is mandatory reading before modifying FMP.

## 1. Mission

Build a forex-only systematic trading engine that can prove or disprove whether a repeatable edge exists after realistic trading costs. Profitability is a hypothesis to test, never an assumption.

## 2. Read order for every new session

Before changing code or project decisions, read in this order:

1. `docs/project-state.md`
2. `docs/decision-log.md`
3. `docs/master-spec.md`
4. the current phase section in `docs/build-order.md`
5. any component spec relevant to the current task
6. recent commits touching the current phase

If a ChatGPT Project Source copy of `FMP_PROJECT_SOURCE.md` exists, treat it as a portable baseline, but the repository's current `project-state.md` and later decision-log entries win for current state.

## 3. Phase discipline

- Work on one numbered phase at a time.
- Do not skip a phase because a later task looks more interesting.
- Do not start a phase until the previous phase's acceptance gate is recorded as PASS in `project-state.md`.
- A phase is not complete because code exists. Tests, validation, artifacts, and acceptance criteria must pass.
- If a phase fails, fix it or document the blocker. Do not route around it.
- New ideas that are not required for the current phase go to the backlog section of `project-state.md`.

## 4. Scope discipline

V1 contains only EUR/USD, GBP/USD, and USD/JPY. The canonical source data is 1-minute bid/ask market data. Derived research bars are 5m, 15m, and 1h.

Do not introduce indices, gold, crypto, commodities, exotic FX pairs, social sentiment, paid data, paid AI APIs, or paid infrastructure without an explicit V1 spec amendment.

## 5. Cost discipline

Development budget is $0. Prefer local computation and free/open-source tooling. If a proposed dependency or service may incur money, stop and document the alternative instead of enabling it.

## 6. Data discipline

- Raw source files are immutable.
- Raw files are never repaired by hand.
- Normalization and cleaning are code-driven and reproducible.
- UTC is the storage time standard.
- Keep bid and ask separate.
- Derived bars must come from canonical 1-minute data using deterministic, tested rules.
- Every dataset used for research needs provenance: source, symbol, time range, ingestion version, schema version, and checksum/manifest where practical.
- Never silently drop or modify suspicious data. Flag and measure it.

## 7. Research discipline

- No look-ahead bias.
- No random train/test shuffling for final time-series evaluation.
- No feature may depend on information unavailable at decision time.
- Fit leakage-sensitive transforms only on the training window.
- Keep a final untouched test period.
- Model bid/ask, spread, slippage assumptions, and relevant fees/financing.
- Ambiguous intrabar stop/target ordering must use a conservative or explicitly documented rule; never choose the profitable path.
- Record rejected signals and `NO TRADE` decisions, not just executed winners/losers.

## 8. Complexity rule

Start simple. Machine learning is optional. A complex model is accepted only when it materially improves robust out-of-sample behavior over a simpler baseline after costs.

Do not add an indicator, feature family, model, dashboard, database, service, or abstraction simply because it is available.

## 9. Risk rule

Risk logic is independent from strategy logic. Initial research/demo defaults are:

- default risk/trade: 0.25% equity
- hard maximum risk/trade: 0.50% equity
- maximum simultaneous open risk: 1.00% equity
- maximum daily realized loss before halt: 1.50% equity

Forbidden: martingale, doubling after losses, removing stops because a trade is losing, or increasing leverage to recover losses.

## 10. TDD and verification

For implementation tasks:

1. write or identify the failing test/acceptance check;
2. run it and observe failure when appropriate;
3. implement the smallest correct change;
4. run focused tests;
5. run the phase/regression suite;
6. inspect output/artifacts;
7. update documentation/state when behavior or phase status changes.

Do not claim a phase or task is complete without actual verification evidence.

## 11. Experiment logging

Every meaningful strategy, feature, model, cost, split, or parameter experiment must get an experiment ID and record in `docs/experiment-log.md` (or a later machine-readable experiment registry that preserves the same fields).

Failed experiments remain in history. Never delete them to make the research record look cleaner.

## 12. Change control

Any change to the following requires an explicit decision-log entry and corresponding source-of-truth edit:

- V1 instruments
- $0 constraint
- canonical data granularity
- testing/promotion gates
- risk hard limits
- real-money deployment rules
- phase order

## 13. Git discipline

- Keep commits scoped to the current task.
- Never commit market-data files or secrets.
- Never commit broker tokens/account credentials.
- Prefer small reviewable commits with tests.
- Tag major phase freezes/checkpoints once verified.

Suggested checkpoint tags:

- `fmp-v1-phase0-source-of-truth`
- `fmp-v1-phase1-data`
- `fmp-v1-phase2-normalized-data`
- `fmp-v1-phase3-backtester`
- `fmp-v1-phase4-baselines`
- `fmp-v1-phase5-features`
- `fmp-v1-phase6-models`
- `fmp-v1-phase7-walk-forward`
- `fmp-v1-phase8-shadow`
- `fmp-v1-phase9-demo`

## 14. Safety rule for live trading

Phase 11 can never start automatically. Even a fully passing Phase 10 requires a new explicit human approval recorded in the decision log before any real-money execution path is enabled.
