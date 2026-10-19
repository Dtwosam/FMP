# DEC-1766 — Safe local reading of frozen Phase7 retrospective evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2012, source SHA `33399e7a97a25327e0e70d62a03c10b27ec9f2f9`.

The DEC-1764/1765 historical cost replay used `Path.read_bytes()` before enforcing its fixed-document hash and maximum byte count. A caller-supplied `--phase7-document` symlink, named pipe or oversized file could therefore be followed/read before validation. This draft uses an opened **read-only O_NOFOLLOW + O_NONBLOCK** file descriptor and **fstat** to accept bounded nonempty regular files only, verify the same descriptor's expected length, and stop before hashing/parsing any suspicious input. It fails closed when required POSIX nofollow semantics are unavailable; it never modifies the document or filesystem permissions.

Adds **6** targeted tests (**6439 proposed cumulative**) for symlink-to-valid-source, FIFO, oversized/empty document, unmodified frozen bytes, and CLI error-code/empty-stdout behavior. Frozen Stage2 run/code/document identity, seven historical windows (including two negative), 199 retrospective trades and the 0.2/0.5/1.0 pip cost sign reversal are untouched. Normal retrospective reporter returns exit **3**, malformed source exit **2**; neither exit code authorizes trading.

No protected annual catalogue data, GitHub administrative/runner controls, protected 2023 run385 dispatch/retry, strategy promotion, broker/demo/live orders or real-money operations. #779/#820/#821 remain BLOCKED. Exact-head Phase3/full historical-general CI and independent qualified review required.
