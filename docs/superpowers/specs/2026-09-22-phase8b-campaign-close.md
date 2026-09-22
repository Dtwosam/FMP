# Phase 8B — Prospective Campaign Evidence Close

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
**Decision:** DEC-053
**Experiment:** EXP-20260922-024
**Scope:** deterministic multi-segment campaign evidence snapshots over exact DEC-052 journals; no broker/order path and no acceptance execution

## 1. Purpose

DEC-052 creates bounded prospective quote-only segments and intentionally runs
DEC-050 compile/replay independently inside each segment.

Those child runtime results are integrity evidence only. They may not be summed
or treated as a continuous campaign account because each bounded compile starts
from the frozen $100,000 baseline.

DEC-053 therefore freezes a separate campaign-close compiler that replays the
exact ordered raw DEC-052 journals across all clean segments as one continuous
virtual campaign and creates the exact DEC-051
`fmp-phase8b-campaign-evidence-v1` artifact.

No Phase 8B live segment has been run when this decision is approved.

## 2. Immutable snapshot, not permanent shutdown

A DEC-053 close is an immutable evidence snapshot.

Each snapshot is written under:

`<campaign-dir>/closures/<closure-id>/`

and binds the exact ordered set of prospective segment fingerprints included in
that snapshot.

A later clean DEC-052 segment may produce a newer closure snapshot. This is
required so DEC-051 `PHASE8B_NEED_MORE_DATA` remains genuinely continuable.

DEC-053 itself does not run DEC-051 acceptance and does not stop future capture.

## 3. Eligible prospective segments

A financially eligible segment must have:

- a valid `fmp-phase8b-prospective-segment-v1` artifact;
- `prospective_evidence=true`;
- `prospective_segment_closed=true`;
- `replay_match=true`;
- exact DEC-049 preflight fingerprint;
- exact child raw/audit/operational SHA-256 values and counts;
- exact valid child DEC-050 segment fingerprint;
- exact valid child DEC-050 replay artifact whose canonical SHA-256 matches the
  prospective-segment replay fingerprint;
- all broker/order/real-money/Phase-9 authorization flags false.

All clean segments are sorted by start UTC then segment ID. Their wall-clock
intervals must not overlap. Duplicate prospective-segment fingerprints,
DEC-050 child segment fingerprints, replay fingerprints, or capture-record
fingerprints fail closed.

Unclosed DEC-052 directories are never admitted into financial replay. They are
retained as operational history and later closure snapshots must not represent
their raw bytes as scored evidence.

## 4. Raw-journal revalidation

DEC-053 reads every eligible `capture-records.jsonl` and validates every
record again against the exact DEC-049 preflight.

Within each child segment, its original receive-monotonic ordering remains
authoritative.

Monotonic values are never compared across process invocations.

Across adjacent segments, DEC-053 requires per-symbol source-time progression.
A source-time regression or duplicate across segment boundaries fails closed.

## 5. Restart gaps

For adjacent clean segments, the wall-clock interval from prior segment end to
later segment start is an explicit restart gap.

A gap is never backfilled.

For deterministic market processing, per-symbol source-time distance between
the last accepted quote before a restart and the first accepted quote after it
is converted to the same stale-market gap semantics used by DEC-050 when that
distance exceeds 15 seconds.

Receive-side restart gaps over 15 seconds are retained as operational bridge-gap
evidence.

## 6. Aggregate DEC-050 segment

DEC-053 recompiles one aggregate `fmp-phase8b-segment-v1` from the exact
ordered raw journals.

The aggregate compiler reuses the DEC-050 implementation for:

- quote normalization;
- complete 1m and required 5m/15m/1h bars;
- immutable strategy reconstruction;
- strategy candidate generation;
- portfolio routing;
- shared Phase 3 risk state;
- 0.2 / 0.5 / 1.0-pip virtual scenarios;
- stale-path invalidation;
- financial metrics.

The full campaign starts with one $100,000 virtual account per slippage
scenario. It does not reset risk equity, open positions, pending decisions, or
daily risk state at DEC-052 process boundaries.

A DEC-053 closure snapshot may be written only when every aggregate slippage
scenario has zero open and zero pending hypothetical decisions. This prevents a
financially incomplete mid-trade snapshot from becoming eligible for DEC-051
acceptance. The operator may capture another segment and close again later.

The aggregate segment binds the exact ordered DEC-052 prospective-segment
fingerprints in addition to the exact ordered raw capture-record fingerprints.

## 7. Aggregate replay

DEC-053 immediately recompiles the aggregate segment from the same immutable
inputs and requires byte-identical output.

