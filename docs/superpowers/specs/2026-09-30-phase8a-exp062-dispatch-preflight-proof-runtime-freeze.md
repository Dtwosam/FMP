# Phase 8A — EXP-062 Dispatch-Preflight Proof Runtime Evidence Binding

**Date:** 2026-09-30  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / DISPATCH STILL LOCKED  
**Decision:** DEC-429  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-426, DEC-427, DEC-428

DEC-429 binds the real successful DEC-426 merged-main dispatch-preflight proof.

Concrete evidence:

- head `f2b2a5629013749b74306201aac29d14b7124cd3`;
- run `36688457000`;
- job `109799712311`;
- artifact `11085100742`;
- artifact/ZIP SHA-256
  `a335347c3e428f8eff653bfe4a8e022b0ed939c188634a5236f2354edaff9ac9`;
- raw DEC-425 preflight SHA-256
  `017f45bcec6633006b3d78c76f09890da0417fbd79f904743de659e614d73974`;
- canonical DEC-425 preflight SHA-256
  `26958a21f832609d2dfc57347f6637c35aaa2923c36ec14a40f9573e6a77cb02`;
- DEC-428 freeze fingerprint
  `4a9a7b3e931fd12585638430afbc38f823b5016ecc11f9f4fe7dd3533aa82454`.

DEC-429 re-runs DEC-427 strict review and DEC-428 deterministic freezing before
binding the concrete artifact ZIP digest.

The executor remains installed and available with zero executor runs. Historical
result dispatch, execute mode, rerun/retry/replacement, reserved-data access,
Phase 8B, demo/live, real-money, and trading remain false.

## Next gate

A separate explicit one-shot executor dispatch authorization is required before the
installed workflow may be triggered.
