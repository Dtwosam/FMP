# DEC-1554 — UTF-8 JSON transport representation budget parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1800 at `35aa0653ac49986ca52ce69f6fca1bb12e22a590`. Nine new synthetic methods (**2,749 proposed source-defined tests**).

The 2,000,000-character and 2,000,000-UTF-8-byte JSON input budgets apply to **submitted JSON text**, not to an equivalent decoded Python value. Literal Unicode scalar strings may be under the byte ceiling while their ASCII-escaped equivalents cross the character/byte ceilings. Tests cover accented scalars and four-byte emoji, the exact 2,000,000-byte literal-unicode boundary and one scalar beyond it, escaped control-character expansion, escaped and actual lone surrogate distinction, and stdout no-echo on a too-long escaped input.

Both exact-head CI suites and independent qualified review required. No changes to parser, ceilings, production code, workflows/security controls or admission. DEC-650/#820 independent protected-original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 admission remain BLOCKED. No protected annual dispatch/retry, original/archive/artifact access, merging, deployment or trading.
