# Phase 8B — Acceptance Review and Shadow-Validation Freeze

**Date:** 2026-09-22
**Status:** APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
**Decision:** DEC-054
**Experiment:** EXP-20260922-025
**Scope:** explicit source-only acceptance review over immutable DEC-053 campaign evidence and one exact DEC-051 spread reference; lifecycle evidence only, no demo execution

## 1. Purpose

DEC-051 freezes the acceptance compiler and DEC-053 creates immutable
prospective campaign-evidence snapshots. No approved command currently binds one
exact snapshot to one exact historical spread reference and persists the
acceptance result/lifecycle consequence.

DEC-054 freezes that review boundary before any real Phase 8B capture or
acceptance result exists.

## 2. Spread-reference freeze and review commands

DEC-054 adds:

`freeze-spread-reference --campaign-dir <path> --dataset-root <path>`

and:

`review-campaign --campaign-dir <path> --closure-id <sha256>`

Both commands are source-only. They do not access MT5, a broker, credentials,
orders, positions, or real money.

The spread reference is frozen create-only at
`<campaign-dir>/spread-reference.json` and the review command may consume only
that exact campaign-bound artifact.

## 3. Historical spread-reference construction

The spread reference must be built from the accepted Phase 8A retrospective
snapshot before any real Phase 8B acceptance result.

For every exact required symbol, the builder loads only complete canonical 1m
bars through `load_phase8a_retrospective_bars` across the full immutable
`2015-01-01 .. 2026-08-21` accepted range.

Manifest locations are fixed under the supplied dataset root:

`manifests/processed/fmp-canonical-1m-v1/<SYMBOL>.json`

No symbol, timeframe, start-date, end-date, percentile, or tolerance override is
available.

For each complete 1m bar:

- historical entry spread = `ask_open - bid_open` in pips;
- historical exit spread = `ask_close - bid_close` in pips.

Per symbol, the artifact stores exact sample counts, median, and nearest-rank
p95 for entry and exit spreads.

The reference binds:

- exact DEC-049 capture-preflight fingerprint;
- exact champion-set fingerprint;
- exact required symbols and slippage scenarios;
- exact retrospective date range and source label;
- exact canonical 1m method;
- exact processed-manifest SHA-256 by symbol;
- exact opened artifact months by symbol;
- spread-reference builder code commit;
- deterministic spread-reference fingerprint.

The file and companion manifest are create-only. Re-running the freeze for the
same campaign fails closed.

## 4. Exact review inputs

Review requires:

- one exact valid DEC-049 capture preflight from the campaign directory;
- one exact DEC-053 closure directory named by `closure-id`;
- the closure's exact `fmp-phase8b-campaign-evidence-v1` artifact;
- the exact DEC-053 closure manifest and campaign-evidence byte SHA-256;
- the exact campaign-bound `spread-reference.json` created by this decision;
- the current review code commit.

The DEC-051 acceptance compiler independently requires exact equality across the
campaign evidence and spread reference for capture-preflight fingerprint,
champion-set fingerprint, required symbols, and slippage scenarios.

Any mismatch or tamper fails closed.

## 5. Immutable review identity

Each review receives a deterministic ID binding:

- campaign-evidence fingerprint;
- spread-reference fingerprint;
- spread-reference source-file SHA-256;
- review code commit.

Artifacts are written create-only under:

`<campaign-dir>/reviews/<review-id>/`

The review directory durably stores:

- the exact source spread-reference bytes;
- DEC-051 `acceptance.json` and its manifest;
- a review manifest binding source SHA-256 values and outcome;
- when and only when PASS occurs, one shadow-validation artifact.

Repeating the exact review fails with `FileExistsError`.

## 6. NEED_MORE_DATA is non-terminal

If DEC-051 returns:

`PHASE8B_NEED_MORE_DATA`

the review:

- writes immutable acceptance evidence;
- writes no lifecycle transition artifact;
- writes no campaign terminal marker;
- leaves DEC-052 capture eligible for later clean segments;
- permits a later DEC-053 closure and a different review ID.

## 7. Terminal rejection

Any DEC-051 rejection outcome is terminal for this exact Phase 8B campaign:

- `PHASE8B_REJECT_OPERATIONAL_MISMATCH`;
- `PHASE8B_REJECT_MARKET_MISMATCH`;
- `PHASE8B_REJECT_FINANCIAL_MISMATCH`;
- `PHASE8B_REJECT_SAFETY_FAILURE`.

A terminal rejection writes no lifecycle transition artifact.

It writes a create-only campaign terminal marker that binds the exact review ID,
acceptance fingerprint, outcome, champion-set fingerprint, and all
order/broker/real-money/Phase-9 authorizations false.

After that marker exists, future `capture-segment` and `review-campaign`
invocations fail closed for that campaign.

## 8. PASS and lifecycle transition

Only exact DEC-051 outcome:

`PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN`

may create:

`fmp-phase8b-shadow-validation-v1`.

The review reconstructs the exact immutable champion strategies from the
DEC-049 preflight and requires every strategy row to enter from
`SHADOW_CANDIDATE`.

It applies the existing registry transition function exactly once:

`SHADOW_CANDIDATE -> SHADOW_VALIDATED`.

The strategy identities and champion-set ID do not change. Re-freezing the
transitioned records must reproduce the exact same champion-set fingerprint.

The shadow-validation artifact binds:

- review ID;
- acceptance fingerprint;
- campaign-evidence fingerprint;
- spread-reference fingerprint;
- exact champion-set ID/fingerprint;
- exact sorted strategy fingerprints;
- prior lifecycle/evidence IDs;
- resulting lifecycle/evidence IDs;
- `demo_design_eligible=true`;
- all demo/live order, broker mutation, real-money, and Phase-9 execution flags
  false;
- deterministic shadow-validation fingerprint.

## 9. PASS is terminal for shadow capture

PASS writes the same campaign terminal-marker protocol used by terminal
rejection.

After PASS, more Phase 8B capture for that campaign is not permitted. The next
allowed activity is a separately frozen Phase 9 demo-design proposal.

PASS does not transition strategies to `DEMO_ELIGIBLE` and does not authorize
demo orders.

## 10. Terminal marker

The create-only marker is:

`<campaign-dir>/campaign-terminal.json`

with protocol:

`fmp-phase8b-campaign-terminal-v1`.

It records whether the terminal result is PASS or rejection, but never carries
any order authorization.

A pre-existing marker blocks another terminal review, another
`review-campaign`, and future `capture-segment`.

## 11. CLI boundary

After DEC-054 the Phase 8B CLI may expose:

- `design`;
- `qualify`;
- `register`;
- `authorize-start`;
- `freeze-spread-reference`;
- `capture-segment`;
- `close-campaign`;
- `review-campaign`.

The first real `capture-segment` invocation requires the campaign-bound spread
reference to already exist and validate against the exact preflight. This
prevents choosing a different historical spread baseline after prospective
results are visible.

It still exposes no generic `run`, `start`, demo-order, live-order, broker,
or real-money command.

## 12. Safety

Throughout DEC-054:

- no demo order placement;
- no live order placement;
- no broker mutation;
- no real-money trading;
- no Phase 9 execution;
- no transition to `DEMO_ELIGIBLE`;
- no champion identity mutation.

Possible EXP-025 source outcomes are the exact DEC-051 acceptance outcomes plus
`PROTOCOL_FAILURE`.

Only PASS may create `SHADOW_VALIDATED` evidence.
