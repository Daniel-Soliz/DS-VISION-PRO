from __future__ import annotations

import time


def seconds_until_next_minute(now: float | None = None) -> float:
    value = time.time() if now is None else float(now)
    remainder = value % 60.0
    remaining = 60.0 - remainder
    if remaining <= 0:
        remaining = 60.0
    return remaining


def countdown_text(now: float | None = None) -> str:
    remaining = seconds_until_next_minute(now)
    whole = max(0, int(remaining))
    return f"00:{whole:02d}"
