# DEC-1849 — Escape untrusted invalid-evidence diagnostics as a single line

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2095 at `c49b0b394a1fcbf5c1f1bca800aa7e1a361f9874`.

The review CLI correctly rejects invalid packets with exit 2 and no stdout, but it previously interpolated `str(exc)` verbatim into stderr. A caller-controlled file name or malformed upstream validation error can include a literal line break or terminal ANSI escape that visually spoofs a second `APPROVED` result, despite the real BLOCKED disposition.

Represent exception detail with `ascii(str(exc))` before diagnostic output, which escapes CR/LF, tabs and ANSI controls, and bound that detail to 400 characters. Only the fixed `BLOCKED:` prefix and a single newline are emitted. These controls **do not** suppress failures or grant execution; valid reviewed packets remain BLOCKED/nonzero exit 3, invalid ones exit 2 without stdout.

Three negative tests (**6,735 cumulative proposed source-defined**) inject newline/ESC/CR in validation exceptions, oversized tab-containing diagnostics and an actual newline-containing invalid packet filename. No external admin/runner proof, protected 2023/run385/attempt1, installed GitHub ref/ruleset/workflow changes, broker/demo/live trade, real money or profit. All eight independently acquired proof packages and #779/#820/#821 remain MISSING/BLOCKED. Own exact-head Phase3/full CI and qualified independent review required.
