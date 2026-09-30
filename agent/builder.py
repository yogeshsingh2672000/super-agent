from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langgraph.checkpoint.memory import InMemorySaver

from prompts import build_system_prompt
from providers import build_model, supports_vision
from tools import ALL_TOOLS, SCREEN_TOOLS
from utils import memory_store


def build_agent(provider: str):
    vision = supports_vision(provider)
    tools = ALL_TOOLS if vision else [t for t in ALL_TOOLS if t not in SCREEN_TOOLS]

    @dynamic_prompt
    def live_prompt(request: ModelRequest) -> str:
        # Rebuilt each call so new memories apply immediately
        return build_system_prompt(memory_store.as_text(), vision)

    return create_agent(
        model=build_model(provider),
        tools=tools,
        middleware=[live_prompt],
        checkpointer=InMemorySaver(),
    )
