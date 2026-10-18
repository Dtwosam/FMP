# DEC-1551 — No-decoder-allocation lexical JSON ceilings

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact one-commit tests/docs child of #1797 at `05bcf099e2086c415bdda7c956d1e31204ddfd05`. Eight new synthetic regression methods; **2,723 proposed source-defined tests**.

Verify the predecode resource guards actually short-circuit expensive JSON decoding: over-limit **global** object members and array items, global UTF-8 document bytes, global document character count, and unbalanced container closers must never call `json.loads`. The independent exact-inventory global object/array cases must call the standard decoder once and reach the ordinary envelope shape refusal. A lexically budget-safe but grammatically invalid trailing-comma document must also be validated and refused by the standard decoder. This prevents silently treating structural lexing as a complete JSON grammar check.

No production code, parsing ceilings, workflow or authorization policy changes. Both exact-head CI suites and qualified independent review are still required. DEC-650/#820 protected-original independent OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 admission remain BLOCKED. No protected annual execution or retry, original/archive/artifact access, merging, deployment or trading.
