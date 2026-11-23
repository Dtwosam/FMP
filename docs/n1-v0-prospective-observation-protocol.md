# N1-v0 prospective observation protocol

**Status:** PILOT AUTHORIZED BY DEC-638. Fetch has not started. The DEC-637 rule is unchanged.

**Rule:** N1-v0 News-Shock USD Continuation, as frozen in DEC-637.  
**Baseline of the authorization:** `845e571a451fed51e638140ea3d1f0c72fa8c907`.

## When collection may start

DEC-638 is the later approval required by DEC-637. It authorizes a two-event prospective quote pilot and nothing else.

The frozen signal commit is `78185a1aded7f5d97c296c16fdfd615f46934353`. The effective authorization timestamp is the committer timestamp of the DEC-638 decision commit. Every collected bar timestamp must be strictly after that instant.

The approved windows, from the BLS calendars accessed 2026-11-23, are:

1. Employment Situation for November 2026, Friday 4 December 2026, 08:30 America/New_York.
2. Consumer Price Index for November 2026, Thursday 10 December 2026, 08:30 America/New_York.

The quote set for each window is EURUSD, GBPUSD, and USDJPY at 08:29–08:34, plus EURUSD at 08:36–09:30. The source is new $0 Dukascopy 1-minute bid/ask for those minutes. November 2026 releases are already past and are not collected. Real Earnings at the CPI minute is not an N1 release.

A release counts as one of the two only when BLS records publication at 08:30 America/New_York. Any other status is kept and does not count. A replacement date needs a new recorded calendar citation before its quotes can be collected.

No quote is fetched before the first bar of an approved window. This pilot authorizes no historical read, no broker connection, and no demo, live, or real-money order.

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

## DEC-638 pilot record

DEC-638 grants the two-window pilot described above. The raw engine trade or rejection is stored separately from `review_n1_observation`. An incomplete label does not erase a stop that the engine already filled. The labeled slippage runs are 0.5, 0.2, and 1.0 adverse pips, each in its own run. The hypothetical commission remains 3.50 USD per standard lot per side, accessed 2026-11-17. Prospective quotes are not verified broker fills.

The recorder does not download quotes. Fetch stays closed until an approved window opens and the signal file still matches commit `78185a1aded7f5d97c296c16fdfd615f46934353`.

## Boundaries

DEC-469 / DEC-268 remain the governing method. N1-v0 is not Strategy V1 and not a catalogue cell. DEC-470 stays frozen. Annual run 385 stays unconsumed. No workflow is dispatched.
