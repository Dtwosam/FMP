# DEC-1543 — Predecode lexical JSON object-member ceilings

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1789 (`1bb3e7601f2cfcb46b8537352e7376275f3b4a87`). Ten new synthetic regression methods; **2,654 proposed source-defined tests**.

DEC-1540 bounds object-pairs counts inside the JSON decoder but must still accept its temporary pairs input. Complement the decoder hook with an iterative lexical object-member preflight that tracks structural commas inside object frames outside strings, respects escaped quote text, rejects unbalanced brackets, and enforces **16,384 members per object** and **32,768 members cumulatively** before `json.loads`. Keep the decoder-side duplicate-key and per-document count checks, array scanner, nesting and UTF-8 input bounds as defense in depth. This preflight does not validate full JSON grammar or avoid all Python string allocations.

Ten synthetic tests check exact/over per-object and aggregate limits, many small objects inside bounded arrays, escaped strings, empty objects, decoder non-invocation on oversized input, safe one-line stdin refusal, and nonauthorizing valid synthetic evidence. None of these local source-shape checks authenticates GitHub records or permits annual protected execution.

Own exact-head Phase 3/full historical-general CI with qualified independent review required. DEC-650/#820 independently witnessed protected originals OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected execution/retry, originals/archive/artifacts, workflow/security changes, merges, deployment or trading.
