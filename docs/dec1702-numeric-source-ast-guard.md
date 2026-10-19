# DEC-1702 — Static test-source guard for grammar precedence and numeric boundaries

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1948 at `b14316b49b43118cfe5fce5e8ba77e7dbb33e518`.

Adds **one source-defined method** (**5,536 proposed total**) verifying Python AST parseability and unique test-method inventory across DEC-1699 (**97**), DEC-1700 (**25**) and DEC-1701 (**25**), a total of **147** methods. It checks in-module and cross-module name uniqueness, fails closed on missing files or syntax errors and avoids importing tested modules. This complements prior AST guards for DEC-1685–1690 and DEC-1693–1697. It does not substitute for runtime test execution, CI or independent review.

Own exact-head Phase3/full historical-general CI and qualified independent review required. Tests/docs only, synthetic source only. No production/parser/workflow/security updates, protected originals/archives/artifacts, annual dispatch/retry, merging/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
