# Phase 8A — EXP-062 One-Shot Historical Executor Source Proof Reviewer

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY REVIEWER / RUNTIME PROOF REQUIRED  
**Decision:** DEC-339  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-336, DEC-337, DEC-338

## Purpose

DEC-339 adds a source-only reviewer for future successful DEC-338 runtime evidence.

It validates the exact proof workflow identity, run #1 / attempt 1 success, the single
read-only proof job, the single non-expired source-contract artifact, and the downloaded
DEC-337 contract bytes.

## Required contract state

The reviewed contract must show:

- DEC-337 source-contract decision/version;
- DEC-336 runtime-freeze decision and exact fingerprint;
- DEC-334 terminal-review decision;
- the exact merged-main head;
- zero historical-result attempts;
- an unconsumed and verified-available slot;
- target run #2 / attempt 1;
- the frozen historical command as evidence only;
- one-shot historical executor source authorization true;
- historical executor availability, dispatch, execute mode, rerun/retry/replacement,
  reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading false.

The reviewer records raw and canonical SHA-256 hashes of the source-contract JSON.

## Source bindings

DEC-339 pins the exact DEC-338 proof workflow, DEC-337 source contract, DEC-336 runtime
freeze, DEC-334 terminal-review contract, and active discovery workflow.

## Safety boundary

DEC-339 performs no dispatch and adds no executor workflow. It only reviews future
runtime proof evidence.

## Next gate

After real DEC-338 evidence passes review, the next safe gate is an immutable
source-proof freeze before any dispatch-capable executor workflow is considered.
