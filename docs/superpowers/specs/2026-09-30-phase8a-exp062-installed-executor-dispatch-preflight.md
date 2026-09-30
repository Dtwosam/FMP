# Phase 8A — EXP-062 Installed Executor Dispatch Preflight

**Date:** 2026-09-30  
**Status:** READ-ONLY CURRENT-MAIN DISPATCH PREFLIGHT / NO RUN  
**Decision:** DEC-425  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-424

DEC-425 verifies the installed one-shot historical executor on the exact current
`main` state before any future dispatch authorization can exist.

It pins:

- DEC-424 install-receipt blob
  `27e714620018413a09ceaf287fb7943bf884ee49`;
- active executor workflow blob
  `51ce87584369be957482460d81649adb1cb9f05d`.

A valid preflight requires:

- exact current `main` head;
- active executor workflow present with the pinned blob;
- executor workflow run count still zero;
- historical discovery proof remains the sole run;
- historical-result attempt count remains zero;
- target remains run #2 / attempt 1.

The preflight exposes only a `plan` CLI surface. It cannot dispatch the executor,
run historical discovery, expose execute mode, unlock reserved data, or authorize
any trading path.

## Next gate

A separate explicit one-shot executor dispatch authorization is required before the
installed workflow may be triggered.
