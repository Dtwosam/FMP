# DEC-1813 — Correct control-character test and reject all ASCII C0 proof edits

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent test repair of #2059 `f90003475039679b775ea3ddcae76e62f8b6d287`.

DEC-1812's first source edit and test accidentally used literal backslash-n/backslash-r, not actual LF/CR, yielding a **false sense of coverage** against newline-based proof-table injection. Preserve other #2059 lexical checks but require every proof-criteria character to have ASCII ordinal at least 32 and be neither a Markdown pipe nor a backtick. Repair the adversarial case to append actual LF and CR via `chr(10)` and `chr(13)`. Add another method verifying rejection of NUL, TAB and unit separator (`chr(0)`, `chr(9)`, `chr(31)`).

This is **source-only report integrity**, not a security attestation or a permission. One additional test: **6,633 cumulative proposed source-defined methods**. Valid output remains BLOCKED exit 3; forged criteria must fail before printing any JSON or Markdown.

No GitHub installed workflow/ruleset/ref/runner mutation, protected 2023/run385/attempt1, broker/demo/live trading, money or profit. Eight independent proof packages and #779/#820/#821 remain MISSING/BLOCKED. Exact-head CI and qualified independent review required.
