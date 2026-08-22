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

## 8. Baseline-first rule

Before ML, test transparent baseline families such as:

- session breakout
- trend continuation
- mean reversion
- previous-day high/low rejection
- volatility breakout
- session high/low sweep/rejection

The ML layer must demonstrate incremental value over these baselines after costs and on unseen data.

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
