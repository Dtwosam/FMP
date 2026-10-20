# DEC-1798 — Close upstream source-only diagnostic field allowlists

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of PR #2044 at `1af41b3b0b48e277615ecbe5489846cf55ea513d`.

The six-source compiler consumes two offline reports: DEC-1752 documentary readiness and DEC-1779 historical workflow audit. It previously checked named denial flags, proof identities, reviewed SHA and runtime gates but could ignore an unexpected additional upstream field (for example a fabricated `approved_live_trade` flag) while emitting its own clean-looking, fully BLOCKED consolidated packet.

Require each upstream report to be a plain Python dictionary with **exactly the reviewed complete field names** — a 22-field documentary schema and a 21-field historical-workflow schema. This is source-only input compatibility, not live installed workflow inspection or administrator attestations. Any unknown, removed or malformed field fails closed as `InvalidHandoff`; it cannot be silently projected away by JSON or Markdown output. No upstream fields or existing downstream JSON fields are added or removed.

Adds 4 adversarial tests (**6,592 cumulative proposed source-defined methods**): unknown documentary approval, unknown workflow order authority, removed source/human provenance, and both CLI formats rejecting forged upstream metadata with status 2 and no stdout. Valid BLOCKED reports remain nonzero exit 3.

No installed GitHub workflow, security, ruleset or ref mutation; no 2023/run385/attempt1 read/dispatch, broker/demo/live action, economic/profit inference, or external permission. #779/#820/#821 and all eight independent proofs still MISSING/BLOCKED. Exact-head Phase3/full CI and qualified independent review required.
