# DEC-1415 — Fail-closed outer strategy/matrix source shape

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit test/docs child of #1638 DEC-1414 at 90759a592f14f14682791d9714c8a0e33c68ed24; +10 tests, **1,415 proposed source-defined methods**.

The canonical annual cell matrix contains 18 datasets, with exactly the reviewed strategy, fail-fast false, max-parallel 3, matrix, dataset, then steps boundaries. The row-level reviewer validates combinations and pinned source literal IDs/digests but could overlook a new matrix include, exclude or additional axis inserted ahead of the dataset block. This forward-only test reviewer checks exact outer shape and fails closed on additional matrix axes, unknown strategy keys, duplicate container, alternate matrix expression or a shifted steps boundary. It is intentionally source-syntax-specific; it is not a full YAML interpreter and cannot establish GitHub server behavior.

No production workflow YAML is edited, no protected artifacts/originals are accessed, and no annual execution, retry, trading or merge is attempted. Independently OS-enforced protected source no-write DEC-650/#820 and exclusive immutable 2023 run385/attempt1 server-side admission DEC-651/#821/#779 remain **BLOCKED**. Exact-head Phase3 and full historical CI plus independent security review required before calling this draft verified.
