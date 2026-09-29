# Phase 8A — EXP-062 Workflow-Install Action Preflight Proof Runtime Binding

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED  
**Decision:** DEC-422  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-419, DEC-420, DEC-421

DEC-422 binds the real successful DEC-419 merged-main workflow-install action
preflight proof.

Concrete evidence:

- head `51a49397e1eddc5b9e342d50b588f774e783a5e7`;
- run `36634716243`;
- job `109632428957`;
- artifact `11063264562`;
- artifact/ZIP SHA-256
  `1f06c7b589f46ca7a473bae5a0666b79b1b627dc6a8eaf85804211424e09f0be`;
- raw DEC-418 preflight SHA-256
  `567af303b2e37131b83c7f316424174632dd34854a38660f910c3072fbd893da`;
- canonical DEC-418 preflight SHA-256
  `66ebc48ff1e6ee8d24e19b0641c012244f93ddfb1e02baf343bec3df6a4f9c26`;
- DEC-421 freeze fingerprint
  `78bcceaf580672b97858ec972c590300316f8b7b369137ca96e957c39d1d9a5d`.

DEC-422 re-runs DEC-420 review and DEC-421 deterministic freezing and pins the
DEC-334 terminal-review contract. All eight source-only gates remain true.

The active executor workflow path remains absent. Actual workflow-install
authorization, installed state, executor availability, historical-result dispatch,
execute mode, reserved 2023-2026 access, candidate compilation/promotion, Phase 8B,
demo, broker/live, real-money, and trading remain false.

## Next gate

Any repository mutation that could install the active executor workflow requires a
separate explicit mutation-authorization gate. DEC-422 itself cannot create the
workflow, dispatch historical discovery, or unlock trading.
