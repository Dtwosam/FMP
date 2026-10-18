# DEC-1549 — End-to-end stdin JSON resource-budget isolation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1795 at `0f2db925a75068eb103adde166c1d5fc2b78bb5c`. Eight synthetic stdin/CLI regression methods; **2,706 proposed source-defined methods**.

DEC-1547 fixed the inherited historical/general assertion that accidentally tested the 16,384-item JSON array limit instead of the intended 32,768-object-member budget. Exercise the corrected exact/one-over object-member boundary and separate per-array overage through the public stdin path as well as the in-memory functions. A serialized unknown key, punctuation canaries and malformed trailing data must return exactly one safe diagnostic record, without echoing caller-supplied values. Unicode escaped/literal documents and differently serialized clean synthetic evidence must agree on source-only verdicts.

The CLI exit 0 is solely caller-supplied source consistency and never protected annual-run authority. No parser limits, test-run workflow, authorization surfaces or production code change.

Own exact-head Phase 3/full historical-general CI plus qualified independent review required. DEC-650/#820 independent protected-original OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected execution or retry, original/archive/artifact access, workflow/security changes, merge, deployment or trading.
