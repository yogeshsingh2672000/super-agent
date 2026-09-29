from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright

import config
from utils import safety, sources
from utils.logger import log
from utils.text import truncate

# Playwright sync API must stay on one thread
_executor = ThreadPoolExecutor(max_workers=1)
_state = {"playwright": None, "browser": None, "page": None}

ELEMENTS_JS = """els => els.slice(0, 60).map(e => {
  const label = (e.innerText || e.value || e.placeholder || e.getAttribute('aria-label') || e.name || '').trim().slice(0, 60);
  return `${e.tagName.toLowerCase()}${e.type ? '[' + e.type + ']' : ''}: ${label}`;
}).filter(s => !s.endsWith(': '))"""


def _run(fn, *args):
    return _executor.submit(fn, *args).result()


def _page():
    if _state["page"] is None or _state["page"].is_closed():
        if _state["playwright"] is None:
            _state["playwright"] = sync_playwright().start()
        if _state["browser"] is None or not _state["browser"].is_connected():
            _state["browser"] = _state["playwright"].chromium.launch(headless=config.BROWSER_HEADLESS)
        _state["page"] = _state["browser"].new_page()
    return _state["page"]


def _find(page, target: str):
    """Find an element by placeholder, label, visible text or CSS selector."""
    finders = [
        lambda: page.get_by_placeholder(target),
        lambda: page.get_by_label(target),
        lambda: page.get_by_role("button", name=target),
        lambda: page.get_by_role("link", name=target),
        lambda: page.get_by_text(target),
        lambda: page.locator(target),
    ]
    for finder in finders:
        try:
            locator = finder()
            if locator.count() > 0:
                return locator.first
        except Exception:
            continue
    return None


def _open(url):
    page = _page()
    page.goto(url, timeout=30000)
    return f"Opened {page.url} | title: {page.title()}"


def _read():
    page = _page()
    text = page.inner_text("body")
    elements = page.eval_on_selector_all("a, button, input, textarea, select", ELEMENTS_JS)
    date = sources.find_page_date(BeautifulSoup(page.content(), "html.parser"))
    n = sources.add(page.url, page.title(), date, opened=True)
    return truncate(
        f"Source [{n}] | URL: {page.url}\nTitle: {page.title()} | page date: {date or 'unknown'}\n\n"
        f"Text:\n{text}\n\nElements:\n" + "\n".join(elements)
    )


def _click(target):
    page = _page()
    element = _find(page, target)
    if element is None:
        return f"Element not found: {target}. Call browser_read to see options."
    element.click(timeout=10000)
    page.wait_for_load_state("domcontentloaded")
    return f"Clicked '{target}'. Now on {page.url}"


def _type(target, text, press_enter):
    page = _page()
    element = _find(page, target)
    if element is None:
        return f"Input not found: {target}. Call browser_read to see options."
    element.fill(text, timeout=10000)
    if press_enter:
        element.press("Enter")
        page.wait_for_load_state("domcontentloaded")
    return f"Typed into '{target}'"


def _press(key):
    _page().keyboard.press(key)
    return f"Pressed {key}"


@tool
def browser_open(url: str) -> str:
    """Open a URL in the browser."""
    log("🌐", f"Opening browser at {url}")
    try:
        return _run(_open, url)
    except Exception as e:
        return f"Open failed: {e}"


@tool
def browser_read() -> str:
    """Read the current page: URL, title, text and clickable elements."""
    log("📖", "Reading browser page")
    try:
        return _run(_read)
    except Exception as e:
        return f"Read failed: {e}"


@tool
def browser_click(target: str) -> str:
    """Click an element by visible text, label or CSS selector."""
    denied = safety.guard(f"click {target}")
    if denied:
        return denied
    log("🖱 ", f'Clicking "{target}"')
    try:
        return _run(_click, target)
    except Exception as e:
        return f"Click failed: {e}"


@tool
def browser_type(target: str, text: str, press_enter: bool = False) -> str:
    """Type text into an input found by placeholder, label or CSS selector."""
    log("⌨️ ", f'Typing into "{target}"')
    try:
        return _run(_type, target, text, press_enter)
    except Exception as e:
        return f"Type failed: {e}"


@tool
def browser_press_key(key: str) -> str:
    """Press a key in the browser, e.g. Enter, Escape, PageDown."""
    log("⌨️ ", f"Pressing {key} in browser")
    try:
        return _run(_press, key)
    except Exception as e:
        return f"Key press failed: {e}"


def close_browser() -> None:
    def _close():
        if _state["browser"]:
            _state["browser"].close()
        if _state["playwright"]:
            _state["playwright"].stop()

    try:
        _run(_close)
    except Exception:
        pass


TOOLS = [browser_open, browser_read, browser_click, browser_type, browser_press_key]
