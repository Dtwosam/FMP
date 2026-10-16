# DEC-1434 — Canonical component validation for draft-only changed paths

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit source-only tests/docs child of #1657 DEC-1433 at cad6ec7e37c50cd63dec50721c7832a462732793. Seven new test methods, **1,571 proposed source-defined methods**.

The DEC-1433 one-commit draft path reviewer checked only string prefix docs/ or tests/. A syntactically noncanonical supplied path such as docs/../src/runtime.py or tests/../../.github/workflows/annual.yml could therefore appear safe by prefix even though its relative components escape the allowlisted subtree. GitHub compare metadata normally uses canonical repository paths, but source evidence readers must not silently trust malformed caller-supplied fixtures.

This forward-only fix introduces a canonical POSIX relative component check: at least two components, first docs or tests, no empty/dot/parent components, backslash, or embedded NUL. It is applied consistently to current and renamed-from filenames. Seven new in-memory negative/positive regression tests cover the bypass and preserve legitimate nested tests/docs paths. No actual GitHub tree or installed workflow is modified.

The code remains a synthetic JSON shape evaluator, not an authenticated GitHub API witness or security permission gate. Exact-head Phase3 and full historical/general CI and qualified review remain required. DEC-650/#820 actual OS original protected no-write and DEC-651/#821/#779 immutable exclusive 2023 run385/attempt1 admission remain **BLOCKED**. No annual dispatch/retry, original/archive reads, installed YAML/branch/ruleset/permissions, merge, production code or trading action.
