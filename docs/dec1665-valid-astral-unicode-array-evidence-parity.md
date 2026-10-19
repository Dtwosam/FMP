# DEC-1665 — Literal supplementary Unicode and escaped pairs inside array evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1911 at `9085c971419090ccf32704a75aafe4bacfd2fec1`. Thirteen new synthetic regression methods (**4,187 proposed**).

This extends DEC-1664's positive Unicode lexical parity to objects contained within six evidence-array pathways: historical/Phase 3 runs, jobs-by-run, comparison files, Phase 3 scenarios, full Git tree entries, and merge parents. Each path tests a synthetic extra child **key** and a synthetic extra child **string value** containing U+1F680. A deep-copied envelope is serialized with literal supplementary Unicode and the valid escaped UTF-16 surrogate-pair spelling. Both JSON texts must decode to the same object and return the same verdict as direct in-memory review, including the stdin command.

An extra evidence field is **not** itself claimed to be reviewed or accepted. The invariant is no false JSON grammar/Unicode rejection of a valid supplementary character, no mutation of caller's clean evidence, no disclosure of synthetic source paths, and no permission for independent-original OS proof, exclusive dispatch gate or annual execution. One clean nonauthorizing control is included.

Own exact-head Phase 3, historical/general CI and independent qualified review remain required. Tests/docs only; no production/parser/limits/workflow/security changes, protected original/archive/artifact access, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
