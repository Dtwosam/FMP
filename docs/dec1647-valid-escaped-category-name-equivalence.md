# DEC-1647 — Valid escaped top-level member spelling preserves source-only meaning

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1893 at `f6e87ab3687e2e0161afe206c3cec243d5b8d2f6`. Seventeen new regression methods (**3,893 proposed source-defined methods**).

DEC-1646 rejects duplicate decoded top-level JSON categories. This companion ensures legal lexical escapes, **without duplicates**, do not spuriously reject the same JSON document. Sixteen tests escape the initial ASCII character of each required top-level member name with a JSON Unicode `\\uXXXX` sequence; ordinary `json.loads` must produce the same clean envelope, and direct-memory, bounded JSON text and stdin must give the identical source-consistent but nonauthorizing verdict. The untouched clean control remains source-only; no protected OS evidence or annual dispatch approval is inferred.

Own exact-head Phase 3 and historical/general CI plus independent qualified review required. Tests/docs only, no production/parser/resource-budget/workflow/security/gate changes, protected originals/archives/artifacts, annual dispatch/retry, merge/deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
