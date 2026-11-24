# N1-v0 prospective observation protocol

**Status:** PILOT AUTHORIZED BY DEC-638. Quote collection is blocked on the daily-file transport envelope. The DEC-637 rule is unchanged. Fetch has not started.

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

No quote is fetched before the first bar of an approved window. The public Dukascopy object for these minutes is a whole UTC-day file. Downloading that file is a separate authorization, and DEC-638 does not include it. This pilot authorizes no historical read, no broker connection, and no demo, live, or real-money order.

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

The recorder rejects a supplied 08:35 bar. The N1 decision timestamp stays 08:35 America/New_York and the earliest execution stays the 08:36 bar. `append_labeled_pilot_evidence` appends three slippage rows to `n1-v0-pilot-evidence.jsonl` and leaves an earlier row in place. A synthetic fixture is class `synthetic_fixture_not_market_evidence`. A prospective class requires origin `prospective_market` plus BLS verification and retrieval timestamps strictly after 2026-11-23T15:13:54+01:00. The recorder does not download quotes. The signal file must still match commit `78185a1aded7f5d97c296c16fdfd615f46934353`.

## Dukascopy transport envelope — not approved

DEC-638 names specific New York minutes. `DukascopySource.url_for` identifies one UTC-day object:

`https://datafeed.dukascopy.com/datafeed/{PAIR}/{YEAR}/{ZERO_BASED_MONTH}/{DD}/{SIDE}_candles_min_1.bi5`

December is zero-based month 11. The 10 December 2026 EURUSD BID object is exactly:

`https://datafeed.dukascopy.com/datafeed/EURUSD/2026/11/10/BID_candles_min_1.bi5`

That object is the whole UTC day. `MINUTE_WINDOW_DOWNLOAD_SUPPORTED` is false. There is no minute-range URL. `acquire_chunk` would download the unauthorized minutes and write them into the historical raw store.

The existing pilot cannot collect valid Dukascopy evidence while staying inside DEC-638. The approved minutes are inside the daily file, and retaining the rest of the file would exceed the approved list.

This record does not grant the missing permission. The minimum additional owner authorization is this sentence:

For the two DEC-638 dates only, 2026-12-04 and 2026-12-10, authorize download of the twelve public daily BID and ASK bi5 files — EURUSD, GBPUSD, and USDJPY, each side — as a transport envelope. Store them outside the historical Dukascopy tree. Refuse any path whose resolved parts include `dukascopy`. SHA-256 the compressed bytes. Pass only the DEC-638 minutes to the recorder. Discard every other minute, including 08:35, and do not evaluate or retain those minutes as research bars. No workflow, schedule, or broker. November 2026 and every other date stay closed. A replacement calendar date needs its own recorded citation.

Until that authorization is recorded, stop before any download.

## Manual event-day procedure

The operator runs this procedure by hand after the relevant bars have completed and the BLS publication status has been verified. It does not start a workflow, a recurring job, an automatic download, or a broker connection.

1. Wait until the window's bars have completed: after 09:30 America/New_York on 4 December 2026 or 10 December 2026. Both dates are EST (UTC−5), so 08:29 New York is 13:29 UTC and 09:30 New York is 14:30 UTC. The whole window sits inside that UTC date.
2. Read the publication status from the official BLS calendar or publication record. Price does not establish publication. A delayed, cancelled, unpublished, or retimed release is retained and does not consume one of the two slots. Quotes for a replacement date wait for a new recorded BLS citation.
3. Stop before any download until the transport envelope above is an approved decision. `append_labeled_pilot_evidence` accepts caller-supplied bars and does not fetch them.
4. After that authorization exists: download the twelve daily files for the event date into a directory outside the historical store, hash the compressed bytes, retain only the approved New York minutes, and drop 08:35 and every other minute. Call `append_labeled_pilot_evidence` with origin `prospective_market`, a UTC BLS verification timestamp, and a UTC retrieval timestamp, both strictly after 2026-11-23T15:13:54+01:00. The signal blob must still match `78185a1aded7f5d97c296c16fdfd615f46934353`.
5. The writer appends three JSON lines, schema `fmp-n1-v0-pilot-evidence-v1`, for slippage 0.5, 0.2, and 1.0. Identity is evidence origin, release id, and slippage. A repeat raises `DuplicatePilotObservation` and leaves the earlier bytes unchanged. A directory whose resolved parts contain `dukascopy`, and a symlink, are refused.
6. When quotes are unavailable, delayed, or incomplete, append the row from the bars that exist. A missing signal-window quote stays NO TRADE `MISSING_QUOTE` and `INCOMPLETE`. A missing 08:36 bar stays `TIMING_CONTRACT` and incomplete. A missing 09:30 bar stays engine `END_OF_DATA` and is not an ordinary N1 time exit. Do not manufacture a 09:30 exit. A missing minute from 08:36 through 09:29, with engine `TIME_EXIT`, stays `INCOMPLETE`. A completed stop followed by missing later quotes stays raw exit `STOP` with quality `INCOMPLETE`.
7. Synthetic fixtures stay `synthetic_fixture_not_market_evidence`. They are engineering checks. The quote hash covers the evaluated bars. The compressed daily-file hash is not stored while that download remains unauthorized.

## Boundaries

DEC-469 / DEC-268 remain the governing method. N1-v0 is not Strategy V1 and not a catalogue cell. DEC-470 stays frozen. Annual run 385 stays unconsumed. No workflow is dispatched.
