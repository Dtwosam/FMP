# DEC-1692 — Portable regression module AST guard

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1938 at `fb92769ac59e399bf9ccbc00ff1666a4e9d79ffd`.

Adds **one** source-defined test (**5,142 proposed total**): a synthetic, offline AST guard that parses the legacy DEC-1478 portable bundle test module and all six regression modules added by DEC-1685 through DEC-1690. It rejects syntax errors, duplicate same-class `test_*` method names (which Python silently shadows), missing expected test methods, or changed source-defined test counts. The six new modules must collectively retain all **300** proposed test methods. This guard avoids importing the modules it inspects and performs no network or protected-evidence operations.

Own exact-head Phase 3/full historical-general CI and qualified independent review required. It does not establish that an individual test passes; it provides static syntax and discovery hygiene only. Test/docs-only change; no production/parser/limits/workflow/security updates, protected original/archive/artifact access, annual execution/dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
