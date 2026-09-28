# Phase 8A — EXP-062 One-Shot Historical Executor Source Proof Freeze

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DETERMINISTIC FREEZE / NO EXECUTOR WORKFLOW  
**Decision:** DEC-340  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-339

## Purpose

DEC-340 adds a deterministic freeze builder for an already-valid DEC-339 review of a
successful DEC-338 one-shot historical executor source proof.

It cannot invent runtime evidence. It preserves the reviewed proof run/job/artifact
identities, artifact digest, raw/canonical source-contract hashes, source bindings,
target run #2 / attempt 1, and the DEC-336 runtime-freeze fingerprint.

## Frozen evidence

A valid freeze preserves:

- DEC-338 proof workflow identity;
- proof run #1 / attempt 1 success;
- concrete proof run, job, and artifact ids;
- non-expired artifact name and SHA-256 digest;
- raw and canonical DEC-337 source-contract hashes;
- exact DEC-339 review source blobs;
- DEC-337 source-contract decision/version;
- DEC-336 runtime-freeze decision/fingerprint;
- DEC-334 terminal-review decision;
- zero historical-result attempts;
- target run #2 / attempt 1;
- the historical command as frozen evidence only.

The freeze emits a deterministic `freeze_fingerprint_sha256`.

## Safety boundary

DEC-340 keeps false:

- historical executor availability;
- historical-result dispatch authorization;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 access;
- candidate compilation / promotion;
- Phase 8B;
- demo / broker / live / real-money / trading.

## Next gate

After real DEC-338 runtime evidence is reviewed by DEC-339, the next safe gate is a
concrete runtime-evidence binding that replays DEC-339 and DEC-340 against those exact
bytes before any dispatch-capable executor workflow is considered.
