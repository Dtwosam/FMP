# Phase 8A — EXP-062 One-Shot Executor Dispatch Action Preflight

**Date:** 2026-09-30  
**Status:** READ-ONLY ACTION PREFLIGHT / AUTHORIZED RUN NOT STARTED  
**Decision:** DEC-431  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-430

DEC-431 is the current-main, read-only action preflight for the explicitly
authorized one-shot executor dispatch.

It pins DEC-430 and the exact active executor workflow. A valid preflight requires:

- exact current `main`;
- zero executor workflow runs;
- historical proof run still present;
- zero historical-result attempts;
- unused historical-result slot;
- executor target run #1 / attempt 1;
- historical target run #2 / attempt 1.

The exact future executor command is exposed as evidence only:

`gh workflow run phase8a-exp062-one-shot-historical-executor.yml --ref main`

DEC-431 has no dispatch or execute CLI surface. The one-shot authorization remains
true, while rerun/retry/replacement, reserved data, Phase 8B, demo/live,
real-money, and trading remain false.

## Next gate

A repository-hosted read-only proof of this action preflight must succeed on merged
`main` before the executor run may be submitted.
