# DEC-1952 — Bounded-memory Phase3 payload verification

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source/tests/docs child of PR #2200 at `9a4c2253c5322a50b58f900325f8ed9c0a3de5aa`.

The read-only Phase3 verifier previously loaded each payload using `Path.read_bytes`, which could allocate memory proportional to a large evidence JSONL file even though the manifest itself is capped at 256 KiB. Retain the trusted four fixed artifact filenames, canonical shape and symlink checks, but compute SHA256 and observed byte size in fixed 1 MiB chunks. Stop immediately when bytes exceed the manifest's declared size and refuse any size/digest disagreement. Preserve the exact public verifier result and schema, with no payload mutation.

Two synthetic methods verify a 2 MiB+ file can be checked without any `Path.read_bytes` call on that payload, and that a file enlarged beyond the declared size is rejected. **6,986 cumulative proposed source-defined test methods**. Own exact-head Phase3/full historical/general suites and independent qualified source review required. This bounds memory for ordinary files; it is not a guarantee against concurrent replacement, malicious pipes, filesystem race, privileged runner compromise, authentic data or profitable trades.

Historical #2178–#2191 full failures are retained as FAILED; #2192–#2200 own full suites require independent completion. Phase8A #779/#820/#821 eight external proof packages remain MISSING/BLOCKED, accepted annual-first catalogue ends 2022/run384; protected 2023/run385/attempt1, later research, Strategy V1 economics, shadow/demo/live broker capital and installed GitHub workflows/refs/rulesets/runners remain unauthorized. No protected dispatch, merge, broker orders or money.
