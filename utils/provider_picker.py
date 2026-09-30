"""Startup menu to choose the provider. The model comes from that provider's .env section."""
from html import escape as html_escape

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import choice
from rich.markup import escape
from rich.table import Table

import config
from providers import PROVIDERS, is_local, model_name, supports_vision
from utils.logger import console

KEYS = list(PROVIDERS)
_state = {"arrows": True}  # False once the terminal can't show the arrow menu


def _price(key: str) -> str:
    settings = PROVIDERS[key].SETTINGS
    if is_local(key):
        return "free"
    if not settings["input_price"] and not settings["output_price"]:
        return "price not set"
    return f"${settings['input_price']:g} / ${settings['output_price']:g} per 1M"


def _label(key: str, status: tuple[bool, str]) -> HTML:
    ok, detail = status
    name = html_escape(PROVIDERS[key].NAME.ljust(18))
    model = html_escape(model_name(key) or "no model set")
    mark = "<ansigreen>✅ ready</ansigreen>" if ok else f"<ansired>❌ {html_escape(detail)}</ansired>"
    return HTML(f"<b>{name}</b> {model}  <ansigray>({_price(key)})</ansigray>  {mark}")


def _arrow_select(statuses: dict, default: str) -> str | None:
    """↑/↓ + Enter menu. None if this terminal can't show it."""
    try:
        return choice(
            message=HTML("<b>Choose a provider</b> <ansigray>(↑/↓ to move, Enter to select)</ansigray>"),
            options=[(key, _label(key, statuses[key])) for key in KEYS],
            default=default,
        )
    except Exception:
        _state["arrows"] = False
        return None


def _show_table(statuses: dict) -> None:
    table = Table(title="Choose a provider", title_justify="left")
    for column in ("#", "Provider", "Model (from .env)", "Price", "Status"):
        table.add_column(column, overflow="fold")  # wrap long model ids instead of cutting them
    for i, key in enumerate(KEYS, 1):
        ok, detail = statuses[key]
        table.add_row(
            str(i), PROVIDERS[key].NAME, escape(model_name(key) or "-"), _price(key),
            f"[green]✅ {escape(detail)}[/]" if ok else f"[red]❌ {escape(detail)}[/]",
        )
    console.print(table)


def _number_select(statuses: dict, default: str) -> str | None:
    """Fallback: numbered table + typed choice."""
    _show_table(statuses)
    number = KEYS.index(default) + 1
    answer = console.input(f"Provider [{number}]: ").strip() or str(number)
    return _resolve(answer)


def _resolve(answer: str) -> str | None:
    if answer.isdigit() and 1 <= int(answer) <= len(KEYS):
        return KEYS[int(answer) - 1]
    return answer.lower() if answer.lower() in PROVIDERS else None


def choose(requested: str = "") -> str:
    """Return a ready provider key. Loops until one is ready."""
    default = config.DEFAULT_PROVIDER if config.DEFAULT_PROVIDER in KEYS else KEYS[0]
    while True:
        statuses = {key: PROVIDERS[key].status() for key in KEYS}
        if requested:
            key, requested = _resolve(requested), ""
            if key is None:
                console.print(f"[red]Unknown provider. Choose one of: {', '.join(KEYS)}[/]")
                continue
        else:
            key = _arrow_select(statuses, default) if _state["arrows"] else None
            if key is None:
                key = _number_select(statuses, default)
            if key is None:
                console.print("[red]Type a number from the table.[/]")
                continue
        ok, detail = statuses[key]
        if ok:
            _notes(key)
            return key
        default = key
        console.print(f"[red]{PROVIDERS[key].NAME} is not ready: {escape(detail)}[/]")
        console.input("Fix it in .env (or start the app) and press Enter to check again: ")


def _notes(key: str) -> None:
    console.print(f"[green]Using {PROVIDERS[key].NAME}[/] with model [bold]{escape(model_name(key))}[/]")
    if is_local(key):
        console.print("[dim]Local model: it must support tool calling (e.g. qwen3, llama3.1) or the agent can't use tools.[/]")
    if not supports_vision(key):
        console.print("[dim]Screen control is off for this model (no image input). Set the provider's *_VISION=true in .env if it supports images.[/]")
