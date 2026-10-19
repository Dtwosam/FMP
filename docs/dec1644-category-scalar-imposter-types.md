# DEC-1644 — Category type validation does not accept scalar imposters

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1890 at `c105e43485db14dca2c47d4043ccc5fdfa6a9d3a`. Seventeen regression methods (**3,844 proposed source-defined tests**).

Required top-level evidence categories have exact Python/JSON container types: `runs` is a list, all non-schema categories are dictionaries. Sixteen synthetic negative inputs substitute null, booleans, numbers or strings into distinct source, CI, Git, PR, compare and run categories. None may pass because an empty/false/truthy value resembles an empty valid collection; all must return `BUNDLE_CATEGORY_TYPE_UNREVIEWED` at direct-memory, JSON text and bounded stdin. Confirm no caller mutation, no source-path echo and false protected proof, server dispatch and annual authority. The exact clean category shape remains source-consistent only.

Tests/docs only; no production/parser/resource limits/workflow/security/admission changes, protected original/archive/artifact access, annual execution/retry, merge/deployment/trading. Own exact-head Phase 3 and full historical/general CI and independent review required. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
