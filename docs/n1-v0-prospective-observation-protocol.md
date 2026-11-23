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

Do not drop NO TRADE rows or failures. Do not replace a missing 09:30 bar with a manufactured exit. Store the `review_n1_observation` label with the engine result. The label does not replace that result.

## What the early record is for

Early observations are an operational check and a descriptive cost check. A count of 12 or 24 events is not statistical proof of profitability. A synthetic pass is not that record. Outcomes from the record must not change the frozen rule, the stop, the entry minute, or the risk fraction.

## Costs

The bid/ask spread stays inside the quotes. A published commission may be added once, through the existing commission model. The IC Markets Raw Spread MetaTrader quotation of 3.50 USD per standard lot per side, accessed 2026-11-17, is the hypothetical commission used in the synthetic check. It is not verified live execution. Dukascopy quotes are not verified broker fills. The engine applies one adverse slippage assumption per run. A worse slippage figure belongs in a separate run. It is not an asymmetric or worst-extreme fill inside one run.

## Data quality

`review_n1_observation` requires these canonical bid/ask bars before an observation is complete:

- EURUSD, GBPUSD, and USDJPY at 08:29, 08:30, 08:31, 08:32, 08:33, and 08:34 America/New_York.
- EURUSD at every minute from 08:36 through 09:30 America/New_York, including the entry bar and the scheduled-exit bar.

The 08:35 EURUSD bar is outside that set. The decision is timestamped 08:35, the position is not open on that bar, and the signal does not read it. Its absence hides no stop path.

The label is applied after the engine returns. It leaves the 08:35 decision, the original stop, and the engine result unchanged.

- `COMPLETE` means every required bar is present.
- `INCOMPLETE` means at least one required bar is absent. The missing labels stay on the row.
- `ordinary_n1_time_exit` is true only when the grid is complete and the engine reason is `TIME_EXIT`.
- A missing 09:30 bar leaves the engine reason `END_OF_DATA`. That reason is kept and is not an ordinary N1 time exit, including if a later reader passes `TIME_EXIT` into the review.
- A missing minute from 08:36 through 09:29 leaves the observation incomplete when the engine still returns `TIME_EXIT`. The unobserved stop path is not treated as clear.
- A missing 08:36 bar stays the existing `TIMING_CONTRACT` rejection and is incomplete.
- A missing signal-window quote stays NO TRADE `MISSING_QUOTE` and is incomplete.
- A duplicate `(timestamp_utc, symbol)` raises. The review does not choose a bar.
- A complete grid with `STOP`, with NO TRADE, or with a risk rejection is not an ordinary time exit. Those rows stay.

## Next owner decision — not approved

This section names the later decision that would be required before any prospective quote is collected. It does not grant that decision. DEC-637 remains a synthetic exception. Until the later decision is recorded, this protocol authorizes no market-data read.

The later decision has to state all of the following.

**Data source.** New canonical 1-minute bid and ask bars for EURUSD, GBPUSD, and USDJPY only, in the existing quote schema, for minutes that occur after the approval timestamp. The feed is the $0 Dukascopy bid/ask source already named in the master spec, limited to bars that did not exist at approval. Protected annual artefacts, the stored historical research files, a new vendor, a paid feed, and a broker tick stream are outside that source. If those bars cannot be captured at $0 without opening a closed path, collection stays blocked.

**Collection start.** The first BLS CPI or BLS Employment Situation release that is actually published at 08:30 America/New_York strictly after the collection approval is recorded. No backfill. No release whose publication minute is already past at approval. The December 2026 BLS list shows how the calendar is read. It is not a start date: Friday 4 December 2026, 08:30 AM Eastern Time, Employment Situation for November 2026; Thursday 10 December 2026, 08:30 AM Eastern Time, Consumer Price Index for November 2026. Real Earnings printed at the same CPI minute is not an N1 release. Schedule: <https://www.bls.gov/schedule/2026/12_sched_list.htm>, accessed 2026-11-23, last modified 9 November 2026. The page states that all times are Eastern Time. CPI home <https://www.bls.gov/cpi/>, accessed 2026-11-23, schedules the November 2026 CPI for 10 December 2026 at 8:30 A.M. Eastern Time. Series calendars: <https://www.bls.gov/schedule/news_release/cpi.htm> and <https://www.bls.gov/schedule/news_release/empsit.htm>. Publication status comes from BLS. It is not inferred from price.

**Data quality.** Store `review_n1_observation` with every row. Keep `INCOMPLETE` rows and `END_OF_DATA` rows. Neither counts as an ordinary 09:30 time exit. Keep NO TRADE, missing-quote, and rejected-entry rows.

**Costs.** The bid/ask spread stays inside the quotes. One published commission figure, labeled hypothetical, and one adverse slippage assumption per run. The IC Markets Raw Spread MetaTrader figure of 3.50 USD per standard lot per side, accessed 2026-11-17, remains the labeled figure until a later decision replaces the citation. The frozen rule exits at 09:30, so the observation does not book overnight financing. Prospective quote observations are not verified broker fills. No order is placed to observe a fill. The development budget stays $0.

**Still closed unless a separate entry says otherwise.** Annual catalogue execution, annual run 385, workflow enablement, DEC-470 edits, parameter changes, broker connection, demo, live, and real-money trading. DEC-469 / DEC-268 remain the governing method.

## Boundaries

DEC-469 / DEC-268 remain the governing method. N1-v0 is not Strategy V1 and not a catalogue cell. DEC-470 stays frozen. Annual run 385 stays unconsumed. No workflow is dispatched.
