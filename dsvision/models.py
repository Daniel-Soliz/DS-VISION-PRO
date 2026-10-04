from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Direction = Literal["ALTA", "BAIXA", "NEUTRO"]


@dataclass(slots=True)
class Candle:
    x: float
    open: float
    high: float
    low: float
    close: float
    color: str

    @property
    def body(self) -> float:
        return abs(self.close - self.open)

    @property
    def range(self) -> float:
        return max(1e-9, self.high - self.low)

    @property
    def bull(self) -> bool:
        return self.close > self.open

    @property
    def bear(self) -> bool:
        return self.close < self.open

    @property
    def upper_wick(self) -> float:
        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> float:
        return min(self.open, self.close) - self.low


@dataclass(slots=True)
class PatternSignal:
    name: str
    direction: Direction
    weight: int
    note: str = ""


@dataclass(slots=True)
class StructureSignal:
    name: str
    direction: Direction
    weight: int
    note: str = ""


@dataclass(slots=True)
class TimeframeAnalysis:
    timeframe: str
    direction: str
    strength: int
    bull_score: int
    bear_score: int
    patterns: list[PatternSignal] = field(default_factory=list)
    structures: list[StructureSignal] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    candle_count: int = 0
    fingerprint: str = ""


@dataclass(slots=True)
class CombinedAnalysis:
    direction: str
    strength: int
    bull_score: float
    bear_score: float
    reasons: list[str]
    timeframes: dict[str, TimeframeAnalysis]
