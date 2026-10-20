# DEC-1905 — Exact BacktestConfig engine-ingress contract

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2153 at `11b1d9fb6a1d5e575fab67982c55903a764cc531`.

`run_backtest` previously accepted an untyped `config` argument until deeper execution, where missing fields or property getters could raise incidental exceptions or run user-defined code. Require the exact immutable `BacktestConfig` record at engine entry before validating input sequences or calling any config attributes. This does not change valid model execution, strategy decisions, risk sizing or any broker interface.

Two synthetic Phase3 tests require controlled `ValueError` for null, Boolean, numbers, strings, containers and opaque objects, and reject a hostile object exposing a side-effecting getter without evaluating that getter. Both prohibit file, network and subprocess access in the tested Python path. **6,882 cumulative proposed source-defined test methods.** Local mocks are not evidence of actual OS isolation.

Own exact-commit Phase3 and full historical/general CI and independent review are required, with no inheritance of another SHA's result. At this document's creation, PR #2153 Phase3 passed; its full historical/general suite was still running. Earlier #2140–#2143 full regression failures remain historically FAILED.

Phase 8A remains externally BLOCKED: #779/#820/#821 open; eight independently authenticated administrator/ref/source/runner OS/provenance/one-shot/human authorization proofs MISSING. Accepted annual research ends 2022/run384. Protected 2023/run385/attempt1, future-year catalogue research, Strategy V1 economics, shadow/demo/Phase10/11, installed workflow/ref/ruleset changes, orders and money are not authorized. No protected input, dispatch/retry, workflow installation or trading occurred.
