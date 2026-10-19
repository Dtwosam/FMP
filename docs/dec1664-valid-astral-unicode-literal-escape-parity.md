# DEC-1664 — Valid supplementary Unicode key/value lexical parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1910 at `59a16181c9b137e5f30c295d99b40a2b0eabe746`; 29 new synthetic regression methods (**4,174 proposed source-defined methods**).

After testing decoded duplicates of literal supplementary Unicode and escaped surrogate-pair keys, this draft verifies the complementary valid case across all fourteen mandatory dictionary-valued evidence categories. One additional synthetic key or string value is introduced via a copied envelope, never mutating the original caller fixture. The same valid U+1F680 scalar is serialized as literal UTF-8 JSON (`ensure_ascii=False`) and as a correct escaped UTF-16 surrogate pair (`ensure_ascii=True`). Both document forms must decode to the *same* in-memory evidence and yield exactly the same source-review verdict, including via stdin.

A newly added evidence field may be separately rejected by the reviewer. These tests **do not claim it is admissible**: they require parity with the direct-memory verdict and explicitly forbid JSON grammar or Unicode refusal of a valid surrogate pair, output echoes of protected synthetic paths, and any elevation of independent-original OS, exclusive dispatch, or annual-run authority.

Own exact-head Phase 3 and full general/historical CI, plus independent qualified review, required. Only tests/docs changed; no production/parser/resource-limit/workflow/security controls, protected originals/archive/artifacts, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
