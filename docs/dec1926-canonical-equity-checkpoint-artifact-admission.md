# DEC-1926 — Canonical chronological equity checkpoint publication

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One exact-parent source/tests/docs child of #2174 at `31436e0bcb4bafd41f263d428c5fe2909443aad4`.

`EquityCheckpoint` previously entered `write_backtest_artifacts` as an exact dataclass even when its timestamp or realized equity field was malformed. The writer could otherwise serialize Boolean or string equity and out-of-order checkpoint evidence with valid manifest hashes. Recheck exact UTC datetime and ordinary finite numeric realized equity, refuse reversed chronological order, preserve valid same-timestamp multi-checkpoint semantics before any filesystem mutation.

Four synthetic source-defined test methods cover invalid/non-UTC timestamps, untyped/nonfinite/huge equity, backward chronological sequence and positive equal-time output control. **6,939 cumulative proposed source-defined methods.** Own exact-head Phase3/full historical/general CI and scoped independent risk/reporting review required. This is not provenance or profitability proof.

Phase8A #779/#820/#821 and eight independent external security packages remain MISSING/BLOCKED; accepted research still through 2022/run384. Protected 2023/run385/attempt1, future annual discovery, Strategy V1 economics, shadow/demo/live brokers/capital and installed GitHub workflow/ref/ruleset/runner edits remain unauthorized. No protected read, execution, trade or money.
