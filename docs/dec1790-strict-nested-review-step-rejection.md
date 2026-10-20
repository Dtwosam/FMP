# DEC-1790 — Fail closed on malformed nested human-review step records

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of #2036 at `895744c03d82c5ea470ce0f086535ffbb556a537`.

The DEC-1786 and DEC-1789 human-review formatter validates historical source hashes, three-job runtime gate positions and the whole dual-pinned pre-gate trace. But an input dictionary with a **non-object nested step** could throw `AttributeError` when the preliminary validator invoked `item.get` before reaching the frozen trace match. This is a malformed **presentation input** problem, not proof of an installed runner bypass.

The formatter now explicitly requires every nested pre-gate row to be an ordinary dictionary with **exactly three fields** (`name`, `payload`, `zero_based_step_index`) of exact `str`, `str`, `int` types. Unknown approval fields, Boolean index aliases, arrays and nulls are denied with controlled `InvalidHandoff` rather than an attribute error or unreviewed text. The subsequent exact trace equality still checks all reviewed names, values and positions.

Adds 3 adversarial methods (6562 cumulative proposed source-defined), without changing the pinned research/documentary evidence, offline reviewer capabilities, installed GitHub Actions YAML, current admin/ruleset/runner configurations, protected 2023 annual/run385, brokerage/demo/live permissions or capital. External #779/#820/#821 security proofs remain MISSING and a full exact-head historical/general plus Phase3 suite is required.
