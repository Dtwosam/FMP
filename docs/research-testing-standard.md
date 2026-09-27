# FMP V1 Research & Testing Standard

**Purpose:** Prevent fake profitability caused by leakage, unrealistic execution, cherry-picking, or unstable tuning.

## 1. Research doctrine

The default assumption for every strategy is: **it has no edge until proven otherwise**.

A strategy can fail and the project can still succeed by correctly rejecting it.

## 2. Chronological evaluation

Never use random train/test shuffling for final trading evaluation.

Final methodology uses chronological periods:

- development/train
- validation
- final untouched test
- later walk-forward windows

Exact date boundaries are selected after data acquisition/quality review and then frozen in a decision-log entry before serious model selection.

## 3. Final-test isolation

The final test period stays untouched until candidate selection is materially complete. Do not repeatedly inspect final-test performance while tuning parameters; that simply turns the test period into another validation set.

## 4. Look-ahead prohibition

At decision time `T`, every input must be computable from information available at or before the allowed observation cutoff for `T`.

Common forbidden leakage examples:

- using the high/low of a candle before that candle has closed when the strategy assumes close-time decisions;
- using tomorrow's session classification/statistics;
- global normalization fit using future data;
- feature selection performed on the final test set;
- labels leaking into rolling calculations;
- choosing stop/target intrabar order after seeing which route is profitable.

## 5. Signal timing contract

Every strategy must declare:

- observation timestamp
- when the signal becomes known
- earliest executable timestamp
- price side used for entry
- stop/target activation semantics

The backtester must enforce the contract.

## 6. Cost realism

Every backtest includes:

- bid/ask execution
- actual/derived spread
- explicit slippage model
- commission if relevant to the chosen venue
- financing/rollover when a holding period makes it relevant

Run cost-sensitivity scenarios rather than trusting one optimistic assumption.

## 7. Intrabar ambiguity

If 1-minute OHLC shows both stop and target could have been touched and ordering cannot be known:

1. use the predefined conservative ambiguity rule; or
2. mark the event ambiguous and exclude it only under a symmetrical, predeclared policy; or
3. revalidate promising candidates with higher-resolution/tick data.

Never pick the outcome that helps PnL.

## 8. Discovery-first rule for new research

The historical baseline families remain useful controls, but DEC-268 supersedes the requirement that all future strategies must begin from those predefined families.

For new post-DEC-268 research:

1. define an allowed discovery data range;
2. define leakage-safe market measurements and fixed future-outcome labels/horizons;
3. examine repeated behaviour across market states such as up/down/sideways structure, volatility, momentum, session/time, and spread conditions;
4. require adequate repeated observations rather than isolated profitable examples;
5. freeze any selected pattern as an exact immutable rule/model;
6. evaluate that frozen candidate on later chronological evidence not used to invent or tune it whenever such evidence exists.

Before a serious discovery run is used for candidate selection, freeze the search method, bounded search budget, minimum support, duplicate handling, transaction-cost treatment, and search-volume/multiple-comparison accounting.

The discovery data is allowed to reveal the pattern. Validation data is not allowed to redesign the pattern.

## 9. Parameter discipline

- Keep search spaces economically/structurally motivated and bounded.
- Record every serious parameter search.
- Penalize fragile single-point optima.
- Prefer broad stable regions of performance to one magic parameter.
- Do not keep retrying random variations until something looks profitable without accounting for the search process.

## 10. Minimum result breakdown

Every serious backtest reports:

- net return after costs
- expectancy per trade
- profit factor
- win rate
- average win
- average loss
- reward/risk distribution
- maximum drawdown
- recovery factor
- Sharpe/Sortino where meaningful
- trade count
- longest losing/winning streaks
- pair breakdown
- timeframe breakdown
- session breakdown
- calendar-year/subperiod breakdown
- cost-sensitivity breakdown

If probabilities are produced, add calibration/discrimination metrics.

## 11. Robustness checks

A candidate should be stress-tested across applicable dimensions:

- slightly worse spread/slippage
- neighboring parameters
- different years/subperiods
- pair-specific results
- session-specific results
- volatility regimes
- delayed entry assumptions when meaningful
- removal of top few winning trades

A strategy whose entire edge disappears after a tiny realism change is not deployment-ready.

## 12. Promotion gates

