# DEC-1724 — Repair real-newline comparison for installed workflow permissions

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent test/docs-only child of #1970 at `f63f97b9041e27023c0b7c312d50c60c1e0b9327`.

The new DEC-1716 installed-workflow regression suite preserved one incorrectly doubled Python escape after DEC-1717: its read-only GitHub permission assertion compares the actual YAML block against a *literal backslash-n* rather than a newline. The installed workflow reads:

```yaml
permissions:
  contents: read
  actions: read
```

The assertion is now `"permissions:\n  contents: read\n  actions: read"` in **Python source**, so its runtime string contains actual line breaks. This does not weaken or change any security predicate: `contents: write` and `actions: write` remain excluded; `protected=true` and read-only token scopes are still **not** equivalent to exclusive locked source identity or OS isolation.

In the reduced `FMP_PREINSTALL_SNAPSHOT=1` historical suite, the 12 DEC-1716 installed-source assertions are skipped by the exact existing exemption; normal-checkout focused execution is still required. DEC-1723 guards the skip's scope but cannot prove the installed source was exercised. Adds **zero** test methods; total remains **5,884 proposed**.

No workflow amendment, production/parser/security settings, protected historical reads, annual run385 dispatch, retry, tag/main mutation, broker/demo/live or trading. Historical/general and Phase 3 exact-head checks plus independent review required; #779 and DEC-650/#820 and DEC-651/#821 stay **BLOCKED**.
