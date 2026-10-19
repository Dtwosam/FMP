# DEC-1652 — Duplicate decoded JSON category fields with invalid last values fail at grammar ingress

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1898 at `25c6ae25b96e8f438ba0460d83b3a1978f90cbfc`. Seventeen new methods (**3,964 proposed source-defined methods**).

DEC-1646 proved null-first, valid-last duplicate Unicode-escaped keys must be rejected even though a permissive decoder yields a clean envelope. The adversarial complement places the **valid reviewed value first and an escaped alias whose value is `null` last**, for each of the sixteen required top-level categories. A last-key-wins parser would instead yield a poisoned schema, missing container or null evidence map. Strict bounded JSON text and stdin must still reject the duplicate as `BUNDLE_JSON_GRAMMAR_UNREVIEWED` *before* downstream category or schema review. The original clean synthetic source remains nonauthorizing.

Own exact-head Phase 3/general CI and qualified independent review required; tests/docs only. No production/parser/resource-limit/workflow/security/admission changes, protected originals/archives/artifacts, annual execution/retry, merge, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
