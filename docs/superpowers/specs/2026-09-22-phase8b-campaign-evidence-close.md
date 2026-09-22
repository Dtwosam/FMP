# Phase 8B — Prospective Receipt and Campaign-Evidence Close Compiler

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
**Decision:** DEC-052
**Experiment:** EXP-20260922-023
**Scope:** source-free prospective-receipt validation and campaign-close evidence assembly; no live tail/capture command

## 1. Purpose

DEC-051 freezes what Phase 8B acceptance requires, but deliberately does not
define how multiple prospective runtime segments become one immutable campaign
artifact.

DEC-052 freezes the evidence bridge between a future live MT5 tail runtime and
DEC-051. It defines an externally produced per-segment prospective receipt and a
pure deterministic close compiler that combines exact DEC-049 preflight,
DEC-050 segment/replay evidence, and those receipts into one
`fmp-phase8b-campaign-evidence-v1` artifact.

DEC-052 does not tail MT5, create live receipts, start a segment, or run
acceptance.

## 2. Exact upstream identities

Campaign close requires one exact valid DEC-049
`fmp-phase8b-capture-preflight-v1` artifact.

Every prospective receipt must bind exactly:

- the same capture-preflight fingerprint;
- the same champion-set fingerprint;
- the same ordered strategy fingerprints;
- the same required symbols;
- the same 0.2 / 0.5 / 1.0-pip scenarios;
- one exact DEC-050 `fmp-phase8b-segment-v1` fingerprint;
- one exact DEC-050 replay result with `match = true`;
- the exact segment capture-record digest/count;
- the registered bridge-session mapping.

Any identity mismatch fails closed.

## 3. Prospective receipt contract

A future live-tail runtime must create one
`fmp-phase8b-prospective-segment-receipt-v1` only after a finite segment is
closed and replay verified.

A valid receipt records:

- `prospective_capture_origin = "LIVE_MT5_FILE_TAIL"`;
- `prospective_segment_closed = true`;
- exact preflight/champion/strategy/symbol/cost identities;
- exact segment/replay fingerprints;
- exact segment start/end UTC;
- first and last accepted market-observation UTC;
- exact capture-record count/digest;
- exact per-symbol registered bridge sessions;
- denominator London dates touched by the segment;
- fully observed London dates;
- structural no-order assertions;
- malformed-record silent-accept count;
- stale-gap trades admitted to financial metrics count;
- operational-event completeness assertion;
- per-record or equivalent exact local processing-latency sample sequence;
- scored entry-deadline violation count;
- scored scheduled-exit deadline violation count;
- live entry/exit spread samples linked to exact completed 0.2-pip decision IDs.

Receipt fingerprints are canonical SHA-256 over the full immutable payload.

DEC-052 does not expose a public helper that turns an arbitrary source-free
segment into a prospective receipt. Receipts are validator inputs only. A later
live-tail protocol must write them from the actual capture process.

## 4. Segment continuity

Receipts supplied to one campaign close must be strictly ordered and
non-overlapping.

For adjacent receipts:

- later `segment_start_utc` must be >= prior `segment_end_utc`;
- first/last observation ranges may not overlap;
- capture record fingerprints/digests may not be reused;
- segment/replay fingerprints may not repeat;
- all receipts must belong to the same immutable campaign preflight.

A restarted process therefore creates a new finite receipt rather than silently
continuing a previous segment.

## 5. Campaign time and London-date aggregation

The close compiler derives:

- campaign start from DEC-049;
- first observation = minimum exact receipt first observation;
- last observation = maximum exact receipt last observation;
- denominator London dates = sorted union across receipts;
- complete London dates = sorted union across receipts.

A date may be complete only if it also appears in the denominator set.
Duplicate date claims across non-overlapping receipts are permitted only when
their completeness claim is identical; conflicting claims fail closed.

The compiler does not invent dates from wall-clock time.

## 6. Financial aggregation

For each 0.2 / 0.5 / 1.0-pip scenario, every exact DEC-050 segment scenario is
reconstructed into the shared campaign trade ledger.

The compiler requires:

- no duplicate trade/decision ID across receipts;
- chronological shared risk-equity continuity from $100,000 across segments;
- terminal segment state: no open or pending decision at campaign close for a
  terminal acceptance artifact;
- identical directional candidate/decision sequence across all cost scenarios;
- 0.2-pip completed trade count reported exactly from the compiled ledger.

Financial metrics are recomputed from the combined trades with the accepted
Phase 3 metric implementation; segment-supplied summary numbers are not simply
summed or trusted.

## 7. Strategy/pair representation

For each completed 0.2-pip decision ID, the compiler resolves the exact
generated candidate metadata from its DEC-050 segment.

It then derives, rather than accepts as free text:

- distinct strategy families with completed scored trades;
- distinct V1 pairs with completed scored trades.

Unknown or ambiguous completed decision IDs fail closed.

## 8. Spread evidence

Each receipt's live spread samples are exact objects:

- decision ID;
- symbol;
- entry spread pips;
- exit spread pips.

For every completed 0.2-pip trade there must be exactly one entry/exit spread
sample in the same receipt/segment. Extra, duplicate, cross-symbol, or missing
samples fail closed.

Campaign live spread summaries are recomputed per required symbol using:

- median;
- nearest-rank p95;
- exact sample counts.

A required symbol with no completed 0.2-pip trade receives zero sample counts
and null median/p95 values.

## 9. Timing and integrity aggregation

The close compiler derives:

- p99 processing latency by nearest-rank p99 over the exact concatenated
  latency samples;
- total entry deadline violation count;
- total scheduled-exit deadline violation count;
- total malformed-silently-accepted count;
- total stale-gap-trades-in-financial-metrics count;
- all-operational-events-logged = true only when every receipt says true.

The compiler may not replace missing latency samples with zero.

## 10. Safety aggregation

Campaign structural safety is true only when every receipt independently states:

- no order surface;
- quote-only bridge;
- zero demo orders;
- zero live orders;
- zero broker mutations;
- zero real-money actions.

Any false value remains preserved into campaign evidence so DEC-051 can reject
it by outcome precedence.

## 11. Output

A successfully compiled close artifact uses the DEC-051 protocol:

`fmp-phase8b-campaign-evidence-v1`

with:

- `prospective_evidence = true`;
- `prospective_segment_closed = true`;
- exact upstream identities and one deterministic campaign-evidence fingerprint;
- deterministic aggregate segment fingerprint over ordered segment identities;
- deterministic replay fingerprint over ordered replay identities;
- all DEC-051-required evidence fields;
- all order/broker/real-money/Phase-9 execution authorizations false.

Compilation success does not mean acceptance PASS. DEC-051 must independently
validate and score the resulting artifact.

## 12. CLI and safety boundary

DEC-052 adds no `capture`, `run`, `start`, `review`, or order command.

The close compiler is a pure source-free API. It cannot generate the
prospective receipts it requires.

A later separately frozen live-tail protocol remains mandatory before any real
prospective receipt or Phase 8B segment can exist.

Throughout DEC-052:

- MT5 AutoTrading remains OFF;
- no demo/live orders;
- no broker mutation;
- no real-money trading;
- no Phase 9 execution;
- no active-champion mutation.

Possible EXP-023 implementation outcomes are:

- `PHASE8B_CAMPAIGN_CLOSE_COMPILER_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome is Phase 8B acceptance.
