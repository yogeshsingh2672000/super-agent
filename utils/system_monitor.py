"""Live CPU / RAM status line shown while the agent works."""
import threading
import time
from contextlib import contextmanager

import psutil

from utils.logger import console

_process = psutil.Process()
_state = {"status": None, "running": False}
psutil.cpu_percent(interval=None)  # first call primes the counter


def _agent_memory_mb() -> float:
    """RAM used by the agent plus its child processes (browser, shell)."""
    total = _process.memory_info().rss
    for child in _process.children(recursive=True):
        try:
            total += child.memory_info().rss
        except psutil.Error:
            continue
    return total / 2**20


def stats_text() -> str:
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    return (
        f"CPU {cpu:.0f}% | RAM {ram.used / 2**30:.1f}/{ram.total / 2**30:.1f} GB ({ram.percent:.0f}%)"
        f" | Agent {_agent_memory_mb():.0f} MB"
    )


def _refresh_loop() -> None:
    while _state["running"]:
        status = _state["status"]
        if status:
            status.update(f"[bold cyan]Working…[/] [dim]{stats_text()}[/]")
        time.sleep(1)


def start() -> None:
    _state["status"] = console.status(f"[bold cyan]Working…[/] [dim]{stats_text()}[/]", spinner="dots")
    _state["status"].start()
    _state["running"] = True
    threading.Thread(target=_refresh_loop, daemon=True).start()


def stop() -> None:
    _state["running"] = False
    if _state["status"]:
        _state["status"].stop()
        _state["status"] = None


@contextmanager
def paused():
    """Hide the live line while waiting for user input."""
    status = _state["status"]
    if status:
        status.stop()
    try:
        yield
    finally:
        if status and _state["status"] is status:
            status.start()
