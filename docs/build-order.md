# FMP V1 Build Order

**Status:** Approved implementation sequence  
**Rule:** Complete phases in order. Do not skip promotion gates.  
**Spec:** `docs/master-spec.md`

## Global constraints

- Forex only: EUR/USD, GBP/USD, USD/JPY.
- Canonical source data: 1-minute bid/ask.
- Derived bars: 5m, 15m, 1h.
- Development budget: $0.
- Raw data immutable.
- Realistic costs mandatory.
- No look-ahead leakage.
- Machine learning optional and downstream of baselines.
- No real money before a separately approved Phase 11.

---

## Phase 0 — Source of truth & repository foundation

### Goal
Freeze the stable rules and create enough project state that future sessions can continue without relying on conversation memory.

### Deliverables
- `README.md`
- `AGENTS.md`
- `docs/master-spec.md`
- `docs/architecture.md`
- `docs/build-order.md`
- `docs/data-spec.md`
- `docs/research-testing-standard.md`
- `docs/risk-execution-policy.md`
- `docs/experiment-log.md`
- `docs/project-state.md`
- `docs/decision-log.md`
- `docs/source-register.md`
- portable `FMP_PROJECT_SOURCE.md`

### Acceptance gate
PASS when documents are internally consistent, contain no unresolved placeholders required for Phase 1, and establish precedence/change-control rules.

### Checkpoint
`fmp-v1-phase0-source-of-truth`

---

## Phase 1 — Historical data acquisition

### Goal
Reproducibly acquire raw 1-minute bid/ask history for the three V1 pairs without paid services.

### Implementation tasks
1. Create minimal Python project/package and test harness.
2. Define source-adapter and acquisition-manifest types.
3. Build a small bounded Dukascopy acquisition spike against official/free historical data access.
4. Freeze retrieval method only after the spike verifies actual fields, timestamps, limits, and reproducibility.
5. Implement resumable chunked downloader/ingestor.
6. Add checksum + atomic-write behavior so partial data cannot be mistaken for complete data.
7. Create CLI for one pair/range and then all V1 pairs.
8. Acquire a small golden sample and test it.
9. Acquire full target history.
10. Produce coverage/manifests, not a claim of cleanliness.

### Required tests
- chunk naming/path determinism
- resume behavior
- duplicate retry does not corrupt existing successful chunk
- checksum/manifest creation
- bad/partial response rejected
- timestamp/source metadata retained

### Acceptance gate
PASS when all three pairs have reproducibly acquired raw history and manifests/checksums, and a clean environment can reacquire a bounded sample using only documented free requirements.

### Checkpoint
`fmp-v1-phase1-data`

---

## Phase 2 — Validation, normalization & derived bars

### Goal
Convert source data into trustworthy canonical 1-minute data and deterministic 5m/15m/1h datasets.

### Implementation tasks
1. Freeze canonical schema types/version.
2. Parse source format to canonical rows without overwriting raw files.
3. Implement structural and quote-sanity validators.
4. Distinguish expected market closures from suspicious gaps where possible.
5. Produce pair-level data-quality reports.
6. Implement deterministic timeframe resampling.
7. Add timezone/session-boundary utility foundations needed later.
8. Produce processed data manifests and checksums.

### Required tests
- OHLC sanity
- ask/bid anomaly detection
- duplicates
- missing timestamps
- exact 5m/15m/1h boundary examples
- weekend gap behavior
- DST-sensitive time utility examples

### Acceptance gate
PASS when all pairs have validated canonical data, quantified anomalies/gaps, deterministic derived bars, and reproducible processed manifests.

### Checkpoint
`fmp-v1-phase2-normalized-data`

---

## Phase 3 — Backtesting engine

### Goal
Create a trustworthy simulator before judging strategies.

### Implementation tasks
1. Freeze signal timing and order lifecycle concepts.
2. Implement account/equity state.
3. Implement long/short bid/ask entry/exit semantics.
4. Implement stop and target handling.
5. Implement explicit intrabar ambiguity policy.
6. Implement position sizing through the risk engine.
7. Implement spread/slippage/cost models.
8. Implement daily halt and open-risk caps.
9. Record rejected signals and reason codes.
10. Produce deterministic run/trade artifacts and metrics.

### Required golden tests
- long buy at ask, exit at bid
- short sell at bid, cover at ask
- stop hit
- target hit
- both stop/target inside one bar -> conservative/documented outcome
- risk size math for JPY and non-JPY pip conventions
- daily halt
- simultaneous-risk rejection
- deterministic repeated run equality

### Acceptance gate
PASS only when hand-calculated golden scenarios agree with the engine and regression tests prove costs/risk semantics.

### Checkpoint
`fmp-v1-phase3-backtester`

---

## Phase 4 — Baseline strategy research

### Goal
Establish transparent benchmarks before ML.

### Initial families
- session breakout
- trend continuation
- mean reversion
- previous-day high/low rejection
- volatility breakout
- session high/low sweep/rejection

