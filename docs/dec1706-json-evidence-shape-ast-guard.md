# DEC-1706 — AST source integrity for nested evidence shape regressions

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent tests/docs child of #1952 at `a7263c6479c672f4a23d3480da5523a0c50cad85`.

Adds **one source-defined method** (**5,642 proposed total**): static Python AST parse and method-name inventory guard for DEC-1703 nested JSON object ordering (37 methods), DEC-1704 element type substitution (37 methods) and DEC-1705 array cardinality/shape changes (31 methods), totaling 105 uniquely named methods. Ensures source files remain syntactically parseable and same-named test methods do not silently overwrite a regression. Runs without importing tested modules, private data, remote APIs or protected artifacts.

Own exact-head Phase 3/full historical-general CI and qualified independent review required. Tests/docs only; no parser/production/limits/workflow/security changes, protected originals/archive/artifacts, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
