# DEC-1493 — Canonical source path labels in offline CI evidence envelopes

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1738 at `d340e9de9da8bcba64e6991cbc5a02e64807dcf4`. Adds 12 synthetic regression methods, **2,176 proposed source-defined methods**.

DEC-1478 source-byte maps previously required non-empty string paths but did not directly reject ambiguous labels such as absolute paths, `../` traversal, `./` or `//` segments, Windows backslashes/drive roots, embedded control characters or unpaired surrogates. These strings are not suitable for stable, platform-independent, repository-relative comparison even though the reviewer does no file I/O. Validate each label before Base64 decode and delegate regular paths—including dotfiles and `.github/workflows`—to the existing full tree/source comparator.

Twelve synthetic tests cover absolute, dot and parent traversal, duplicate or trailing separator, backslash, drive path, NUL/newline, positive dotfile paths, stdin output non-disclosure and clean source-consistency-only regression. Failed review codes never contain untrusted path content, and success still sets all protected annual authorization flags false.

Own exact-head PR-associated Phase 3 and full historical/general CI plus independent qualified review required. DEC-650/#820 independently witnessed original-file OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected annual run/dispatch/retry, originals/archives/artifacts, installed workflow or security setting changes, merges, deployments or trading.
