from __future__ import annotations

import json
import os
from pathlib import Path


DEFAULT_CONFIG = {
    "scan_ms": 1000,
    "expiry_seconds": 60,
    "min_candles": 14,
    "ignore_rightmost": 1,
    "trend_period": 10,
    "sr_period": 30,
    "lt_period": 20,
    "doji_percent": 12,
    "touch_tolerance_percent": 30,
    "signal_threshold": 4,
    "strong_threshold": 8,
    "voice_alerts": True,
    "regions": {
        "M5": None,
        "M15": None,
        "M1": None,
    },
}


def app_data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if base:
        path = Path(base) / "DS VISION PRO"
    else:
        path = Path.home() / ".ds_vision_pro"
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_path() -> Path:
    return app_data_dir() / "config.json"


def journal_path() -> Path:
    return app_data_dir() / "signals.csv"


def load_config() -> dict:
    path = config_path()
    config = json.loads(json.dumps(DEFAULT_CONFIG))

    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            config.update({k: v for k, v in loaded.items() if k != "regions"})
            if isinstance(loaded.get("regions"), dict):
                config["regions"].update(loaded["regions"])
        except Exception:
            pass

    return config


def save_config(config: dict) -> None:
    config_path().write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
