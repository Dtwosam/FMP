# DEC-1671 — Escaped controls under array-contained evidence retain JSON semantic parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1917 at `b4f9ee3fc9e79461c6d537a03473003ecf00261b`. Adds 25 source-defined regression methods (**4,345 proposed total**).

The companion to DEC-1670's invalid raw controls adds the **valid JSON-escaped** U+0000, LF, CR and TAB spellings in nested objects within six evidence-array paths. Each case creates a deep-copied synthetic envelope and serializes its added key or value using `json.dumps`, which escapes the control. The strict JSON/text and stdin paths must return the same verdict as direct-memory review. Any semantic refusal of extra evidence is preserved, but a valid escape must not be incorrectly labeled `BUNDLE_JSON_GRAMMAR_UNREVIEWED` or `BUNDLE_JSON_UNICODE_UNREVIEWED`.

The source fixture remains unchanged; only allowlisted verdict keys are emitted, with no synthetic sample paths and no protected original OS, exclusive dispatch or annual-run authority. A clean control is included.

Own exact-head Phase 3/historical-general CI and qualified independent review required. Tests/docs only. No production/parser/limits/workflow/security changes, protected originals/archive/artifact access, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
