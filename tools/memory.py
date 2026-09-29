from langchain_core.tools import tool

from utils import memory_store
from utils.logger import log


@tool
def remember(fact: str) -> str:
    """Save a lasting fact, preference, goal or rule from the user."""
    memory_store.add(fact)
    log("💾", f'Remembered: "{fact}"', style="green")
    return "Saved to memory."


@tool
def recall() -> str:
    """List all saved memories with their numbers."""
    log("🧠", "Recalling memories")
    return memory_store.as_text()


@tool
def forget(number: int) -> str:
    """Delete a saved memory by its number from recall."""
    removed = memory_store.remove(number)
    if removed is None:
        return f"No memory #{number}."
    log("🧽", f'Forgot: "{removed}"', style="yellow")
    return f"Forgot: {removed}"


TOOLS = [remember, recall, forget]
