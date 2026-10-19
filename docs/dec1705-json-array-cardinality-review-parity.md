# DEC-1705 — JSON array cardinality changes defer to normal evidence review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1951 at `5da7bec39e09923191bda11635cfcebf67b34026`.

Adds **31 source-defined methods** (**5,641 proposed total**). Five JSON-legal cardinality/shape changes are applied to each of six required nested evidence arrays: empty list, singleton empty object, pair of empty objects, duplicate first item, and singleton null. Each modified array remains valid JSON. Strict JSON-text/stdin must preserve exact verdict parity with direct-memory review, allowing ordinary inventory/identity/shape diagnostics rather than falsely labeling valid JSON as grammar or Unicode failure.

Deep-copy synthetic caller evidence remains unchanged, stdout has exact safe fields and echoes no sample source paths, original OS proof, exclusive server dispatch and annual authority all remain false. Own exact-head Phase 3/full historical-general CI and independent qualified review required. Tests/docs only, no parser/production/workflow/security updates, protected originals/archive/artifacts, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
