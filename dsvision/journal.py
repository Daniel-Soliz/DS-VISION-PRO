from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .models import CombinedAnalysis

LOG_PATH = Path(__file__).resolve().parent.parent / "signals.csv"


def append_signal(result: CombinedAnalysis) -> None:
    exists = LOG_PATH.exists()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter=";")
        if not exists:
            writer.writerow([
                "timestamp",
                "direction",
                "strength",
                "bull_score",
                "bear_score",
                "reasons",
            ])
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            result.direction,
            result.strength,
            result.bull_score,
            result.bear_score,
            " | ".join(result.reasons),
        ])


def load_recent(limit: int = 100) -> list[dict[str, str]]:
    if not LOG_PATH.exists():
        return []

    with LOG_PATH.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))

    return rows[-max(1, int(limit)):][::-1]
