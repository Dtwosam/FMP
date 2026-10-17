# DEC-1506 — Unicode scalar validity for direct in-memory evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1751 at `c9ca558f6b06fdae745d331a1a9a294903339c52`. Nine synthetic unittest methods, **2,305 proposed source-defined tests**.

The stdin/JSON path rejects unpaired UTF-16 surrogate code points in JSON strings before nested source review (DEC-1491), but the direct Python-object API permits caller-provided plain `str` values without JSON decoding. Such strings can contain U+D800–U+DFFF code points that cannot be encoded as ordinary UTF-8, potentially reaching source comparison or logging. Extend the bounded, cycle-safe direct-memory preflight to reject any such code point in text keys or values, including strings inside tuples; retain the existing aggregate scalar budget and all other type/number guards. Return only the safe `BUNDLE_STRUCTURE_BUDGET_UNREVIEWED` diagnostic for direct objects, and retain `BUNDLE_JSON_UNICODE_UNREVIEWED` for JSON input.

Nine synthetic tests cover high/low surrogates, dict keys, nested tuples, direct-envelope non-disclosure and false annual flags; valid emoji/multilingual/private-use code points and clean source-only fixtures continue to pass. This check never authenticates the caller's GitHub records, independently protects originals at OS level, or grants annual execution authority.

Own exact-head Phase 3/full historical-general CI and independent qualified review mandatory. DEC-650/#820 independently witnessed protected original OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected annual dispatch/retry, original/archive/artifact access, workflow/security modifications, merges, deployment or trading.
