# DEC-1643 — Missing mandatory evidence cannot be replaced by forged extra fields

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1889 at `15a64213846ba429a43fd204c6e085d97ed4dff6`. Fifteen proposed synthetic regression methods (**3,827 proposed test methods**).

Fourteen pairwise fixtures remove one independently required portable envelope category and add an unrelated field claiming approval, provenance, schema, copied CI evidence or a replacement source. A matching count of dictionary members does **not** replace the exact reviewed `REQUIRED` key set. Each mutated envelope must fail `BUNDLE_KEY_INVENTORY_UNREVIEWED` with exact direct-memory/JSON-text/bounded-stdin agreement, unchanged caller values, no changed-source path echo and all three protected authorization/proof flags false. The untouched fixture remains source-only.

Tests/docs only, no production, parser, resource limits, workflow/security/admission changes, protected original/archive/artifact access, annual execution/retry, merging, deployment or trading. Require own exact-head Phase 3/historical-general CI and qualified independent review. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
