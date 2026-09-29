"""Collapsed / expanded views of the last answer's sources."""
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from utils import sources
from utils.logger import console, write_file_log

_last = {"answer": "", "expanded": False}


def _link(url: str) -> Style:
    return Style(link=url, color="bright_blue", underline=True)


def _used() -> tuple[list, bool]:
    """Cited sources, or all sources if the answer cited none."""
    used = sources.cited(_last["answer"])
    return (used, True) if used else (sources.all_sources(), False)


def _footer(body: Text, missing: dict) -> str:
    if missing.get(0):
        body.append(f"\n❌ Numbers with no citation, found in no source: {', '.join(missing[0])}", style="bold red")
    if any(missing.values()):
        body.append("\n⚠️  Some numbers are not in their cited source. Treat them as unverified.", style="bold red")
        return "red"
    return "blue"


def collapsed() -> Panel | None:
    used, has_citations = _used()
    if not used:
        return None
    missing = sources.check_numbers(_last["answer"])
    body = Text()
    for n, s in used:
        icon = "✅" if s["opened"] else "⚠️ "
        body.append(f"[{n}] {icon} ")
        body.append((s["title"] or s["url"])[:70], style=_link(s["url"]))
        if not s["opened"]:
            body.append(" (snippet)", style="dim")
        if missing.get(n):
            body.append(f"  ❌ {len(missing[n])} issue(s)", style="bold red")
        body.append("\n")
    border = _footer(body, missing)
    body.rstrip()
    label = f"📚 {len(used)} sources" if has_citations else "⚠️  No citations, sources looked at"
    return Panel(body, title=f"{label} · F2 expand", title_align="left", border_style=border)


def expanded() -> Panel | None:
    used, has_citations = _used()
    if not used:
        return None
    missing = sources.check_numbers(_last["answer"])
    body = Text()
    for n, s in used:
        status = "✅ opened" if s["opened"] else "⚠️  snippet only"
        body.append(f"[{n}] {status} · {s['date'] or 'date unknown'}\n", style="bold")
        body.append(f"    {s['title'] or 'untitled'}\n")
        body.append(f"    {s['url']}\n", style=_link(s["url"]))
        snippet = sources.excerpt(n, _last["answer"])
        if snippet:
            body.append(f'    Read more: "{snippet}"\n', style="italic dim")
        if missing.get(n):
            body.append(f"    ❌ not found in this source: {', '.join(missing[n])}\n", style="bold red")
        body.append("\n")
    body.rstrip()
    body.append("\n")
    border = _footer(body, missing)
    body.rstrip()
    return Panel(body, title="📚 Sources (expanded) · F2 collapse · /sources N for more", title_align="left", border_style=border)


def one(n: int) -> Panel | None:
    """Long excerpt of a single source."""
    all_sources = dict(sources.all_sources())
    if n not in all_sources:
        return None
    s = all_sources[n]
    body = Text()
    body.append(f"{s['title'] or 'untitled'}\n", style="bold")
    body.append(f"{s['url']}\n\n", style=_link(s["url"]))
    body.append(sources.excerpt(n, _last["answer"], size=1500) or "(no text saved for this source)", style="italic")
    return Panel(body, title=f"📖 Source [{n}] · read more", title_align="left", border_style="blue")


def show_after_answer(answer: str) -> None:
    """Print the collapsed view and log sources."""
    _last["answer"], _last["expanded"] = answer, False
    panel = collapsed()
    if panel:
        console.print(panel)
    missing = sources.check_numbers(answer)
    for n, s in _used()[0]:
        write_file_log(f"SOURCE [{n}] opened={s['opened']} {s['date']} {s['url']} missing={missing.get(n, [])}")


def toggle() -> None:
    """F2: switch between expanded and collapsed view."""
    _last["expanded"] = not _last["expanded"]
    panel = expanded() if _last["expanded"] else collapsed()
    console.print(panel or "No sources for the last answer.")


def show(arg: str = "") -> None:
    """/sources (expand all) or /sources N (read more on one)."""
    if arg.isdigit():
        console.print(one(int(arg)) or f"No source [{arg}] in the last answer.")
        return
    _last["expanded"] = True
    console.print(expanded() or "No sources for the last answer.")
