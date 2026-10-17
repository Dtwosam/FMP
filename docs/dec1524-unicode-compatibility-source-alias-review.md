# DEC-1524 — Source path identity across Unicode compatibility forms

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict exact-parent one-commit tests/docs child of #1769 at `4d1da5b57d05234968378aaefa1d74d6574c1cd6`. Nine synthetic methods; **2,478 proposed source-defined tests**.

The source maps enforce NFC, portable path structure and Unicode case-fold uniqueness, but two lexical paths such as `src/ＡＢＣ.py` and `src/abc.py` can remain distinct under `casefold()` even though NFKC compatibility normalization maps them to the same visual/compatibility identity. To prevent accidental source inventory aliasing across tools and reviewer platforms, calculate a **comparison-only** source identity via `unicodedata.normalize("NFKC", path).casefold()`. Use it for uniqueness within changed-source and CI-workflow maps and across these maps. Keep supplied literal path strings intact, never rewrite or dereference them, and retain existing NFC, UTF-8 length, resource and diagnostics checks.

Nine regression methods cover fullwidth Latin letters, circled numerals, Roman numerals, workflow map aliases, cross-map aliases, distinct directories, safe stdin and the unchanged positive source-consistency-only bundle. NFKC comparison is a conservative alias check, not evidence that GitHub or a specific filesystem performs NFKC normalization.

Own exact-head Phase 3/full historical-general CI and independent qualified review required. DEC-650/#820 independently witnessed protected originals OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected annual execution/retry, originals/archive/artifact access, workflow/security modifications, merges, deployment or trading.