### Process
1. Implement one strategy at a time behind a common interface.
2. Predeclare parameter ranges/hypotheses.
3. Backtest per pair and timeframe.
4. Apply cost sensitivity and subperiod breakdowns.
5. Log every serious experiment, including failures.
6. Promote only candidates meeting research gate.

### Acceptance gate
PASS when baseline benchmark tables exist for every tested family and at least one of these is true:
- one or more strategies qualify as serious candidates; or
- evidence clearly shows current baselines have no robust edge, with failures recorded and next research question justified.

### Checkpoint
`fmp-v1-phase4-baselines`

---

## Phase 5 — Leakage-safe feature engine

### Goal
Create reusable descriptive market features without hiding future information.

### Feature families
- returns
- volatility/range
- trend/structure
- momentum
- candle structure
- session/time
- market location vs previous/session highs/lows
- spread/quote quality
- relative source activity where valid

### Required tests
- each rolling feature uses only allowed past/current closed data
- session/DST correctness
- previous-day/session-level reset boundaries
- deterministic feature regeneration
- no accidental forward-fill across inappropriate market closures

### Acceptance gate
PASS when feature datasets are versioned/reproducible and leakage tests cover all promoted feature families.

### Checkpoint
`fmp-v1-phase5-features`

---

## Phase 6 — Statistical / ML experiments

### Goal
Determine whether models add robust incremental value over transparent baselines.

### Initial model priority
Prefer simple models first (e.g., logistic regression, tree boosting) before neural/deep models.

### Potential tasks
- target-before-stop probability
- expected-return estimation
- strategy signal filtering
- market-regime classification

### Rules
- chronological splits only
- fit preprocessors on training windows only
- compare against baseline without ML
- calibrate probabilities where relevant
- record model/data/config/seed
- reject complexity that does not materially improve robust out-of-sample results

### Acceptance gate
PASS means the ML question has been answered honestly. Models may be rejected entirely. V1 does not require ML to progress if simple strategies are stronger.

### Checkpoint
`fmp-v1-phase6-models`

---

## Phase 7 — Walk-forward evaluation

### Goal
Approximate repeated real-world retraining/selection through historical time without peeking ahead.

### Process
1. Freeze training/validation/forward window protocol.
2. Refit only using information available before each forward window.
3. Trade/simulate the next forward window untouched.
4. Roll forward and repeat.
5. Aggregate stability, drawdown, costs, and regime breakdowns.

### Acceptance gate
PASS for promotion only if aggregate walk-forward expectancy remains positive/acceptable and the edge is not isolated to one window.

### Checkpoint
`fmp-v1-phase7-walk-forward`

---

## Phase 8 — Live shadow mode

### Goal
Run the engine on live quotes with **structurally impossible order submission**.

### Implementation tasks
- choose free live quote/practice integration after a small connector spike
- live quote normalization
- stale-data detection
- scheduler/event loop
- strategy + decision + risk execution in shadow mode
- prediction/outcome ledger
- operational error logging

### Acceptance gate
PASS when live signals, observed spreads, timing, and hypothetical outcomes materially match research assumptions and the shadow adapter proves it cannot place orders.

### Checkpoint
`fmp-v1-phase8-shadow`

---

## Phase 9 — Demo trading

### Goal
Execute the same approved logic against a practice/demo account with no real capital.

### Candidate execution paths
- OANDA fxTrade Practice REST/streaming API
- MetaTrader 5 demo bridge

Choice is deferred until this phase and must consider availability to the operator/broker jurisdiction, reliability, and actual demo access at that time.

### Required controls
- practice-account assertion
- broker symbol mapping
- order validation
- protective stop handling
- requested-vs-fill price logging
- position reconciliation
- restart/recovery behavior
- daily halt
- no secret committed to Git

### Acceptance gate
PASS when demo execution behaves reliably over enough trades/time to compare actual execution costs and operational behavior with research assumptions.

### Checkpoint
`fmp-v1-phase9-demo`

---

## Phase 10 — Deployment review

### Goal
Decide whether evidence justifies risking any real money.

### Review package
- full backtest and robustness results
- final untouched test
- walk-forward record
- shadow record
- demo record
- execution-cost reconciliation
- drawdown and tail events
- operational failures
- risk-control events
- known limitations

### Possible outcomes
- `REJECT_LIVE`
- `EXTEND_DEMO`
- `RESEARCH_REVISION_REQUIRED`
- `ELIGIBLE_FOR_EXPLICIT_LIVE_APPROVAL`

No outcome automatically activates live trading.

---

## Phase 11 — Live execution

### Entry condition
A new explicit human approval is recorded after Phase 10. Without that record, live execution remains disabled.

### Initial principle
If ever approved, start materially smaller than the risk ceiling used in simulation/demo and preserve immediate kill-switch capability. Exact live capital/risk is not part of the V1 source-of-truth today and must be decided from Phase 10 evidence.

---

## Build-order change control

Changing phase order or skipping an acceptance gate requires:

1. reason documented in `decision-log.md`;
2. master spec/build order updated together;
3. `project-state.md` updated;
4. change committed before implementation proceeds.
