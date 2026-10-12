# DEC-975 — Native inotify mask, unlink and symlink identity reviewer matrix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** This is a documentation-only, strict one-commit child of DEC-974/#1195. It preserves **636 distinct source-defined test methods** and changes no observer runtime, executable test, CI configuration, runner or protected artifact.

## Distinct watch-registration rules demonstrated by genuine Linux controls

| Draft | Kernel behavior demonstrated with disposable public files | Why the behavior matters |
| --- | --- | --- |
| DEC-965/#1186 | Replacing a source mask without `IN_MASK_ADD` retains its numeric WD but loses earlier source content-write subscriptions | WD equality cannot prove subscription completeness |
| DEC-966/#1187 | Replacing a parent mask without `IN_MASK_ADD` retains its numeric WD but misses sibling namespace activity | Parent presence alone cannot prove a full directory-event census |
| DEC-968/#1189 | `IN_ONESHOT` source emits its first matching event and automatic `IN_IGNORED`; parent continues | Later source activity is no longer directly registered |
| DEC-969/#1190 | `IN_ONESHOT` parent observes the first sibling create then automatic `IN_IGNORED`; source continues | Later sibling deletions are missed by the removed parent registration |
| DEC-970/#1191 | `IN_MASK_ADD` preserves original write subscriptions and adds actual `IN_OPEN` | Unknown event masks are rejected as untrusted, not silently ignored |
| DEC-972/#1193 | `IN_MASK_CREATE` returns genuine `EEXIST` on already watched source and parent | No replace/add occurs; original source and parent watches still observe writes and entries |
| DEC-973/#1194 | Two independent directory instances differ with `IN_EXCL_UNLINK`: normal instance sees an open unlinked child's subsequent writes and close; filtering instance misses these but observes still-linked siblings | Empty filtered queue is not a write-free history |
| DEC-974/#1195 | Watching a symlink by default follows its target; `IN_DONT_FOLLOW` watches the symlink inode, invalidated when the link is unlinked | Symlink-entry identity and target-inode observation are different |

These cases use original private generated `/tmp` files and watch descriptors, real Linux kernel events, bounded reads, identity/metadata checks, and descriptor closure. The same numeric WD can survive mask replacement or be reused after removal; neither an FD nor a WD number proves uninterrupted registration, and independent instances can legitimately observe different subsets of events. It is incorrect to promote absence of events from a deliberately filtered or removed watch into authorization.

**Security interpretation:** The observer's only local statuses remain `BLOCKED` or `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`. The unmodified evaluator cannot authorize dispatch: `can_authorize_dispatch=false` and `independent_os_proof_verified=false` exactly. Genuine watch-registration behavior is still not independently OS-enforced no-write protection or qualified security review.

## Verification ledger and restrictions

At creation, this child requires its **own** exact-head Phase 3 and full historical regression, regardless of its parents' status; later passing descendants never retroactively make a failed SHA green. This reviewer document is not a live CI-status claim. Formatting corrections in DEC-968–971 replace literal backslash-escaped Markdown backticks with correct inline code spans; they do not change experiment assertions or claimed results.

Independently enforced protected no-write DEC-650/#820 and immutable exclusive one-shot annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. Do not run, test, retry or dispatch annual run385; access protected source/evidence; alter production workflow, refs, runners, rulesets or permissions; execute broker/trading operations; merge or promote this draft stack.
