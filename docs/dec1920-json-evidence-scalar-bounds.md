# DEC-1920 — Bounded scalar JSON evidence admission

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2168 at `af3c5248bd73fdd608dfde72069dc382e8fe3eb6`.

The deterministic Phase3 serializer formerly accepted arbitrary `str` and built-in `int` values. Python JSON UTF-8 output can fail with an uncontrolled UnicodeEncodeError on an unpaired surrogate, while extremely wide integers can stress JSON encoding or trip interpreter digit limits. Reject surrogate code points in evidence strings and bound ordinary source-defined integer scalar width to **512 bits** before serialization. Preserve ordinary Unicode, accepted financial scalar types and valid small/medium JSON values. These are validation rules, not a claim that artifacts provide trusted external financial evidence.

Three synthetic regression methods check no filesystem I/O for surrogate strings or extreme integers, with a Unicode/512-bit valid control. **6,922 cumulative proposed source-defined methods**. Requires own exact-head Phase3 and full historical/general CI plus independent review; no checks inherited from parent.

Phase8A independent #779/#820/#821 blocker proofs (eight packages) remain MISSING. Protected 2023/run385/attempt1, future annual research, Strategy V1 economics, shadow/demo/Phase10/11, installed GitHub workflow/ref/ruleset/runner changes and broker/live capital remain BLOCKED. No protected dispatch, trade, money or realized profit.
