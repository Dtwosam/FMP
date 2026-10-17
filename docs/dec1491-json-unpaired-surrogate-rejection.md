# DEC-1491 — Reject unpaired JSON surrogates in offline CI bundles

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit, tests/docs-only child of #1736 at `59f06887f693adb590ab69315cc67589a5ce7e55`. Ten synthetic regression methods; **2,152 proposed source-defined methods**.

The portable evidence review command reads caller-provided JSON text. Python's `json.loads` can accept escaped, lone UTF-16 surrogate code points in JSON string keys or values. Such strings are not valid Unicode scalar text and can fail when serialized or passed to UTF-8-based tools. After grammar and nesting checks, walk the bounded parsed document iteratively, reject any U+D800–U+DFFF code point in keys or values with `BUNDLE_JSON_UNICODE_UNREVIEWED`, and never reflect its content. A valid paired escape decodes to a Unicode scalar and remains permitted.

Ten negative/positive tests cover high/low unpaired escapes, object keys, nested evidence, valid paired emoji, multilingual BMP/non-BMP text, stdin non-disclosure and a clean synthetic source-consistent envelope. The check does **not** authenticate caller-supplied GitHub records, protect original files at OS level or authorize annual execution.

Own PR-associated Phase 3 and full historical/general CI at exact head, plus independent review, required. DEC-650/#820 protected-original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No annual dispatch/retry, protected originals/archives/artifacts, installed workflow/security changes, merges, deployment or trading.
