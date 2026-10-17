# DEC-1526 — Bound normalized source path identities and separators

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1771 at `b08258deeb8543f160e2e306adea15e82a0df91b`. Eleven new synthetic tests; **2,500 proposed source-defined methods**.

DEC-1524 compares source map labels by a non-mutating Unicode NFKC compatibility identity, and DEC-1525 uses NFKC only for reserved Windows device checks. Compatibility normalization may expand a source component/path beyond the original UTF-8 byte caps or turn a visually unusual code point into a backslash, colon or trailing full stop. Validate **both** the supplied original spelling and the NFKC comparison spelling against the existing **255 bytes per component / 4096 bytes per path** limits and reject any newly introduced separator/colon, empty/dot segment or trailing space/dot. Do not rewrite Git source names or touch the filesystem. The normal NFC and supplied-source review rules remain authoritative.

Eleven tests cover exact/over normalized UTF-8 segment and total bounds, trailing fullwidth period, introduced reverse solidus/colon, source/workflow map refusals, safe stdin non-disclosure and a clean nonauthorizing source-only positive fixture. Passing this check cannot authorize protected annual execution.

Own exact-head Phase 3/full historical-general CI and independent qualified review required. DEC-650/#820 witnessed protected original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected dispatch/retry, original/archive/artifacts, installed workflow/security changes, merge, deployment or trading.
