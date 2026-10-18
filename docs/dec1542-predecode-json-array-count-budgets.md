# DEC-1542 — Pre-decode lexical JSON array-count budgets

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict exact-parent tests/docs child of #1788 at `7a7ff2e971babb24e3a311538f5ee8d226e8467f`. Ten synthetic methods; **2,644 proposed source-defined methods**.

DEC-1541 checks decoded JSON array lengths before nested source evidence review. Its post-decoder check necessarily allows JSON to allocate the temporary list first. Add an iterative **lexical scanner before `json.loads`** that tracks comma-separated members only inside array frames, skips characters inside strings and escaped quotes, refuses mismatched brackets, and enforces the same 16,384 items per array and 65,536 array elements in aggregate. Retain post-decoder verification as an independent backstop; the scanner is a conservative resource preflight, not a general JSON parser or proof of allocation-free processing.

Ten synthetic tests check exact/over per-array and aggregate limits, arrays of empty arrays, commas/brackets in ordinary or escaped strings, malformed container closings, predecode refusal without invoking `json.loads`, and a clean consistency-only fixture with all annual authorization flags false.

Own exact-head Phase 3 and historical/general CI and independent qualified review required. DEC-650/#820 witnessed protected-original OS no-write and DEC-651/#821/#779 immutable exclusive protected annual 2023 run385/attempt1 GitHub admission remain **BLOCKED**. No protected annual dispatch/retry, originals/artifacts, installed workflow/security controls changes, merges, deployment or trading.
