# DEC-1386 — Review-only annual workflow_dispatch input allowlist

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit child of #1609 DEC-1385 at `5c17c926ccf15ac4268430684602b422276af9e7`. **Ten new source-only unittest methods, 1,168 proposed.**

The committed annual workflow currently declares only `annual_segment_label` (required choice) and `previous_annual_freeze_run_id` (optional string). The predecessor field is optional because 2015 has no predecessor; the workflow performs its subsequent-year checks *inside* the preflight job. The new tests require those declarations to remain unchanged and detect an extra input, a duplicate, a missing predecessor, a change in type/requirement, or an unreviewed input reference injected into workflow source text. Mutations remain entirely in-memory. They read only a committed Git blob and never invoke the annual CLI or dispatch.

A checked-in input allowlist is not an independent external administrator-controlled GitHub run admission. It does not close the mutable `main` source SHA race or authenticate the protected 2023 run385 attempt1 slot. Any change to trusted dispatch ref source or installed workflow requires a separate reviewed design; no new input is installed here.

**DEC-650/#820** original protected OS no-write and **DEC-651/#821/#779** immutable exclusive server-side single-shot admission remain BLOCKED. New exact-head Phase3 and historical suite success plus qualified independent review required. No protected data, real artifacts, annual run/retry, GitHub workflow/ruleset/permission changes, broker/trading, merge or promotion.
