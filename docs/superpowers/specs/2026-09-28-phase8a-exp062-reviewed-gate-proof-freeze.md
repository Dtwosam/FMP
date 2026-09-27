# Phase 8A — EXP-062 Reviewed Gate-Proof Freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY FREEZE BUILDER / RUNTIME PROOF EVIDENCE STILL REQUIRED  
**Decision:** DEC-305  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-301, DEC-302, DEC-303, DEC-304

## Purpose

DEC-305 adds the deterministic freeze boundary for an EXP-062 gate proof that has
already passed DEC-304 review.

It does not manufacture or infer runtime evidence. The caller must supply a valid
DEC-304 reviewed result tied to the exact proof head. DEC-305 only revalidates that
review, copies the immutable proof identities into a canonical freeze record, and
adds a SHA-256 fingerprint over the freeze payload.

## Required reviewed result

The source review must remain exactly:

- DEC-304 / `fmp-exp062-proof-result-review-v1`;
- fail-closed proof stage;
- DEC-301 proof contract and DEC-303 executor identities;
- proof run #1 / attempt #1 / terminal failure;
- one valid preflight artifact identity and digest;
- zero cell-result and aggregate-result artifacts;
- no historical discovery execution;
- historical-result slot still closed;
- no proof rerun/retry/replacement authority;
- no reserved-data, candidate, Phase 8B, demo, broker, live, real-money, or trading
  authority.

Runtime run IDs, artifact IDs, job names, and the proof head are not hard-coded before
evidence exists. DEC-305 freezes the values only after DEC-304 has validated them.

## Output

A successful freeze produces:

- `EXP062_GATE_PROOF_REVIEWED_FAIL_CLOSED_AND_FROZEN`;
- the exact proof run/artifact/job identities from DEC-304;
- `fail_closed_semantics_verified=true`;
- all historical-result/demo/live/trading authority false;
- `freeze_fingerprint_sha256` over canonical JSON;
- next gate:
  `SOURCE_ONLY_HISTORICAL_RUN_AUTHORIZATION_CONTRACT`.

## Safety boundary

DEC-305 does not open the historical-result slot and does not authorize a historical
run. It also does not authorize candidate compilation, promotion, Phase 8B, demo
orders, broker mutation, live orders, real-money action, or trading.

The actual EXP-062 proof must still exist and pass DEC-304 review before a real freeze
record can be produced.
