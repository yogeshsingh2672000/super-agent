import os
import re
from pathlib import Path

from utils import system_monitor
from utils.logger import console, log

# Never allowed
BLOCKED_PATTERNS = [
    r"\bformat(-volume)?\s+[a-z]:?",
    r"\bdiskpart\b",
    r"\bbcdedit\b",
    r"\breg\s+delete\b",
    r"remove-item\s+.*hk(lm|cu):",
    r"\bshutdown\b",
    r"\b(stop|restart)-computer\b",
    r"\bclear-disk\b",
    r"\bcipher\s+/w",
    r"(remove-item|\brm\b|\bdel\b|\berase\b|\brd\b|\brmdir\b).*[a-z]:\\(windows|program files|programdata|users\\?\s*$)",
    r"(remove-item|\brm\b|\bdel\b|\berase\b|\brd\b|\brmdir\b)\s+.*['\"]?[a-z]:\\?\*?['\"]?\s*(-|/|$)",
    r"\brm\s+-rf\s+/",
]

# Allowed only after user says yes
RISKY_PATTERNS = [
    r"\b(remove-item|rm|del|erase|rd|rmdir|ri)\b",
    r"\b(pip|npm|winget|choco|scoop)\s+(install|uninstall)",
    r"\b(uninstall|msiexec)\b",
    r"\bsend-mailmessage\b",
    r"\b(set-executionpolicy|new-localuser|net\s+user)\b",
    r"\b(pay|payment|checkout|buy now|place order|purchase|subscribe|transfer|send money)\b",
]


PROTECTED_DIRS = [
    Path(os.environ.get("SystemDrive", "C:") + "\\"),
    Path(os.environ.get("SystemRoot", r"C:\Windows")),
    Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
    Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
    Path(os.environ.get("ProgramData", r"C:\ProgramData")),
    Path.home().parent,
    Path.home(),
]


def is_protected_path(path: Path) -> bool:
    """True for drive roots, system folders and the user home itself."""
    resolved = path.resolve()
    if resolved == Path(resolved.anchor):
        return True
    for protected in PROTECTED_DIRS:
        if resolved == protected.resolve():
            return True
    system_dirs = PROTECTED_DIRS[1:5]
    return any(resolved.is_relative_to(d.resolve()) for d in system_dirs)


def _matches(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def ask_user(action: str) -> bool:
    log("⚠️ ", f"Approval needed: {action}", style="bold yellow")
    with system_monitor.paused():
        answer = console.input("[bold yellow]   Allow? (y/n): [/]").strip().lower()
    return answer in ("y", "yes")


def guard(action: str) -> str | None:
    """Return an error string if the action is not allowed, else None."""
    if _matches(BLOCKED_PATTERNS, action):
        log("⛔", f"Blocked: {action}", style="bold red")
        return "BLOCKED: this action is never allowed. Find a safer way or tell the user."
    if _matches(RISKY_PATTERNS, action) and not ask_user(action):
        log("🚫", "User denied the action", style="red")
        return "DENIED: the user did not approve this action. Do not retry it; find another way or ask."
    return None
