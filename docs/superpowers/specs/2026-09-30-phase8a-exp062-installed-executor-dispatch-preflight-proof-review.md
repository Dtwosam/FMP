# Phase 8A — EXP-062 Installed Executor Dispatch-Preflight Proof Review

**Date:** 2026-09-30  
**Status:** STRICT RUNTIME-EVIDENCE REVIEW / DISPATCH STILL LOCKED  
**Decision:** DEC-427  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-426

DEC-427 reviews the successful merged-main DEC-426 proof.

Bound evidence:

- head `f2b2a5629013749b74306201aac29d14b7124cd3`;
- run `36688457000`;
- job `109799712311`;
- artifact `11085100742`;
- artifact/ZIP SHA-256
  `a335347c3e428f8eff653bfe4a8e022b0ed939c188634a5236f2354edaff9ac9`;
- raw DEC-425 preflight SHA-256
  `017f45bcec6633006b3d78c76f09890da0417fbd79f904743de659e614d73974`;
- canonical DEC-425 preflight SHA-256
  `26958a21f832609d2dfc57347f6637c35aaa2923c36ec14a40f9573e6a77cb02`.

A valid review requires run #1 / attempt 1 success, exactly one successful job,
exactly one non-expired artifact, exact DEC-425 preflight bytes, the installed
executor state to remain true, executor run count zero, and every dispatch/execute/
reserved-data/trading authority to remain false.

Next gate: deterministic immutable proof freeze.
