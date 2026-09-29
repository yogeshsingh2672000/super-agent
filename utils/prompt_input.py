"""'You:' prompt with hotkeys (F2 = expand/collapse sources)."""
from prompt_toolkit import PromptSession
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings

from utils import source_view
from utils.logger import console

_bindings = KeyBindings()
_state = {"session": None, "fallback": False}


@_bindings.add("f2")
def _toggle_sources(event) -> None:
    run_in_terminal(source_view.toggle)


def _session():
    """Create the hotkey prompt once; None if this terminal can't run it."""
    if _state["session"] is None and not _state["fallback"]:
        try:
            _state["session"] = PromptSession(key_bindings=_bindings)
        except Exception:
            _state["fallback"] = True
            console.print("[dim]F2 hotkey not supported in this terminal. Use /sources instead.[/]")
    return _state["session"]


def ask() -> str:
    session = _session()
    if session is None:
        return console.input("[bold green]You:[/] ")
    return session.prompt(HTML("<ansigreen><b>You:</b></ansigreen> "))
