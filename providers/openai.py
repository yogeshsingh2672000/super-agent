"""OpenAI API."""
import config
from utils.env import env, env_bool, env_float

NAME = "OpenAI"
SETTINGS = {
    "api_key": env("OPENAI_API_KEY"),
    "model": env("OPENAI_MODEL"),
    "base_url": env("OPENAI_BASE_URL"),
    "input_price": env_float("OPENAI_INPUT_PRICE_PER_M"),
    "output_price": env_float("OPENAI_OUTPUT_PRICE_PER_M"),
    "vision": env_bool("OPENAI_VISION", True),
}


def status() -> tuple[bool, str]:
    if not SETTINGS["api_key"]:
        return False, "OPENAI_API_KEY missing in .env"
    if not SETTINGS["model"]:
        return False, "OPENAI_MODEL missing in .env"
    return True, "API key set"


def build(callbacks: list):
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=SETTINGS["model"],
        api_key=SETTINGS["api_key"],
        base_url=SETTINGS["base_url"] or None,
        max_tokens=config.MAX_TOKENS,
        callbacks=callbacks,
    )
