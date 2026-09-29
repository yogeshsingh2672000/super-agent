import base64
import io

import pyautogui
from langchain_core.tools import tool

from utils.logger import log

pyautogui.FAILSAFE = True  # move mouse to a screen corner to abort
MAX_WIDTH = 1280
_scale = {"value": 1.0}


@tool
def take_screenshot() -> list:
    """Capture the screen. Coordinates in the image are what mouse_click expects."""
    log("📸", "Taking screenshot")
    image = pyautogui.screenshot()
    _scale["value"] = min(1.0, MAX_WIDTH / image.width)
    if _scale["value"] < 1.0:
        image = image.resize((int(image.width * _scale["value"]), int(image.height * _scale["value"])))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    data = base64.b64encode(buffer.getvalue()).decode()
    return [
        {"type": "text", "text": f"Screenshot {image.width}x{image.height}"},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{data}"}},
    ]


@tool
def mouse_click(x: int, y: int, button: str = "left", double: bool = False) -> str:
    """Click at (x, y) from the latest screenshot. button: left or right."""
    real_x, real_y = int(x / _scale["value"]), int(y / _scale["value"])
    log("🖱 ", f"{'Double-clicking' if double else 'Clicking'} at ({x}, {y})")
    pyautogui.click(real_x, real_y, clicks=2 if double else 1, button=button)
    return f"Clicked at ({x}, {y})"


@tool
def type_text(text: str) -> str:
    """Type text at the current keyboard focus."""
    log("⌨️ ", f"Typing {len(text)} chars")
    pyautogui.write(text, interval=0.02)
    return "Typed text"


@tool
def press_keys(keys: str) -> str:
    """Press a key or combo, e.g. 'enter', 'ctrl+s', 'alt+tab'."""
    log("⌨️ ", f"Pressing {keys}")
    pyautogui.hotkey(*keys.lower().split("+"))
    return f"Pressed {keys}"


@tool
def scroll(amount: int) -> str:
    """Scroll the mouse wheel. Positive = up, negative = down."""
    log("🖱 ", f"Scrolling {amount}")
    pyautogui.scroll(amount)
    return f"Scrolled {amount}"


TOOLS = [take_screenshot, mouse_click, type_text, press_keys, scroll]
