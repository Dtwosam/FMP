# DEC-1610 — Order-independent compound Git tree faults

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1856 at `90b796d113e0220a8f8e70b8f5aa49e6d43801db`. Sixteen regression methods (**3,346 proposed source-defined methods**).

Two independent mutations must not accidentally cancel one another, hide a diagnostic, or make the verdict depend on the order the caller populates its evidence. Test fifteen pairs of executable leaf modes, contradictory source-blob SHAs, renamed Git entries, invalid parent type, independently forged flat node modes, orphan snapshots, malformed SHA fields and truncated children. Apply each pair in both orders to a fresh synthetic envelope, assert the *complete verdicts agree*, and then check all relevant reviewed diagnostic codes across direct-memory, JSON text, and bounded stdin with no path echo. Preserve a clean, nonauthorizing control.

These are caller-provided offline evidence consistency checks, not provider authentication or protected annual authorization. Own exact-head Phase 3/full historical-general CI and qualified independent review required. Tests/docs only, no production/parser/budgets/workflow/security/admission changes, original/archive/artifact access, annual dispatch/retry, merging, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
