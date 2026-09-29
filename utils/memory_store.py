from datetime import date

import config
from utils.storage import load_json, save_json


def load() -> list[dict]:
    return load_json(config.MEMORY_FILE, [])


def add(fact: str) -> None:
    memories = load()
    memories.append({"fact": fact, "date": str(date.today())})
    save_json(config.MEMORY_FILE, memories)


def remove(index: int) -> str | None:
    """Remove by 1-based index; returns the removed fact."""
    memories = load()
    if not 1 <= index <= len(memories):
        return None
    removed = memories.pop(index - 1)
    save_json(config.MEMORY_FILE, memories)
    return removed["fact"]


def as_text() -> str:
    memories = load()
    if not memories:
        return "No saved memories."
    return "\n".join(f"{i}. {m['fact']}" for i, m in enumerate(memories, 1))
