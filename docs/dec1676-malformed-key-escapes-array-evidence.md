# DEC-1676 — Malformed JSON escapes in nested member keys inside evidence arrays

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1922 at `b5e736ef62510eefbc7477417da9ffa69546eccd`, with 25 synthetic regression methods (**4,510 proposed source-defined methods**).

The preceding DEC-1675 draft covers malformed member names directly inside dictionary-valued top-level evidence. This complement goes deeper: six array-contained evidence object paths (runs, jobs, comparisons, Phase 3 scenarios, full tree entries and merge parents) each receive one of four invalid key escapes (`\\q`, `\\x00`, `\\u00G0`, `\\u12`). Each malformed string remains inside a nested *key*, never a scalar value. Strict Python `json.loads` must reject; bounded JSON-text and stdin must return exactly `BUNDLE_JSON_GRAMMAR_UNREVIEWED`.

The serializer rewrites only the named evidence array object, preserving caller input, the clean synthetic source-only control, exact verdict shape, no source path echo and all false protected annual authority flags. The DEC-1674 uniqueness guard remains active.

Exact-head Phase 3/full general CI and qualified independent review are required. Tests/docs only, no production/parser/resource-limit/workflow/security changes, protected originals/archives/artifacts, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