### Research -> Candidate
Required:
- positive net expectancy after realistic costs;
- adequate sample size for the strategy frequency;
- no discovered leakage;
- no obvious dependence on one tiny period or a few outlier trades;
- acceptable drawdown under fixed risk.

### Candidate -> Walk-forward
Required:
- untouched out-of-sample results remain viable;
- no material collapse of the underlying edge;
- robustness checks do not reveal a fragile artifact.

### Walk-forward -> Shadow
Required:
- repeated forward windows show positive aggregate expectancy and acceptable stability;
- training/tuning procedure is reproducible without peeking forward.

### Shadow -> Demo
Required:
- live quote handling, spread behavior, signal timing, and hypothetical outcomes materially resemble tested assumptions;
- operational/data errors are handled and logged;
- no orders have been sent in shadow mode.

### Demo -> Deployment Review
Required:
- enough demo trades and elapsed market regimes to compare live execution against research assumptions;
- realized spreads/slippage/execution errors are understood;
- risk controls are observed in practice;
- performance is not merely a very short lucky streak.

### Deployment Review -> Live
Never automatic. Requires separate explicit human approval and a new decision-log entry.

## 13. Experiment identity

Every serious experiment gets a stable ID, suggested format:

`EXP-YYYYMMDD-NNN`

Record hypothesis before reading results where practical.

## 14. Failed experiments

Keep them. A failed experiment prevents duplicate work and protects the project from rediscovering the same false edge.

## 15. Notebooks

Notebooks are for exploration and visualization, not hidden production logic. Any behavior required to reproduce a result must migrate into versioned library code with tests before that result can promote a strategy.


## 16. Post-final-test research revisions

DEC-039 recognizes that the original 2024-01-01 through 2026-08-20 final-test period was opened during Phase 7. That history remains valid market evidence, but it is no longer untouched for strategies invented or materially changed afterward.

For post-Phase-7 research:

- previously opened history may be reused for discovery, diagnostics, stress testing, and retrospective walk-forward analysis;
- results from already inspected periods must be labeled retrospective, not untouched OOS;
- discovery algorithms may search broadly inside their declared discovery data, but the discovery range, measurements/features, future-outcome definitions, minimum support, search algorithm/budget, search-volume accounting, candidate-freeze rule, and later validation procedure must be frozen before the run is used for promotion;
- a newly discovered pattern does not need to belong to a predefined strategy family;
- the number of patterns/rules/models, parameter variants, pair/timeframe cells, regime variants, and portfolio combinations inspected must be recorded where practical;
- broad search results require stronger robustness/concentration review than a one-shot predeclared candidate;
- no candidate may be promoted solely because it is the best result among a large search;
- genuinely prospective evidence begins only after the exact challenger version and evaluation protocol are frozen.

## 17. Multi-strategy and portfolio research

A portfolio can contain multiple independently validated strategy versions across EURUSD, GBPUSD, and USDJPY, but diversification claims must be measured rather than assumed.

Portfolio research must report:

- per-strategy and per-pair contribution;
- overlapping position periods;
- net and gross USD-direction exposure where applicable;
- concentration of positive PnL by strategy/pair/window;
- portfolio maximum drawdown;
- daily return distribution;
- cost sensitivity;
- performance with top contributors removed where meaningful.

A portfolio result is not considered robust merely because weak strategies are aggregated together.

## 18. Continuous-learning and demo-iteration separation

New observations may be used to research challengers, but the active champion set remains immutable during a registered shadow/demo/live campaign.

A challenger must:

1. receive a new immutable strategy/version identity;
2. record the data available at discovery or revision time;
3. pass the applicable frozen historical/retrospective gates;
4. enter fresh prospective evidence collection before any later promotion;
5. never replace a champion automatically.

Demo trading is an iterative learning source, not permission to tune the running strategy after every result. At a frozen review boundary, completed demo observations may be analysed and may motivate or train a challenger. Once those observations influence the challenger, that demo window is no longer fresh validation for the new version. The changed challenger must be tested on a later prospective shadow/demo window that was not used to design it.

The intended cycle is `fixed demo version -> analyse completed evidence -> new immutable challenger -> historical/retrospective checks -> fresh prospective evidence -> later fixed demo version`.

Self-modifying production behavior, hot-swapping, martingale, leverage escalation, post-loss emergency retuning, and outcome-aware threshold relaxation remain forbidden.
