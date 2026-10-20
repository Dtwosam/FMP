# DEC-1788 — Repair Markdown interpolated historical identifiers and scope

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of #2034 at `2a0814c3be32a394428d99f3811df07e7a362e21`.

The new human-review detail in DEC-1787 introduced five literal `$` prefixes inside Python f-strings around the **run385/attempt1**, segment 2023 and source-only 18-cell/nine-source numbers. A `$` prefix is neither part of the one-shot run ID nor currency notation in these fields. Confirmed full historical/general CI for #2034 failed **two presentation assertions** requiring `Frozen next run: 385` and `Declared historical research cells: 18`. Its Phase3 accepted but full CI remains FAILED.

This patch removes the five extraneous dollars and adds 1 exact-render/no-dollar regression (6554 proposed cumulative source-defined methods). This is display-only: the source-only six-input report remains **BLOCKED** with nonzero exit3, all eight independent security proofs MISSING, all downstream strategy/trading gates BLOCKED. No annual run385 dispatch, current runner attestation, administrator permissions, broker/demo/live operation, market data access or money movement. Independent #779/#820/#821 reviewer evidence still absent. A fresh exact-head Phase3/full regression run is required.
