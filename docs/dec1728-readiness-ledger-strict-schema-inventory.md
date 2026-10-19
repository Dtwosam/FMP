# DEC-1728 — Exact schema inventory and type guard for offline Phase 8A ledger

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1974 at `d0488443f8ce78f832a8030a8c513767fd625899`.

Adds **eight** independent test methods (**5,915 proposed source-defined methods**). The original DEC-1726/#1973 machine-readable ledger was intentionally nonauthorizing but did not assert the *names* of its 14 denial fields, or the absence of additional unreviewed members at the root and per-year levels. An unexpected field (e.g. a fabricated `annual_authorized:true`) must not silently coexist with an otherwise complete source-only snapshot.

The new independent inventory checks enforce:

- Exact top-level fields, no shadow authorization/secret fields and strict duplicate-key JSON decoding.
- Exact names and Python boolean types of all 14 non-authority flags; every one must remain `false`.
- Exactly 2015–2022 eight historical rows with strict key inventory and evidence class, and the exact distinct blocked reasons for 2023, 2024, 2025, 2026-YTD.
- Literal `2023/run385/attempt1` integers (reject `true == 1` equivalence), the historical 2022 run384 predecessor and original `main` Git SHA explicitly disqualified as live authorization evidence.
- No phase-8B/demo/live approvals, no Strategy V1 economic proof, no allowed actions and `BLOCKED` external gate.

No protected data, source-of-truth annual workflow, parser, security settings, runner, dispatch, artifact, broker, real money or trading changes. All values are documented **source-only**, cannot authenticate effective GitHub administrator bypass/enforcement or prove the run385 inventory. Exact-head Phase 3/full historical-general CI and qualified review required; #779, DEC-650/#820, DEC-651/#821 remain **BLOCKED**.
