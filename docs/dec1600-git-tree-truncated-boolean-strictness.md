# DEC-1600 — Git tree snapshot truncated must be literal Boolean false

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1846 at `150769b6f76380841abd3afb14e91c537d0eb3a8`. Seventeen synthetic regression methods (**3,205 proposed source-defined tests**).

Literal Boolean `false` is the only acceptable full Git tree snapshot completeness claim. Python's truthy/falsy equivalence is insufficient: caller-provided `0`, `0.0`, `null`, `""`, `"false"`, `[]`, `{}`, or a missing `truncated` member must fail. Exercise both the root and child Git tree object snapshots and the separate flat root-tree snapshot. Require `TREE_CHAIN_TREE_OBJECT_UNREVIEWED` or `COMMIT_TREE_ROOT_UNREVIEWED`, and stable direct-memory, JSON-text and bounded stdin fail-closed verdicts. A literal-Boolean control stays source-only and nonauthorizing.

All test artifacts are synthetic caller evidence; no independently authenticated GitHub source, protected original OS, annual gate or execution permission. Own exact-head Phase 3 and full historical/general CI, independent qualified review required. Tests/docs only; no production, parser limits, workflow/security/admission changes, protected original/archive/artifact access, annual dispatch/retry, merge, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
