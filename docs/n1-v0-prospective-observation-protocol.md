# N1-v0 prospective observation protocol

**Status:** WRITTEN UNDER DEC-637. Collection is not approved.

**Rule:** N1-v0 News-Shock USD Continuation, as frozen in DEC-637.  
**Baseline of the authorization:** `845e571a451fed51e638140ea3d1f0c72fa8c907`.

## When collection may start

Two approvals are required before any quote is collected:

1. DEC-637 is the repository record of the rule.
2. A later, separate owner approval names this frozen rule and authorizes collection.

Until that second approval, this document authorizes no market-data read, no historical backtest, no broker connection, and no demo, live, or real-money order.

## What a later collection would record

Record every scheduled BLS CPI release and every scheduled BLS Employment Situation release in the approved window. Keep releases that were not published, were delayed, were cancelled, or were published at a time other than 08:30 America/New_York.

For each release, keep:

- the release identity, kind, publication status, and actual publication timestamp;
- the N1-v0 decision, including NO TRADE and its reason code;
- the original protective stop when a directional decision exists;
- the engine rejection or the closed trade, including a missing entry bar, an invalid stop at the entry open, a gap stop, and a 09:30 New York exit;
- the one slippage assumption used for that run;
- the commission figure and its published source, labeled as a hypothetical package.

Do not drop NO TRADE rows or failures. Do not replace a missing 09:30 bar with a manufactured exit.

## What the early record is for

Early observations are an operational check and a descriptive cost check. A count of 12 or 24 events is not statistical proof of profitability. A synthetic pass is not that record. Outcomes from the record must not change the frozen rule, the stop, the entry minute, or the risk fraction.

## Costs

The bid/ask spread stays inside the quotes. A published commission may be added once, through the existing commission model. The IC Markets Raw Spread MetaTrader quotation of 3.50 USD per standard lot per side, accessed 2026-11-17, is the hypothetical commission used in the synthetic check. It is not verified live execution. Dukascopy quotes are not verified broker fills. The engine applies one adverse slippage assumption per run. A worse slippage figure belongs in a separate run. It is not an asymmetric or worst-extreme fill inside one run.

## Boundaries

DEC-469 / DEC-268 remain the governing method. N1-v0 is not Strategy V1 and not a catalogue cell. DEC-470 stays frozen. Annual run 385 stays unconsumed. No workflow is dispatched.
