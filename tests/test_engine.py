from dsvision.models import Candle
from dsvision.patterns import detect_patterns
from dsvision.structure import detect_structure
from dsvision.confluence import analyze_timeframe, combine_timeframes
from dsvision.timing import seconds_until_next_minute, countdown_text


def c(o, h, l, cl, x=0):
    return Candle(x=x, open=o, high=h, low=l, close=cl, color="green" if cl > o else "red")


def test_bullish_engulfing_is_detected():
    candles = [
        c(10, 11, 8, 9, 1),
        c(9.5, 10, 8, 8.5, 2),
        c(8.4, 10.2, 8.2, 10.0, 3),
    ]
    patterns = detect_patterns(candles, 2, trend_period=2)
    names = {p.name for p in patterns}
    assert "ENGOLFO DE ALTA" in names


def test_tweezer_bottom_is_detected():
    candles = [
        c(11, 11.5, 9.5, 10.5, 1),
        c(10.5, 10.8, 8.0, 8.6, 2),
        c(8.5, 10.0, 8.05, 9.7, 3),
    ]
    names = {p.name for p in detect_patterns(candles, 2, trend_period=2)}
    assert "TWEEZER BOTTOM" in names


def test_structure_returns_list():
    candles = [c(10+i*0.1, 11+i*0.1, 9+i*0.1, 10.5+i*0.1, i) for i in range(15)]
    result = detect_structure(candles, 14, sr_period=10, lt_period=8)
    assert isinstance(result, list)


def test_combiner_blocks_m5_m15_conflict():
    cfg = {
        "ignore_rightmost": 1,
        "trend_period": 3,
        "sr_period": 5,
        "lt_period": 5,
        "doji_percent": 12,
        "touch_tolerance_percent": 30,
        "signal_threshold": 1,
        "strong_threshold": 5,
    }

    up = [c(10+i, 11+i, 9+i, 10.8+i, i) for i in range(12)]
    down = [c(30-i, 31-i, 28-i, 29-i, i) for i in range(12)]

    m5 = analyze_timeframe(up, "M5", cfg)
    m15 = analyze_timeframe(down, "M15", cfg)
    combined = combine_timeframes({"M5": m5, "M15": m15})

    if m5.direction != "AGUARDAR" and m15.direction != "AGUARDAR" and m5.direction != m15.direction:
        assert combined.direction == "AGUARDAR"


def test_countdown_helper():
    assert seconds_until_next_minute(120.0) == 60.0
    assert seconds_until_next_minute(125.5) == 54.5
    assert countdown_text(125.5) == "00:54"
\n\ndef test_default_runtime_config_has_all_timeframes():\n    assert DEFAULT_CONFIG["regions"] == {"M5": None, "M15": None, "M1": None}\n    assert DEFAULT_CONFIG["expiry_seconds"] == 60\n