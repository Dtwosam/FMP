# DEC-1848 — Prevent mixed --help from returning false verification success

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2094 at `229cfff754925a840a8322248c4278b07fc9fd93`.

The read-only security-review CLI uses exit 3 for valid **BLOCKED** evidence and exit 2 for invalid evidence. Python argparse can short-circuit parsing when `--help` or `-h` appears anywhere, returning zero and printing help without verifying the supplied packet. An operator or downstream wrapper could misinterpret `--verify-report forged.json --help` as a successful verification when no packet was checked.

Require **help to be the only argument** for exit 0; any mix of help with verification flags, output formats, repeated help, or other inputs fails closed at code 2 with empty stdout and a BLOCKED error. Pure `-h` or `--help` remains ordinary help output and does not construct or authorize any evidence.

Three focused regression methods bring the proposed source-defined cumulative count to **6,732**. Existing canonical local saved evidence checks, all eight MISSING owners, the protected 2023/run385/attempt1 BLOCKED run identity and nonzero valid result are unchanged. This is a CLI ambiguity fix, not independent administrator/OS attestation or a decision. #779/#820/#821 remain OPEN and all eight external proofs MISSING; no protected annual dispatch, workflow/ref/ruleset mutation, broker/demo/live order, capital or profit. Own exact-head Phase3/full regression CI and qualified review required.
