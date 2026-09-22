from __future__ import annotations

# Source-level execution lock. No setter, environment override, config hook,
# artifact hook, or CLI mutation exists under DEC-061.
DEMO_EXECUTION_SOURCE_ARMED = False

__all__ = ["DEMO_EXECUTION_SOURCE_ARMED"]
