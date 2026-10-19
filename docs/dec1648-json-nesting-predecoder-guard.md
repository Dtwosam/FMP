# DEC-1648 — Over-depth JSON containers cannot reach the decoder or nested source review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1894 at `31648c15e7e94bf5b77335017cfb5d00848d28b6`. Thirteen regression methods (**3,906 proposed source-defined methods**).

Twelve adversarial JSON documents substitute an otherwise required top-level field's value with a valid JSON array nested beyond `MAX_JSON_NESTING`. The input remains small enough to avoid text limits, but its container stack exceeds the reviewed pre-decoding budget. Assert the lexical depth guard refuses before JSON object materialization, returning only `BUNDLE_JSON_GRAMMAR_UNREVIEWED` to both JSON text and bounded stdin, without exposing changed paths or protected annual authority. The unchanged in-memory envelope remains source-consistent only. This directly tests the parser's bounded nesting invariant and does not claim that an overdeep JSON input has a direct-memory equivalent.

Require own exact-head Phase 3/general CI and qualified independent review. Tests/docs only, no production/parser/resource limits/workflow/security/admission changes, protected originals/archive/artifacts, annual execution/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
