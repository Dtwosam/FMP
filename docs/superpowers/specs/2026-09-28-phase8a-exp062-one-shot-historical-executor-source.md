# Phase 8A — EXP-062 One-Shot Historical Executor Source

**Date:** 2026-09-28  
**Status:** SOURCE AUTHORIZED / RUNTIME DISPATCH LOCKED  
**Decision:** DEC-337  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-336

## Purpose

DEC-337 adds the source-only contract for the eventual one-shot EXP-062 historical
executor. It requires the concrete DEC-336 runtime freeze and a fresh DEC-331
activation preflight proving the historical-result slot is still empty.

The source validates and freezes the exact future discovery command, but it does not
run that command and contains no subprocess or GitHub Actions dispatch surface.

## Required state

A valid source contract requires:

- exact DEC-336 runtime-freeze fingerprint
  `147ab77116979afa8d0d07c3c748fb80e02865a382317824320f6af534bfc374`;
- DEC-334 terminal-review criteria already pinned by DEC-336;
- zero historical-result attempts;
- an unconsumed slot;
- target run #2 / attempt 1;
- the exact fresh DEC-331 activation preflight command.

## Safety boundary

DEC-337 sets only the one-shot executor **source** authorization true.

Historical executor availability, historical-result dispatch authorization, execute
mode, rerun/retry/replacement, reserved 2023-2026 access, candidate
compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading all remain
false.

## Next gate

The next safe gate is a repository-hosted proof of the one-shot executor source
contract before any dispatch-capable workflow is introduced.
