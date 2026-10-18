# DEC-1540 — Global JSON object-member budget for offline source evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1785 at `c76cd7b4aad64aa5d8c2b1a1803775f3fb2f5594`. Adds **nine synthetic unittest methods**, reaching **2,625 proposed source-defined methods**.

A per-object 16,384-key JSON decoding cap already exists (DEC-1522). A malicious caller can stay under that per-object cap while submitting tens of thousands of small JSON objects and exhausting aggregate parsing work. For each distinct `review_bundle_json_text` call, give the standard JSON parser a fresh bounded object-pairs hook. Count each decoded object's members across all nested objects and refuse above **32,768 total members** with the existing safe `BUNDLE_JSON_GRAMMAR_UNREVIEWED` verdict. The previous per-object cap, duplicate-key rejection, text/UTF-8 budgets and all annual refusal flags remain intact. This is a post-pairs decoder guard; it is not proof of memory isolation.

Nine regression tests cover exact/over total budgets, duplicate/per-object guard precedence, many small objects, per-document counter reset, safe stdin output and a clean synthetic source-only consistency result. No GitHub provider authentication, witnessed protected-original OS no-write, or annual one-shot admission is established.

Own exact-head Phase 3 and full historical/general CI plus independent qualified review required. DEC-650/#820 independently witnessed protected original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected execution/retry, originals/archives/artifacts, installed workflow/security changes, merge, deployment or trading.
