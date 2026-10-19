# DEC-1645 — Envelope key inventory outranks schema, schema outranks category types

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1891 at `9b5d1ae89f2aca1a75c2636bc68dcf47151b679a`. Fifteen synthetic regression methods (**3,859 proposed source-defined tests**).

Fail-closed precedence is part of the portable reviewer contract. Fourteen pairs mutate two top-level evidence properties in **both orders**: an invalid schema with malformed category container, or a missing/extra mandatory key with an invalid schema. Demand identical exact public diagnostics, where `BUNDLE_KEY_INVENTORY_UNREVIEWED` precedes schema validation and `BUNDLE_SCHEMA_UNREVIEWED` precedes category type validation, irrespective of insertion order. Direct-memory, JSON text and bounded stdin agree without caller modification, echoing paths or claiming annual authorization. An untouched fixture is source-consistent only.

Require own exact-head Phase 3/historical general CI and qualified independent review. Tests/docs only; no production/parser/limits/workflow/security/gate changes, protected originals/archives/artifacts, annual dispatch/retry, merging, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
