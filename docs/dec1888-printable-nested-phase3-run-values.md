# DEC-1888 — Printable nested source-only decision provenance values

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2136 `502febb53ca0c65ed0758228a2c383aaca705e33`.

The recursively immutable decision metadata checks guard keys, finite JSON scalars, depth and size, but values could still embed LF, CR, NUL, ANSI Escape or DEL, potentially spoofing a displayed human audit record. Reject such characters anywhere in nested string values, plus unpaired Unicode surrogate codepoints in both keys and values. Ordinary valid Unicode names and multilingual synthetic labels stay supported.

Three new Phase3 test methods (**6,841 cumulative proposed source-defined**) assert nested terminal-control denial, surrogate denial and safe multilingual metadata round-tripping. Source-only configuration validation is not external authentication, privileged runner OS proof, a real market backtest or a verified profitable strategy. Own exact-head Phase3/full regression and qualified code review required.

Phase8A accepted annual catalogue ends at 2022/run384. Protected 2023/run385/attempt1, later research, Strategy V1 synthesis, shadow/demo/live broker orders, capital and installed GitHub ref/workflow/ruleset changes remain BLOCKED. Independent #779/#820/#821 eight administrator/ref/runner/provenance/inventory/human proofs remain MISSING.