The replay artifact uses the DEC-050 replay protocol and binds:

- expected aggregate segment fingerprint;
- replay aggregate segment fingerprint;
- canonical expected/replay SHA-256 values;
- `match=true`.

A mismatch fails closed and no DEC-051 campaign-evidence artifact is written.

## 8. Campaign observation window

`first_observation_utc` and `last_observation_utc` are derived from the first
and last accepted capture-record receive timestamps in the aggregate journals.

At least one accepted capture record is required.

The DEC-051 campaign-start timestamp is copied exactly from the DEC-049
preflight and may not be caller supplied.

## 9. London denominator and complete dates

London dates use `Europe/London`.

Denominator dates are every Monday-Friday London civil date from the first
accepted observation date through the last accepted observation date,
inclusive. Weekends are excluded. No holiday rescue calendar is introduced.

A denominator date is complete only when the union of clean DEC-052 segment
wall-clock intervals covers the full London civil day with:

- start coverage no later than 15 seconds after local midnight;
- no uncovered internal restart gap greater than 15 seconds;
- end coverage no earlier than 15 seconds before the next local midnight.

This rule is DST-aware because the local civil-day boundaries are converted
through `Europe/London`.

## 10. Processing latency and integrity

Every eligible raw capture record must have exactly one audit row with the same
record fingerprint and original receive monotonic value.

Campaign p99 processing latency is nearest-rank p99 over all exact DEC-052 audit
latency samples.

DEC-053 derives:

- malformed-silently-accepted count = 0, because malformed input terminates
  DEC-052 rather than entering a closed segment;
- stale-gap trades admitted to financial metrics count = 0, because DEC-050
  removes invalid stale-path outcomes from completed trades;
- all-operational-events-logged = true only when every eligible segment's
  operational journal is digest-valid and contains both start and clean bounded
  stop events.

## 11. Timing violations

Entry and scheduled-exit deadline violation counts are derived from the
aggregate 0.2-pip scenario outcome ledger.

`ENTRY_DEADLINE_MISSED` and `EXIT_DEADLINE_MISSED` are counted exactly.

## 12. Strategy/pair representation

Completed 0.2-pip decision IDs must resolve exactly to aggregate generated
candidate metadata.

DEC-053 derives, rather than accepts:

- sorted distinct strategy families with completed scored trades;
- sorted distinct required pairs with completed scored trades.

Unknown or ambiguous completed decision IDs fail closed.

## 13. Live spread summaries

For every completed 0.2-pip trade, entry and exit source timestamps must resolve
to exactly one captured quote for the trade symbol.

Spread pips are:

- EURUSD/GBPUSD: `(ask-bid) / 0.0001`;
- USDJPY: `(ask-bid) / 0.01`.

Per required symbol, DEC-053 derives exact sample counts, median, and nearest-rank
p95 separately for entry and exit spreads.

A required symbol with no completed 0.2-pip trade receives zero counts and null
median/p95 values.

## 14. DEC-051 campaign evidence

A successful closure writes the exact
`fmp-phase8b-campaign-evidence-v1` contract frozen by DEC-051, including:

- prospective evidence true;
- closed aggregate snapshot true;
- exact preflight, aggregate segment, replay, champion, strategy, symbol, and
  cost identities;
- denominator/complete London dates;
- aggregate 0.2-pip completed trade count;
- same candidate sequence across scenarios;
- structural no-order safety;
- integrity and p99 timing evidence;
- scenario financial metrics;
- derived representation;
- derived live spread summaries;
- all execution authorization flags false;
- deterministic campaign-evidence fingerprint.

Compilation success is not acceptance PASS. DEC-051 independently decides
`NEED_MORE_DATA`, rejection, or PASS.

## 15. CLI boundary

DEC-053 adds only:

`close-campaign --campaign-dir <path>`

The command is source-only over already captured immutable DEC-052 artifacts.
It does not access MT5, tail files, or invoke a broker.

After DEC-053 the Phase 8B CLI still exposes no generic `run`, `start`,
`review`, demo-order, live-order, or broker command.

## 16. Safety

Throughout DEC-053:

- no demo orders;
- no live orders;
- no broker mutation;
- no real-money trading;
- no Phase 9 execution;
- no champion mutation;
- no acceptance/promotion execution.

Possible EXP-024 source outcomes are:

- `PHASE8B_CAMPAIGN_EVIDENCE_SNAPSHOT_READY`;
- `PROTOCOL_FAILURE`.

Neither outcome itself changes lifecycle state.
