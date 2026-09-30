"""LM Studio local server (OpenAI-compatible, free)."""
import requests

import config
from utils.env import env, env_bool

NAME = "LM Studio (local)"
SETTINGS = {
    "base_url": env("LMSTUDIO_BASE_URL", "http://localhost:1234/v1").rstrip("/"),
    "model": env("LMSTUDIO_MODEL"),
    "input_price": 0.0,
    "output_price": 0.0,
    "vision": env_bool("LMSTUDIO_VISION", False),
}


def _available() -> list[str]:
    response = requests.get(f"{SETTINGS['base_url']}/models", timeout=2)
    response.raise_for_status()
    return [m["id"] for m in response.json().get("data", [])]


def status() -> tuple[bool, str]:
    model = SETTINGS["model"]
    if not model:
        return False, "LMSTUDIO_MODEL missing in .env"
    try:
        available = _available()
    except requests.RequestException:
        return False, f"server not running at {SETTINGS['base_url']} (LM Studio > Developer > Start Server)"
    if model not in available:
        return False, f"{model} not found in LM Studio (available: {', '.join(available[:5]) or 'none'})"
    return True, "server running, model available"


def build(callbacks: list):
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=SETTINGS["model"],
        base_url=SETTINGS["base_url"],
        api_key="lm-studio",  # LM Studio ignores the key but the client needs one
        max_tokens=config.MAX_TOKENS,
        callbacks=callbacks,
    )
