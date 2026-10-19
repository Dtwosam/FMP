# DEC-1710 — AST syntax and method inventory for JSON preflight boundary tests

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent tests/docs-only child of #1956 at `9f1960a22bae531a9d14ad21fea4439fb25a5023`.

Adds **one source-defined method** (**5,754 proposed**) to verify Python AST parseability and exact unique test-name counts in DEC-1707 (37 methods), DEC-1708 (49 methods) and DEC-1709 (25 methods): **111** tests in total. The guard checks both intra-module and cross-module names, without importing or running the reviewed test modules. It is a source discovery check, not a replacement for runtime tests, exact-head CI or independent review.

No changes to production/parser/security/workflow code, protected originals/archive/artifacts or annual dispatch/retry, merging, deployment or trading. Own Phase 3/full historical/general CI and qualified independent review required. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
