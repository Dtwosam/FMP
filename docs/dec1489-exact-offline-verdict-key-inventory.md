# DEC-1489 — Closed five-field offline CI evidence review verdict

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1734 at `7d5d6c8342d7e16b20c48325548c9f1057db9996`. Nine new synthetic unittest methods, **2,133 proposed source-defined methods**.

The DEC-1478/1484 portable offline JSON evaluator checked the types and semantics of its five documented result fields, but did not reject additional fields from the nested evidence reviewer. The stdin-only CLI serializes the reviewer's returned dictionary. An extra field holding raw evidence or protected material could therefore be echoed despite all expected flags being false.

Enforce exactly `source_consistency`, `diagnostics`, `independent_original_os_proof`, `exclusive_server_dispatch_gate_proven`, and `can_authorize_annual_run`. Any missing, unexpected or non-string key, or dictionary subclass, yields only the existing safe `BUNDLE_RESULT_SHAPE_UNREVIEWED` failure. A valid five-field negative result remains acceptable with sorted safe diagnostics. Nine new synthetic tests include direct and stdin JSON outputs, positive and negative controls, missing fields, unexpected keys and protected-string non-disclosure.

This is an offline source-review output contract, not provider provenance, independently witnessed OS protections or GitHub server admission. Own exact-head Phase 3/full historical-general CI and qualified independent review mandatory. DEC-650/#820 independently witnessed protected originals OS no-write and DEC-651/#821/#779 exclusive immutable 2023 run385/attempt1 server admission remain **BLOCKED**. No annual dispatch/retry, protected originals/archive/artifact access, installed workflow/security setting changes, merge, deployment or trading.
