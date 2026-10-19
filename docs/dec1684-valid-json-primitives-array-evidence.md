# DEC-1684 — Legal JSON primitives inside array-contained evidence preserve source review parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1930 at `c66739f22014e93ece36b94c847842391dbaf6dc`. Adds 19 source-defined methods (**4,841 proposed total**).

DEC-1683 verified that Boolean/null primitives cannot substitute top-level required evidence category types. This companion tests the correct lexical behavior *inside* six array-contained evidence objects: runs, CI job records, comparison files, Phase 3 scenarios, full Git-tree entries and merge parents. An additional synthetic `true`, `false` or `null` field is inserted into a deep-copied nested dictionary. Strict JSON-text/stdin parsing must agree with direct-memory review, without a false grammar/Unicode error. The additional field may be rejected by normal evidence validation; equivalence, not semantic admission, is the invariant.

All cases preserve the original clean caller fixture, exact safe verdict inventory, no synthetic changed-file path echo and false independent original OS, exclusive server dispatch and annual-run proof/authority flags. One clean synthetic source-only control is included. Test-name uniqueness guard remains.

Own exact-head Phase 3/full historical-general CI and independent qualified review required. Tests/docs only. No production/parser/limits/workflow/security changes, protected original/archive/artifact access, annual execution/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
