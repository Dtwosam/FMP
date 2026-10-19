# DEC-1762 — Bounded, no-follow source reads for offline evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent tests and offline-report helper child of PR #2008 at `423d4a5b1b0b8a2a4c39ba8fb562261bb9312e20`.

The DEC-1752 report's `Path.read_bytes()` followed symlinks and permitted special files or oversized inputs to be treated as evidence. This was not evidence of a live exploit, but it could make an operator-run offline review hang on a FIFO, hash an unintended file or consume unbounded memory. New ingestion uses a **read-only no-follow file descriptor**, rejects anything other than bounded nonempty regular files before reading, limits each JSON packet to 1 MiB and verifies the byte count against the opened descriptor. If the current OS lacks the necessary no-follow primitive, the report fails closed rather than guessing.

Adds 6 source-only regression checks (**6410 proposed methods cumulative**) including symlink, FIFO, oversized file, empty source, no writes, and CLI code2/no-stdout on invalid input. A normal still-BLOCKED report continues to exit 3; the tool remains offline, uses only the five named documentary packets and **never** becomes an independent administrator or runner witness.

No protected annual market data, no annual run385 dispatch or retry, main/ref/protection/workflow/runner mutation, Phase8B, broker/demo/live orders, money movement or trading. Issues #779/#820/#821 remain BLOCKED. Needs exact-head Phase 3/full regression CI and independent qualified review.
