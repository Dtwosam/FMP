# N1-v0 prospective observation protocol

**Status:** PILOT AUTHORIZED BY DEC-638. DAILY-FILE TRANSPORT AUTHORIZED BY DEC-639. Download waits for a verified 08:30 America/New_York publication and a completed window. The DEC-637 rule is unchanged. Fetch has not started.

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

No quote is fetched before the release is verified published at 08:30 America/New_York and the observation window has completed. The public Dukascopy object for these minutes is a whole UTC-day file. DEC-639 authorizes that file for the two dates above, as a transport envelope. DEC-638's minute list is unchanged. This pilot authorizes no historical read, no broker connection, and no demo, live, or real-money order.

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

The recorder rejects a supplied 08:35 bar. The N1 decision timestamp stays 08:35 America/New_York and the earliest execution stays the 08:36 bar. `append_labeled_pilot_evidence` appends three slippage rows to `n1-v0-pilot-evidence.jsonl` and leaves an earlier row in place. A synthetic fixture is class `synthetic_fixture_not_market_evidence`. Caller-supplied bars, labels, and timestamps do not establish market provenance. The signal file must still match commit `78185a1aded7f5d97c296c16fdfd615f46934353`.

## Dukascopy transport envelope — approved by DEC-639

DEC-638 names specific New York minutes. `DukascopySource.url_for` identifies one UTC-day object:

`https://datafeed.dukascopy.com/datafeed/{PAIR}/{YEAR}/{ZERO_BASED_MONTH}/{DD}/{SIDE}_candles_min_1.bi5`

December is zero-based month 11. The 10 December 2026 EURUSD BID object is exactly:

`https://datafeed.dukascopy.com/datafeed/EURUSD/2026/11/10/BID_candles_min_1.bi5`

That object is the whole UTC day. `MINUTE_WINDOW_DOWNLOAD_SUPPORTED` is false. There is no minute-range URL. `acquire_chunk` remains unused because it writes the historical raw store.

DEC-639 authorizes the twelve public daily BID and ASK files for 4 December 2026 and 10 December 2026. Six files on one date. The instruments are EURUSD, GBPUSD, and USDJPY. The files are a transport envelope. After SHA-256 of the compressed bytes, only these minutes are kept:

- EURUSD, GBPUSD, and USDJPY at 08:29, 08:30, 08:31, 08:32, 08:33, and 08:34 America/New_York.
- EURUSD at every minute from 08:36 through 09:30 America/New_York.

Every other minute, including 08:35, is discarded. It is not evaluated and it is not retained as a research bar. The temporary full-day payload is deleted after the hash is recorded and extraction finishes. The source manifest, the hashes, the permitted bars, and the evidence rows remain. A path whose resolved parts include `dukascopy` is refused. No workflow, schedule, or broker is authorized. November 2026 and every other date stay closed. A replacement calendar date needs its own recorded citation.

A real download stays closed until the operator has verified BLS publication at 08:30 America/New_York and the system UTC clock is at or after 09:31 America/New_York on that event date. The 09:30 bar is then complete. The real HTTP client checks that system clock before any request. A caller-supplied `now_utc` cannot open the request earlier. `bls_status_verified_at_utc` is the time of the operator's manual BLS check. That timestamp does not prove publication. The release record has to carry the BLS status, and the code does not contact BLS.

09:31 America/New_York is the earliest permitted attempt. It does not mean the Dukascopy whole-day file is already available. The operator should wait until that UTC day has ended before the first download: 00:00 UTC on 5 December 2026 for the Employment Situation, and 00:00 UTC on 11 December 2026 for the CPI. Those instants are 19:00 America/New_York on the event date. An earlier attempt can record an unavailable or incomplete file. This recommendation does not add a source file, a replacement date, or another download. If a source file is missing, incomplete, or undecodable, record that limitation. Do not invent a price and do not switch feeds.

## Manual event-day procedure

The operator runs this procedure by hand. It does not start a workflow, a recurring job, an automatic download, or a broker connection.

1. The earliest permitted attempt is 09:31 America/New_York on 4 December 2026 or 10 December 2026. Both dates are EST (UTC−5), so 08:29 New York is 13:29 UTC and 09:30 New York is 14:30 UTC. The whole window sits inside that UTC date. The real HTTP client reads the system UTC clock for this cutoff. For the first attempt, wait until the UTC day has ended: 00:00 UTC on 5 December 2026, or 00:00 UTC on 11 December 2026. That is 19:00 America/New_York on the event date. The daily file is more likely to be complete then. 09:31 remains the earliest cutoff, and the later wait does not authorize a second download.
2. Read the publication status from the official BLS calendar or publication record. Price does not establish publication. The verification timestamp records when that check was made. It is not independent proof that BLS published the release. A delayed, cancelled, unpublished, or retimed release is retained and does not consume one of the two slots. Its daily files are not downloaded. Quotes for a replacement date wait for a new recorded BLS citation.
3. Call `observe_n1_transport_window` for that one date. It fetches the six public daily files into a temporary directory outside the historical Dukascopy store, hashes the compressed bytes, extracts the approved minutes, and deletes the full-day payloads. `append_labeled_pilot_evidence` by itself accepts synthetic bars and does not fetch. A prospective row has to come from `observe_n1_transport_window`. The signal blob must still match `78185a1aded7f5d97c296c16fdfd615f46934353`.
4. The writer appends three JSON lines, schema `fmp-n1-v0-pilot-evidence-v1`, for slippage 0.5, 0.2, and 1.0. Each line carries the source-file hashes and the extracted-bar hash. Identity is evidence origin, release id, and slippage. A repeat raises `DuplicatePilotObservation` and leaves the earlier bytes unchanged. A directory whose resolved parts contain `dukascopy`, and a symlink, are refused.
5. When quotes are unavailable, delayed, or incomplete, append the row from the bars that were actually extracted. A missing signal-window quote stays NO TRADE `MISSING_QUOTE` and `INCOMPLETE`. A missing 08:36 bar stays `TIMING_CONTRACT` and incomplete. A missing 09:30 bar stays engine `END_OF_DATA` and is not an ordinary N1 time exit. Do not manufacture a 09:30 exit. A missing minute from 08:36 through 09:29, with engine `TIME_EXIT`, stays `INCOMPLETE`. A completed stop followed by missing later quotes stays raw exit `STOP` with quality `INCOMPLETE`.
6. Synthetic fixtures stay `synthetic_fixture_not_market_evidence`. They are engineering checks. A hand-supplied timestamp does not turn them into prospective market evidence.

## Boundaries

DEC-469 / DEC-268 remain the governing method. N1-v0 is not Strategy V1 and not a catalogue cell. DEC-470 stays frozen. Annual run 385 stays unconsumed. No workflow is dispatched.
