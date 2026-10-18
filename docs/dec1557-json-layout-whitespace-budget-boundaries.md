# DEC-1557 — JSON layout, whitespace and document ceiling boundaries

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1803 at `d9790df1d1ad4fd52ce745405712a815576bf76a`, adding nine synthetic regression methods (**2,774 proposed source-defined tests**).

The 2,000,000-character/UTF-8-byte input ceiling covers the complete submitted JSON document, including otherwise valid trailing whitespace and pretty-printing. Tests verify exact versus one-over text limits with trailing spaces; identical decoded arrays where compact formatting fits but pretty formatting crosses the cap; the four legal JSON whitespace bytes around a valid document; and refusal of vertical tab, nonbreaking space, leading BOM and raw NUL outside strings. Legal whitespace wrapping the synthetic source bundle must preserve source consistency alone, with all protected annual authority flags false.

Both exact-head Phase 3/full historical-general CI and independent qualified review required. No parser behavior, limits, workflow/security controls or admission changes. DEC-650/#820 independently witnessed protected-original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain BLOCKED. No protected annual execution/retry, original/archive/artifact access, merge, deployment or trading.
