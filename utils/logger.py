from datetime import datetime

from rich.console import Console

import config

console = Console()
_log_file = config.LOG_DIR / f"{datetime.now():%Y-%m-%d}.log"


def log(icon: str, message: str, style: str = "cyan") -> None:
    """Print an activity line and save it to today's log file."""
    console.print(f"{icon} {message}", style=style, markup=False, highlight=False)
    write_file_log(f"{icon} {message}")


def write_file_log(line: str) -> None:
    config.LOG_DIR.mkdir(exist_ok=True)
    with open(_log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%H:%M:%S}] {line}\n")
