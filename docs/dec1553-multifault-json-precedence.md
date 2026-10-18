# DEC-1553 — Deterministic JSON multi-fault diagnostic precedence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1799 at `49e15ed76989e1886168d1c36b0e25a132fb8a34`. Nine new synthetic unittest methods; **2,740 proposed source-defined tests**.

Several independent rejectors may apply to the same malformed caller JSON. Preserve the established order: document character/UTF-8 caps before lexical or duplicate-key checks; nesting/lexical container budgets before decoder parsing; decoded duplicate keys before the surrogate walker; unpaired Unicode before bundle key inventory; and bundle inventory after valid JSON syntax. A malformed escaped-key alias cannot invoke the downstream source reviewer. Every rejection remains a closed diagnostic without granting independent OS evidence, exclusive server admission or annual permission.

No change to parser implementation, existing diagnostic names or resource ceilings. Both exact-head CI suites and qualified independent review are required. DEC-650/#820 independent protected-original OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 admission remain **BLOCKED**. No protected annual dispatch/retry, original/archive/artifact access, workflow/security-control change, merge, deployment or trading.
