from __future__ import annotations

import math

import cv2
import mss
import numpy as np

from .models import Candle


def capture_region(region: dict) -> np.ndarray:
    with mss.mss() as sct:
        shot = sct.grab({
            "left": int(region["left"]),
            "top": int(region["top"]),
            "width": int(region["width"]),
            "height": int(region["height"]),
        })
        arr = np.asarray(shot)
    return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)


def _color_masks(bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    green = cv2.inRange(
        hsv,
        np.array([35, 65, 45]),
        np.array([100, 255, 255]),
    )

    red_a = cv2.inRange(
        hsv,
        np.array([0, 75, 45]),
        np.array([18, 255, 255]),
    )
    red_b = cv2.inRange(
        hsv,
        np.array([160, 75, 45]),
        np.array([180, 255, 255]),
    )
    red = cv2.bitwise_or(red_a, red_b)

    kernel = np.ones((2, 2), np.uint8)
    green = cv2.morphologyEx(green, cv2.MORPH_OPEN, kernel)
    red = cv2.morphologyEx(red, cv2.MORPH_OPEN, kernel)
    return green, red


def _runs(xs: np.ndarray, gap: int = 2) -> list[tuple[int, int]]:
    if len(xs) == 0:
        return []
    result = []
    start = prev = int(xs[0])
    for raw in xs[1:]:
        value = int(raw)
        if value - prev > gap:
            result.append((start, prev))
            start = value
        prev = value
    result.append((start, prev))
    return result


def _candles_from_mask(mask: np.ndarray, color: str) -> list[Candle]:
    column_counts = (mask > 0).sum(axis=0)
    columns = np.where(column_counts >= 3)[0]
    groups = _runs(columns, gap=2)
    candles: list[Candle] = []

    for x0, x1 in groups:
        width = x1 - x0 + 1
        if width < 2 or width > 24:
            continue

        roi = mask[:, x0:x1 + 1]
        ys, _ = np.where(roi > 0)
        if len(ys) < 8:
            continue

        y_top = int(ys.min())
        y_bottom = int(ys.max())
        if y_bottom - y_top + 1 < 6:
            continue

        row_counts = (roi > 0).sum(axis=1)
        max_fill = int(row_counts.max())
        body_threshold = max(2, int(math.ceil(max_fill * 0.45)))
        body_rows = np.where(row_counts >= body_threshold)[0]
        if len(body_rows) == 0:
            continue

        body_top = int(body_rows.min())
        body_bottom = int(body_rows.max())
        if body_bottom - body_top + 1 < 2:
            continue

        high = -float(y_top)
        low = -float(y_bottom)

        if color == "green":
            open_ = -float(body_bottom)
            close = -float(body_top)
        else:
            open_ = -float(body_top)
            close = -float(body_bottom)

        candle = Candle(
            x=(x0 + x1) / 2.0,
            open=open_,
            high=max(high, open_, close),
            low=min(low, open_, close),
            close=close,
            color=color,
        )

        if candle.range <= 0 or candle.body / candle.range > 1.05:
            continue
        candles.append(candle)

    return candles


def detect_candles(bgr: np.ndarray) -> list[Candle]:
    green, red = _color_masks(bgr)
    candidates = _candles_from_mask(green, "green") + _candles_from_mask(red, "red")
    candidates.sort(key=lambda candle: candle.x)

    merged: list[Candle] = []
    for candle in candidates:
        if not merged or abs(candle.x - merged[-1].x) > 4:
            merged.append(candle)
            continue

        previous = merged[-1]
        prev_quality = previous.range + (2 * previous.body)
        curr_quality = candle.range + (2 * candle.body)
        if curr_quality > prev_quality:
            merged[-1] = candle

    return merged
