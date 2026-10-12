# DEC-972 — Existing native inotify registrations reject IN_MASK_CREATE

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict child of DEC-971/#1192. New Linux regression and this document only.

Linux `IN_MASK_CREATE` (0x10000000) is a create-only watch-registration option. On the same live inotify instance, retrying `inotify_add_watch` for an already watched disposable public source inode or its parent directory with this flag must return `-1` and `errno.EEXIST`, rather than replace or add subscriptions. This is distinct from DEC-965–966 mask replacement and DEC-970 additive `IN_MASK_ADD`.

The new test installs real source and parent registrations, checks both actual native EEXIST errors, then changes and restores generated fixture bytes. Both original source and named parent write observations must still be present and well formed. A later unrelated disposable sibling creation/deletion also remains visible on the parent WD. Exact source/parent device, inode and mode plus final single-entry inventory are preserved; native FD closure is checked.

Actual write evidence is always evaluated as `BLOCKED` with `can_authorize_dispatch=false` and `independent_os_proof_verified=false`. A refused `IN_MASK_CREATE` attempt is **not** independent OS-enforced write prevention or proof of uninterrupted registration. One Linux source-defined method brings the draft stack to **634**. Exact-head Phase 3 and full historical regression and qualified independent security review remain required.

Protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No annual run385 dispatch/test/retry/rerun, protected source/evidence, production changes, broker/trading, merge, or promotion.