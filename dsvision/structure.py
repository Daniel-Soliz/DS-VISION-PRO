from __future__ import annotations

import numpy as np

from .models import Candle, StructureSignal


def _linreg(values: list[float], period: int) -> tuple[float | None, float | None]:
    if len(values) < period or period < 3:
        return None, None
    y = np.asarray(values[-period:], dtype=float)
    x = np.arange(period, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    value = intercept + slope * (period - 1)
    return float(value), float(slope)


def detect_structure(
    candles: list[Candle],
    idx: int,
    sr_period: int = 30,
    lt_period: int = 20,
    touch_tolerance_percent: float = 30,
) -> list[StructureSignal]:
    if idx < 5:
        return []

    current = candles[idx]
    previous = candles[idx - 1]
    prior = candles[:idx]
    out: list[StructureSignal] = []

    sr_n = min(sr_period, len(prior))
    if sr_n >= 5:
        window = prior[-sr_n:]
        support = min(c.low for c in window)
        resistance = max(c.high for c in window)
        avg_range = float(np.mean([c.range for c in window[-min(10, len(window)):]]))
        tolerance = avg_range * (touch_tolerance_percent / 100.0)

        if current.low <= support + tolerance and current.close >= support and current.bull:
            out.append(StructureSignal("REJEIÇÃO NO SUPORTE", "ALTA", 3))

        if current.high >= resistance - tolerance and current.close <= resistance and current.bear:
            out.append(StructureSignal("REJEIÇÃO NA RESISTÊNCIA", "BAIXA", 3))

        if current.close > resistance and previous.close <= resistance and current.bull:
            out.append(StructureSignal("ROMPIMENTO DE RESISTÊNCIA", "ALTA", 4))

        if current.close < support and previous.close >= support and current.bear:
            out.append(StructureSignal("ROMPIMENTO DE SUPORTE", "BAIXA", 4))

        distance_to_res = resistance - current.close
        distance_to_sup = current.close - support
        if current.bull and 0 <= distance_to_res <= tolerance * 0.70:
            out.append(StructureSignal("RESISTÊNCIA MUITO PRÓXIMA", "BAIXA", 1, "freio para alta"))
        if current.bear and 0 <= distance_to_sup <= tolerance * 0.70:
            out.append(StructureSignal("SUPORTE MUITO PRÓXIMO", "ALTA", 1, "freio para baixa"))
    else:
        tolerance = 0.0

    lt_n = min(lt_period, len(prior))
    if lt_n >= 5:
        lows = [c.low for c in prior]
        highs = [c.high for c in prior]
        lta_value, lta_slope = _linreg(lows, lt_n)
        ltb_value, ltb_slope = _linreg(highs, lt_n)

        if lta_value is not None and lta_slope is not None and lta_slope > 0:
            out.append(StructureSignal("LTA ATIVA", "ALTA", 1))
            if current.low <= lta_value + tolerance and current.close >= lta_value and current.bull:
                out.append(StructureSignal("PULLBACK NA LTA", "ALTA", 3))
            if current.close < lta_value and current.bear:
                out.append(StructureSignal("ROMPIMENTO DA LTA", "BAIXA", 2))

        if ltb_value is not None and ltb_slope is not None and ltb_slope < 0:
            out.append(StructureSignal("LTB ATIVA", "BAIXA", 1))
            if current.high >= ltb_value - tolerance and current.close <= ltb_value and current.bear:
                out.append(StructureSignal("PULLBACK NA LTB", "BAIXA", 3))
            if current.close > ltb_value and current.bull:
                out.append(StructureSignal("ROMPIMENTO DA LTB", "ALTA", 2))

    recent = candles[max(0, idx - 3): idx + 1]
    if len(recent) >= 3:
        closes = [c.close for c in recent]
        if all(a < b for a, b in zip(closes, closes[1:])):
            out.append(StructureSignal("MOMENTUM COMPRADOR", "ALTA", 2))
        if all(a > b for a, b in zip(closes, closes[1:])):
            out.append(StructureSignal("MOMENTUM VENDEDOR", "BAIXA", 2))

    body_ratio = current.body / current.range
    if current.bull and body_ratio >= 0.65 and current.upper_wick <= current.body * 0.50:
        out.append(StructureSignal("VELA DE FORÇA COMPRADORA", "ALTA", 2))
    if current.bear and body_ratio >= 0.65 and current.lower_wick <= current.body * 0.50:
        out.append(StructureSignal("VELA DE FORÇA VENDEDORA", "BAIXA", 2))

    return out
