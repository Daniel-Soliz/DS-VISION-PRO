from __future__ import annotations

import numpy as np

from .models import Candle, CombinedAnalysis, TimeframeAnalysis
from .patterns import detect_patterns
from .structure import detect_structure


def _trend_component(candles: list[Candle], idx: int, period: int = 10) -> tuple[int, int, list[str]]:
    if idx < 3:
        return 0, 0, []

    usable = candles[: idx + 1]
    n = min(period, len(usable))
    if n < 3:
        return 0, 0, []

    closes = np.asarray([c.close for c in usable[-n:]], dtype=float)
    x = np.arange(n, dtype=float)
    slope = float(np.polyfit(x, closes, 1)[0])

    if slope > 0:
        return 2, 0, ["Tendência curta inclinada para ALTA (+2)"]
    if slope < 0:
        return 0, 2, ["Tendência curta inclinada para BAIXA (+2)"]
    return 0, 0, []


def analyze_timeframe(candles: list[Candle], timeframe: str, cfg: dict) -> TimeframeAnalysis:
    ignore = max(1, int(cfg.get("ignore_rightmost", 1)))
    idx = len(candles) - 1 - ignore

    if idx < 4:
        return TimeframeAnalysis(
            timeframe=timeframe,
            direction="AGUARDAR",
            strength=0,
            bull_score=0,
            bear_score=0,
            reasons=["Velas insuficientes para análise."],
            candle_count=len(candles),
        )

    patterns = detect_patterns(
        candles,
        idx,
        trend_period=int(cfg.get("trend_period", 10)),
        doji_percent=float(cfg.get("doji_percent", 12)),
    )
    structures = detect_structure(
        candles,
        idx,
        sr_period=int(cfg.get("sr_period", 30)),
        lt_period=int(cfg.get("lt_period", 20)),
        touch_tolerance_percent=float(cfg.get("touch_tolerance_percent", 30)),
    )

    bull = sum(item.weight for item in patterns if item.direction == "ALTA")
    bear = sum(item.weight for item in patterns if item.direction == "BAIXA")
    reasons = []

    for item in patterns:
        if item.direction == "ALTA":
            reasons.append(f"{item.name}: ALTA +{item.weight}")
        elif item.direction == "BAIXA":
            reasons.append(f"{item.name}: BAIXA +{item.weight}")
        else:
            reasons.append(f"{item.name}: NEUTRO")

    for item in structures:
        if item.direction == "ALTA":
            bull += item.weight
            reasons.append(f"{item.name}: ALTA +{item.weight}")
        elif item.direction == "BAIXA":
            bear += item.weight
            reasons.append(f"{item.name}: BAIXA +{item.weight}")

    extra_bull, extra_bear, trend_reasons = _trend_component(
        candles,
        idx,
        int(cfg.get("trend_period", 10)),
    )
    bull += extra_bull
    bear += extra_bear
    reasons.extend(trend_reasons)

    diff = bull - bear
    threshold = int(cfg.get("signal_threshold", 4))
    strong_threshold = int(cfg.get("strong_threshold", 8))

    if diff >= threshold:
        direction = "ALTA"
    elif diff <= -threshold:
        direction = "BAIXA"
    else:
        direction = "AGUARDAR"

    strength = min(100, int(45 + min(55, abs(diff) * 6 + abs(bull + bear) * 1.2)))
    if direction == "AGUARDAR":
        strength = min(54, int(abs(diff) * 8 + (bull + bear) * 1.5))

    if abs(diff) >= strong_threshold and direction != "AGUARDAR":
        reasons.insert(0, "CONFLUÊNCIA FORTE")
    elif direction == "AGUARDAR":
        reasons.insert(0, "SEM VANTAGEM TÉCNICA CLARA")

    c = candles[idx]
    fingerprint = f"{timeframe}:{round(c.x,1)}:{round(c.open,1)}:{round(c.close,1)}"

    return TimeframeAnalysis(
        timeframe=timeframe,
        direction=direction,
        strength=strength,
        bull_score=bull,
        bear_score=bear,
        patterns=patterns,
        structures=structures,
        reasons=reasons,
        candle_count=len(candles),
        fingerprint=fingerprint,
    )


def combine_timeframes(results: dict[str, TimeframeAnalysis]) -> CombinedAnalysis:
    # M5 recebe maior peso porque está mais próximo do horizonte de 60s.
    # M15 funciona como contexto macro; M1, quando presente, melhora o timing.
    weights = {"M5": 0.45, "M15": 0.35, "M1": 0.20}

    available = {tf: result for tf, result in results.items() if result.candle_count >= 5}
    if not available:
        return CombinedAnalysis("AGUARDAR", 0, 0, 0, ["Sem gráficos válidos."], results)

    weight_sum = sum(weights.get(tf, 0.2) for tf in available)
    bull = 0.0
    bear = 0.0
    reasons: list[str] = []

    for tf, result in available.items():
        w = weights.get(tf, 0.2) / max(weight_sum, 1e-9)
        bull += result.bull_score * w
        bear += result.bear_score * w
        reasons.append(
            f"{tf}: {result.direction} | ALTA {result.bull_score} x BAIXA {result.bear_score}"
        )

    # Conflito direto entre M5 e M15 é tratado como zona de cautela.
    m5 = available.get("M5")
    m15 = available.get("M15")
    conflict = (
        m5 is not None
        and m15 is not None
        and m5.direction in ("ALTA", "BAIXA")
        and m15.direction in ("ALTA", "BAIXA")
        and m5.direction != m15.direction
    )

    diff = bull - bear
    if conflict:
        direction = "AGUARDAR"
        reasons.insert(0, "CONFLITO M5 x M15: entrada bloqueada")
    elif diff >= 2.0:
        direction = "ALTA"
    elif diff <= -2.0:
        direction = "BAIXA"
    else:
        direction = "AGUARDAR"

    strength = min(100, int(50 + abs(diff) * 7))
    if direction == "AGUARDAR":
        strength = min(54, int(abs(diff) * 10 + 20))

    # Sem M1 o sistema funciona, mas não exibe força máxima para um horizonte de 60s.
    if "M1" not in available and direction != "AGUARDAR":
        strength = min(strength, 82)
        reasons.append("M1 não selecionado: timing de 60s sem confirmação micro")

    return CombinedAnalysis(
        direction=direction,
        strength=strength,
        bull_score=round(bull, 2),
        bear_score=round(bear, 2),
        reasons=reasons,
        timeframes=results,
    )
