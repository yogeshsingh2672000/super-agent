import subprocess

from langchain_core.tools import tool

import config
from utils import safety
from utils.logger import log
from utils.text import truncate


@tool
def run_command(command: str) -> str:
    """Run a Windows PowerShell command and return its output."""
    denied = safety.guard(command)
    if denied:
        return denied
    log("💻", f"Running: {command}")
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=config.SHELL_TIMEOUT,
            cwd=config.ROOT,
        )
    except subprocess.TimeoutExpired:
        return f"Timed out after {config.SHELL_TIMEOUT}s. Use Start-Process for long-running programs."
    output = f"exit code: {result.returncode}\n{result.stdout}"
    if result.stderr:
        output += f"\nstderr:\n{result.stderr}"
    return truncate(output)


TOOLS = [run_command]
