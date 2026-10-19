# DEC-1687 — Legal JSON escapes in array-contained evidence values

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1933 at `e266ef05758fe366dd7b85493de0c1e94617370e`.

Adds **49 methods** (**5,024 proposed source-defined total**): eight valid JSON string escape spellings at each of six array-contained evidence dictionaries (runs, comparison files, run jobs, Phase 3 scenarios, full-tree entries and merge parents), plus a clean synthetic control. Escape spellings include escaped slash, ASCII and BMP Unicode, tab/newline, a valid surrogate pair, quote and backslash. A uniquely marked synthetic field is encoded with each escape form; strict JSON and stdin review must match the same decoded direct-memory fixture verdict without incorrectly classifying valid escapes as grammar or Unicode refusal.

Checks original caller immutability, exact stdout verdict field inventory, no source-path or marker echo and false protected annual proof/authority flags. Only synthetic evidence and tests/docs. Own exact-head Phase 3/full historical-general CI and qualified independent review required. No production/parser/limit/workflow/security changes, protected originals/archive/artifacts, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
