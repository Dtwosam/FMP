# Phase 8A — EXP-062 Workflow-Install Source-Preflight Recovery Runtime Freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RECOVERY-EVIDENCE BINDING / NO INSTALL OR DISPATCH  
**Decision:** DEC-410  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-404, DEC-407, DEC-408, DEC-409

## Purpose

DEC-410 binds the concrete successful DEC-407 recovery proof while permanently
preserving the failed DEC-404 run #1 provenance.

The lineage is:

- failed DEC-404 proof run #1 / attempt 1:
  - head `0db04ae49b3533778b08afa31e9ef9a26576b80c`;
  - run `36613664506`;
  - job `109561121322`;
  - conclusion `failure`;
- successful DEC-407 recovery run #2 / attempt 1:
  - head `3ea7d3f7bfe8f1dfb3bbac612f74255da4fee432`;
  - run `36616131587`;
  - job `109569478100`;
  - artifact `11054938805`;
  - artifact/ZIP SHA-256
    `e71ad4c19602bec2c3fa71ad6f76e41eadea53edd5ef310ea2110d251002da25`;
  - raw DEC-403 preflight SHA-256
    `aea9a6f510ee7f5147adb7aea4cba2e9662093dfc2a8465adc9b7aec61556639`;
  - canonical DEC-403 preflight SHA-256
    `4f96d9df7e7e4fba224a376b500539e4581bc34d852178f00796ee7be66f6c6b`.

DEC-410 re-runs the merged DEC-408 reviewer and DEC-409 freeze and requires the
exact DEC-409 fingerprint
`c0c04735c57638fde0a57122c240ea6c9aacd86fc7e43cdc532aaf8ba54cd9d3`.

## Authority boundary

All six source-only workflow-install gates remain true. The active executor workflow
path remains absent.

Actual workflow-install authorization, installed state, historical executor
availability, historical-result dispatch, execute mode, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

## Next gate

The next safe gate is a source-only final workflow-install authorization contract
before any installation mutation is permitted.
