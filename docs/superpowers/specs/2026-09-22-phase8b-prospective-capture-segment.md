# Phase 8B — Prospective Capture Segment Journal

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
**Decision:** DEC-052
**Experiment:** EXP-20260922-023
**Scope:** explicit bounded quote-only capture segments with durable raw evidence and immediate deterministic replay; no campaign acceptance review

## 1. Purpose

DEC-049 through DEC-051 freeze the preflight, runtime/replay, and acceptance
contracts but intentionally expose no live capture path. DEC-052 freezes the
first operator-invoked prospective capture surface.

A DEC-052 segment may read only the fixed required-symbol MT5 FILE_COMMON demo
bridge files already bound by the exact campaign registration/start/preflight.
It may persist raw quote/heartbeat evidence, processing-latency audit rows,
operational events, one DEC-050 segment artifact, and one deterministic replay
artifact.

DEC-052 does not compile campaign acceptance, change strategy lifecycle, place
orders, mutate broker state, or authorize Phase 9.

## 2. Explicit operator boundary

The only new live command is:

`capture-segment --campaign-dir <path> --duration-seconds <n>`

It is never started by CI or implicitly by another command.

The duration is an operational segmentation choice only and may be any positive
integer from 1 through 86400 seconds. It does not alter strategy, risk, cost,
acceptance, or bar semantics.

Polling interval is fixed in source at 0.10 seconds and is not caller
configurable.

## 3. First-segment preflight

If `capture-preflight.json` does not yet exist, `capture-segment` must:

1. load the exact immutable DEC-047 registration and DEC-048 start
   authorization from the campaign directory;
2. discover exactly the frozen required-symbol bridge files;
3. create fresh `Phase8BBridgeFileTail` readers, each starting at current EOF;
4. build and write the exact DEC-049 capture preflight;
5. continue capture using those same reader instances.

There is no gap between preflight reader creation and the first segment caused
by reopening the files.

If a preflight already exists, it is validated before capture and fresh readers
begin at current EOF. This restart boundary intentionally excludes records
written while FMP was not observing.

Every fresh reader must still match the preflight protocol, symbol,
bridge-session ID, account fingerprint, approved server, and DEMO mode.

## 4. Append-only raw evidence

Each segment has an immutable directory under:

`<campaign-dir>/segments/<segment-id>/`

The deterministic segment ID binds:

- capture-preflight fingerprint;
- segment-start UTC;
- runtime code commit.

Before reading post-EOF records, the segment writes a start record containing
those identities and all safety flags false.

Accepted bridge records are converted using the existing
`Phase8BCaptureFeedEnvelope` contract and appended to
`capture-records.jsonl`.

Every JSONL append is flushed and fsynced before it is considered durable.
Files are create-only; an existing segment directory fails closed.

Malformed bridge records, file truncation, session replacement, identity drift,
or unsupported symbols terminate the segment as protocol failure. They are not
silently skipped.

## 5. Processing-latency audit

For each durable capture-record append, DEC-052 writes one audit row binding the
record fingerprint and:

- receive UTC;
- receive monotonic nanoseconds;
- append-completed monotonic nanoseconds;
- processing latency milliseconds.

Latency is measured from the exact local monotonic receive timestamp stored in
the capture envelope to completion of fsync for that envelope.

Audit rows are append-only and fsynced.

## 6. Operational events

The segment journal records process start, process stop, and any caught
protocol/bridge failure before termination when the failure can still be
durably written.

A clean bounded stop records `SEGMENT_DURATION_REACHED`.

A process interruption or machine loss may leave a segment without a close
artifact. Such an unclosed directory is retained but can never count as closed
prospective campaign evidence.

## 7. Segment close

On a clean bounded stop, DEC-052:

1. closes the raw capture journal;
2. runs the exact DEC-050 segment compiler over the durable capture envelopes;
3. runs exact DEC-050 offline replay over the same envelopes;
4. requires replay `match=true`;
5. writes the DEC-050 segment/replay artifacts;
6. writes `prospective-segment.json` with protocol
   `fmp-phase8b-prospective-segment-v1`.

The prospective-segment artifact binds:

- exact capture-preflight fingerprint;
- start/end UTC;
- runtime code commit;
- raw-record count and SHA-256;
- audit-row count and SHA-256;
- operational-event SHA-256;
- DEC-050 segment fingerprint;
- deterministic replay fingerprint;
- `prospective_evidence=true`;
- `prospective_segment_closed=true`;
- all order/broker/real-money/Phase-9 authorization flags false.

The replay fingerprint is the SHA-256 of the canonical replay artifact.

## 8. Restart semantics

Each process invocation is one independent prospective segment. Segment-local
monotonic values are never compared across invocations.

A later campaign-close decision must aggregate only clean, replay-matching,
immutable DEC-052 segments in chronological order and must explicitly account
for restart gaps. DEC-052 itself performs no multi-segment acceptance
aggregation.

## 9. CLI and safety boundary

After DEC-052 the Phase 8B CLI may expose:

- `design`
- `qualify`
- `register`
- `authorize-start`
- `capture-segment`

It still exposes no generic `run`, `start`, `review`, broker command, or
campaign-acceptance command.

Throughout DEC-052:

- MT5 AutoTrading remains OFF;
- bridge role is quote-only;
- no demo order placement;
- no live order placement;
- no broker mutation;
- no real-money trading;
- no Phase 9 execution;
- no champion-set mutation;
- no acceptance/promotion decision.

Possible EXP-023 source outcomes are:

- `PHASE8B_PROSPECTIVE_SEGMENT_CLOSED`;
- `PROTOCOL_FAILURE`.

Only explicit operator invocation can create the former.
