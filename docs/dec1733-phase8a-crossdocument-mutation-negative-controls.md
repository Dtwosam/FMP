# DEC-1733 — Negative mutations must break Phase 8A cross-document consistency

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent tests/docs child of #1979 at `76043caa588a0a6f3724f36b972591212979558d`.

Adds **14 source-defined methods** (**5,995 proposed total**) that exercise the **real DEC-1732 cross-document guards** on deliberately altered *in-memory copies* of the five Markdown sources and the DEC-1726 nonauthorizing JSON ledger. Each mutation must make the corresponding DEC-1732 method raise an assertion while leaving the original source-doc objects unchanged.

Negative cases include falsely claiming current Phase 11, replacing Phase 8A discovery-first text, forging predecessor run384 into run385, changing the protected one-shot 2023 attempt 1 into attempt 2, mislabeling 2024 frozen, asserting the old unprotected main observation is current, claiming external gates PASS, creating unearned Phase 8A economic proof, counting PR/test metrics as revenue, allowing shadow, forging administrator validation or annual dispatch approval. A pristine control executes all 13 actual source-consistency guards successfully.

This remains a cross-document *source-only* validation exercise: document agreement or mutation resistance does **not** authenticate real GitHub administrator enforcement, the runner host/OS isolation, annual-run history, Strategy V1 returns or readiness for orders. No real data/private evidence is fetched and no production/runtime/parser/workflow/security code, GitHub rulesets/tags, annual dispatch/retry, broker/live operations or trading is changed.

Exact-head Phase3/full historical-general CI and independent qualified review required. Issue #779, DEC-650/#820 and DEC-651/#821 remain **BLOCKED**. There is no authorization or profit claim.
