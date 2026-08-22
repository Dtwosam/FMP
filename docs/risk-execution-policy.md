# FMP V1 Risk & Execution Policy

**Status:** Approved V1 research/demo baseline

## 1. Separation

Risk management is independent from alpha/strategy logic. A strategy may request a trade; the risk engine may reject it.

## 2. Initial research/demo risk defaults

- Default risk per trade: **0.25% of current equity**
- Hard maximum risk per trade: **0.50% of current equity**
- Maximum simultaneous open risk: **1.00% of current equity**
- Maximum daily realized loss before trading halt: **1.50% of start-of-day/current policy equity basis**

The exact daily-loss equity basis must be frozen during Phase 3 before demo execution. Until then, no alternate interpretation may be silently used.

## 3. Position sizing principle

Position size is derived from:

```text
allowed monetary risk
/ loss per unit if stop is hit
= maximum position units
```

Desired profit never determines position size.

## 4. Mandatory order protection

Any demo/live order design must have a defined invalidation/stop policy before submission. Strategies may not remove or widen a stop merely because a position is losing.

## 5. Forbidden behavior

- martingale
- doubling after losses
- revenge/loss-chasing logic
- increasing size to recover a drawdown
- averaging down solely to improve entry
- removing stops because a trade is losing
- silently exceeding portfolio/open-risk limits

## 6. `NO TRADE`

The risk engine can reject a trade because of:

- per-trade risk cap
- simultaneous risk cap
- daily halt
- bad/abnormal spread
- invalid quote/data state
- conflicting exposure
- correlated exposure
- broker/order validation failure
- later event-risk filter

Every rejection receives a machine-readable reason code and human-readable explanation.

## 7. Correlation/exposure

EUR/USD, GBP/USD, and USD/JPY can express overlapping USD risk. Before multi-position demo/live operation, the system must prevent multiple positions from accidentally creating much larger effective USD exposure than the nominal per-trade risks imply.

The exact method can begin conservative (aggregate caps/rules) before requiring a more complex rolling-correlation model.

## 8. Spread policy

A signal can be valid while execution is invalid. The decision/risk boundary must support rejecting a signal when current spread is abnormal relative to the strategy's tested distribution.

## 9. Slippage

Backtests use explicit slippage assumptions and sensitivity scenarios. Demo mode records requested price, fill price, timestamp, and slippage so research assumptions can be reconciled against reality.

## 10. Daily halt behavior

When the configured daily realized-loss threshold is reached:

- block new entries;
- do not automatically close existing positions unless a separate risk rule requires it;
- log the halt reason and time;
- require the next trading-day reset policy to be deterministic and tested.

## 11. Operational safety

Demo/live execution must fail closed where possible. Examples:

- stale quote -> reject new order
- missing price side -> reject
- unknown symbol mapping -> reject
- size calculation error -> reject
- broker rejects protective stop -> do not treat the position as safely opened

## 12. Shadow mode guarantee

Shadow mode cannot send an order. This must be enforced structurally, not by relying on a UI toggle or operator memory.

## 13. Demo/live adapter boundary

The core engine emits broker-independent `OrderIntent`. A broker adapter translates it to venue-specific parameters. Broker credentials and account IDs stay outside Git and outside experiment records.

## 14. Real-money lock

Live execution remains disabled by default. Phase 10 cannot flip it on automatically. Phase 11 requires a new explicit approval recorded in `docs/decision-log.md` after demo evidence is reviewed.
