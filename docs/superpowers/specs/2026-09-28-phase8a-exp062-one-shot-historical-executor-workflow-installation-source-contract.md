# Phase 8A — EXP-062 One-Shot Historical Executor Workflow-Installation Source Contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY DORMANT INSTALLATION CONTRACT / ACTIVE WORKFLOW ABSENT  
**Decision:** DEC-354  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-353

## Purpose

DEC-354 adds the source-only contract for a future dormant one-shot historical
executor workflow template.

It pins the concrete DEC-353 runtime freeze and defines both the dormant template
path and the reserved active workflow path without creating or installing either
runtime executor surface.

## Frozen predecessor

DEC-354 pins:

- DEC-353 runtime-freeze blob:
  `2183798aa137e234849f92a0aee13e14a76876e2`;
- DEC-353 runtime-freeze fingerprint:
  `aa2eafcf48f19f694ac9acac08b91174b2ca1282c2a2b6ea2a33cb16aa2d4385`;
- DEC-352 freeze fingerprint:
  `75fad6795f4046d83f5ae29f08475c969e29d3fe3af0e3448dde46292a959f4a`;
- DEC-334 terminal-review identity;
- zero historical-result attempts;
- target run #2 / attempt 1.

## Future source identity

Dormant template path:

`docs/superpowers/templates/phase8a-exp062-one-shot-historical-executor.yml.disabled`

Reserved active workflow path:

`.github/workflows/phase8a-exp062-one-shot-historical-executor.yml`

DEC-354 sets only:

`one_shot_historical_executor_workflow_installation_source_authorized = true`

It keeps the dormant template absent, active workflow absent, install authorization
false, installed state false, executor availability false, dispatch false, and execute
mode false.

## Next gate

The next safe gate is the dormant one-shot historical executor workflow template
source itself, still outside `.github/workflows/` and still non-installing.
