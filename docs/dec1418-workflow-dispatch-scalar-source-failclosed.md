# DEC-1418 — Fail-closed scalar value on existing workflow_dispatch event

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit test/docs child #1641 DEC-1417 at 67404c708763f4ac321ecf057fa867628dee849b. +4 methods; **1,438 proposed source-defined methods**.

DEC-1417 expanded the source trigger inventory to detect inline unexpected event mappings. Its scanner still compared only event *key names*, ignoring an inline scalar attached to the existing workflow_dispatch key. One negative fixture added in that prior draft consequently reveals a false-safe source result. This forward-only repair captures both event key and exact scalar suffix, allowing only one workflow_dispatch event with empty suffix. Source changes to an inline dictionary/list/false value now trigger explicit review rather than being silently treated as the canonical manual event.

This is a deliberately narrow YAML source-regression diagnostic, not a parser, control-plane admission authority or installed workflow change. No protected original, annual artifact, actual run385/attempt1 or trading is touched. Own exact-head Phase3 and historical CI plus qualified review required. DEC-650/#820 OS protected original no-write and DEC-651/#821/#779 exclusive immutable server-side admission remain BLOCKED. No annual dispatch/retry, branch/ruleset/permission mutation, merge or promotion.
