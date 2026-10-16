# DEC-1378 — Annual calendar / market matrix source coherence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit child of #1601 DEC-1377 at `c5e1ef6ab32d90ac0a53b11ad5aed032d8a32a7c`. Ten static test methods added; **1,118 proposed source-defined tests**.

Compares the literal frozen market universe in `src/fmp/discovery/pattern_protocol.py` (three symbols, three timeframes and two minute horizons) with the 18 cells in the *actual tracked* annual GitHub YAML; checks the 12 annual segment choices and date boundaries against the current method source, and the 18+2 jobs/artifacts / 216 full-collection cell contract against the workflow-plan source. Offline mutations test mismatched cells, missing rows and the partial final segment label. The checks are *read-only source* assertions and do not run 216 cells, collect any new data, access historical archives, evaluate patterns or synthesize a strategy. Four repo-controlled sources may agree without independently proving server-side admission or original historical object authenticity.

The actual 2026 collection cutoff remains **2026-08-20**, even though the wall clock is later. Existing no-synthesis/no-trading flags stay documented. Prior frozen outcomes, annual execution and protected history are not touched. All tests use local `git show HEAD:path` and AST literal parsing; no FMP production module imports.

Own exact-head Phase 3 plus complete historical CI and qualified review are required. Independent protected original OS no-write DEC-650/#820 and immutable exclusive 2023 run385/attempt1 GitHub dispatcher DEC-651/#821/#779 remain **BLOCKED**. No annual jobs, one-shot dispatch/retry, protected evidence, workflow/ruleset/permission mutation, broker/trading, merge or promotion.
