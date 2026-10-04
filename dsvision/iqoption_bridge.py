from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import mss
import numpy as np
import psutil
import win32con
import win32gui
import win32process
import win32ui
from ctypes import windll


IQ_PROCESS_NAME = "iq option.exe"


@dataclass(slots=True)
class IQWindow:
    hwnd: int
    pid: int
    title: str
    rect: tuple[int, int, int, int]

    @property
    def left(self) -> int:
        return self.rect[0]

    @property
    def top(self) -> int:
        return self.rect[1]

    @property
    def right(self) -> int:
        return self.rect[2]

    @property
    def bottom(self) -> int:
        return self.rect[3]

    @property
    def width(self) -> int:
        return max(1, self.right - self.left)

    @property
    def height(self) -> int:
        return max(1, self.bottom - self.top)


def find_iqoption_window() -> IQWindow | None:
    pids = {
        proc.pid
        for proc in psutil.process_iter(["name"])
        if proc.info.get("name")
        and proc.info["name"].lower() == IQ_PROCESS_NAME
    }
    if not pids:
        return None

    matches: list[IQWindow] = []

    def callback(hwnd: int, _extra) -> bool:
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd).strip()
        if not title:
            return True
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
        except Exception:
            return True
        if pid not in pids:
            return True

        rect = win32gui.GetWindowRect(hwnd)
        width = max(0, rect[2] - rect[0])
        height = max(0, rect[3] - rect[1])
        if width >= 400 and height >= 300:
            matches.append(IQWindow(hwnd, pid, title, rect))
        return True

    win32gui.EnumWindows(callback, None)
    if not matches:
        return None

    return max(matches, key=lambda item: item.width * item.height)


def known_iqoption_paths() -> list[Path]:
    candidates = [
        Path(r"C:\Program Files\IQ Option\IQ Option.exe"),
        Path(r"C:\Program Files (x86)\IQ Option\IQ Option.exe"),
    ]

    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidates.extend(
            [
                Path(local) / "Programs" / "IQ Option" / "IQ Option.exe",
                Path(local) / "IQ Option" / "IQ Option.exe",
            ]
        )
    return candidates


def launch_iqoption() -> bool:
    if find_iqoption_window() is not None:
        return True

    for path in known_iqoption_paths():
        if path.exists():
            try:
                subprocess.Popen([str(path)], cwd=str(path.parent))
                return True
            except Exception:
                continue
    return False


def activate_iqoption(window: IQWindow) -> bool:
    try:
        win32gui.ShowWindow(window.hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(window.hwnd)
        return True
    except Exception:
        return False


def relative_region(
    absolute: dict,
    window_rect: tuple[int, int, int, int],
) -> dict:
    left, top, right, bottom = window_rect
    width = max(1, right - left)
    height = max(1, bottom - top)

    return {
        "x": (float(absolute["left"]) - left) / width,
        "y": (float(absolute["top"]) - top) / height,
        "width": float(absolute["width"]) / width,
        "height": float(absolute["height"]) / height,
    }


def absolute_region(
    relative: dict,
    window_rect: tuple[int, int, int, int],
) -> dict:
    left, top, right, bottom = window_rect
    width = max(1, right - left)
    height = max(1, bottom - top)

    x = max(0.0, min(1.0, float(relative["x"])))
    y = max(0.0, min(1.0, float(relative["y"])))
    w = max(0.001, min(1.0 - x, float(relative["width"])))
    h = max(0.001, min(1.0 - y, float(relative["height"])))

    return {
        "left": int(round(left + x * width)),
        "top": int(round(top + y * height)),
        "width": max(1, int(round(w * width))),
        "height": max(1, int(round(h * height))),
    }


def _print_window(hwnd: int) -> np.ndarray | None:
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = max(1, right - left)
    height = max(1, bottom - top)

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    if not hwnd_dc:
        return None

    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)

    try:
        result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)
        if result != 1:
            return None
        raw = bitmap.GetBitmapBits(True)
        image = np.frombuffer(raw, dtype=np.uint8).reshape((height, width, 4))
        bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        if float(bgr.mean()) < 2.0:
            return None
        return bgr
    finally:
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)


def _screen_capture(window: IQWindow) -> np.ndarray:
    activate_iqoption(window)
    time.sleep(0.12)
    with mss.mss() as sct:
        shot = sct.grab(
            {
                "left": window.left,
                "top": window.top,
                "width": window.width,
                "height": window.height,
            }
        )
        array = np.asarray(shot)
    return cv2.cvtColor(array, cv2.COLOR_BGRA2BGR)


def capture_iqoption_window(window: IQWindow) -> np.ndarray:
    image = _print_window(window.hwnd)
    if image is not None:
        return image
    return _screen_capture(window)


def crop_relative(image: np.ndarray, region: dict) -> np.ndarray:
    height, width = image.shape[:2]
    x1 = int(max(0, min(width - 1, round(float(region["x"]) * width))))
    y1 = int(max(0, min(height - 1, round(float(region["y"]) * height))))
    x2 = int(max(x1 + 1, min(width, round((float(region["x"]) + float(region["width"])) * width))))
    y2 = int(max(y1 + 1, min(height, round((float(region["y"]) + float(region["height"])) * height))))
    return image[y1:y2, x1:x2].copy()
