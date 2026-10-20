# DEC-1797 — Reject contradictory permissions in source-only upstream diagnostics

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of PR #2043 at `734f2ace8ae5a0d56021581730802dd052cf24c9`.

The six-source consolidated compiler formerly checked the protected annual/broker/live flags, but overlooked two explicit documentary permissions: `allows_shadow` and `allows_demo`. If an upstream documentary producer claimed one of those permissions while preserving the other denial flags, the consolidated JSON report could still look unconditionally BLOCKED without flagging the contradictory statement. The compiler also did not explicitly bind the documentary schema/decision and historical-workflow provenance markers.

Require both upstream shadow/demo flags to be the exact Boolean **False**, the documentary schema/decision to remain source-only DEC-1752, and the historical workflow report to retain its explicit fixture-only identity, audited source-workflow name, schema and *live ref not authenticated* flag. These are **source-only consistency assertions**, not real installed runner or GitHub administration attestation.

Four adversarial test methods cover shadow/demo approval claims, documentary schema drift, forged current-workflow/live-ref claims and CLI failure (both formats exit 2 with empty stdout). The normal fully BLOCKED CLI stays exit 3. Total **6,588 proposed source-defined tests** at this draft.

No installed GitHub workflow/ruleset/ref/runner modification, protected 2023/run385/attempt1 access/dispatch, broker/demo/live trading, real-money operation, or economic result. Eight independent external proof packages remain MISSING; issues #779/#820/#821 remain blocked. Exact-head Phase3/full regression CI and qualified review required.
