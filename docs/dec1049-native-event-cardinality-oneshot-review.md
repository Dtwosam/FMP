# DEC-1049 — Native inotify write counts, one-shot disarm and quiet status accuracy

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only, one-commit review child of DEC-1048/#1269. This child does not add a test; the stack remains at **685 source-defined methods**. No runtime, protected evidence/source, production workflow, runner, rule, permission, broker or trading change.

## Equal receipt counts can describe materially different kernel histories

| Generated-public Linux control | Actual kernel activity on disposable `/tmp/sample` | Native source-only stream | Separate native source+parent observer | Security distinction |
| --- | --- | --- | --- | --- |
| DEC-978 (earlier source-only coalescing control) | Two genuine direct writes before source-only queue drain | One `IN_MODIFY` followed by eventual `IN_CLOSE_WRITE`; no `IN_IGNORED` | Observes real file modifications independently | Consecutive identical unread inotify events may coalesce |
| DEC-1044/#1265 | Six genuine `os.write` calls on ONE writable FD, original public bytes restored before queue drain | **One `IN_MODIFY`**, watch remains registered, no `IN_IGNORED`; each later per-write drain can observe a new MODIFY | >=6 source MODIFY and >=6 named parent MODIFY | One observed modification is not a per-syscall operation count |
| DEC-1045/#1266 | Six genuine `os.chmod` permission toggles, original `0600` mode restored | **One `IN_ATTRIB`**, watch remains registered, no `IN_IGNORED`; per-change drains observe later ATTRIB events | >=6 source ATTRIB and >=6 named parent ATTRIB | One attribute receipt is not the number of metadata operations |
| **DEC-1048/#1269** | Six real writes on one FD after source-only watch installed with `IN_MODIFY | IN_ONESHOT` | **Exactly one `IN_MODIFY` THEN `IN_IGNORED`**: kernel auto-removes watch at first trigger; later write/restore and close yield no source-only events | >=6 source and >=6 named parent MODIFY for first batch, independent later writes visible | One MODIFY can mean **auto-disarm**, not coalescing; `IN_IGNORED` is necessary evidence that subscription ended |

These tests use genuine Linux `inotify_init1`, independent watch instances, actual successful `os.write`/`os.chmod`, raw native kernel event record parsing, restored public source/parent device+inode+mode, original bytes, bounded inventory and closed native FDs. A disposable native Linux probe for DEC-1048 observed `IN_MODIFY` followed by `IN_IGNORED` and the separately witnessed modifications.

A **quiet native event buffer** can represent a valid, locally coherent observation without proving protected security controls. The unchanged `_evaluate` returns exact **`LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`** for a syntactically valid empty, unchanged-byte public receipt with no independent OS proof, and exact **`BLOCKED`** for real unsafe writes, attribute mutation, watch invalidation and other blocked outcomes. **Both** have exact `can_authorize_dispatch=false` and `independent_os_proof_verified=false`. Do not mislabel locally unverified as `BLOCKED`, but also never interpret locally unverified as authorization. DEC-1047/#1268 fixes the earlier two incorrect `BLOCKED` test assertions on empty receipts; no source observer runtime code is edited.

## Exact-commit CI failure ledger, no retroactive green

- Last established fully two-suite verified individual draft before the new experimental group: DEC-1039/#1260 `66fe18449dc56386af6b9a4d8f2162ecd3c50cc0`.
- **Original exact heads #1261–#1266 all FAILED historical regression**. Inspected CI logs show two erroneous empty-receipt exact-status assertions inherited from DEC-1040 and DEC-1042; these are **test expectation defects**, not evidence that the evaluator granted protected dispatch. Each exact red commit remains red permanently.
- Original #1267 at `b1d4e573b186238abfa5ea5d6c69dea81e336ef8` passed Phase 3; its historical suite was still in progress at this document's preparation. Do not infer it will pass.
- DEC-1047/#1268 at `8668343157a2831f894b924595b91838dd948e83` corrects the two exact assertions and the written contract; Phase 3 passed and historical remained in progress when checked. DEC-1048/#1269 and this child independently require their own completed Phase 3 AND full historical regression.
- Original failed exact heads #1201–#1205, #1212 and #1237 remain failed too. #1237's original historical failure cause is unknown due to unavailable job logs. Passing descendants cannot rewrite failed exact predecessor checks.
- Qualified independent security review is **separate** from CI and required even if both suites succeed. All drafts remain **DRAFT / NEVER MERGE / NEVER PROMOTE**.

Independent protected OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected annual evidence/sources, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading, merges, promotion or authorization.
