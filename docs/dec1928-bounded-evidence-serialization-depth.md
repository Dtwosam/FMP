# DEC-1928 — Bounded deterministic evidence serialization depth

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source/tests/docs child of PR #2176 at `c2b550783ebf6c682eb46fb73f724aa0181445a2`.

The deterministic serializer previously recursively expanded mapping/list/dataclass values with no depth cap. Self-referential or extremely deeply nested caller-supplied run identity/metric trees could end in uncontrolled Python `RecursionError` before artifact publication. Limit recursive JSON-like evidence traversal to 64 nested levels, preserving the previously accepted 32-level decision-config metadata budget with room for enclosing run identity and record envelopes. Use exact tuple/list admission at this serialization boundary to avoid user-defined sequence overrides. Reject exceeding depth with a controlled `ValueError` before any artifact-directory mutation.

Three synthetic methods cover cyclic identity refusal with zero filesystem writes, excessive nested metric refusal and a valid 32-level nested identity roundtrip. **6,945 cumulative proposed source-defined methods.** Own exact-head Phase3 and full historical/general CI plus independent evidence review are required; the limit is not a full breadth or resource-use guarantee.

Phase8A #779/#820/#821 and eight independent external security proof packages remain MISSING. Protected 2023/run385/attempt1, later annual research, Strategy V1 economic approval, shadow/demo/Phase10/11, installed GitHub ref/workflow/ruleset/runner changes and broker/live capital remain BLOCKED. No protected research dispatch, money or trading.
