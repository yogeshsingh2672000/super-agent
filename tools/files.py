import shutil
from pathlib import Path

from langchain_core.tools import tool

import config
from utils import safety
from utils.logger import log
from utils.text import truncate


def _resolve(path: str) -> Path:
    p = Path(path).expanduser()
    return p if p.is_absolute() else config.ROOT / p


@tool
def list_directory(path: str = ".") -> str:
    """List files and folders in a directory."""
    target = _resolve(path)
    log("📂", f"Listing {target}")
    if not target.is_dir():
        return f"Not a directory: {target}"
    rows = [f"{'[DIR] ' if p.is_dir() else '      '}{p.name}" for p in sorted(target.iterdir())]
    return truncate("\n".join(rows) or "(empty)")


@tool
def read_file(path: str) -> str:
    """Read a text file."""
    target = _resolve(path)
    log("📖", f"Reading {target}")
    if not target.is_file():
        return f"File not found: {target}"
    return truncate(target.read_text(encoding="utf-8", errors="replace"))


@tool
def write_file(path: str, content: str, append: bool = False) -> str:
    """Write text to a file (creates folders). Set append=True to add to the end."""
    target = _resolve(path)
    if safety.is_protected_path(target):
        log("⛔", f"Blocked write to protected path {target}", style="bold red")
        return "BLOCKED: writing to system folders is not allowed."
    log("📝", f"{'Appending to' if append else 'Writing'} {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a" if append else "w", encoding="utf-8") as f:
        f.write(content)
    return f"Saved {len(content)} chars to {target}"


@tool
def delete_path(path: str) -> str:
    """Delete a file or folder. Always asks the user first."""
    target = _resolve(path)
    if safety.is_protected_path(target):
        log("⛔", f"Blocked delete of protected path {target}", style="bold red")
        return "BLOCKED: deleting system folders, drive roots or the home folder is not allowed."
    if not target.exists():
        return f"Not found: {target}"
    if not safety.ask_user(f"delete {target}"):
        return "DENIED: the user did not approve this deletion."
    log("🗑️ ", f"Deleting {target}", style="yellow")
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    return f"Deleted {target}"


TOOLS = [list_directory, read_file, write_file, delete_path]
