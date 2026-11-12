"""Desktop actions via pyautogui, behind a small typed interface.

Every action is a plain dict: {"type": "click|type|scroll|key|wait|done",
"x": int, "y": int, "text": str, "amount": int, "key": str, "reason": str}
Coordinates are absolute screen pixels from the planner.
"""
from __future__ import annotations

import time

ACTION_DELAY_SECONDS = 0.6


def _pyautogui():
    import pyautogui

    pyautogui.FAILSAFE = True  # mouse to top-left corner = emergency stop
    pyautogui.PAUSE = 0.1
    return pyautogui


def screenshot(path: str = "screen.png") -> str:
    """Capture the current screen to a PNG and return its path."""
    gui = _pyautogui()
    image = gui.screenshot()
    image.save(path)
    return path


def screen_size() -> tuple[int, int]:
    gui = _pyautogui()
    size = gui.size()
    return int(size.width), int(size.height)


def execute(action: dict) -> None:
    """Perform one action dict on the desktop."""
    gui = _pyautogui()
    kind = action.get("type")
    if kind == "click":
        gui.click(int(action["x"]), int(action["y"]))
    elif kind == "double_click":
        gui.doubleClick(int(action["x"]), int(action["y"]))
    elif kind == "type":
        gui.write(str(action.get("text", "")), interval=0.02)
    elif kind == "key":
        gui.press(str(action.get("key", "enter")))
    elif kind == "scroll":
        gui.scroll(int(action.get("amount", -5)), x=int(action.get("x", 500)), y=int(action.get("y", 400)))
    elif kind == "wait":
        time.sleep(float(action.get("seconds", 1)))
    elif kind == "done":
        pass
    else:
        raise ValueError(f"Unknown action type: {kind}")
    time.sleep(ACTION_DELAY_SECONDS)
