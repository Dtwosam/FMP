# Phase 8A — EXP-062 Workflow-Install Source-Preflight Recovery Proof Freeze

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY DETERMINISTIC RECOVERY FREEZE / NO INSTALL OR DISPATCH  
**Decision:** DEC-409  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-408

DEC-409 deterministically freezes an already-valid DEC-408 review of a successful
DEC-407 recovery proof.

The freeze preserves both sides of the proof lineage:

- failed DEC-404 run #1 / attempt 1;
- failed run ID `36613664506`;
- failed head `0db04ae49b3533778b08afa31e9ef9a26576b80c`;
- failed job `109561121322`;
- successful DEC-407 recovery run #2 / attempt 1;
- recovery run/job/artifact identities;
- recovery artifact digest;
- raw/canonical DEC-403 preflight hashes;
- exact review source map;
- active executor workflow absent state;
- target historical run #2 / attempt 1.

It emits one canonical `freeze_fingerprint_sha256` for later concrete runtime
binding. It cannot create runtime evidence, install the workflow, dispatch historical
discovery, or expose execute mode.

The next gate after a successful DEC-407 recovery run is concrete runtime-evidence
binding of this frozen recovery proof.
