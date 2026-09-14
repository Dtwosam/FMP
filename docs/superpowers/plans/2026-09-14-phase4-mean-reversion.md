# Phase 4 Mean-Reversion Implementation Plan

Spec: `docs/superpowers/specs/2026-09-14-phase4-mean-reversion-design.md`
Decision: DEC-020.
Experiment: EXP-20260914-003.

Execute test-first in this order:

1. Source-of-truth state test and planned experiment record.
2. Strategy configuration/statistic primitives.
3. Deterministic candidate generation and timing/geometry tests.
4. Research-grid orchestration using existing loader/adapter/reporter/backtester.
5. Thin CLI with development/validation-only inputs.
6. Source-free fixed matrix workflow and workflow-structure tests.
7. Exact-head CI/safety review and guarded merge.
8. Merged-main artifact verification across the complete matrix.
9. RED result-state test, evidence document, experiment outcome, and project-state update.

No common simulator behavior change is planned. Exact values, formulas, time rules, split rules, evidence rules, and non-goals are authoritative in the approved spec and DEC-020.
