from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.memory import InMemorySaver

import config
from prompts import build_system_prompt
from tools import ALL_TOOLS
from utils import memory_store
from utils.cost_tracker import CostTracker


@dynamic_prompt
def live_prompt(request: ModelRequest) -> str:
    # Rebuilt each call so new memories apply immediately
    return build_system_prompt(memory_store.as_text())


def build_model() -> ChatBedrockConverse:
    return ChatBedrockConverse(
        model=config.MODEL_ID,
        region_name=config.AWS_REGION,
        max_tokens=config.MAX_TOKENS,
        callbacks=[CostTracker()],
    )


def build_agent():
    return create_agent(
        model=build_model(),
        tools=ALL_TOOLS,
        middleware=[live_prompt],
        checkpointer=InMemorySaver(),
    )
