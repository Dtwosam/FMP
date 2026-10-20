# DEC-1862 — Reject overflowing or nonfinite derived fixed commissions

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2109 `1efae676a367565f5de1ca1782831e11fd2ac9e1`.

The now strictly integer-unit `FixedCommissionPerMillion.cost_usd` still multiplies by a finite rate and may produce `inf` for a sufficiently large, but individually valid, finite rate or integer size. Python may also raise an uncaught `OverflowError` converting very large integers to float. Either outcome can pollute hypothetical backtest cost/equity metrics or cause inconsistent error handling.

Wrap the arithmetic with a controlled `OverflowError -> ValueError` conversion, then require that the derived commission remain finite before returning it. Preserve signed whole-unit symmetry, zero-rate behavior for ordinary sizes and exact per-million-per-execution-side formula. Two new source-defined methods (6,768 cumulative proposed) exercise huge signed integer sizes and finite input pairs that produce nonfinite derived costs.

This is a scoped *draft* change to the pure backtester cost contract, not a real market backtest, broker order, strategy validation or installation. Exact-head Phase3/full CI and independent human review required. The eight external security/inventory/provenance/human proof packages #779/#820/#821 remain MISSING/BLOCKED; protected 2023/run385/attempt1, shadow/demo/live, real capital, workflow/ref/ruleset modifications and claims of profit remain forbidden.
