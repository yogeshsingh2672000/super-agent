import sys
import uuid

from langgraph.errors import GraphRecursionError
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

import config
from agent.builder import build_agent
from tools.browser import close_browser
from utils import ledger, memory_store, sources, system_monitor
from utils.logger import console, log, write_file_log
from utils.text import message_text

HELP = "Commands: /budget  /memory  /stats  /new (fresh chat)  /exit"


def show_banner() -> None:
    s = ledger.summary()
    count = len(memory_store.load())
    console.print(Panel.fit(
        f"[bold]Super Agent[/] | model {config.MODEL_ID}\n"
        f"Today: cost ${s['total_cost']:.4f} | income ${s['income']:.2f} | limit ${s['daily_limit']:.2f}\n"
        f"{count} memories loaded | {HELP}",
        border_style="cyan",
    ))


def show_sources(answer: str) -> None:
    """Print cited sources as clickable links; warn if web was used without citations."""
    used = sources.cited(answer)
    title, border = "📚 Sources", "blue"
    if not used:
        used = sources.all_sources()
        if not used:
            return
        title, border = "⚠️  No citations in answer, sources looked at", "yellow"

    missing = sources.check_numbers(answer)
    body = Text()
    for n, s in used:
        status = "✅ opened" if s["opened"] else "⚠️  snippet only"
        body.append(f"[{n}] {status} · {s['date'] or 'date unknown'} · {s['title'] or 'untitled'}\n")
        body.append(f"    {s['url']}\n", style=Style(link=s["url"], color="bright_blue", underline=True))
        if missing.get(n):
            body.append(f"    ❌ not found in this source: {', '.join(missing[n])}\n", style="bold red")
        write_file_log(f"SOURCE [{n}] {status} {s['date']} {s['url']} missing={missing.get(n, [])}")
    if missing.get(0):
        body.append(f"\n❌ Numbers with no citation, found in no source: {', '.join(missing[0])}", style="bold red")
    if any(missing.values()):
        border = "red"
        body.append("\n⚠️  Some numbers are not in their cited source. Treat them as unverified.", style="bold red")
    body.rstrip()
    console.print(Panel(body, title=title, border_style=border))


def run_task(agent, task: str, thread_id: str) -> None:
    run_config = {"configurable": {"thread_id": thread_id}, "recursion_limit": config.MAX_STEPS}
    cost_before = ledger.summary()["total_cost"]
    sources.reset()
    write_file_log(f"TASK: {task}")

    system_monitor.start()
    try:
        for update in agent.stream({"messages": [{"role": "user", "content": task}]}, run_config, stream_mode="updates"):
            for node, data in update.items():
                if node != "model" or not data:
                    continue
                for message in data.get("messages", []):
                    text = message_text(message).strip()
                    if not text:
                        continue
                    if message.tool_calls:
                        log("🧠", text, style="magenta")
                    else:
                        write_file_log(f"ANSWER: {text}")
                        console.print(Panel(text, title="✅ Done", border_style="green"))
                        show_sources(text)
    finally:
        system_monitor.stop()

    task_cost = ledger.summary()["total_cost"] - cost_before
    log("💰", f"Task cost ${task_cost:.4f}", style="bold")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    show_banner()
    agent = build_agent()
    thread_id = str(uuid.uuid4())

    while True:
        try:
            console.print(f"\n🖥️  {system_monitor.stats_text()}", style="dim", highlight=False)
            task = console.input("[bold green]You:[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not task:
            continue
        if task == "/exit":
            break
        if task == "/budget":
            console.print(ledger.summary())
            continue
        if task == "/stats":
            console.print(system_monitor.stats_text(), highlight=False)
            continue
        if task == "/memory":
            console.print(memory_store.as_text())
            continue
        if task == "/new":
            thread_id = str(uuid.uuid4())
            log("🆕", "Started a fresh chat (memories kept)")
            continue

        try:
            run_task(agent, task, thread_id)
        except ledger.BudgetExceeded as e:
            log("🛑", f"Stopped: {e}", style="bold red")
        except GraphRecursionError:
            log("🛑", f"Stopped: hit the {config.MAX_STEPS}-step limit. Say 'continue' to keep going.", style="bold red")
        except KeyboardInterrupt:
            log("⏹️ ", "Task interrupted by you. Starting a fresh chat.", style="yellow")
            thread_id = str(uuid.uuid4())  # old chat may hold a half-finished step
        except Exception as e:
            log("❌", f"Error: {e}. Starting a fresh chat.", style="bold red")
            thread_id = str(uuid.uuid4())

    close_browser()
    console.print("Bye!")


if __name__ == "__main__":
    main()
