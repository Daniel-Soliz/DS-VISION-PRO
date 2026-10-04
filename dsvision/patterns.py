from __future__ import annotations

import numpy as np

from .models import Candle, PatternSignal


def _sma(values: list[float], period: int) -> float | None:
    if period <= 0 or len(values) < period:
        return None
    return float(np.mean(values[-period:]))


def detect_patterns(
    candles: list[Candle],
    idx: int,
    trend_period: int = 10,
    doji_percent: float = 12,
) -> list[PatternSignal]:
    if idx < 2:
        return []

    c1 = candles[idx]
    c2 = candles[idx - 1]
    c3 = candles[idx - 2]

    closes = [c.close for c in candles[: idx + 1]]
    period_now = min(trend_period, len(closes))
    period_prev = min(trend_period, max(1, len(closes) - 1))

    trend_now = _sma(closes, period_now)
    trend_prev = _sma(closes[:-1], period_prev)

    uptrend = bool(
        trend_now is not None
        and trend_prev is not None
        and c1.close > trend_now
        and trend_now > trend_prev
    )
    downtrend = bool(
        trend_now is not None
        and trend_prev is not None
        and c1.close < trend_now
        and trend_now < trend_prev
    )

    out: list[PatternSignal] = []

    is_doji = c1.body * 100 <= c1.range * doji_percent
    dragonfly = is_doji and c1.lower_wick >= c1.range * 0.60 and c1.upper_wick <= c1.range * 0.15
    gravestone = is_doji and c1.upper_wick >= c1.range * 0.60 and c1.lower_wick <= c1.range * 0.15
    spinning = (
        c1.body > c1.range * 0.10
        and c1.body <= c1.range * 0.35
        and c1.upper_wick >= c1.body * 0.70
        and c1.lower_wick >= c1.body * 0.70
    )

    if dragonfly:
        out.append(PatternSignal("DRAGONFLY DOJI", "ALTA", 2, "rejeição inferior"))
    elif gravestone:
        out.append(PatternSignal("GRAVESTONE DOJI", "BAIXA", 2, "rejeição superior"))
    elif is_doji:
        out.append(PatternSignal("DOJI", "NEUTRO", 0, "indecisão"))
    elif spinning:
        out.append(PatternSignal("SPINNING TOP", "NEUTRO", 0, "indecisão"))

    if downtrend and c1.body > 0 and c1.lower_wick >= c1.body * 2 and c1.upper_wick <= c1.body * 0.60:
        out.append(PatternSignal("MARTELO", "ALTA", 3, "reversão após queda"))

    if downtrend and c1.body > 0 and c1.upper_wick >= c1.body * 2 and c1.lower_wick <= c1.body * 0.60:
        out.append(PatternSignal("MARTELO INVERTIDO", "ALTA", 2, "possível reversão"))

    if uptrend and c1.body > 0 and c1.lower_wick >= c1.body * 2 and c1.upper_wick <= c1.body * 0.60:
        out.append(PatternSignal("HOMEM ENFORCADO", "BAIXA", 2, "alerta após alta"))

    if uptrend and c1.body > 0 and c1.upper_wick >= c1.body * 2 and c1.lower_wick <= c1.body * 0.60:
        out.append(PatternSignal("ESTRELA CADENTE", "BAIXA", 3, "rejeição superior"))

    bullish_engulfing = (
        c2.bear and c1.bull
        and c1.open <= c2.close
        and c1.close >= c2.open
        and c1.body > c2.body
    )
    bearish_engulfing = (
        c2.bull and c1.bear
        and c1.open >= c2.close
        and c1.close <= c2.open
        and c1.body > c2.body
    )

    if bullish_engulfing:
        out.append(PatternSignal("ENGOLFO DE ALTA", "ALTA", 4, "controle comprador"))
    if bearish_engulfing:
        out.append(PatternSignal("ENGOLFO DE BAIXA", "BAIXA", 4, "controle vendedor"))

    midpoint = (c2.open + c2.close) / 2
    if downtrend and c2.bear and c1.bull and c1.close > midpoint and c1.close < c2.open:
        out.append(PatternSignal("PIERCING LINE", "ALTA", 3))
    if uptrend and c2.bull and c1.bear and c1.close < midpoint and c1.close > c2.open:
        out.append(PatternSignal("DARK CLOUD COVER", "BAIXA", 3))

    bullish_harami = (
        c2.bear and c1.bull
        and c1.open > c2.close
        and c1.close < c2.open
        and c1.body < c2.body
    )
    bearish_harami = (
        c2.bull and c1.bear
        and c1.open < c2.close
        and c1.close > c2.open
        and c1.body < c2.body
    )
    if bullish_harami:
        out.append(PatternSignal("HARAMI DE ALTA", "ALTA", 2))
    if bearish_harami:
        out.append(PatternSignal("HARAMI DE BAIXA", "BAIXA", 2))

    middle_small = c2.body <= c2.range * 0.40
    morning = (
        c3.bear and middle_small and c1.bull
        and c3.body >= c3.range * 0.50
        and c1.close > (c3.open + c3.close) / 2
    )
    evening = (
        c3.bull and middle_small and c1.bear
        and c3.body >= c3.range * 0.50
        and c1.close < (c3.open + c3.close) / 2
    )
    if morning:
        out.append(PatternSignal("MORNING STAR", "ALTA", 4))
    if evening:
        out.append(PatternSignal("EVENING STAR", "BAIXA", 4))

    three_white = (
        c3.bull and c2.bull and c1.bull
        and c2.close > c3.close and c1.close > c2.close
        and c3.body >= c3.range * 0.45
        and c2.body >= c2.range * 0.45
        and c1.body >= c1.range * 0.45
    )
    three_black = (
        c3.bear and c2.bear and c1.bear
        and c2.close < c3.close and c1.close < c2.close
        and c3.body >= c3.range * 0.45
        and c2.body >= c2.range * 0.45
        and c1.body >= c1.range * 0.45
    )
    if three_white:
        out.append(PatternSignal("3 SOLDADOS BRANCOS", "ALTA", 4, "continuação forte"))
    if three_black:
        out.append(PatternSignal("3 CORVOS NEGROS", "BAIXA", 4, "continuação forte"))

    if c1.bull and c1.body >= c1.range * 0.85:
        out.append(PatternSignal("MARUBOZU DE ALTA", "ALTA", 2, "pressão compradora"))
    if c1.bear and c1.body >= c1.range * 0.85:
        out.append(PatternSignal("MARUBOZU DE BAIXA", "BAIXA", 2, "pressão vendedora"))

    return out
